"""
四维决策 Pipeline — 串联融合四个模型
  Alpha(LGBM) × Timing(XGBoost) × Regime(规则) × Event(LLM)
"""
from dataclasses import dataclass
from typing import Optional
from strategy.rules.sentiment import SentimentEngine, SentimentReport
from learning.plugins.predictor_lgb import AlphaPredictor, AlphaSignal
from learning.plugins.timing_xgb import TimingPredictor, TimingSignal
from learning.plugins.event_llm import EventEngine, EventSignal


@dataclass
class FinalDecision:
    action: str              # BUY / SELL / HOLD
    position_pct: float      # 建议仓位
    confidence: float        # 综合置信度
    alpha_signal: Optional[AlphaSignal] = None
    timing_signal: Optional[TimingSignal] = None
    regime_report: Optional[SentimentReport] = None
    event_signal: Optional[EventSignal] = None
    reason: str = ""


class DecisionPipeline:
    """
    四维决策 Pipeline (串联, 不是Ensemble投票)

    选什么 → 何时进 → 做多少 → 有新信息吗
     LGBM    XGBoost   Regime    Event
    """

    def __init__(self):
        self.alpha = AlphaPredictor()
        self.timing = TimingPredictor()
        self.regime = SentimentEngine()
        self.event = EventEngine()

    def decide(self, symbol: str,
               features: dict,
               l2_features: dict,
               market_stats: dict,
               event_texts: list[str]) -> FinalDecision:
        """
        四维串联决策
        """

        # 维度1: Alpha — 选什么
        alpha = self.alpha.predict(features)

        # 维度2: Timing — 何时进
        timing = self.timing.predict(l2_features)

        # 维度3: Regime — 做多少 (最高优先级)
        regime = self.regime.evaluate(market_stats)

        # 维度4: Event — 有新信息吗
        event = self.event.analyze(symbol, event_texts)

        # ── 融合决策 ──

        # Regime 否决 (最高优先级)
        if regime.phase == "退潮期":
            return FinalDecision(
                action="HOLD", position_pct=0.0, confidence=0.95,
                alpha_signal=alpha, timing_signal=timing,
                regime_report=regime, event_signal=event,
                reason=f"退潮期禁止买入 (情绪值={regime.score:.0f})",
            )

        # Alpha 为空
        if alpha.direction == "HOLD":
            return FinalDecision(
                action="HOLD", position_pct=0.0, confidence=0.60,
                alpha_signal=alpha, timing_signal=timing,
                regime_report=regime, event_signal=event,
                reason="Alpha信号=HOLD",
            )

        # Alpha 卖出
        if alpha.direction == "SELL":
            return FinalDecision(
                action="SELL", position_pct=0.0, confidence=alpha.confidence,
                alpha_signal=alpha, timing_signal=timing,
                regime_report=regime, event_signal=event,
                reason=f"Alpha信号=SELL (prob={alpha.probability:.2f})",
            )

        # Alpha 买入 — 检查 Timing + Regime + Event
        base_position = regime.recommend_position  # Regime决定仓位上限

        # Timing 调节
        if timing.timing == "NOW":
            position = base_position
            timing_adj = ""
        else:
            position = base_position * 0.5  # 时机不对, 降半仓
            timing_adj = ", 时机=WAIT降半仓"

        # Event 调节
        override = self.event.should_override(event)
        if override == "BLOCK":
            return FinalDecision(
                action="HOLD", position_pct=0.0, confidence=0.80,
                alpha_signal=alpha, timing_signal=timing,
                regime_report=regime, event_signal=event,
                reason=f"Event阻止: {event.summary}",
            )
        elif override == "REDUCE":
            position *= 0.5
            timing_adj += ", Event利空降半仓"

        # 综合置信度
        confidence = (
            alpha.confidence * 0.40 +
            timing.confidence * 0.20 +
            (1.0 if regime.phase in ("高潮期", "回暖期") else 0.5) * 0.25 +
            (0.8 if event.direction == "POSITIVE" else 0.5) * 0.15
        )

        return FinalDecision(
            action="BUY",
            position_pct=round(position, 2),
            confidence=round(confidence, 2),
            alpha_signal=alpha, timing_signal=timing,
            regime_report=regime, event_signal=event,
            reason=f"Alpha=BUY{timing_adj}, Regime={regime.phase}, Event={event.direction}",
        )
