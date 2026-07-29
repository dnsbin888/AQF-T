"""
M5 Evidence Builder — Pattern Evidence Package自动生成
"""
import json
from datetime import datetime
from data_quality.replay.validation.backtest_runner import BacktestRunner, BacktestResult
from data_quality.replay.validation.statistical_tests import ValidationResult


class EvidenceBuilder:
    """自动生成Pattern Evidence Package"""

    def build(self, pattern_name: str, bt: BacktestResult,
              vt: ValidationResult, dataset_version: str) -> dict:
        return {
            "pattern": pattern_name,
            "version": "1.0",
            "status": vt.conclusion,
            "dataset": dataset_version,
            "backtest": {
                "samples": bt.sample_size,
                "win_rate": bt.win_rate,
                "profit_factor": bt.profit_factor,
                "max_drawdown": bt.max_drawdown,
                "avg_return": bt.avg_return,
            },
            "statistics": {
                "sharpe": vt.sharpe,
                "dsr": vt.dsr,
                "pbo": vt.pbo,
                "cpcv_stable": vt.cpcv_stable,
            },
            "timestamp": datetime.now().isoformat(),
        }

    def export(self, evidence: dict, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(evidence, f, indent=2, ensure_ascii=False)

    def print_summary(self, evidence: dict) -> str:
        return (
            f"Pattern: {evidence['pattern']}\n"
            f"Status: {evidence['status']}\n"
            f"Samples: {evidence['backtest']['samples']} | "
            f"WinRate: {evidence['backtest']['win_rate']:.1%} | "
            f"PF: {evidence['backtest']['profit_factor']:.2f}\n"
            f"DSR: {evidence['statistics']['dsr']} | "
            f"PBO: {evidence['statistics']['pbo']} | "
            f"CPCV: {evidence['statistics']['cpcv_stable']}"
        )
