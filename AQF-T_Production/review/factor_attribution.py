"""
Factor Attribution — 因子归因复盘
回答: 哪笔赚的? 哪个因子贡献的? 哪个拖后腿?
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TradeAttribution:
    trade_id: str
    symbol: str
    pnl_pct: float
    entry_signals: dict          # {signal_name: contribution}
    regret: Optional[str] = None # 如果有幸存者偏差


class ReviewEngine:
    """复盘引擎"""

    def __init__(self):
        self.trades: list[TradeAttribution] = []
        self.success_cases: list[dict] = []
        self.failure_cases: list[dict] = []

    def attribute(self, trade: dict) -> TradeAttribution:
        """归因单笔交易到具体因子"""
        signals = {}

        # 情绪周期贡献
        phase = trade.get("sentiment_phase", "")
        if phase == "高潮期":
            signals["情绪周期"] = 0.30
        elif phase == "回暖期":
            signals["情绪周期"] = 0.20
        elif phase == "退潮期":
            signals["情绪周期"] = -0.30  # 逆势交易
        elif phase == "冰点期":
            signals["情绪周期"] = 0.05

        # 板型贡献
        board = trade.get("board_type", "")
        if board == "换手板":
            signals["板型"] = 0.25
        elif board == "回封板":
            signals["板型"] = 0.30
        elif board == "烂板":
            signals["板型"] = -0.20

        # L2信号贡献
        if trade.get("seal_quality", 0) > 0.7:
            signals["封单质量"] = 0.20
        if trade.get("opponent_type") == "Hot_Money":
            signals["游资接力"] = 0.15
        elif trade.get("opponent_type") == "Quant":
            signals["量化干扰"] = -0.20

        # Alpha贡献
        if trade.get("alpha_confidence", 0) > 0.7:
            signals["Alpha模型"] = 0.15

        # 回封贡献
        if trade.get("reseal_score", 0) > 0.7:
            signals["回封确认"] = 0.25

        attr = TradeAttribution(
            trade_id=trade.get("id", ""),
            symbol=trade.get("symbol", ""),
            pnl_pct=trade.get("pnl_pct", 0),
            entry_signals=signals,
        )
        self.trades.append(attr)

        # 归类经验
        if attr.pnl_pct > 0.03:
            self.success_cases.append(trade)
        elif attr.pnl_pct < -0.02:
            self.failure_cases.append({
                **trade,
                "failure_reason": self._diagnose_failure(trade, signals),
            })

        return attr

    def _diagnose_failure(self, trade: dict, signals: dict) -> str:
        """诊断失败原因"""
        reasons = []
        if trade.get("sentiment_phase") == "退潮期":
            reasons.append("退潮期不应交易")
        if trade.get("board_type") == "烂板":
            reasons.append("烂板打板风险高")
        if trade.get("opponent_type") == "Quant":
            reasons.append("量化主导应回避")
        if trade.get("reseal_score", 1) < 0.5:
            reasons.append("回封质量不足")
        if trade.get("alpha_confidence", 1) < 0.6:
            reasons.append("Alpha信号弱")
        return "; ".join(reasons) if reasons else "多因素综合"

    def summary(self) -> dict:
        """归因总结"""
        if not self.trades:
            return {"total": 0}

        wins = [t for t in self.trades if t.pnl_pct > 0]
        losses = [t for t in self.trades if t.pnl_pct <= 0]

        # 归因聚合
        top_signals = {}
        for t in wins:
            for sig, contrib in t.entry_signals.items():
                top_signals[sig] = top_signals.get(sig, 0) + contrib

        return {
            "total_trades": len(self.trades),
            "win_rate": len(wins) / len(self.trades) if self.trades else 0,
            "avg_win": sum(t.pnl_pct for t in wins) / len(wins) if wins else 0,
            "avg_loss": sum(t.pnl_pct for t in losses) / len(losses) if losses else 0,
            "top_contributing_signals": sorted(top_signals.items(), key=lambda x: -x[1])[:5],
            "success_cases": len(self.success_cases),
            "failure_cases": len(self.failure_cases),
        }
