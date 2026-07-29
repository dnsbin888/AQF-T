"""
M5 Statistical Tests — CPCV / DSR / PBO
"""
import math
import random
from dataclasses import dataclass


@dataclass
class ValidationResult:
    pattern_name: str
    sharpe: float = 0.0
    dsr: float = 0.0          # Deflated Sharpe Ratio (>0 = significant)
    pbo: float = 0.0          # Probability of Backtest Overfitting (<0.1 = safe)
    cpcv_stable: bool = True  # Cross-validation stability
    conclusion: str = "RESEARCH"


def compute_dsr(sharpe: float, n_trials: int, n_samples: int,
                skew: float = -0.5, kurt: float = 3.0) -> float:
    """
    Deflated Sharpe Ratio (简化版 — 生产用完整实现)
    DSR > 0: Sharpe显著, 非运气
    DSR < 0: 可能是过拟合
    """
    if n_samples < 30 or sharpe <= 0:
        return -1.0
    # Expected max Sharpe under multiple testing
    expected_max = math.sqrt(2 * math.log(n_trials)) if n_trials > 1 else 1.0
    se = math.sqrt((1 + 0.5 * sharpe**2) / n_samples)
    dsr = (sharpe - expected_max) / se if se > 0 else -1.0
    return round(dsr, 4)


def compute_pbo(returns: list[float], n_bootstrap: int = 500) -> float:
    """
    Probability of Backtest Overfitting (简化版)
    PBO < 0.1: 安全
    PBO > 0.5: 严重过拟合
    """
    if len(returns) < 30:
        return 1.0
    sharpe_in = 0.0
    for _ in range(n_bootstrap):
        sample = [random.choice(returns) for _ in range(len(returns))]
        mean = sum(sample) / len(sample)
        std = (sum((x - mean)**2 for x in sample) / len(sample))**0.5
        s = mean / std * math.sqrt(252) if std > 0 else 0
        if s > sharpe_in:
            sharpe_in = s
    return round(1.0 - min(sharpe_in, 1.0), 4)


def cpcv_check(returns: list[float], n_folds: int = 5) -> tuple[bool, list[float]]:
    """Combinatorial Purged CV — 简化为K-fold稳定性检查"""
    if len(returns) < n_folds * 10:
        return False, []
    fold_size = len(returns) // n_folds
    sharpe_list = []
    for i in range(n_folds):
        fold = returns[i * fold_size:(i + 1) * fold_size]
        mean = sum(fold) / len(fold)
        std = (sum((x - mean)**2 for x in fold) / len(fold))**0.5
        s = mean / std * math.sqrt(252) if std > 0 else 0
        sharpe_list.append(round(s, 2))
    # 稳定: 各fold Sharpe偏差<50%
    stable = all(abs(s - sharpe_list[0]) < abs(sharpe_list[0]) * 0.5
                 for s in sharpe_list)
    return stable, sharpe_list


def validate_pattern(pattern_name: str, returns: list[float],
                     n_trials: int = 10) -> ValidationResult:
    """综合验证一个Pattern"""
    if not returns or len(returns) < 30:
        return ValidationResult(pattern_name=pattern_name, conclusion="INSUFFICIENT_DATA")

    mean = sum(returns) / len(returns)
    std = (sum((x - mean)**2 for x in returns) / len(returns))**0.5
    sharpe = mean / std * math.sqrt(252) if std > 0 else 0

    dsr = compute_dsr(round(sharpe, 2), n_trials, len(returns))
    pbo = compute_pbo(returns)
    stable, fold_sharpes = cpcv_check(returns)

    if dsr > 0 and pbo < 0.1 and stable:
        conclusion = "PRODUCTION"
    elif dsr > 0 and pbo < 0.3:
        conclusion = "VALIDATED"
    else:
        conclusion = "RESEARCH"

    return ValidationResult(
        pattern_name=pattern_name, sharpe=round(sharpe, 2),
        dsr=dsr, pbo=pbo, cpcv_stable=stable, conclusion=conclusion,
    )
