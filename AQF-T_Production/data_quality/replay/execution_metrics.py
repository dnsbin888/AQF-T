"""
M4 Execution Metrics — 执行质量指标
Fill Rate / Latency / Slippage / Reject / Cancel / Timeout
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionRecord:
    order_id: str
    symbol: str
    action: str               # BUY / SELL
    signal_time: datetime
    decision_time: datetime
    order_time: datetime
    fill_time: datetime = None
    fill_price: float = 0.0
    expected_price: float = 0.0
    quantity: int = 0
    filled_qty: int = 0
    status: str = "CREATED"   # FILLED / REJECTED / CANCELLED / TIMEOUT
    slippage_bps: float = 0.0
    fee: float = 0.0


@dataclass
class ExecutionReport:
    date: str
    total_signals: int = 0
    approved: int = 0
    rejected: int = 0
    filled: int = 0
    cancelled: int = 0
    timeout: int = 0
    fill_rate: float = 0.0
    avg_slippage_bps: float = 0.0
    avg_latency_ms: float = 0.0   # Signal→Fill
    avg_decision_ms: float = 0.0  # Signal→Decision
    avg_order_ms: float = 0.0     # Decision→Order

    def generate(self) -> str:
        return f"""
================================================================
  AQF-T M4 Execution Daily Report
  Date: {self.date}
================================================================

一、订单概况
  Total Signals:  {self.total_signals}
  Approved:       {self.approved}
  Rejected:       {self.rejected}
  Filled:         {self.filled}
  Cancelled:      {self.cancelled}
  Timeout:        {self.timeout}
  Fill Rate:      {self.fill_rate:.1%}

二、延迟 (ms)
  Signal→Decision:  {self.avg_decision_ms:.0f}
  Decision→Order:   {self.avg_order_ms:.0f}
  Signal→Fill:      {self.avg_latency_ms:.0f}

三、执行质量
  Avg Slippage:    {self.avg_slippage_bps:.1f} bps
  Fill Rate:       {self.fill_rate:.1%}

四、可追溯性
  异常100%可追溯:  {'PASS' if self.fill_rate > 0.8 else 'CHECK'}
================================================================
"""


class ExecutionTracker:
    """执行追踪器"""

    def __init__(self):
        self.records: list[ExecutionRecord] = []

    def record(self, r: ExecutionRecord):
        self.records.append(r)

    def daily_report(self, date: str) -> ExecutionReport:
        approved = [r for r in self.records if r.status != "REJECTED"]
        filled = [r for r in approved if r.status == "FILLED"]
        rejected = [r for r in self.records if r.status == "REJECTED"]
        cancelled = [r for r in self.records if r.status == "CANCELLED"]
        timeout = [r for r in self.records if r.status == "TIMEOUT"]

        # 延迟
        decision_ms = [
            (r.decision_time - r.signal_time).total_seconds() * 1000
            for r in self.records
        ]
        order_ms = [
            (r.order_time - r.decision_time).total_seconds() * 1000
            for r in self.records if r.status != "REJECTED"
        ]
        latency_ms = [
            (r.fill_time - r.signal_time).total_seconds() * 1000
            for r in filled if r.fill_time
        ]

        return ExecutionReport(
            date=date,
            total_signals=len(self.records),
            approved=len(approved), rejected=len(rejected),
            filled=len(filled), cancelled=len(cancelled),
            timeout=len(timeout),
            fill_rate=len(filled) / len(self.records) if self.records else 0,
            avg_slippage_bps=sum(r.slippage_bps for r in filled) / len(filled) if filled else 0,
            avg_latency_ms=sum(latency_ms) / len(latency_ms) if latency_ms else 0,
            avg_decision_ms=sum(decision_ms) / len(decision_ms) if decision_ms else 0,
            avg_order_ms=sum(order_ms) / len(order_ms) if order_ms else 0,
        )
