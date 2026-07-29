"""M1 tests — anomaly_detector"""
from datetime import datetime, timedelta
from data_quality.anomaly_detector import AnomalyDetector, L2FreezeDetector


def test_normal_no_anomaly():
    d = AnomalyDetector()
    t1 = datetime.now()
    t2 = t1 + timedelta(seconds=3)
    events = d.detect("SH.600519", t1, 100.0, 10000)
    assert len(events) == 0
    events = d.detect("SH.600519", t2, 101.0, 11000)
    assert len(events) == 0


def test_duplicate_timestamp():
    d = AnomalyDetector()
    t = datetime.now()
    d.detect("SH.600519", t, 100.0, 10000)
    events = d.detect("SH.600519", t, 100.0, 10000)
    assert any(e.event_type == "DUPLICATE" for e in events)


def test_price_jump_detection():
    d = AnomalyDetector(max_price_jump_pct=5.0)
    t1 = datetime.now()
    t2 = t1 + timedelta(seconds=3)
    d.detect("SH.600519", t1, 100.0, 10000)
    events = d.detect("SH.600519", t2, 120.0, 10000)  # 20% jump
    assert any(e.event_type == "JUMP" for e in events)


def test_gap_detection():
    d = AnomalyDetector(max_gap_seconds=5)
    t1 = datetime.now()
    t2 = t1 + timedelta(seconds=30)  # 30s gap
    d.detect("SH.600519", t1, 100.0, 10000)
    events = d.detect("SH.600519", t2, 101.0, 10000)
    assert any(e.event_type == "GAP" for e in events)


def test_l2_freeze_detection():
    fd = L2FreezeDetector(max_stale_seconds=1)
    fd.heartbeat()
    # 不等待, 直接检查 — 刚heartbeat完应该正常
    result = fd.check()
    should_be_none = (result is None)
    assert should_be_none, "刚heartbeat完应该无冻结"
