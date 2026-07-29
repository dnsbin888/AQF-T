"""
M1 Data Quality — 统一数据模型
所有数据源(QMT L2 / akshare) → 统一 DataRecord → Validator
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TickRecord:
    """逐笔成交"""
    symbol: str           # SH.600519
    timestamp: datetime   # UTC
    price: float
    volume: int
    direction: str        # BUY / SELL / UNKNOWN


@dataclass(frozen=True)
class BarRecord:
    """K线"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float


@dataclass(frozen=True)
class OrderBookRecord:
    """十档盘口快照"""
    symbol: str
    timestamp: datetime
    bid_prices: tuple
    bid_volumes: tuple
    ask_prices: tuple
    ask_volumes: tuple
