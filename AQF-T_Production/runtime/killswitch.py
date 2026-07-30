"""
KillSwitch Integration — V1.2 P0-4
Hard-wired into execution path: Decision -> Risk -> [KillSwitch] -> Execution
"""
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class KillSwitchState:
    active: bool = False
    reason: str = ""
    triggered_at: str = ""
    triggered_by: str = ""
    blocked_orders: int = 0
    history: list = field(default_factory=list)

class KillSwitch:
    """紧急熔断器 — Risk内部第一道检查"""

    TRIGGERS = {
        "MAX_DAILY_LOSS": "当日亏损超限",
        "MAX_DRAWDOWN": "总回撤超限",
        "DATA_DISCONNECT": "行情断开",
        "QMT_ERROR": "QMT连接异常",
        "POSITION_DRIFT": "持仓不一致",
        "MANUAL": "人工触发",
        "SUPERVISOR": "Supervisor触发",
    }

    def __init__(self):
        self.state = KillSwitchState()
        self._state_path = Path("runtime/killswitch_state.json")

    def trigger(self, reason: str, triggered_by: str = "system") -> str:
        if not self.state.active:
            self.state.active = True
            self.state.reason = reason
            self.state.triggered_at = datetime.now().isoformat()
            self.state.triggered_by = triggered_by
            self.state.history.append({
                "action": "TRIGGERED", "reason": reason,
                "by": triggered_by, "timestamp": self.state.triggered_at,
            })
            self._save()
        return "BLOCKED"

    def release(self, by: str = "system") -> bool:
        if self.state.active:
            self.state.active = False
            self.state.history.append({
                "action": "RELEASED", "by": by,
                "timestamp": datetime.now().isoformat(),
            })
            self._save()
            return True
        return False

    def check(self, context: dict = None) -> str:
        """
        Called before EVERY order. Returns PASS or BLOCKED.
        Must be called inside Risk layer BEFORE any other check.
        """
        if self.state.active:
            self.state.blocked_orders += 1
            return "BLOCKED"
        return "PASS"

    @property
    def is_active(self) -> bool:
        return self.state.active

    def status(self) -> dict:
        return {
            "active": self.state.active,
            "reason": self.state.reason,
            "triggered_at": self.state.triggered_at,
            "blocked_orders": self.state.blocked_orders,
        }

    def _save(self):
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(json.dumps(self.status(), ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

# Global instance
killswitch = KillSwitch()
