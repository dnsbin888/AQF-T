"""
Decision Core — 唯一决策中枢
统一Candidate接口: 所有策略输出Candidate, 不是BUY指令
"""
from dataclasses import dataclass, field
from typing import Optional
from strategy.market_regime import MarketRegime


@dataclass
class TradingCandidate:
    """统一候选 — 所有策略(Path A/B/未来新策略)统一输出此格式"""
    symbol: str
    strategy: str            # reseal / trend / theme / intraday / ...
    score: float             # 综合评分 0-100
    confidence: float        # 0-1
    expected_return: float   # 预期收益
    risk: float              # 风险评分 0-100
    position_hint: float     # 建议仓位
    evidence: dict = field(default_factory=dict)  # 决策依据
    path: str = ""           # A / B1 / B2 / B3


@dataclass
class TradingSignal:
    """最终交易信号 — Decision输出"""
    symbol: str
    action: str              # BUY / SELL / HOLD
    strategy: str
    position_pct: float
    confidence: float
    reasoning: str


class DecisionCore:
    """
    唯一决策中枢

    接收: TradingCandidate列表 (来自Path A/B/未来新策略)
    处理: 排序→冲突消解→仓位优化
    输出: TradingSignal列表 (统一格式, 进入Risk)
    """

    def __init__(self):
        self.candidates: list[TradingCandidate] = []

    def collect(self, candidates: list[TradingCandidate]):
        """收集所有策略的候选"""
        self.candidates.extend(candidates)

    def decide(self, regime: MarketRegime,
               current_positions: dict) -> list[TradingSignal]:
        """
        核心决策流程:
          1. Regime过滤
          2. 评分排序
          3. 冲突消解 (同标的多个信号→取最高分)
          4. 仓位分配 (A优先, 总上限控制)
          5. 输出统一TradingSignal
        """

        # ── Regime过滤 ──
        if regime.operation_mode == "stop":
            return []

        active = [c for c in self.candidates
                  if (c.path == "A" and regime.path_a_allowed) or
                     (c.path.startswith("B") and regime.path_b_allowed)]

        # ── 评分排序 ──
        active.sort(key=lambda c: c.score, reverse=True)

        # ── 冲突消解 (同标的取最高分) ──
        seen = {}
        for c in active:
            if c.symbol not in seen or c.score > seen[c.symbol].score:
                seen[c.symbol] = c
        unique = list(seen.values())
        unique.sort(key=lambda c: c.score, reverse=True)

        # ── 仓位分配 ──
        signals = []
        remaining = regime.max_position_pct

        for c in unique:
            if remaining <= 0.05:
                break
            pos = min(c.position_hint, remaining)
            signals.append(TradingSignal(
                symbol=c.symbol,
                action="BUY" if c.score > 50 else "HOLD",
                strategy=c.strategy,
                position_pct=round(pos, 2),
                confidence=c.confidence,
                reasoning=f"{c.strategy}: score={c.score:.0f}, risk={c.risk:.0f}",
            ))
            remaining -= pos

        # ── 清空, 准备下一轮 ──
        self.candidates = []

        return signals
