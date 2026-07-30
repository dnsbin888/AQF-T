"""
MarketDataProvider — 统一行情接口 (GPT 🔴 P0)
==============================================
所有模块通过此接口获取行情，禁止直接调 QMT/akshare

实现:
  - QMTProvider:    国金QMT xtdata (实盘)
  - ReplayProvider:  历史数据回放 (确定性)
  - SimulatorProvider: 模拟数据 (Paper Trading)

统一接口:
  get_snapshot(symbol)  → {price, bid, ask, volume, ...}
  get_orderbook(symbol) → {bids: [...], asks: [...]}
  get_tick(symbol)      → {price, volume, direction, timestamp}
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# Unified Data Types
# ═══════════════════════════════════════════════════════════════

@dataclass
class MarketSnapshot:
    """统一快照 — 所有Provider返回此格式"""
    symbol: str
    price: float                # 最新价
    open: float = 0
    high: float = 0
    low: float = 0
    pre_close: float = 0
    volume: int = 0
    amount: float = 0
    bid1: float = 0             # 买一价
    bid1_vol: int = 0           # 买一量
    ask1: float = 0             # 卖一价
    ask1_vol: int = 0           # 卖一量
    is_limit_up: bool = False
    is_limit_down: bool = False
    timestamp: str = ""


@dataclass
class OrderBook:
    """统一订单簿"""
    symbol: str
    bids: list[tuple[float, int]]   # [(price, volume), ...] 买1-10
    asks: list[tuple[float, int]]   # [(price, volume), ...] 卖1-10
    bid_total: int = 0
    ask_total: int = 0
    timestamp: str = ""


@dataclass
class Tick:
    """统一逐笔"""
    symbol: str
    price: float
    volume: int
    direction: str          # B / S
    type: str = ""          # 特大单/大单/中单/小单
    timestamp: str = ""


# ═══════════════════════════════════════════════════════════════
# Provider Interface
# ═══════════════════════════════════════════════════════════════

class MarketDataProvider(ABC):
    """统一行情接口 — 所有Provider实现此接口"""

    @abstractmethod
    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        """获取实时快照 (最新价+盘口)"""
        ...

    @abstractmethod
    def get_orderbook(self, symbol: str) -> OrderBook:
        """获取十档盘口"""
        ...

    @abstractmethod
    def get_tick(self, symbol: str) -> Optional[Tick]:
        """获取最新逐笔"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider名称"""
        ...


# ═══════════════════════════════════════════════════════════════
# QMT Provider (实盘)
# ═══════════════════════════════════════════════════════════════

class QMTProvider(MarketDataProvider):
    """国金QMT xtdata — 真实行情"""

    def __init__(self):
        self._connected = False
        try:
            from xtquant import xtdata
            self.xtdata = xtdata
            self._connected = True
        except ImportError:
            self.xtdata = None

    @property
    def name(self) -> str:
        return "QMT"

    @property
    def connected(self) -> bool:
        return self._connected

    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        if not self._connected:
            return MarketSnapshot(symbol=symbol, price=0)

        try:
            quote = self.xtdata.get_full_tick([symbol])
            if quote and symbol in quote:
                q = quote[symbol]
                limit_up = q.get("limitUp", q.get("lastClose", 10) * 1.10)
                limit_down = q.get("limitDown", q.get("lastClose", 10) * 0.90)
                return MarketSnapshot(
                    symbol=symbol,
                    price=q.get("lastPrice", 0),
                    open=q.get("open", 0),
                    high=q.get("high", 0),
                    low=q.get("low", 0),
                    pre_close=q.get("lastClose", 0),
                    volume=q.get("volume", 0),
                    amount=q.get("amount", 0),
                    bid1=q.get("bid1", 0),
                    bid1_vol=q.get("bid1_volume", 0),
                    ask1=q.get("ask1", 0),
                    ask1_vol=q.get("ask1_volume", 0),
                    is_limit_up=(q.get("lastPrice", 0) >= limit_up),
                    is_limit_down=(q.get("lastPrice", 0) <= limit_down),
                    timestamp=datetime.now().isoformat(),
                )
        except Exception as e:
            print(f"[QMT] snapshot error for {symbol}: {e}")
        return MarketSnapshot(symbol=symbol, price=0)

    def get_orderbook(self, symbol: str) -> OrderBook:
        if not self._connected:
            return OrderBook(symbol=symbol, bids=[], asks=[])

        try:
            quote = self.xtdata.subscribe_quote(symbol, period="l2quote")
            if quote is None:
                return OrderBook(symbol=symbol, bids=[], asks=[])

            bids = [(quote.get(f"bid{i}", 0), quote.get(f"bid{i}_volume", 0))
                    for i in range(1, 11)]
            asks = [(quote.get(f"ask{i}", 0), quote.get(f"ask{i}_volume", 0))
                    for i in range(1, 11)]

            return OrderBook(
                symbol=symbol,
                bids=[(p, v) for p, v in bids if p > 0],
                asks=[(p, v) for p, v in asks if p > 0],
                bid_total=sum(v for _, v in bids),
                ask_total=sum(v for _, v in asks),
                timestamp=datetime.now().isoformat(),
            )
        except Exception as e:
            print(f"[QMT] orderbook error for {symbol}: {e}")
        return OrderBook(symbol=symbol, bids=[], asks=[])

    def get_tick(self, symbol: str) -> Optional[Tick]:
        if not self._connected:
            return None

        try:
            data = self.xtdata.get_l2_transaction(symbol)
            if not data:
                return None
            last = data[-1]
            return Tick(
                symbol=symbol,
                price=last[1],
                volume=last[2],
                direction="B" if last[3] > 0 else "S",
                type=self._classify(last[2]),
                timestamp=str(last[0]),
            )
        except Exception:
            return None

    @staticmethod
    def _classify(vol: int) -> str:
        if vol >= 1_000_000: return "特大单"
        if vol >= 200_000:  return "大单"
        if vol >= 40_000:   return "中单"
        return "小单"


# ═══════════════════════════════════════════════════════════════
# Simulator Provider (Paper Trading)
# ═══════════════════════════════════════════════════════════════

class SimulatorProvider(MarketDataProvider):
    """
    模拟行情 — Paper Trading / 测试

    使用预设价格池 + 随机波动, 确定性可复现
    """

    # 价格池
    PRICE_POOL = {
        "000001": 12.50, "000002": 15.30, "000858": 168.00,
        "002594": 260.00, "300750": 210.00, "600519": 1850.00,
        "601012": 35.00,  "688981": 55.00,  "300059": 22.00,
        "002230": 48.00,
    }

    def __init__(self, seed: int = 42):
        import random
        self._rng = random.Random(seed)
        self._prices: dict[str, float] = {}

    @property
    def name(self) -> str:
        return "Simulator"

    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        price = self._get_price(symbol)
        pre_close = self.PRICE_POOL.get(symbol, 25.0)
        return MarketSnapshot(
            symbol=symbol,
            price=price,
            open=pre_close * self._rng.uniform(0.99, 1.01),
            high=price * self._rng.uniform(1.00, 1.03),
            low=price * self._rng.uniform(0.97, 1.00),
            pre_close=pre_close,
            volume=self._rng.randint(100000, 5000000),
            amount=price * self._rng.randint(100000, 5000000),
            bid1=round(price * 0.999, 2),
            bid1_vol=self._rng.randint(100, 5000) * 100,
            ask1=round(price * 1.001, 2),
            ask1_vol=self._rng.randint(100, 5000) * 100,
            timestamp=datetime.now().isoformat(),
        )

    def get_orderbook(self, symbol: str) -> OrderBook:
        price = self._get_price(symbol)
        bids = [(round(price * (1 - 0.001 * i), 2), self._rng.randint(10, 100) * 100)
                for i in range(1, 11)]
        asks = [(round(price * (1 + 0.001 * i), 2), self._rng.randint(10, 100) * 100)
                for i in range(1, 11)]
        return OrderBook(
            symbol=symbol, bids=bids, asks=asks,
            bid_total=sum(v for _, v in bids),
            ask_total=sum(v for _, v in asks),
            timestamp=datetime.now().isoformat(),
        )

    def get_tick(self, symbol: str) -> Optional[Tick]:
        price = self._get_price(symbol)
        return Tick(
            symbol=symbol,
            price=round(price * self._rng.uniform(0.999, 1.001), 2),
            volume=self._rng.randint(1, 500) * 100,
            direction="B" if self._rng.random() > 0.45 else "S",
            type=self._rng.choice(["小单", "中单", "大单"]),
            timestamp=datetime.now().isoformat(),
        )

    def _get_price(self, symbol: str) -> float:
        """获取模拟价格 (缓存+波动)"""
        if symbol not in self._prices:
            base = self.PRICE_POOL.get(symbol, 25.0)
            self._prices[symbol] = base

        # 随机波动 ±2%
        self._prices[symbol] *= self._rng.uniform(0.98, 1.02)
        return round(self._prices[symbol], 2)


# ═══════════════════════════════════════════════════════════════
# Replay Provider (历史回放)
# ═══════════════════════════════════════════════════════════════

class ReplayProvider(MarketDataProvider):
    """
    历史数据回放 — 确定性, 同输入=同输出

    数据格式: {date: {symbol: {open/high/low/close/volume/bid1/ask1/...}}}
    """

    def __init__(self, replay_data: dict):
        self._data = replay_data
        self._current_date: str = ""
        self._cursor: dict[str, int] = {}  # symbol → tick index

    @property
    def name(self) -> str:
        return "Replay"

    def set_date(self, date: str):
        self._current_date = date
        self._cursor = {}

    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        day_data = self._data.get(self._current_date, {})
        bar = day_data.get(symbol, {})
        if not bar:
            return MarketSnapshot(symbol=symbol, price=0)

        price = bar.get("close", 0)
        return MarketSnapshot(
            symbol=symbol,
            price=price,
            open=bar.get("open", 0),
            high=bar.get("high", 0),
            low=bar.get("low", 0),
            pre_close=bar.get("pre_close", price),
            volume=bar.get("volume", 0),
            bid1=bar.get("bid1", price * 0.999),
            ask1=bar.get("ask1", price * 1.001),
            is_limit_up=bar.get("is_limit_up", False),
            is_limit_down=bar.get("is_limit_down", False),
            timestamp=f"{self._current_date}T09:30:00",
        )

    def get_orderbook(self, symbol: str) -> OrderBook:
        snap = self.get_snapshot(symbol)
        return OrderBook(
            symbol=symbol,
            bids=[(snap.bid1, 10000)],
            asks=[(snap.ask1, 10000)],
            timestamp=snap.timestamp,
        )

    def get_tick(self, symbol: str) -> Optional[Tick]:
        day_data = self._data.get(self._current_date, {})
        ticks = day_data.get(f"{symbol}_ticks", [])
        if not ticks:
            return None

        idx = self._cursor.get(symbol, 0)
        if idx >= len(ticks):
            return None

        t = ticks[idx]
        self._cursor[symbol] = idx + 1
        return Tick(
            symbol=symbol,
            price=t.get("price", 0),
            volume=t.get("volume", 0),
            direction=t.get("direction", "B"),
            timestamp=t.get("timestamp", ""),
        )


# ═══════════════════════════════════════════════════════════════
# Factory
# ═══════════════════════════════════════════════════════════════

def create_provider(mode: str = "simulator", **kwargs) -> MarketDataProvider:
    """
    创建行情Provider

    Args:
        mode: "qmt" | "simulator" | "replay"
        **kwargs: replay_data (for replay mode), seed (for simulator)
    """
    if mode == "qmt":
        provider = QMTProvider()
        if not provider.connected:
            print("[Provider] QMT not available, falling back to Simulator")
            return SimulatorProvider(seed=kwargs.get("seed", 42))
        return provider
    elif mode == "replay":
        return ReplayProvider(replay_data=kwargs.get("replay_data", {}))
    else:
        return SimulatorProvider(seed=kwargs.get("seed", 42))
