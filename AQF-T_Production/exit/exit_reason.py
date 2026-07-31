"""
Exit Reason Taxonomy — DEC-027 Frozen
======================================
Risk Exit (priority=80): risk protection, cannot be overridden by strategy
Strategy Exit (priority=50): pattern/alpha lifecycle, requires evidence
"""
from enum import Enum


class ExitPriority:
    KILLSWITCH = 100    # 熔断 — 最高
    RISK = 80           # 风控止损/回撤/Regime
    STRATEGY = 50       # 策略失效/龙头结束/动量衰减
    MANUAL = 30         # 人工干预


class ExitReason(Enum):
    # ── Risk Exit (不可被策略覆盖) ──
    KILLSWITCH = "killswitch"          # 熔断触发 — 全部清仓
    HARD_STOP = "hard_stop"            # 硬止损 — 亏损超限
    ATR_STOP = "atr_stop"              # ATR自适应止损
    DRAWDOWN_LIMIT = "drawdown_limit"  # 回撤限制 — 从最高点回落超限
    REGIME_BREAK = "regime_break"      # 情绪周期转退潮 — 强制清仓
    TIME_STOP = "time_stop"            # 时间止损 — 持仓N天未达预期

    # ── Strategy Exit (策略管理自己的退出) ──
    PATTERN_INVALID = "pattern_invalid"   # Pattern 失效 — 信号条件已不满足
    LEADER_END = "leader_end"           # 龙头生命周期结束
    MOMENTUM_FADE = "momentum_fade"     # 动量衰减
    SIGNAL_DECAY = "signal_decay"       # 因子信号衰减
    BREAK_EXIT = "break_exit"           # 炸板退出 (游资)
    GAP_WEAK_EXIT = "gap_weak_exit"     # 竞价转弱退出
    SECTOR_DIE = "sector_die"           # 题材退潮退出
    MA_BREAK = "ma_break"               # 均线破位退出
