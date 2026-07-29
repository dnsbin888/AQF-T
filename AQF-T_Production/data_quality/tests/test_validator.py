"""M1 tests — validator"""
from datetime import datetime
from data_quality.data_model import BarRecord
from data_quality.validator import bar_validator, Validator, ValidationResult


def test_normal_bar_passes():
    b = BarRecord("SH.600519", datetime.now(), 100, 110, 90, 105, 10000, 1000000)
    results = bar_validator.validate(b)
    assert all(r.passed for r in results), f"正常Bar应全部通过: {results}"


def test_negative_price_fails():
    b = BarRecord("SH.600519", datetime.now(), -1, 10, -5, 5, 10000, 1000000)
    results = bar_validator.validate(b)
    assert any(not r.passed and r.rule_name == "price_positive" for r in results)


def test_ohlc_violation_fails():
    b = BarRecord("SH.600519", datetime.now(), 100, 50, 200, 105, 10000, 1000000)
    results = bar_validator.validate(b)
    assert any(not r.passed and r.rule_name == "ohlc_invariant" for r in results)


def test_negative_volume_fails():
    b = BarRecord("SH.600519", datetime.now(), 100, 110, 90, 105, -100, 1000000)
    results = bar_validator.validate(b)
    assert any(not r.passed and r.rule_name == "volume_nonzero" for r in results)


def test_custom_rule_registration():
    v = Validator()
    def always_fail(r):
        return ValidationResult("always", False, "test", "info")
    v.register(always_fail)
    b = BarRecord("SH.600519", datetime.now(), 100, 110, 90, 105, 10000, 1000000)
    results = v.validate(b)
    assert any(r.rule_name == "always" for r in results)


def test_critical_severity_in_result():
    b = BarRecord("SH.600519", datetime.now(), -1, -1, -1, -1, -1, 0)
    results = bar_validator.validate(b)
    assert any(r.severity == "critical" for r in results)
