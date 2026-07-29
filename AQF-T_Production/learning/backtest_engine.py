"""
Backtest Engine — 事件驱动回测
A股规则: T+1/涨跌停/费率/滑点/100股
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import numpy as np


@dataclass
class BacktestConfig:
    start_date: str = "2023-01-01"
    end_date: str = "2026-06-30"
    initial_cash: float = 1_000_000.0
    commission_rate: float = 0.00025
    stamp_tax_rate: float = 0.001       # 仅卖出
    slippage_bps: float = 20             # 滑点20基点
    delay_ticks: int = 1                 # 延迟1个Bar成交
    max_position_pct: float = 0.70
    single_position_pct: float = 0.15


@dataclass
class BacktestResult:
    total_return: float = 0.0
    annual_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    equity_curve: list = field(default_factory=list)
    trades: list = field(default_factory=list)


class BacktestEngine:
    """事件驱动回测引擎"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.cash = config.initial_cash
        self.positions: dict[str, dict] = {}
        self.trades: list[dict] = []
        self.equity: list[dict] = []
        self.peak_value = config.initial_cash

    def run(self, data: dict, signals: list[dict]) -> BacktestResult:
        """
        运行回测

        data: {date: {symbol: {open/high/low/close/volume/limit_up/limit_down}}}
        signals: [{date, symbol, action, quantity, price, confidence}]
        """
        dates = sorted(data.keys())

        for i, date in enumerate(dates):
            # ── 日初: T+1解锁 ──
            for pos in self.positions.values():
                pos["available"] = pos["shares"]

            # ── 执行当日信号 ──
            day_signals = [s for s in signals if s["date"] == date]
            for sig in day_signals:
                self._execute_signal(sig, data[date], dates, i)

            # ── 记录权益 ──
            total = self._total_value(data[date])
            self.equity.append({"date": date, "value": total})
            if total > self.peak_value:
                self.peak_value = total

        return self._calculate_result()

    def _execute_signal(self, sig: dict, day_data: dict,
                        dates: list, idx: int):
        """执行单条信号"""
        symbol = sig["symbol"]
        action = sig["action"]
        qty = sig.get("quantity", 100)
        confidence = sig.get("confidence", 0.5)

        if symbol not in day_data:
            return

        bar = day_data[symbol]
        price = bar["close"]

        # ── T+1检查 ──
        if action == "SELL":
            pos = self.positions.get(symbol, {})
            available = pos.get("available", 0)
            if available < qty:
                qty = available
            if qty < 100:
                return

        # ── 涨跌停检查 ──
        if action == "BUY" and bar.get("is_limit_up"):
            return  # 涨停买不到
        if action == "SELL" and bar.get("is_limit_down"):
            return  # 跌停卖不出

        # ── 滑点 ──
        slip = self.config.slippage_bps / 10000
        if action == "BUY":
            fill_price = price * (1 + slip)
        else:
            fill_price = price * (1 - slip)

        # ── 费用 ──
        amount = fill_price * qty
        commission = max(amount * self.config.commission_rate, 5.0)
        stamp = amount * self.config.stamp_tax_rate if action == "SELL" else 0
        fee = commission + stamp

        # ── 资金检查 ──
        if action == "BUY":
            if amount + fee > self.cash * self.config.single_position_pct:
                qty = int(self.cash * self.config.single_position_pct /
                          (fill_price * 1.0003) / 100) * 100
                if qty < 100:
                    return
                amount = fill_price * qty
                commission = max(amount * self.config.commission_rate, 5.0)
                fee = commission
            if amount + fee > self.cash:
                return
            self.cash -= (amount + fee)
            if symbol not in self.positions:
                self.positions[symbol] = {"shares": 0, "available": 0, "avg_cost": 0}
            pos = self.positions[symbol]
            pos["avg_cost"] = (pos["avg_cost"] * pos["shares"] + fill_price * qty) / (pos["shares"] + qty)
            pos["shares"] += qty
            pos["available"] = 0  # T+1: 当日买入不可卖
        else:
            self.cash += (amount - fee)
            pos = self.positions.get(symbol, {"shares": 0, "available": 0})
            pos["shares"] -= qty
            pos["available"] -= qty

        # ── 记录 ──
        pnl = 0
        if action == "SELL" and symbol in self.positions:
            pnl = (fill_price - self.positions[symbol]["avg_cost"]) * qty

        self.trades.append({
            "date": sig["date"], "symbol": symbol, "action": action,
            "qty": qty, "price": round(fill_price, 2), "fee": round(fee, 2),
            "pnl": round(pnl, 2), "confidence": confidence,
        })

    def _total_value(self, day_data: dict) -> float:
        total = self.cash
        for sym, pos in self.positions.items():
            if sym in day_data:
                total += pos["shares"] * day_data[sym]["close"]
            else:
                total += pos["shares"] * pos["avg_cost"]
        return round(total, 2)

    def _calculate_result(self) -> BacktestResult:
        """计算回测绩效"""
        if not self.equity:
            return BacktestResult()

        returns = []
        for i in range(1, len(self.equity)):
            r = (self.equity[i]["value"] / self.equity[i-1]["value"] - 1)
            returns.append(r)

        total_ret = (self.equity[-1]["value"] / self.config.initial_cash - 1)
        days = len(self.equity)
        annual_ret = (1 + total_ret) ** (252 / max(days, 1)) - 1

        # Sharpe
        if returns:
            avg_ret = np.mean(returns)
            std_ret = np.std(returns)
            sharpe = (avg_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0
        else:
            sharpe = 0

        # Max Drawdown
        peak = self.config.initial_cash
        max_dd = 0
        for e in self.equity:
            if e["value"] > peak:
                peak = e["value"]
            dd = (peak - e["value"]) / peak
            max_dd = max(max_dd, dd)

        # Win Rate
        sells = [t for t in self.trades if t["action"] == "SELL"]
        wins = [t for t in sells if t["pnl"] > 0]
        win_rate = len(wins) / len(sells) if sells else 0

        # Profit Factor
        gross_profit = sum(t["pnl"] for t in sells if t["pnl"] > 0)
        gross_loss = abs(sum(t["pnl"] for t in sells if t["pnl"] < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        return BacktestResult(
            total_return=round(total_ret * 100, 2),
            annual_return=round(annual_ret * 100, 2),
            sharpe_ratio=round(sharpe, 2),
            max_drawdown=round(max_dd * 100, 2),
            win_rate=round(win_rate * 100, 1),
            profit_factor=round(profit_factor, 2),
            total_trades=len(self.trades),
            equity_curve=[{"date": e["date"], "value": e["value"]} for e in self.equity],
            trades=self.trades,
        )
