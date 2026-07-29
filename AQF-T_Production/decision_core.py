"""
Decision Core — 融合/优先级/冲突解决/仓位分配
职责: 选谁? 多少? (Risk只管合法/超仓/熔断)
"""
from dataclasses import dataclass
from typing import Optional
from strategy.market_regime import MarketRegime
from strategy.arbitration import HypothesisArbitrator, ArbitrationResult


@dataclass
class UnifiedSignal:
    """统一交易信号 — Decision输出"""
    symbol: str
    action: str          # BUY / SELL / HOLD
    path: str            # A(回封板) / B1(Trend) / B2(Theme) / B3(Intraday)
    position_pct: float
    confidence: float
    reason: str


class DecisionCore:
    """
    决策核心 — Strategy和Risk之间的独立层

    职责:
      ① 融合 Path A 和 Path B 的信号
      ② 冲突解决 (用Hypothesis Arbitration)
      ③ 仓位分配 (A优先于B)
      ④ 输出统一TradingSignal
    """

    def __init__(self):
        self.arbitrator = HypothesisArbitrator()

    def decide(self, path_a_signals: list[dict],
               path_b_signals: list[dict],
               regime: MarketRegime,
               current_positions: dict) -> list[UnifiedSignal]:
        """
        核心决策:
          1. Regime过滤 (退潮→全部拒绝)
          2. 路径融合 (A优先于B)
          3. 仓位分配 (总仓位上限控制)
        """

        # ── Regime总开关 ──
        if not regime.path_a_allowed:
            path_a_signals = []
        if not regime.path_b_allowed:
            path_b_signals = []

        all_signals = []

        # ── Path A 优先处理 (确定性更高) ──
        remaining_position = regime.max_position_pct
        for sig in path_a_signals:
            if remaining_position <= 0:
                break
            pos = min(sig.get("position_pct", 0.10), remaining_position)
            all_signals.append(UnifiedSignal(
                symbol=sig["symbol"], action=sig.get("action", "BUY"),
                path="A", position_pct=round(pos, 2),
                confidence=sig.get("confidence", 0.7),
                reason=sig.get("reason", ""),
            ))
            remaining_position -= pos

        # ── Path B 剩余仓位 ──
        for sig in path_b_signals:
            if remaining_position <= 0.05:  # <5%不做
                break
            pos = min(sig.get("position_pct", 0.05), remaining_position)
            all_signals.append(UnifiedSignal(
                symbol=sig["symbol"], action=sig.get("action", "BUY"),
                path=sig.get("path", "B"),
                position_pct=round(pos, 2),
                confidence=sig.get("confidence", 0.5),
                reason=sig.get("reason", ""),
            ))
            remaining_position -= pos

        return all_signals
