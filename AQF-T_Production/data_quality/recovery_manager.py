"""
M1 Data Quality — 恢复管理器
PASS / RETRY / SWITCH_BACKUP / FAIL
"""
from enum import Enum


class RecoveryAction(Enum):
    PASS = "pass"              # 正常, 继续
    RETRY = "retry"            # 重试当前源
    SWITCH_BACKUP = "switch"   # 切换到备用源
    FAIL = "fail"              # 停止传播, 禁止下游


class RecoveryManager:
    """恢复管理器"""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._retry_count: dict[str, int] = {}
        self._source_status: dict[str, str] = {}  # primary / backup / failed

    def decide(self, anomaly_severity: str,
               source_name: str = "primary") -> RecoveryAction:
        """根据异常严重程度决定恢复策略"""
        # critical → 直接FAIL
        if anomaly_severity == "critical":
            return RecoveryAction.FAIL

        # warning → 重试
        if anomaly_severity == "warning":
            key = f"{source_name}_retry"
            self._retry_count[key] = self._retry_count.get(key, 0) + 1
            if self._retry_count[key] <= self.max_retries:
                return RecoveryAction.RETRY
            # 重试耗尽 → 切换备用源
            if source_name == "primary" and self._source_status.get("backup") != "failed":
                self._retry_count[key] = 0
                return RecoveryAction.SWITCH_BACKUP
            return RecoveryAction.FAIL

        # info → 正常
        return RecoveryAction.PASS

    def mark_source_failed(self, source_name: str):
        self._source_status[source_name] = "failed"

    def mark_source_recovered(self, source_name: str):
        self._source_status[source_name] = "primary"
        self._retry_count[f"{source_name}_retry"] = 0

    def reset_retries(self, source_name: str = "primary"):
        self._retry_count[f"{source_name}_retry"] = 0
