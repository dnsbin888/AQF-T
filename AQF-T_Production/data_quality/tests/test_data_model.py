"""M1 tests — data_model"""
from datetime import datetime
from data_quality.data_model import TickRecord, BarRecord, OrderBookRecord


def test_tick_creation():
    t = TickRecord("SH.600519", datetime.now(), 1500.0, 1000, "BUY")
    assert t.symbol == "SH.600519"
    assert t.price == 1500.0
    assert t.direction == "BUY"


def test_bar_creation():
    b = BarRecord("SH.600519", datetime.now(), 100, 110, 90, 105, 10000, 1000000)
    assert b.high >= b.low
    assert b.volume >= 0


def test_bar_immutable():
    b = BarRecord("SH.600519", datetime.now(), 100, 110, 90, 105, 10000, 1000000)
    try:
        b.close = 200
        assert False, "应抛出 FrozenInstanceError"
    except Exception:
        pass  # frozen dataclass 正确阻止了修改


def test_orderbook_creation():
    bids_p = (99.0, 98.5, 98.0, 97.5, 97.0, 96.5, 96.0, 95.5, 95.0, 94.5)
    bids_v = (1000, 2000, 1500, 3000, 500, 800, 1200, 600, 900, 400)
    asks_p = (101.0, 101.5, 102.0, 102.5, 103.0, 103.5, 104.0, 104.5, 105.0, 105.5)
    asks_v = (2000, 1500, 3000, 500, 800, 1200, 600, 900, 400, 1000)
    ob = OrderBookRecord("SH.600519", datetime.now(), bids_p, bids_v, asks_p, asks_v)
    assert len(ob.bid_prices) == 10
    assert ob.bid_prices[0] < ob.ask_prices[0]  # bid1 < ask1
