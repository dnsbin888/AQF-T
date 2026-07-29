"""
Paper Broker — 模拟交易引擎
模拟: 滑点/手续费/涨跌停/排队/撤单
"""
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FillResult:
    order_id: str
    symbol: str
    action: str
    requested_price: float
    fill_price: float
    fill_quantity: int
    slippage_bps: float
    fee: float
    status: str            # FILLED / PARTIAL / REJECTED / QUEUED
    reason: str
    timestamp: str


class PaperBroker:
    """模拟交易引擎"""

    def __init__(self, cash: float = 1_000_000.0):
        self.cash = cash
        self.positions: dict[str, dict] = {}
        self.orders: list[dict] = []
        self.trades: list[FillResult] = []

        # A股费率
        self.COMMISSION = 0.00025   # 佣金0.025%
        self.STAMP_TAX = 0.001      # 印花税(仅卖出)
        self.TRANSFER = 0.00001     # 过户费
        self.MIN_COMMISSION = 5.0   # 最低佣金

    def simulate_fill(self, order: dict, market_price: float,
                      is_limit_up: bool = False,
                      is_limit_down: bool = False) -> FillResult:
        """模拟成交"""
        symbol = order.get("symbol", "")
        action = order.get("action", "BUY")
        qty = order.get("quantity", 0)
        price = order.get("price", market_price)
        order_id = order.get("order_id", "")

        # ── 涨跌停检查 ──
        if action == "BUY" and is_limit_up:
            return FillResult(order_id, symbol, action, price, 0, 0, 0, 0,
                              "QUEUED", "涨停封死, 排队中", datetime.now().isoformat())
        if action == "SELL" and is_limit_down:
            return FillResult(order_id, symbol, action, price, 0, 0, 0, 0,
                              "QUEUED", "跌停封死, 排队中", datetime.now().isoformat())

        # ── 滑点 (买入+0.1%~0.3%, 卖出-0.1%~0.3%) ──
        slip = random.uniform(0.001, 0.003)
        if action == "BUY":
            fill_price = market_price * (1 + slip)
        else:
            fill_price = market_price * (1 - slip)
        slippage_bps = abs(fill_price - price) / price * 10000

        # ── 成交概率 (95%) ──
        if random.random() > 0.95:
            return FillResult(order_id, symbol, action, price, fill_price, 0,
                              round(slippage_bps, 1), 0,
                              "REJECTED", "模拟成交失败(流动性不足)",
                              datetime.now().isoformat())

        # ── 手续费 ──
        amount = fill_price * qty
        commission = max(amount * self.COMMISSION, self.MIN_COMMISSION)
        transfer = amount * self.TRANSFER
        stamp = amount * self.STAMP_TAX if action == "SELL" else 0
        total_fee = commission + stamp + transfer

        # ── 更新资金/持仓 ──
        if action == "BUY":
            cost = amount + total_fee
            if cost > self.cash:
                max_qty = int(self.cash / (fill_price * 1.0003) / 100) * 100
                if max_qty < 100:
                    return FillResult(order_id, symbol, action, price, fill_price, 0,
                                      round(slippage_bps, 1), 0,
                                      "REJECTED", "资金不足", datetime.now().isoformat())
                qty = max_qty
                amount = fill_price * qty
                total_fee = max(amount * self.COMMISSION, self.MIN_COMMISSION) + amount * self.TRANSFER

            self.cash -= (amount + total_fee)
            if symbol not in self.positions:
                self.positions[symbol] = {"shares": 0, "available": 0, "locked": 0, "avg_cost": 0}
            pos = self.positions[symbol]
            total_shares = pos["shares"] + qty
            pos["avg_cost"] = (pos["avg_cost"] * pos["shares"] + fill_price * qty) / total_shares
            pos["shares"] = total_shares
            pos["locked"] += qty          # T+1锁定

        else:  # SELL
            pos = self.positions.get(symbol, {"shares": 0, "available": 0})
            sell_qty = min(qty, pos.get("available", 0))
            if sell_qty < 100:
                return FillResult(order_id, symbol, action, price, fill_price, 0,
                                  round(slippage_bps, 1), 0,
                                  "REJECTED", "可卖数量不足(T+1)", datetime.now().isoformat())
            self.cash += (fill_price * sell_qty - total_fee)
            pos["shares"] -= sell_qty
            pos["available"] -= sell_qty
            qty = sell_qty

        result = FillResult(order_id, symbol, action, price, round(fill_price, 2),
                            qty, round(slippage_bps, 1), round(total_fee, 2),
                            "FILLED", "", datetime.now().isoformat())
        self.trades.append(result)
        return result

    def daily_refresh(self):
        """日初刷新: T+1解锁"""
        for pos in self.positions.values():
            pos["available"] = pos["shares"]   # 全部解锁
            pos["locked"] = 0

    def summary(self) -> dict:
        """账户总览"""
        total_value = self.cash
        for pos in self.positions.values():
            total_value += pos["shares"] * pos["avg_cost"]
        return {
            "cash": round(self.cash, 2),
            "positions": len(self.positions),
            "total_value": round(total_value, 2),
            "total_trades": len(self.trades),
        }
