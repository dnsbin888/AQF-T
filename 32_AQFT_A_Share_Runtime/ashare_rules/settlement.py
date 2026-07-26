"""
A股交易规则汇总 — Settlement Engine

整合: T+1 + 涨跌停 + 手续费 + 最小交易单位
"""
from dataclasses import dataclass
from datetime import date
from .t_plus_one import TPlusOneEngine
from .limit_price import LimitPriceEngine, get_board_type
from .trading_fee import TradingFeeEngine


MIN_LOT_SIZE = 100  # A股最小交易单位: 100股 (1手)


@dataclass
class AshareOrder:
    symbol: str
    direction: str       # BUY / SELL
    shares: int
    price: float
    trade_date: date


class AshareSettlementEngine:
    """A股综合交易规则引擎"""

    def __init__(self):
        self.t1 = TPlusOneEngine()
        self.fee = TradingFeeEngine()

    def validate(self, order: AshareOrder) -> tuple[bool, str]:
        """验证订单是否符合A股规则"""
        # 1. 最小交易单位
        if order.shares % MIN_LOT_SIZE != 0:
            return False, f"必须是{MIN_LOT_SIZE}股的整数倍"
        if order.shares < MIN_LOT_SIZE:
            return False, f"最少交易{MIN_LOT_SIZE}股"

        # 2. 涨跌停
        limit = LimitPriceEngine(order.symbol, prev_close=order.price, is_st=False)
        ok, msg = limit.can_trade(order.price, order.direction)
        if not ok:
            return False, msg

        # 3. T+1 卖出限制
        if order.direction == "SELL":
            sold, msg = self.t1.sell(order.symbol, order.shares, order.trade_date)
            if sold == 0:
                return False, msg

        return True, "OK"

    def execute_buy(self, order: AshareOrder) -> dict:
        """执行买入"""
        valid, msg = self.validate(order)
        if not valid:
            return {"status": "REJECTED", "reason": msg}

        fee_detail = self.fee.calc_buy_fee(order.price * order.shares)
        self.t1.buy(order.symbol, order.shares, order.price, order.trade_date)

        return {
            "status": "FILLED",
            "order": order,
            "fee": fee_detail,
            "effective_cost": fee_detail["effective_cost"],
        }

    def execute_sell(self, order: AshareOrder) -> dict:
        """执行卖出"""
        valid, msg = self.validate(order)
        if not valid:
            return {"status": "REJECTED", "reason": msg}

        fee_detail = self.fee.calc_sell_fee(order.price * order.shares)
        return {
            "status": "FILLED",
            "order": order,
            "fee": fee_detail,
            "effective_income": fee_detail["effective_income"],
        }

    def daily_refresh(self, trade_date: date):
        """每日开盘前刷新状态"""
        self.t1.refresh_all(trade_date)

    def summary(self) -> dict:
        return {
            "positions": self.t1.summary(),
        }
