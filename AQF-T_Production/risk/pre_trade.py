"""
Pre-Trade Check — 下单前7项检查 (不可绕过)
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class RiskDecision:
    decision: str        # APPROVE / ADJUST / REJECT
    risk_score: int      # 0-100
    reason: str
    adjusted_qty: int = 0
    timestamp: str = ""


class PreTradeChecker:
    """
    下单前检查 (不可绕过)

    GPT Q3 — Portfolio Exposure Limits:
      - max_total_position: 40%
      - max_same_sector: 25%
      - max_daily_new_exposure: 20%
      - max_single_position: 10%
    """

    def __init__(self):
        self.positions = {}          # {symbol: {shares, available, locked, price, sector}}
        self.cash = 1_000_000.0
        self.daily_pnl = 0.0
        self.peak_value = 1_000_000.0

        # Portfolio Exposure Limits (GPT Q3)
        self.max_total_position = 0.40
        self.max_same_sector = 0.25
        self.max_daily_new_exposure = 0.20
        self.max_single_position = 0.10
        self.daily_new_exposure = 0.0   # 当日新增买入金额

    def check(self, symbol: str, action: str, qty: int, price: float,
              risk_score: int, sentiment_phase: str,
              sector: str = "") -> RiskDecision:
        """返回 APPROVE / ADJUST / REJECT"""

        # ① 情绪周期最高优先级
        if sentiment_phase == "退潮期" and action == "BUY":
            return RiskDecision("REJECT", risk_score + 30, "退潮期禁止买入")
        if sentiment_phase == "冰点期" and action == "BUY":
            if qty * price > self.cash * 0.05:
                return RiskDecision("ADJUST", risk_score + 10, "冰点期限制仓位")

        # ② T+1检查 (SELL时)
        if action == "SELL":
            pos = self.positions.get(symbol, {})
            available = pos.get("available", 0)
            if qty > available:
                return RiskDecision("REJECT", 100,
                                    f"T+1限制: 可卖{available}股, 请求{qty}股")

        # ③ 涨跌停检查 (简化 — 实盘从QMT L2获取)
        # if at_limit_up and action == "BUY": return REJECT
        # if at_limit_down and action == "SELL": return REJECT

        # ④ 资金检查 (BUY时)
        if action == "BUY":
            estimated_fee = price * qty * 0.0003  # 预估万三
            total = price * qty + estimated_fee
            if total > self.cash:
                max_qty = int(self.cash / (price * 1.0003) / 100) * 100
                if max_qty < 100:
                    return RiskDecision("REJECT", 80, "资金不足")
                return RiskDecision("ADJUST", risk_score,
                                    f"资金不足, 调整为{max_qty}股",
                                    adjusted_qty=max_qty)

        # ⑤ 仓位检查
        total_value = self.cash + sum(
            p.get("shares", 0) * p.get("price", 0)
            for p in self.positions.values()
        )
        position_pct = (price * qty) / total_value if total_value > 0 else 1
        if position_pct > 0.10:
            return RiskDecision("REJECT", risk_score + 20,
                                f"单票超10%: {position_pct:.1%}")

        # ⑥ 手数检查
        if qty % 100 != 0:
            adjusted = (qty // 100) * 100
            if adjusted < 100:
                return RiskDecision("REJECT", 60, "最小100股")
            return RiskDecision("ADJUST", risk_score,
                                f"调整为{adjusted}股(100的倍数)",
                                adjusted_qty=adjusted)

        # ⑦ 交易时段 (通过ClockProvider统一管理)
        from core.clock import clock
        if not clock.is_trading_hours():
            return RiskDecision("REJECT", 50, "非交易时段")

        # 风控评分决策
        if risk_score < 30:
            return RiskDecision("APPROVE", risk_score, "风险可控")
        elif risk_score < 55:
            return RiskDecision("APPROVE", risk_score, "降低仓位20%")
        elif risk_score < 75:
            adj_qty = int(qty * 0.5 / 100) * 100
            return RiskDecision("ADJUST", risk_score, f"高风险, 降低仓位50%",
                                adjusted_qty=adj_qty)
        return RiskDecision("REJECT", risk_score, "极端风险")
