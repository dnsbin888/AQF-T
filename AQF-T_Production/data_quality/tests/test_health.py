"""M1 tests — health_monitor"""
from datetime import datetime
from data_quality.health_monitor import HealthMonitor


def test_initial_score_full():
    hm = HealthMonitor()
    s = hm.snapshot()
    assert s.score >= 90, f"初始满分应≥90: {s.score}"


def test_failed_validations_lower_score():
    hm = HealthMonitor()
    for _ in range(50):
        hm.record_validation(True)
    for _ in range(50):
        hm.record_validation(False)
    s = hm.snapshot()
    assert s.score < 95


def test_missing_data_lowers_completeness():
    hm = HealthMonitor()
    for _ in range(90):
        hm.record_data_arrival(datetime.now())
    for _ in range(10):
        hm.record_missing()
    s = hm.snapshot()
    assert s.completeness < 1.0


def test_is_healthy():
    hm = HealthMonitor()
    s = hm.snapshot()
    assert s.is_healthy()
    assert not s.is_healthy(threshold=101)  # default score=100, 100<101→unhealthy
