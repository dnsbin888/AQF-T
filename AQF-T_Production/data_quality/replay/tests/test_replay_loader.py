"""M2.1 tests — Replay Loader"""
from datetime import datetime, timedelta
from data_quality.replay.replay_loader import ReplayLoader, ReplayConfig


def test_load_and_replay():
    config = ReplayConfig(
        replay_id="REPLAY-001",
        dataset_version="L2_20260730_v1",
        git_commit="abc123",
    )
    loader = ReplayLoader(config)

    # 模拟L2历史数据
    base_time = datetime(2026, 7, 30, 9, 30, 0)
    ticks = [
        {"symbol": "SH.600519", "timestamp": base_time + timedelta(seconds=i*3),
         "price": 1500.0 + i, "volume": 1000 + i*100, "direction": "BUY",
         "bid1": 1499.0 + i, "ask1": 1501.0 + i}
        for i in range(100)
    ]
    loader.load_list(ticks)
    assert loader.session.total_ticks == 100


def test_ordering():
    config = ReplayConfig(replay_id="R001", dataset_version="v1")
    loader = ReplayLoader(config)
    base = datetime(2026, 7, 30, 9, 30, 0)
    ticks = [
        {"symbol": "SH.600519", "timestamp": base + timedelta(seconds=i),
         "price": 100.0, "volume": 1000}
        for i in range(50)
    ]
    loader.load_list(ticks)
    assert loader.verify_ordering()


def test_determinism():
    """同一数据, 两次Replay, Tick序列完全一致"""
    config = ReplayConfig(replay_id="R001", dataset_version="v1")
    base = datetime(2026, 7, 30, 9, 30, 0)
    ticks = [
        {"symbol": "SH.600519", "timestamp": base + timedelta(seconds=i),
         "price": 100.0 + i, "volume": 1000}
        for i in range(30)
    ]

    loader1 = ReplayLoader(config)
    loader1.load_list(ticks)
    while loader1.next_tick():
        pass

    loader2 = ReplayLoader(config)
    loader2.load_list(ticks)
    while loader2.next_tick():
        pass

    assert loader1.session.is_consistent_with(loader2.session)


def test_reset_and_replay_consistent():
    """Reset后Replay结果一致"""
    config = ReplayConfig(replay_id="R001", dataset_version="v1")
    base = datetime(2026, 7, 30, 9, 30, 0)
    ticks = [
        {"symbol": "SH.600519", "timestamp": base + timedelta(seconds=i),
         "price": 100.0, "volume": 1000}
        for i in range(20)
    ]

    loader = ReplayLoader(config)
    loader.load_list(ticks)
    while loader.next_tick():
        pass
    session1_hashes = loader.session.tick_hashes.copy()

    loader.reset()
    while loader.next_tick():
        pass

    assert loader.session.tick_hashes == session1_hashes


def test_no_gaps():
    config = ReplayConfig(replay_id="R001", dataset_version="v1")
    loader = ReplayLoader(config)
    base = datetime(2026, 7, 30, 9, 30, 0)
    ticks = [
        {"symbol": "SH.600519", "timestamp": base + timedelta(seconds=i),
         "price": 100.0, "volume": 1000}
        for i in range(100)
    ]
    loader.load_list(ticks)
    assert loader.verify_no_gaps(max_gap_seconds=10)
