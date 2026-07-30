"""
QMT Recovery — V1.2 P0-2
Market data disconnect detection / state snapshot / reconnect / tick sync / resume
"""
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class DataHealth(Enum):
    NORMAL = "normal"
    DEGRADED = "degraded"
    DISCONNECTED = "disconnected"
    RECOVERING = "recovering"

@dataclass
class RecoveryState:
    health: DataHealth = DataHealth.NORMAL
    last_data_time: str = ""
    disconnect_count: int = 0
    reconnect_success: int = 0
    degraded_seconds: float = 0
    snapshot: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)

class QMTRecoveryManager:
    """QMT行情中断恢复管理器"""

    def __init__(self, data_timeout: float = 5.0, max_reconnect: int = 5):
        self.state = RecoveryState()
        self.data_timeout = data_timeout
        self.max_reconnect = max_reconnect
        self._last_tick_time: float = 0
        self._disconnect_start: float = 0

    def mark_data_arrival(self):
        self._last_tick_time = time.time()
        if self.state.health == DataHealth.DISCONNECTED:
            self.state.health = DataHealth.RECOVERING
            self.state.reconnect_success += 1
        elif self.state.health == DataHealth.RECOVERING:
            age = time.time() - self._disconnect_start
            if age > 3 and self._last_tick_time > self._disconnect_start:
                self.state.health = DataHealth.NORMAL

    def check(self) -> DataHealth:
        age = time.time() - self._last_tick_time if self._last_tick_time > 0 else 0
        if self.state.health == DataHealth.NORMAL and age > self.data_timeout:
            self.state.health = DataHealth.DEGRADED
            self.state.degraded_seconds = age
        if age > self.data_timeout * 3:
            if self.state.health != DataHealth.DISCONNECTED:
                self.state.health = DataHealth.DISCONNECTED
                self.state.disconnect_count += 1
                self._disconnect_start = time.time()
                self._save_snapshot()
        return self.state.health

    def should_pause_trading(self) -> bool:
        return self.state.health in (DataHealth.DISCONNECTED,)

    def should_retry_connect(self) -> bool:
        return (self.state.health == DataHealth.DISCONNECTED and
                self.state.disconnect_count <= self.max_reconnect)

    def _save_snapshot(self):
        import json
        try:
            snap = {"health": self.state.health.value, "disconnect_count": self.state.disconnect_count,
                    "timestamp": datetime.now().isoformat(), "last_data": self.state.last_data_time}
            from pathlib import Path
            p = Path("runtime/recovery_state.json")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def status(self) -> dict:
        age = time.time() - self._last_tick_time if self._last_tick_time > 0 else float("inf")
        return {"health": self.state.health.value, "data_age_seconds": round(age, 1),
                "disconnects": self.state.disconnect_count, "reconnects": self.state.reconnect_success}

# Global instance
recovery = QMTRecoveryManager()
