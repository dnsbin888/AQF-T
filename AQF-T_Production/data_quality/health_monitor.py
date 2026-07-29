"""
M1 Data Quality — 健康监控
Data Health Score: 仅Dashboard, 不参与交易决策
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class DataHealthSnapshot:
    timestamp: datetime
    completeness: float = 1.0     # 完整率
    freshness: float = 1.0        # 新鲜度
    latency_p50_ms: float = 0
    consistency: float = 1.0      # 一致性
    validation_pass_rate: float = 1.0
    score: float = 100.0          # 综合 0-100

    def is_healthy(self, threshold: float = 95.0) -> bool:
        return self.score >= threshold


class HealthMonitor:
    """数据健康监控 — 不参与交易决策"""

    def __init__(self):
        self._validation_total = 0
        self._validation_passed = 0
        self._last_data_time: datetime | None = None
        self._missing_count = 0
        self._total_count = 0

    def record_validation(self, passed: bool):
        self._validation_total += 1
        if passed:
            self._validation_passed += 1

    def record_data_arrival(self, timestamp: datetime):
        self._last_data_time = timestamp
        self._total_count += 1

    def record_missing(self):
        self._missing_count += 1

    def snapshot(self) -> DataHealthSnapshot:
        now = datetime.now()

        # 完整率
        total = self._total_count + self._missing_count
        completeness = self._total_count / total if total > 0 else 1.0

        # 新鲜度
        freshness = 1.0
        if self._last_data_time:
            age = (now - self._last_data_time).total_seconds()
            freshness = max(0, 1.0 - age / 300)  # 5分钟内满分

        # 校验通过率
        pass_rate = (self._validation_passed / self._validation_total
                     if self._validation_total > 0 else 1.0)

        # 综合评分
        score = (completeness * 30 + freshness * 30 +
                 pass_rate * 30 + 10)

        return DataHealthSnapshot(
            timestamp=now,
            completeness=round(completeness, 4),
            freshness=round(freshness, 4),
            consistency=1.0,
            validation_pass_rate=round(pass_rate, 4),
            score=round(score, 2),
        )
