"""
M2.1 Replay Data Loader — L2历史数据回放
目标: L2历史数据 → Replay Tick Stream (时序一致)
"""
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ReplayConfig:
    """Replay配置快照 — 可复现的基础"""
    replay_id: str
    dataset_version: str
    engine_version: str = "2.1.0"
    git_commit: str = ""
    config_hash: str = ""
    created_at: str = ""


@dataclass
class ReplayTick:
    """回放Tick — 与实时Tick格式完全一致"""
    symbol: str
    timestamp: datetime
    price: float
    volume: int
    direction: str           # BUY / SELL / UNKNOWN
    bid1: float = 0.0
    ask1: float = 0.0
    source: str = "REPLAY"


@dataclass
class ReplaySession:
    """Replay会话 — 全程可审计"""
    config: ReplayConfig
    total_ticks: int = 0
    errors: int = 0
    tick_hashes: list = field(default_factory=list)  # 用于验证Determinism

    def is_consistent_with(self, other: "ReplaySession") -> bool:
        """两次Replay是否一致"""
        if self.total_ticks != other.total_ticks:
            return False
        return self.tick_hashes == other.tick_hashes


class ReplayLoader:
    """L2历史数据加载器 — 按时序回放"""

    def __init__(self, config: ReplayConfig):
        self.config = config
        self._ticks: list[ReplayTick] = []
        self._position = 0
        self._session = ReplaySession(config=config)

    def load_csv(self, filepath: str):
        """从CSV加载L2历史数据"""
        import csv
        self._ticks = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tick = ReplayTick(
                    symbol=row.get("symbol", ""),
                    timestamp=datetime.fromisoformat(row.get("timestamp", "")),
                    price=float(row.get("price", 0)),
                    volume=int(row.get("volume", 0)),
                    direction=row.get("direction", "UNKNOWN"),
                    bid1=float(row.get("bid1", 0)),
                    ask1=float(row.get("ask1", 0)),
                )
                self._ticks.append(tick)

        # 按时序排序 (Replay必须)
        self._ticks.sort(key=lambda t: t.timestamp)
        self._position = 0
        self._session.total_ticks = len(self._ticks)
        return len(self._ticks)

    def load_list(self, ticks: list[dict]):
        """从dict列表加载 (测试用)"""
        self._ticks = [
            ReplayTick(
                symbol=t["symbol"],
                timestamp=t["timestamp"],
                price=t["price"],
                volume=t.get("volume", 0),
                direction=t.get("direction", "UNKNOWN"),
                bid1=t.get("bid1", 0),
                ask1=t.get("ask1", 0),
            )
            for t in ticks
        ]
        self._ticks.sort(key=lambda t: t.timestamp)
        self._position = 0
        self._session.total_ticks = len(self._ticks)
        return len(self._ticks)

    def next_tick(self) -> Optional[ReplayTick]:
        """获取下一个Tick (模拟实时流)"""
        if self._position >= len(self._ticks):
            return None
        tick = self._ticks[self._position]
        self._position += 1

        # 记录hash用于Determinism验证
        tick_hash = hashlib.md5(
            f"{tick.symbol}{tick.timestamp.isoformat()}{tick.price}".encode()
        ).hexdigest()
        self._session.tick_hashes.append(tick_hash)

        return tick

    def reset(self):
        """重置到起始位置 — 同一数据多次Replay必须一致"""
        self._position = 0
        self._session = ReplaySession(config=self.config)
        self._session.total_ticks = len(self._ticks)

    def verify_ordering(self) -> bool:
        """验证时序一致性"""
        for i in range(1, len(self._ticks)):
            if self._ticks[i].timestamp < self._ticks[i-1].timestamp:
                return False
        return True

    def verify_no_gaps(self, max_gap_seconds: int = 300) -> bool:
        """验证无长时间断档"""
        for i in range(1, len(self._ticks)):
            gap = (self._ticks[i].timestamp - self._ticks[i-1].timestamp).total_seconds()
            if gap > max_gap_seconds:
                return False
        return True

    @property
    def session(self) -> ReplaySession:
        return self._session
