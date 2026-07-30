"""
ClockProvider — 统一时钟源
============================
所有模块通过 clock.now() 获取时间，禁止直接调用 datetime.now()

模式:
  - live:  真实系统时间
  - replay: 固定回放时间
  - paper:  真实时间 (模拟交易)

用法:
  from core.clock import clock
  now = clock.now()
"""

from datetime import datetime
from typing import Optional


class ClockProvider:
    """
    统一时钟源 — AQF-T 唯一时间入口

    量化系统标准设计:
      - replay 模式: 固定时间，确保确定性
      - live 模式:   真实时间
      - paper 模式:  真实时间

    禁止任何模块直接调用 datetime.now()
    """

    def __init__(self):
        self._mode: str = "live"            # live | replay | paper
        self._frozen_time: Optional[datetime] = None
        self._time_override: Optional[datetime] = None  # 测试用

    # ── 公开API ──

    def now(self) -> datetime:
        """获取当前时间 — 唯一入口"""
        if self._time_override is not None:
            return self._time_override
        if self._mode == "replay" and self._frozen_time is not None:
            return self._frozen_time
        return datetime.now()

    def today_str(self) -> str:
        """今日日期字符串 YYYY-MM-DD"""
        return self.now().strftime("%Y-%m-%d")

    def now_iso(self) -> str:
        """当前时间 ISO 格式"""
        return self.now().isoformat()

    # ── 模式切换 ──

    def set_mode(self, mode: str):
        """切换模式: live | replay | paper"""
        if mode not in ("live", "replay", "paper"):
            raise ValueError(f"Unknown clock mode: {mode}")
        self._mode = mode

    def set_replay_time(self, dt: datetime):
        """设置回放时间 — replay模式专用"""
        self._mode = "replay"
        self._frozen_time = dt

    def advance_replay(self, days: int = 1):
        """回放时间前进N天"""
        if self._frozen_time is None:
            self._frozen_time = datetime(2026, 1, 1, 9, 30, 0)
        from datetime import timedelta
        self._frozen_time += timedelta(days=days)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def is_replay(self) -> bool:
        return self._mode == "replay"

    @property
    def is_live(self) -> bool:
        return self._mode == "live"

    # ── 交易时段判断 ──

    def is_trading_hours(self) -> bool:
        """是否在交易时段内 (9:30-11:30, 13:00-15:00)"""
        now = self.now()
        morning_start = now.replace(hour=9, minute=30, second=0, microsecond=0)
        morning_end = now.replace(hour=11, minute=30, second=0, microsecond=0)
        afternoon_start = now.replace(hour=13, minute=0, second=0, microsecond=0)
        afternoon_end = now.replace(hour=15, minute=0, second=0, microsecond=0)

        morning = morning_start <= now <= morning_end
        afternoon = afternoon_start <= now <= afternoon_end
        return morning or afternoon

    def is_market_open(self) -> bool:
        """是否在开盘时间 (含集合竞价 9:15-15:00)"""
        now = self.now()
        open_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
        close_time = now.replace(hour=15, minute=0, second=0, microsecond=0)
        return open_time <= now <= close_time

    # ── 测试辅助 ──

    def override(self, dt: datetime):
        """测试用: 临时覆盖时间"""
        self._time_override = dt

    def clear_override(self):
        """清除测试时间覆盖"""
        self._time_override = None


# 全局单例
clock = ClockProvider()
