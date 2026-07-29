"""
M5 Backtest Runner — Pattern统计证据生成器
"""
import random
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BacktestResult:
    pattern_name: str
    sample_size: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    avg_return: float = 0.0
    regime_distribution: dict = field(default_factory=dict)

    def summary(self) -> str:
        return (
            f"{self.pattern_name}: Samples={self.sample_size} "
            f"WinRate={self.win_rate:.1%} PF={self.profit_factor:.2f} "
            f"MaxDD={self.max_drawdown:.1%}"
        )


class BacktestRunner:
    def run(self, pattern_name: str, trades: list[dict]) -> BacktestResult:
        if not trades:
            return BacktestResult(pattern_name=pattern_name)
        wins = [t for t in trades if t.get("pnl_pct", 0) > 0]
        losses = [t for t in trades if t.get("pnl_pct", 0) <= 0]
        returns = [t.get("pnl_pct", 0) for t in trades]
        gross_profit = sum(t["pnl_pct"] for t in wins)
        gross_loss = abs(sum(t["pnl_pct"] for t in losses))
        peak = cumulative = max_dd = 0
        for r in returns:
            cumulative += r
            if cumulative > peak: peak = cumulative
            if cumulative < peak: max_dd = max(max_dd, peak - cumulative)
        regimes = {}
        for t in trades:
            r = t.get("regime", "unknown")
            regimes[r] = regimes.get(r, 0) + 1
        return BacktestResult(
            pattern_name=pattern_name, sample_size=len(trades),
            win_rate=round(len(wins)/len(trades), 4),
            profit_factor=round(gross_profit/gross_loss, 2) if gross_loss > 0 else 0,
            max_drawdown=round(max_dd, 4),
            avg_return=round(sum(returns)/len(trades), 4),
            regime_distribution=regimes,
        )
