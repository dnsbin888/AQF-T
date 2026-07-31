"""
QMT L2 数据加载器 — 国金证券专用
逐笔成交 / 十档盘口 / 委托队列 / 大单统计
"""
import sqlite3
from datetime import datetime
from pathlib import Path

# QMT xtquant (需安装: pip install xtquant)
try:
    from xtquant import xtdata
    QMT_AVAILABLE = True
except ImportError:
    QMT_AVAILABLE = False
    print("[L2] xtquant not installed. Run: pip install xtquant")


class QMTL2Loader:
    """国金QMT Level-2 数据加载器"""

    def __init__(self, db_path: str = "data/aqft.db"):
        self.db_path = db_path
        self.connected = False
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> bool:
        if not QMT_AVAILABLE:
            return False
        try:
            # xtdata.connect()  # QMT客户端运行后自动连接
            self.connected = True
            return True
        except Exception as e:
            print(f"[L2] Connect error: {e}")
            return False

    def get_l2_transaction(self, symbol: str) -> list[dict]:
        """逐笔成交"""
        if not self.connected:
            return []
        try:
            data = xtdata.get_l2_transaction(symbol)
            if data is None:
                return []
            return [
                {
                    "symbol": symbol,
                    "time": row[0],
                    "price": row[1],
                    "volume": row[2],
                    "direction": "B" if row[3] > 0 else "S",
                    "type": self._classify_order(row[2])
                }
                for row in data
            ]
        except Exception as e:
            print(f"[L2] Transaction error for {symbol}: {e}")
            return []

    def get_l2_orderbook(self, symbol: str) -> dict:
        """十档盘口"""
        if not self.connected:
            return {}
        try:
            data = xtdata.subscribe_quote(symbol, period="l2quote")
            if data is None:
                return {}
            return {
                "symbol": symbol,
                "time": datetime.now().isoformat(),
                "bid1_p": data.get("bid1", 0),
                "bid1_v": data.get("bid1_volume", 0),
                "ask1_p": data.get("ask1", 0),
                "ask1_v": data.get("ask1_volume", 0),
                "bid_volume": sum(data.get(f"bid{i}_volume", 0) for i in range(1, 11)),
                "ask_volume": sum(data.get(f"ask{i}_volume", 0) for i in range(1, 11)),
            }
        except Exception as e:
            print(f"[L2] OrderBook error for {symbol}: {e}")
            return {}

    def get_big_order_stats(self, symbol: str) -> dict:
        """大单统计"""
        if not self.connected:
            return {}
        try:
            data = xtdata.get_l2_transaction_count(symbol)
            if data is None:
                return {}
            return {
                "symbol": symbol,
                "big_buy": data.get("big_buy_volume", 0),
                "big_sell": data.get("big_sell_volume", 0),
                "net_big_flow": data.get("big_buy_volume", 0) - data.get("big_sell_volume", 0),
                "time": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"[L2] BigOrder error: {e}")
            return {}

    def save_transaction(self, symbol: str):
        """保存逐笔成交到SQLite"""
        data = self.get_l2_transaction(symbol)
        if not data:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """INSERT OR IGNORE INTO l2_transaction
                   (symbol, time, price, volume, direction, type)
                   VALUES (:symbol, :time, :price, :volume, :direction, :type)""",
                data
            )

    @staticmethod
    def _classify_order(volume: int) -> str:
        if volume >= 1000000:   return "特大单"
        if volume >= 200000:    return "大单"
        if volume >= 40000:     return "中单"
        return "小单"
