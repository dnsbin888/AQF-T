"""
A股 T+1 交易规则引擎
当日买入 → 次日才能卖出
"""
from datetime import datetime, date
from dataclasses import dataclass, field


@dataclass
class Position:
    symbol: str
    shares: int
    avg_cost: float
    buy_date: date
    available_shares: int = 0  # 可卖数量
    locked_shares: int = 0     # T+1 锁定数量

    def __post_init__(self):
        self.locked_shares = self.shares
        self.available_shares = 0

    def can_sell(self, target_date: date) -> int:
        """T+1: 当日买入的股票次日才能卖出"""
        if target_date > self.buy_date:
            return self.shares  # 次日全部可卖
        return 0  # 当日不可卖

    def refresh(self, target_date: date):
        """每日刷新可卖数量"""
        self.available_shares = self.can_sell(target_date)
        self.locked_shares = self.shares - self.available_shares


class TPlusOneEngine:
    """A股 T+1 引擎"""

    def __init__(self):
        self.positions: dict[str, Position] = {}

    def buy(self, symbol: str, shares: int, price: float, trade_date: date) -> Position:
        """买入 — 当日锁定"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            total_cost = pos.avg_cost * pos.shares + price * shares
            pos.shares += shares
            pos.avg_cost = total_cost / pos.shares if pos.shares > 0 else 0
            pos.locked_shares += shares
        else:
            self.positions[symbol] = Position(
                symbol=symbol, shares=shares,
                avg_cost=price, buy_date=trade_date,
                available_shares=0, locked_shares=shares
            )
        return self.positions[symbol]

    def sell(self, symbol: str, shares: int, trade_date: date) -> tuple[int, str]:
        """卖出 — 只能卖 available 的"""
        pos = self.positions.get(symbol)
        if not pos:
            return 0, f"无持仓: {symbol}"

        pos.refresh(trade_date)
        if shares > pos.available_shares:
            return 0, f"T+1限制: 可卖{pos.available_shares}股, 请求{shares}股"

        pos.shares -= shares
        pos.available_shares -= shares
        return shares, "OK"

    def refresh_all(self, trade_date: date):
        """盘前刷新所有持仓"""
        for pos in self.positions.values():
            pos.refresh(trade_date)

    def summary(self) -> dict:
        return {
            symbol: {
                "shares": p.shares, "available": p.available_shares,
                "locked": p.locked_shares, "buy_date": str(p.buy_date)
            }
            for symbol, p in self.positions.items() if p.shares > 0
        }
