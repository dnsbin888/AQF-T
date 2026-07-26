"""
AQF-T Market Data Feed — 市场数据模拟器

生产环境替换为真实行情 API (QMT / Tushare / Wind)
"""
import random
import time
from datetime import datetime
from event_bus.event_bus import bus, EventType

# 模拟 A 股市场状态
SCENARIOS = [
    {"regime": "Bull Expansion", "trend": "UP", "volatility": 0.15, "weight": 0.35},
    {"regime": "Sideways", "trend": "NEUTRAL", "volatility": 0.08, "weight": 0.40},
    {"regime": "Bear Decline", "trend": "DOWN", "volatility": 0.25, "weight": 0.15},
    {"regime": "High Volatility", "trend": "NEUTRAL", "volatility": 0.50, "weight": 0.10},
]


class MarketDataSimulator:
    """市场数据模拟器 — 生成真实感市场数据流"""

    def __init__(self, symbols: list[str] = None):
        self.symbols = symbols or ["000300", "000905", "600519", "300750"]
        self.prices = {s: random.uniform(10, 200) for s in self.symbols}

    def generate_tick(self) -> dict:
        """生成一个 Tick"""
        scenario = random.choices(SCENARIOS, weights=[s["weight"] for s in SCENARIOS])[0]
        symbol = random.choice(self.symbols)
        change = random.gauss(0, scenario["volatility"])
        self.prices[symbol] *= (1 + change)
        self.prices[symbol] = max(self.prices[symbol], 0.01)

        return {
            "symbol": symbol,
            "price": round(self.prices[symbol], 2),
            "volume": random.randint(1000, 100000),
            "trend": scenario["trend"],
            "regime": scenario["regime"],
            "volatility": scenario["volatility"],
            "timestamp": datetime.now().isoformat(),
        }

    def start_stream(self, interval: float = 2.0):
        """开始持续输出市场数据到 Event Bus"""
        print(f"[MarketData] Starting data stream (interval={interval}s)...")
        while True:
            tick = self.generate_tick()
            bus.publish(EventType.MARKET_DATA, tick, "market_data_feed")
            print(f"[MarketData] {tick['symbol']} {tick['price']:.2f} "
                  f"({tick['trend']}, {tick['regime']}, vol={tick['volatility']:.2f})")
            time.sleep(interval)
