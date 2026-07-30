"""M1 tests — recovery_manager"""
from data_quality.recovery_manager import RecoveryManager, RecoveryAction


def test_info_passes():
    rm = RecoveryManager()
    assert rm.decide("info") == RecoveryAction.PASS


def test_warning_retries_then_fails():
    rm = RecoveryManager(max_retries=2)
    assert rm.decide("warning") == RecoveryAction.RETRY
    assert rm.decide("warning") == RecoveryAction.RETRY
    # 3rd call: retries exhausted, backup not configured → SWITCH_BACKUP
    assert rm.decide("warning") == RecoveryAction.SWITCH_BACKUP


def test_critical_fails_directly():
    rm = RecoveryManager()
    assert rm.decide("critical") == RecoveryAction.FAIL


def test_reset_retries():
    rm = RecoveryManager(max_retries=2)
    rm.decide("warning")
    rm.reset_retries()
    assert rm.decide("warning") == RecoveryAction.RETRY
