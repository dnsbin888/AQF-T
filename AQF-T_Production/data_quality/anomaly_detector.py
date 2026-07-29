"""
M1 Data Quality — 异常检测器
只检测, 不修复。检测: 缺失/重复/跳空/冻结
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class AnomalyEvent:
    event_type: str         # MISSING / DUPLICATE / GAP / FREEZE / JUMP
    symbol: str
    timestamp: datetime
    detail: str
    severity: str           # info / warning / critical


class AnomalyDetector:
    """异常检测器"""

    def __init__(self, max_gap_seconds: int = 60,
                 max_price_jump_pct: float = 10.0,
                 max_stale_seconds: int = 30):
        self.max_gap_seconds = max_gap_seconds
        self.max_price_jump_pct = max_price_jump_pct
        self.max_stale_seconds = max_stale_seconds
        self._last_timestamp: dict[str, datetime] = {}
        self._last_price: dict[str, float] = {}

    def detect(self, symbol: str, timestamp: datetime,
               price: float, volume: int) -> list[AnomalyEvent]:
        events = []

        # 重复检测
        if symbol in self._last_timestamp:
            if timestamp == self._last_timestamp[symbol]:
                events.append(AnomalyEvent(
                    "DUPLICATE", symbol, timestamp,
                    f"重复时间戳", "critical"))

        # 跳空检测
        if symbol in self._last_price:
            prev = self._last_price[symbol]
            if prev > 0:
                change = abs(price - prev) / prev * 100
                if change > self.max_price_jump_pct:
                    events.append(AnomalyEvent(
                        "JUMP", symbol, timestamp,
                        f"价格跳空 {change:.1f}%", "warning"))

        # 时间间隔检测
        if symbol in self._last_timestamp:
            gap = (timestamp - self._last_timestamp[symbol]).total_seconds()
            if gap > self.max_gap_seconds:
                events.append(AnomalyEvent(
                    "GAP", symbol, timestamp,
                    f"数据间隔 {gap:.0f}秒", "warning"))

        # 更新追踪
        self._last_timestamp[symbol] = timestamp
        self._last_price[symbol] = price

        return events


class L2FreezeDetector:
    """L2数据冻结检测"""

    def __init__(self, max_stale_seconds: int = 30):
        self.max_stale_seconds = max_stale_seconds
        self._last_update: Optional[datetime] = None

    def check(self) -> Optional[AnomalyEvent]:
        now = datetime.now()
        if self._last_update:
            gap = (now - self._last_update).total_seconds()
            if gap > self.max_stale_seconds:
                return AnomalyEvent(
                    "FREEZE", "L2", now,
                    f"L2数据冻结 {gap:.0f}秒", "critical")
        return None

    def heartbeat(self):
        self._last_update = datetime.now()
