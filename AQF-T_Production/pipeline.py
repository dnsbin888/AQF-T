"""
AQF-T Production Pipeline  主管线串联器
===========================================
完整交易主链 (不可绕过):
  Market Regime -> Perception -> Path A/B -> Decision Core -> Risk -> Execution

旁路服务:
  Learning (预测/确认) -> Knowledge Hub (归因/经验/训练)

模式: paper (模拟) / live (实盘)
"""

import yaml
import random
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

from strategy.market_regime import MarketRegimeEngine, MarketRegime
from strategy.rules.sentiment import SentimentEngine
from strategy.rules.dragon import DragonStrategy
from strategy.l2.limitup_perception import LimitUpPerception
from strategy.arbitration import HypothesisArbitrator
from decision_core import DecisionCore, TradingCandidate, TradingSignal
from risk.pre_trade import PreTradeChecker, RiskDecision
from execution.paper_broker import PaperBroker, FillResult
from learning.decision_pipeline import DecisionPipeline, FinalDecision
from learning.plugins.predictor_lgb import AlphaPredictor
from learning.plugins.timing_xgb import TimingPredictor
from learning.plugins.event_llm import EventEngine
from learning.model_registry import ModelRegistry
from learning.backtest_engine import BacktestEngine, BacktestConfig, BacktestResult
from review.factor_attribution import ReviewEngine
from knowledge_hub import KnowledgeHub, StrategyLifecycle, StrategyStatus
from core.event_bus import bus, EVENTS
from core.system_monitor import SystemMonitor
from core.report_writer import ReportWriter


# ===============================================================
# Pipeline State
# ===============================================================

@dataclass
class PipelineState:
    """主管线运行状态  单次交易日"""
    date: str = ""
    mode: str = "paper"                     # paper | live

    # 市场状态
    regime: Optional[MarketRegime] = None
    market_stats: dict = field(default_factory=dict)

    # 候选与信号
    candidates: list = field(default_factory=list)
    signals: list = field(default_factory=list)

    # 风控决策
    risk_decisions: list = field(default_factory=list)

    # 成交结果
    fills: list = field(default_factory=list)

    # 统计
    total_candidates: int = 0
    total_signals: int = 0
    total_fills: int = 0
    total_rejected: int = 0

    # 状态
    tradable: bool = True
    errors: list = field(default_factory=list)


# ===============================================================
# Production Pipeline
# ===============================================================

class ProductionPipeline:
    """
    AQF-T 生产主管线

    串联 Market Regime -> Perception -> Path A/B -> Decision -> Risk -> Execution
    Learning 作为旁路服务提供预测/确认
    Knowledge Hub 记录所有交易和归因

    使用方式:
      pipeline = ProductionPipeline(config)
      pipeline.run_daily(market_stats, watchlist_data)
    """

    def __init__(self, config_path: str = "config/system.yaml"):
        self.config = self._load_config(config_path)
        self.mode = self.config.get("system", {}).get("mode", "paper")

        # -- 一级模块: 交易主链 --
        self.regime_engine = MarketRegimeEngine()
        self.sentiment_engine = SentimentEngine()
        self.dragon = DragonStrategy()
        self.perception = LimitUpPerception()
        self.arbitrator = HypothesisArbitrator()
        self.decision_core = DecisionCore()
        self.risk_checker = PreTradeChecker()

        # -- 行情Provider (GPT P0: 统一接口) --
        from data.market_data_provider import create_provider
        provider_mode = self.config.get("data", {}).get("provider", "simulator")
        self.market_data = create_provider(provider_mode)

        # -- 执行层 --
        initial_cash = 1_000_000.0
        self.broker = PaperBroker(cash=initial_cash)
        self.risk_checker.cash = initial_cash

        # -- 旁路: Learning --
        self.alpha = AlphaPredictor()
        self.timing = TimingPredictor()
        self.event_engine = EventEngine()
        self.learning_pipeline = DecisionPipeline()

        # -- 旁路: Knowledge Hub --
        self.knowledge = KnowledgeHub()
        self.model_registry = ModelRegistry()

        # -- 基础设施 --
        self.monitor = SystemMonitor()
        self.report_writer = ReportWriter()

        # -- 回测引擎 (按需) --
        self.backtest_engine: Optional[BacktestEngine] = None

        # -- 缓存 --
        self._last_regime: Optional[MarketRegime] = None

    # ===========================================================
    # 主循环: 每日运行
    # ===========================================================

    def run_daily(self, market_stats: dict,
                  watchlist: list[dict] = None,
                  event_texts: dict[str, list[str]] = None) -> PipelineState:
        """
        每日主管线运行  完整 M2-M7 链路

        Args:
            market_stats: 全市场统计数据
                {limit_up_count, limit_down_count, max_board_height,
                 炸板率, board_ladder, promotion_rate,
                 north_bound_net, margin_balance_change}
            watchlist: 监控列表, 每个元素为 {symbol, features, l2_features, ctx}
            event_texts: {symbol: [texts]} 各标的关联事件文本

        Returns:
            PipelineState: 本次运行完整状态
        """
        state = PipelineState(
            date=datetime.now().strftime("%Y-%m-%d"),
            mode=self.mode,
        )

        try:
            # -- Phase 1: Market Regime (M2 验证可信) --
            state.regime = self._run_regime(state, market_stats)
            if not state.tradable:
                return state

            # -- Phase 2: 系统健康检查 --
            health = self.monitor.check(mode=self.mode)
            if health.overall == "CRITICAL":
                state.errors.append(f"系统CRITICAL: {health.to_dict()}")
                state.tradable = False
                return state
            bus.publish(EVENTS["MARKET_REGIME"], {
                "regime": state.regime.sentiment_phase,
                "mode": state.regime.operation_mode,
                "health": health.overall,
            }, source="pipeline")

            # -- Phase 3: Perception + Path A/B -> Candidates (M3 决策可解释) --
            if watchlist:
                state.candidates = self._run_perception_and_strategy(
                    state, watchlist, event_texts or {}
                )
            state.total_candidates = len(state.candidates)

            # -- Phase 4: Decision Core (M4 执行可评估) --
            if state.candidates:
                state.signals = self._run_decision(state)
            state.total_signals = len(state.signals)

            # -- Phase 5: Risk -> Execution (M5 策略可证明) --
            if state.signals:
                state.risk_decisions, state.fills = self._run_risk_and_execution(state)
            state.total_fills = len([f for f in state.fills if f.status == "FILLED"])
            state.total_rejected = len([f for f in state.fills if f.status != "FILLED"])

            # -- Phase 6: Knowledge Hub 记录 (M6 系统可自动运行) --
            self._run_knowledge_recording(state)

            # -- Phase 7: 发布事件 (M7 系统可真实运行) --
            self._publish_results(state)

        except Exception as e:
            state.errors.append(f"Pipeline异常: {e}")
            bus.publish(EVENTS["KILL_SWITCH"], {
                "reason": str(e),
                "state": state.date,
            }, source="pipeline")

        return state

    # ===========================================================
    # Phase 1: Market Regime
    # ===========================================================

    def _run_regime(self, state: PipelineState,
                    market_stats: dict) -> MarketRegime:
        """市场状态评估  总开关"""
        state.market_stats = market_stats

        # 双引擎评估 (互相校验)
        regime = self.regime_engine.evaluate(market_stats)
        sentiment = self.sentiment_engine.evaluate(market_stats)

        # 一致性检查: 如果两引擎矛盾, 以更保守的为准
        if regime.operation_mode == "aggressive" and sentiment.phase == "退潮期":
            # 降级到 cautious
            regime.operation_mode = "cautious"
            regime.path_a_allowed = False
            regime.max_position_pct = 0.20

        self._last_regime = regime

        # 退潮/停止 -> 不交易
        if regime.operation_mode == "stop":
            state.tradable = False
            state.errors.append(f"Regime=stop ({regime.sentiment_phase}), 今日不交易")

        return regime

    # ===========================================================
    # Phase 2: Perception + Path A/B
    # ===========================================================

    def _run_perception_and_strategy(self, state: PipelineState,
                                     watchlist: list[dict],
                                     event_texts: dict[str, list[str]]) -> list[TradingCandidate]:
        """运行 Perception + Path A/B, 产出 TradingCandidate 列表"""
        candidates = []

        for stock in watchlist:
            symbol = stock.get("symbol", "")
            ctx = stock.get("ctx", {})
            features = stock.get("features", {})
            l2_features = stock.get("l2_features", {})

            try:
                # -- Path A: 回封板 (规则驱动, Perception优先) --
                if state.regime.path_a_allowed:
                    path_a_candidate = self._run_path_a(symbol, ctx, features)
                    if path_a_candidate:
                        candidates.append(path_a_candidate)
                        bus.publish(EVENTS["SIGNAL_A"], {
                            "symbol": symbol, "score": path_a_candidate.score,
                            "confidence": path_a_candidate.confidence,
                        }, source="path_a")

                # -- Path B: 半路/接力 (ML统计驱动) --
                if state.regime.path_b_allowed:
                    path_b_candidate = self._run_path_b(
                        symbol, features, l2_features,
                        event_texts.get(symbol, [])
                    )
                    if path_b_candidate:
                        candidates.append(path_b_candidate)
                        bus.publish(EVENTS["SIGNAL_B"], {
                            "symbol": symbol, "score": path_b_candidate.score,
                            "confidence": path_b_candidate.confidence,
                        }, source="path_b")

            except Exception as e:
                state.errors.append(f"{symbol}: {e}")
                continue

        return candidates

    def _run_path_a(self, symbol: str, ctx: dict,
                    features: dict) -> Optional[TradingCandidate]:
        """
        Path A  回封板
        漏斗: 板块地位 -> 炸板分类 -> 回封确认
        纯规则驱动, 不用ML
        """
        # Perception 综合判断
        should_enter, reason, confidence = self.perception.should_enter(ctx)

        if not should_enter:
            return None

        # Dragon 龙头判定加分 (归一化: 龙头=1.0, 非龙头=0)
        dragon_signal = self.dragon.is_dragon(ctx)
        dragon_score = 1.0 if dragon_signal.is_dragon else 0.0

        # 综合评分 (GPT Q2: 归一化权重, Pattern之间可比较)
        # Score = 0.5*Confidence + 0.3*Position + 0.2*Reseal + 0.1*Dragon
        board_status = self.perception.evaluate_board_status(ctx)
        reseal_quality = self.perception.evaluate_reseal(ctx)

        normalized_score = (
            0.50 * confidence +
            0.30 * board_status.position_score +
            0.20 * reseal_quality.total_score +
            0.10 * dragon_score
        )
        score = normalized_score * 100  # 转为0-100与Path B统一

        # 仓位: 主线15%, 次线8%
        position_hint = 0.15 if board_status.is_main_theme else 0.08

        return TradingCandidate(
            symbol=symbol,
            strategy="reseal",
            score=min(score, 100),
            confidence=confidence,
            expected_return=0.05 if board_status.is_main_theme else 0.03,
            risk=30 if dragon_signal.is_dragon else 50,
            position_hint=position_hint,
            evidence={
                "score_version": "pathA_v1",   # GPT V1.1: 权重版本追踪
                "board_status": board_status.position_score,
                "is_main_theme": board_status.is_main_theme,
                "break_type": self.perception.classify_break(ctx).type,
                "reseal_score": reseal_quality.total_score,
                "is_dragon": dragon_signal.is_dragon,
                "dragon_score": dragon_score,
                "normalized_score": round(normalized_score, 3),
                "reason": reason,
            },
            path="A",
        )

    def _run_path_b(self, symbol: str, features: dict,
                    l2_features: dict,
                    event_texts: list[str]) -> Optional[TradingCandidate]:
        """
        Path B  半路/接力
        B1 Trend(LGBM) / B2 Theme(规则) / B3 Intraday(XGBoost确认)
        ML统计驱动
        """
        # B1: Alpha预测 (LGBM)
        alpha_signal = self.alpha.predict(features)

        # B3: Timing确认 (XGBoost)
        timing_signal = self.timing.predict(l2_features)

        # B2: 题材热度 (规则)
        theme_heat = features.get("theme_heat", 0)
        sector_score = features.get("sector_score", 0)

        # Event分析 (GPT V1.1: evidence-rich override)
        event_signal = self.event_engine.analyze(symbol, event_texts)
        override = self.event_engine.should_override(event_signal)

        # Event阻止/降权 (GPT V1.1: dict with evidence)
        event_action = None
        event_evidence = {}
        if override:
            event_action = override.get("action", "")
            event_evidence = override.get("evidence", {})

        if event_action == "BLOCK":
            return None

        # Alpha必须方向明确
        if alpha_signal.direction != "BUY":
            return None

        # 综合评分
        score = (
            alpha_signal.confidence * 40 +
            timing_signal.confidence * 25 +
            theme_heat * 20 +
            sector_score * 15
        )

        # Event降权
        if event_action == "REDUCE":
            score *= 0.7

        if score < 40:
            return None

        # 仓位: 基于Regime上限  Alpha置信度
        position_hint = min(
            alpha_signal.confidence * 0.15,
            theme_heat * 0.10 if theme_heat > 0.5 else 0.05
        )

        return TradingCandidate(
            symbol=symbol,
            strategy="trend" if theme_heat < 0.7 else "theme",
            score=min(score, 100),
            confidence=alpha_signal.confidence,
            expected_return=alpha_signal.expected_return,
            risk=40 if timing_signal.timing == "NOW" else 55,
            position_hint=min(position_hint, 0.10),
            evidence={
                "score_version": "pathB_v1",
                "alpha_direction": alpha_signal.direction,
                "alpha_prob": alpha_signal.probability,
                "timing": timing_signal.timing,
                "timing_confidence": timing_signal.confidence,
                "theme_heat": theme_heat,
                "event_direction": event_signal.direction,
                "event_impact": event_signal.impact_score,
                "event_action": event_action,
                "event_evidence": event_evidence,
            },
            path="B1" if theme_heat < 0.7 else "B2",
        )

    # ===========================================================
    # Phase 3: Decision Core
    # ===========================================================

    def _run_decision(self, state: PipelineState) -> list[TradingSignal]:
        """决策中枢: 收集候选 -> 排序 -> 冲突消解 -> 仓位分配"""
        current_positions = {
            sym: {"shares": p["shares"], "available": p.get("available", p["shares"])}
            for sym, p in self.broker.positions.items()
        }

        # 仓位 = base  confidence_multiplier  regime_multiplier (GPT V1.1)
        confidence = state.regime.regime_confidence if state.regime else 1.0
        if confidence >= 0.8:
            confidence_mult = 1.0
        elif confidence >= 0.6:
            confidence_mult = 0.70
        else:
            confidence_mult = 0.50

        regime_mult = state.regime.regime_multiplier if state.regime else 1.0
        final_multiplier = confidence_mult * regime_mult

        # 调整 Regime max_position
        original_max = state.regime.max_position_pct
        state.regime.max_position_pct = original_max * final_multiplier

        # 喂入所有候选
        self.decision_core.collect(state.candidates)

        # 执行决策
        signals = self.decision_core.decide(state.regime, current_positions)

        # 恢复原始值 (不影响日志)
        state.regime.max_position_pct = original_max

        return signals

    # ===========================================================
    # Phase 4: Risk -> Execution
    # ===========================================================

    def _run_risk_and_execution(self, state: PipelineState) -> tuple[list, list]:
        """风控审批 + 订单执行 (含 GPT Q3 Portfolio Exposure)"""
        from core.clock import clock

        risk_decisions = []
        fills = []

        for signal in state.signals:
            # 获取标的相关候选的 sector 信息
            matching_candidate = next(
                (c for c in state.candidates if c.symbol == signal.symbol),
                None
            )
            sector = matching_candidate.evidence.get("sector", "") if matching_candidate else ""

            # -- Risk Check (最高否决权, 不可绕过) --
            risk_decision = self.risk_checker.check(
                symbol=signal.symbol,
                action=signal.action,
                qty=int(signal.position_pct * 10000),  # 仓位% -> 股数估算
                price=self._estimate_price(signal.symbol),
                risk_score=int((1 - signal.confidence) * 100),
                sentiment_phase=state.regime.sentiment_phase,
                sector=sector,  # GPT Q3: 板块集中度
            )
            risk_decisions.append(risk_decision)

            bus.publish(EVENTS["RISK_DECISION"], {
                "symbol": signal.symbol,
                "decision": risk_decision.decision,
                "reason": risk_decision.reason,
            }, source="risk")

            # -- REJECT -> 跳过 --
            if risk_decision.decision == "REJECT":
                bus.publish(EVENTS["ORDER_REJECTED"], {
                    "symbol": signal.symbol,
                    "reason": risk_decision.reason,
                }, source="risk")
                fills.append(FillResult(
                    order_id=f"{signal.symbol}-{clock.now().timestamp()}",
                    symbol=signal.symbol,
                    action=signal.action,
                    requested_price=0, fill_price=0, fill_quantity=0,
                    slippage_bps=0, fee=0,
                    status="REJECTED",
                    reason=risk_decision.reason,
                    timestamp=clock.now_iso(),
                ))
                continue

            # -- 确定最终数量 --
            final_qty = risk_decision.adjusted_qty if risk_decision.adjusted_qty > 0 else int(signal.position_pct * 10000)
            final_qty = max(100, (final_qty // 100) * 100)  # 100股整数倍

            # -- Execution --
            order = {
                "order_id": f"{signal.symbol}-{clock.now().timestamp()}",
                "symbol": signal.symbol,
                "action": signal.action,
                "quantity": final_qty,
                "price": self._estimate_price(signal.symbol),
                "confidence": signal.confidence,
            }

            bus.publish(EVENTS["ORDER_CREATED"], order, source="execution")

            if self.mode == "live":
                # TODO: 实盘接入国金QMT xttrader.order()
                fill = FillResult(
                    order_id=order["order_id"],
                    symbol=signal.symbol,
                    action=signal.action,
                    requested_price=order["price"],
                    fill_price=order["price"],
                    fill_quantity=final_qty,
                    slippage_bps=0,
                    fee=0,
                    status="FILLED",
                    reason="Live QMT (待接入)",
                    timestamp=clock.now_iso(),
                )
            else:
                # Paper Trading
                fill = self.broker.simulate_fill(
                    order=order,
                    market_price=order["price"],
                )

            fills.append(fill)

            # GPT Q3: 记录成交到 Risk Checker (更新敞口)
            if fill.status == "FILLED" and signal.action == "BUY":
                self.risk_checker.record_fill(
                    symbol=signal.symbol,
                    price=fill.fill_price,
                    qty=fill.fill_quantity,
                    action=signal.action,
                    sector=sector,
                )

            bus.publish(EVENTS["ORDER_FILLED"], {
                "symbol": signal.symbol, "status": fill.status,
                "fill_price": fill.fill_price, "qty": fill.fill_quantity,
            }, source="execution")

        return risk_decisions, fills

    # ===========================================================
    # Phase 5: Knowledge Hub 记录
    # ===========================================================

    def _run_knowledge_recording(self, state: PipelineState):
        """记录所有交易到 Knowledge Hub"""
        for fill in state.fills:
            if fill.status == "FILLED":
                # 找到对应的 signal
                matching_signal = next(
                    (s for s in state.signals if s.symbol == fill.symbol),
                    None
                )

                trade_record = {
                    "id": fill.order_id,
                    "symbol": fill.symbol,
                    "pnl_pct": 0,  # 待实际平仓后更新
                    "sentiment_phase": state.regime.sentiment_phase,
                    "board_type": "回封板" if (matching_signal and matching_signal.strategy == "reseal") else "半路",
                    "seal_quality": 0.7,
                    "alpha_confidence": matching_signal.confidence if matching_signal else 0,
                    "reseal_score": 0.7,
                    "opponent_type": "Hot_Money",
                }
                self.knowledge.record_trade(trade_record)

    # ===========================================================
    # Phase 6: 发布结果
    # ===========================================================

    def _publish_results(self, state: PipelineState):
        """发布日终结果"""
        summary = {
            "date": state.date,
            "regime": state.regime.sentiment_phase if state.regime else "UNKNOWN",
            "mode": state.regime.operation_mode if state.regime else "UNKNOWN",
            "candidates": state.total_candidates,
            "signals": state.total_signals,
            "fills": state.total_fills,
            "rejected": state.total_rejected,
            "errors": len(state.errors),
            "account": self.broker.summary(),
        }
        bus.publish(EVENTS["DAILY_REPORT"], summary, source="pipeline")

        # -- 持久化报告 (GPT P0-3) --
        try:
            report_path = self.report_writer.write_daily_report(state, self)
            if state.fills:
                self.report_writer.write_execution_report(state.fills, state.date)
        except Exception as e:
            state.errors.append(f"Report persist error: {e}")

        # 日终报告
        if state.regime:
            report = self.knowledge.daily_report(
                state.regime,
                self.broker.positions,
                state.signals,
            )
        else:
            report = f"AQF-T {state.date}  未交易"

    # ===========================================================
    # 回测模式
    # ===========================================================

    def run_backtest(self, data: dict, signals: list[dict],
                     config: BacktestConfig = None) -> BacktestResult:
        """运行回测"""
        if config is None:
            config = BacktestConfig()
        self.backtest_engine = BacktestEngine(config)
        return self.backtest_engine.run(data, signals)

    # ===========================================================
    # Utilities
    # ===========================================================

    def _estimate_price(self, symbol: str) -> float:
        """获取当前价格  通过 MarketDataProvider 统一接口 (GPT P0)"""
        snap = self.market_data.get_snapshot(symbol)
        if snap.price > 0:
            return snap.price
        # 终极fallback (不应到达)
        return 25.0

    def _load_config(self, path: str) -> dict:
        p = Path(path)
        if p.exists():
            return yaml.safe_load(p.read_text(encoding="utf-8"))
        return {}

    # ===========================================================
    # 状态查询
    # ===========================================================

    def status(self) -> dict:
        """获取管道运行状态"""
        return {
            "mode": self.mode,
            "last_regime": self._last_regime.sentiment_phase if self._last_regime else None,
            "account": self.broker.summary(),
            "positions": len(self.broker.positions),
            "trades_today": len(self.broker.trades),
            "health": self.monitor.check(mode=self.mode).to_dict(),
        }

    def daily_summary(self, state: PipelineState) -> str:
        """生成日终摘要"""
        if not state.regime:
            return f"AQF-T {state.date}  Pipeline未运行"

        lines = [
            f"{'='*60}",
            f"  AQF-T Production  {state.date}",
            f"  Regime: {state.regime.sentiment_phase} ({state.regime.operation_mode})",
            f"  PathA: {'[OK]' if state.regime.path_a_allowed else '[FAIL]'}  PathB: {'[OK]' if state.regime.path_b_allowed else '[FAIL]'}",
            f"  MaxPosition: {state.regime.max_position_pct:.0%}",
            f"",
            f"  Candidates: {state.total_candidates}",
            f"  Signals:    {state.total_signals}",
            f"  Fills:      {state.total_fills}",
            f"  Rejected:   {state.total_rejected}",
            f"  Errors:     {len(state.errors)}",
            f"",
            f"  Account: {self.broker.summary()}",
            f"{'='*60}",
        ]

        if state.fills:
            lines.append("\n  Fills:")
            for f in state.fills:
                status_icon = "[OK]" if f.status == "FILLED" else "[FAIL]"
                lines.append(
                    f"    {status_icon} {f.symbol} {f.action} "
                    f"{f.fill_quantity}股 @{f.fill_price:.2f} "
                    f"[{f.status}] {f.reason}"
                )

        if state.errors:
            lines.append(f"\n  [WARN] Errors:")
            for e in state.errors:
                lines.append(f"    - {e}")

        return "\n".join(lines)


# ===============================================================
# Canonical Alias
# ===============================================================

# 统一入口名：AQFTPipeline = ProductionPipeline
# 使用: from pipeline import AQFTPipeline
AQFTPipeline = ProductionPipeline

# ===============================================================
# 工厂函数
# ===============================================================

def create_pipeline(mode: str = "paper") -> ProductionPipeline:
    """创建管道实例"""
    # 确保 mode 写入配置
    config_path = Path("config/system.yaml")
    if config_path.exists():
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        config["system"]["mode"] = mode
        config_path.write_text(
            yaml.dump(config, allow_unicode=True, default_flow_style=False),
            encoding="utf-8"
        )
    return ProductionPipeline(str(config_path))
