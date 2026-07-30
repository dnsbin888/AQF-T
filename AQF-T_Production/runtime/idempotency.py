"""
Idempotency Key — V1.2 P0-5
Prevent duplicate orders: same Pattern + Symbol + Minute = one order only.
"""
import hashlib
import time
from datetime import datetime

class IdempotencyGuard:
    """防重复下单 — 基于 Signal Hash"""

    def __init__(self, window_seconds: int = 60):
        self._sent: dict[str, float] = {}   # hash -> timestamp
        self._window = window_seconds
        self._blocked = 0
        self._allowed = 0

    def make_key(self, pattern: str, symbol: str, action: str) -> str:
        """Generate idempotency key: pattern + symbol + action + minute bucket"""
        minute_bucket = int(time.time() / 60)
        raw = f"{pattern}|{symbol}|{action}|{minute_bucket}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def check_and_mark(self, key: str) -> bool:
        """
        Returns True if this is a new unique order.
        Returns False if duplicate (already sent in window).
        """
        now = time.time()

        # Clean expired entries
        expired = [k for k, t in self._sent.items() if now - t > self._window]
        for k in expired:
            del self._sent[k]

        if key in self._sent:
            self._blocked += 1
            return False

        self._sent[key] = now
        self._allowed += 1
        return True

    def status(self) -> dict:
        return {
            "allowed": self._allowed,
            "blocked": self._blocked,
            "active_keys": len(self._sent),
            "window_seconds": self._window,
        }

# Global instance
guard = IdempotencyGuard()
