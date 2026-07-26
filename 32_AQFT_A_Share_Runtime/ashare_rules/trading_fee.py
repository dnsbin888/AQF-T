"""
A股真实交易费用计算

买入: 佣金 0.025% (最低5元) + 过户费 0.001%
卖出: 佣金 0.025% (最低5元) + 过户费 0.001% + 印花税 0.1%
"""


class TradingFeeEngine:
    """A股交易费用引擎"""

    # A股真实费率
    COMMISSION_RATE = 0.00025   # 佣金 万分之2.5
    COMMISSION_MIN = 5.0        # 佣金最低5元
    STAMP_TAX_RATE = 0.001      # 印花税 千分之1 (仅卖出)
    TRANSFER_RATE = 0.00001     # 过户费 十万分之1

    def calc_buy_fee(self, amount: float) -> dict:
        """计算买入费用"""
        commission = max(amount * self.COMMISSION_RATE, self.COMMISSION_MIN)
        transfer = amount * self.TRANSFER_RATE
        total_fee = commission + transfer
        return {
            "commission": round(commission, 2),
            "transfer": round(transfer, 2),
            "stamp_tax": 0.0,
            "total": round(total_fee, 2),
            "effective_cost": round(amount + total_fee, 2),
        }

    def calc_sell_fee(self, amount: float) -> dict:
        """计算卖出费用"""
        commission = max(amount * self.COMMISSION_RATE, self.COMMISSION_MIN)
        stamp_tax = amount * self.STAMP_TAX_RATE
        transfer = amount * self.TRANSFER_RATE
        total_fee = commission + stamp_tax + transfer
        return {
            "commission": round(commission, 2),
            "stamp_tax": round(stamp_tax, 2),
            "transfer": round(transfer, 2),
            "total": round(total_fee, 2),
            "effective_income": round(amount - total_fee, 2),
        }

    def calc_roundtrip(self, buy_price: float, sell_price: float, shares: int) -> dict:
        """计算完整买卖来回费用"""
        buy_amount = buy_price * shares
        sell_amount = sell_price * shares
        buy_fee = self.calc_buy_fee(buy_amount)
        sell_fee = self.calc_sell_fee(sell_amount)
        total_fee = buy_fee["total"] + sell_fee["total"]

        gross_pnl = sell_amount - buy_amount
        net_pnl = gross_pnl - total_fee

        return {
            "gross_pnl": round(gross_pnl, 2),
            "total_fee": round(total_fee, 2),
            "net_pnl": round(net_pnl, 2),
            "fee_impact_pct": round(total_fee / buy_amount * 100, 3) if buy_amount > 0 else 0,
            "buy_fee": buy_fee,
            "sell_fee": sell_fee,
        }
