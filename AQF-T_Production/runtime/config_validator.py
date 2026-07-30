"""
Config Validation — V1.2 P0-6
Startup config integrity check. Refuse to run if config is invalid.
"""
import yaml
from pathlib import Path
from typing import Optional

REQUIRED_KEYS = {
    "system": ["name", "version", "mode"],
    "qmt": ["path", "account"],
    "data": ["database"],
    "risk": ["max_single_position", "max_total_position", "max_daily_loss", "kill_switch"],
    "execution": ["mode"],
}

VALUE_RANGES = {
    "risk.max_single_position": (0.01, 0.30),
    "risk.max_total_position": (0.10, 1.0),
    "risk.max_daily_loss": (-0.10, 0.0),
    "risk.max_total_drawdown": (-0.30, 0.0),
}

VALID_MODES = ["paper", "live"]
VALID_EXECUTION_MODES = ["paper", "live"]


class ConfigValidator:
    """配置完整性校验器 — 启动时运行，不通过则拒绝启动"""

    def __init__(self, config_path: str = "config/system.yaml"):
        self.config_path = Path(config_path)
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> bool:
        """Returns True if config is production-safe"""
        self.errors = []
        self.warnings = []

        if not self.config_path.exists():
            self.errors.append(f"Config file not found: {self.config_path}")
            return False

        try:
            config = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))
        except Exception as e:
            self.errors.append(f"Config parse error: {e}")
            return False

        # Check required keys
        for section, keys in REQUIRED_KEYS.items():
            if section not in config:
                self.errors.append(f"Missing section: {section}")
                continue
            for key in keys:
                if key not in config[section]:
                    self.errors.append(f"Missing key: {section}.{key}")

        # Check value ranges
        for path, (lo, hi) in VALUE_RANGES.items():
            section, key = path.split(".")
            val = config.get(section, {}).get(key)
            if val is not None:
                if not (lo <= val <= hi):
                    self.errors.append(f"{path}={val} out of range [{lo}, {hi}]")

        # Check modes
        mode = config.get("system", {}).get("mode", "")
        if mode and mode not in VALID_MODES:
            self.errors.append(f"system.mode='{mode}' not in {VALID_MODES}")

        exec_mode = config.get("execution", {}).get("mode", "")
        if exec_mode and exec_mode not in VALID_EXECUTION_MODES:
            self.errors.append(f"execution.mode='{exec_mode}' not in {VALID_EXECUTION_MODES}")

        # Live-mode specific checks
        if mode == "live":
            qmt_path = config.get("qmt", {}).get("path", "")
            if qmt_path and not Path(qmt_path).exists():
                self.warnings.append(f"QMT path not found: {qmt_path}")
            account = config.get("qmt", {}).get("account", "")
            if not account:
                self.errors.append("Live mode requires qmt.account")

            if not config.get("risk", {}).get("kill_switch", False):
                self.errors.append("Live mode requires risk.kill_switch=true")

        # Results
        if self.errors:
            print("[ConfigValidator] FAILED:")
            for e in self.errors:
                print(f"  ERROR: {e}")
            return False

        if self.warnings:
            print("[ConfigValidator] WARNINGS:")
            for w in self.warnings:
                print(f"  WARN: {w}")

        print("[ConfigValidator] PASSED")
        return True

    def validate_or_exit(self):
        """Validate and sys.exit(1) on failure"""
        import sys
        if not self.validate():
            print("\n[ConfigValidator] Config validation failed. Refusing to start.")
            sys.exit(1)
