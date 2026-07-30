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

        # ⑤ 单票仓位检查
        total_value = self.cash + sum(
            p.get("shares", 0) * p.get("price", 0)
            for p in self.positions.values()
        )
        trade_value = price * qty
        position_pct = trade_value / total_value if total_value > 0 else 1
        if position_pct > self.max_single_position:
            return RiskDecision("REJECT", risk_score + 20,
                                f"单票超{self.max_single_position:.0%}: {position_pct:.1%}")

        # ⑤b 总仓位检查 (GPT Q3 — Portfolio Exposure)
        current_exposure = sum(
            p.get("shares", 0) * p.get("price", 0)
            for p in self.positions.values()
        )
        new_total_exposure_pct = (current_exposure + trade_value) / total_value
        if action == "BUY" and new_total_exposure_pct > self.max_total_position:
            return RiskDecision("REJECT", risk_score + 15,
                                f"总仓位超{self.max_total_position:.0%}: {new_total_exposure_pct:.1%}")

        # ⑤c 同板块集中度检查 (GPT Q3)
        if sector and action == "BUY":
            sector_exposure = sum(
                p.get("shares", 0) * p.get("price", 0)
                for p in self.positions.values()
                if p.get("sector") == sector
            )
            new_sector_pct = (sector_exposure + trade_value) / total_value
            if new_sector_pct > self.max_same_sector:
                return RiskDecision("REJECT", risk_score + 10,
                                    f"板块[{sector}]超{self.max_same_sector:.0%}: {new_sector_pct:.1%}")

        # ⑤d 当日新增敞口检查 (GPT Q3)
        if action == "BUY":
            new_daily_pct = (self.daily_new_exposure + trade_value) / total_value
            if new_daily_pct > self.max_daily_new_exposure:
                return RiskDecision("REJECT", risk_score + 10,
                                    f"当日新增超{self.max_daily_new_exposure:.0%}: {new_daily_pct:.1%}")

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
            decision = RiskDecision("APPROVE", risk_score, "风险可控")
        elif risk_score < 55:
            decision = RiskDecision("APPROVE", risk_score, "降低仓位20%")
        elif risk_score < 75:
            adj_qty = int(qty * 0.5 / 100) * 100
            decision = RiskDecision("ADJUST", risk_score, f"高风险, 降低仓位50%",
                                    adjusted_qty=adj_qty)
        else:
            decision = RiskDecision("REJECT", risk_score, "极端风险")

        # 记录当日新增敞口 (APPROVE/ADJUST时)
        if decision.decision in ("APPROVE", "ADJUST") and action == "BUY":
            final_qty = decision.adjusted_qty if decision.adjusted_qty > 0 else qty
            self.daily_new_exposure += price * final_qty

        return decision

    # ── Portfolio Exposure 管理 ──

    def record_fill(self, symbol: str, price: float, qty: int, action: str,
                    sector: str = ""):
        """记录成交后更新仓位 (供Pipeline调用)"""
        if action == "BUY":
            if symbol not in self.positions:
                self.positions[symbol] = {"shares": 0, "available": 0, "locked": 0,
                                          "price": 0, "sector": sector}
            pos = self.positions[symbol]
            total = pos["shares"] + qty
            pos["price"] = (pos["price"] * pos["shares"] + price * qty) / total if total > 0 else price
            pos["shares"] = total
            pos["sector"] = sector

    def daily_reset(self):
        """日初重置: T+1解锁 + 清零当日敞口"""
        for pos in self.positions.values():
            pos["available"] = pos["shares"]
            pos["locked"] = 0
        self.daily_new_exposure = 0.0

    def exposure_summary(self) -> dict:
        """敞口总览"""
        total_value = self.cash + sum(
            p.get("shares", 0) * p.get("price", 0)
            for p in self.positions.values()
        )
        current_exposure = sum(
            p.get("shares", 0) * p.get("price", 0)
            for p in self.positions.values()
        )
        sector_exposure = {}
        for p in self.positions.values():
            sec = p.get("sector", "未知")
            sector_exposure[sec] = sector_exposure.get(sec, 0) + p.get("shares", 0) * p.get("price", 0)

        return {
            "total_value": round(total_value, 2),
            "total_exposure_pct": round(current_exposure / total_value * 100, 1) if total_value > 0 else 0,
            "daily_new_exposure_pct": round(self.daily_new_exposure / total_value * 100, 1) if total_value > 0 else 0,
            "sector_exposure": {k: round(v / total_value * 100, 1) for k, v in sector_exposure.items()} if total_value > 0 else {},
            "max_total_limit_pct": round(self.max_total_position * 100, 0),
            "max_sector_limit_pct": round(self.max_same_sector * 100, 0),
        }
