"""
M1 Data Quality — 数据校验器
规则注册制, 配置驱动
"""
from dataclasses import dataclass, field
from typing import Callable
from data_quality.data_model import BarRecord, TickRecord, OrderBookRecord


@dataclass
class ValidationResult:
    rule_name: str
    passed: bool
    detail: str = ""
    severity: str = "info"  # info / warning / critical


class Validator:
    """数据校验器 — 规则注册制"""

    def __init__(self):
        self._rules: list[Callable] = []

    def register(self, rule: Callable):
        """注册校验规则"""
        self._rules.append(rule)

    def validate(self, record) -> list[ValidationResult]:
        """运行所有规则"""
        results = []
        for rule in self._rules:
            try:
                r = rule(record)
                if isinstance(r, ValidationResult):
                    results.append(r)
            except Exception as e:
                results.append(ValidationResult(
                    rule.__name__, False, str(e), "critical"))
        return results


# ── 内置规则 ──

def rule_price_positive(record: BarRecord) -> ValidationResult:
    """价格必须为正"""
    ok = all(v > 0 for v in [record.open, record.high, record.low, record.close])
    return ValidationResult("price_positive", ok,
                            "" if ok else f"负价格: {record.symbol}",
                            "critical" if not ok else "info")


def rule_ohlc_invariant(record: BarRecord) -> ValidationResult:
    """OHLC不变量: high>=low, high>=open, high>=close, low<=open, low<=close"""
    checks = [
        record.high >= record.low,
        record.high >= record.open,
        record.high >= record.close,
        record.low <= record.open,
        record.low <= record.close,
    ]
    ok = all(checks)
    return ValidationResult("ohlc_invariant", ok,
                            "" if ok else "OHLC不变量违反",
                            "critical" if not ok else "info")


def rule_volume_nonzero(record: BarRecord) -> ValidationResult:
    """成交量不为负"""
    ok = record.volume >= 0
    return ValidationResult("volume_nonzero", ok,
                            "" if ok else f"负成交量: {record.volume}",
                            "critical" if not ok else "info")


# 创建默认校验器
bar_validator = Validator()
bar_validator.register(rule_price_positive)
bar_validator.register(rule_ohlc_invariant)
bar_validator.register(rule_volume_nonzero)
