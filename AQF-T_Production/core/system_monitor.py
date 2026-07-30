"""
Infrastructure Monitor — 系统健康监控 (V1.2 Health Profile分层)
================================================================
SIMULATOR: CPU / Memory / Config
PAPER:     CPU / Memory / Report存储 / Market Provider
LIVE:      CPU / Memory / DB / QMT / L2 freshness / Position Sync
"""
import psutil
import sqlite3
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class SystemHealth:
    qmt_connected: bool = False
    qmt_checked: bool = False
    l2_data_age_seconds: float = 999
    l1_data_age_seconds: float = 999
    db_ok: bool = False
    db_checked: bool = False
    models_loaded: dict = None
    cpu_pct: float = 0
    memory_pct: float = 0
    disk_free_gb: float = 0
    report_writable: bool = False
    report_checked: bool = False
    overall: str = "UNKNOWN"
    skipped_checks: list = None

    def to_dict(self) -> dict:
        qmt_str = "OK" if self.qmt_connected else ("DOWN" if self.qmt_checked else "SKIPPED")
        db_str = "OK" if self.db_ok else ("FAIL" if self.db_checked else "SKIPPED")
        l2_str = f"{self.l2_data_age_seconds:.1f}s" if self.qmt_checked else "SKIPPED"
        return {
            "qmt": qmt_str,
            "l2_age": l2_str,
            "l1_age": f"{self.l1_data_age_seconds:.1f}s",
            "db": db_str,
            "report_storage": "OK" if self.report_writable else ("SKIPPED" if not self.report_checked else "FAIL"),
            "models": self.models_loaded or {},
            "cpu": f"{self.cpu_pct:.0f}%",
            "memory": f"{self.memory_pct:.0f}%",
            "disk": f"{self.disk_free_gb:.0f}GB",
            "skipped": self.skipped_checks or [],
            "overall": self.overall,
        }


# Health Profiles
HEALTH_PROFILES = {
    "simulator": {
        "cpu": True, "memory": True, "disk": True,
        "report_storage": True,
        "qmt": False, "l2": False, "db": False, "l1": False,
    },
    "paper": {
        "cpu": True, "memory": True, "disk": True,
        "report_storage": True, "market_provider": True,
        "qmt": False, "l2": False, "db": False, "l1": False,
    },
    "live": {
        "cpu": True, "memory": True, "disk": True,
        "db": True, "qmt": True, "l2": True, "l1": True,
        "report_storage": True, "position_sync": True,
    },
}


class SystemMonitor:
    """基础设施健康监控 — 按Health Profile分层检查"""

    def __init__(self, db_path: str = "data/aqft.db"):
        self.db_path = db_path
        self.last_l2_time: Optional[datetime] = None
        self.last_l1_time: Optional[datetime] = None

    def check(self, mode: str = "paper") -> SystemHealth:
        profile = HEALTH_PROFILES.get(mode, HEALTH_PROFILES["simulator"])
        health = SystemHealth(skipped_checks=[])
        issues = []

        # ── 通用检查 (所有模式) ──
        health.cpu_pct = psutil.cpu_percent()
        health.memory_pct = psutil.virtual_memory().percent
        health.disk_free_gb = psutil.disk_usage("/").free / (1024**3)
        health.models_loaded = {"lgbm_trend": False, "xgb_timing": False}

        if health.memory_pct > 85:
            issues.append("内存不足")

        # ── Report存储 ──
        if profile.get("report_storage"):
            health.report_checked = True
            try:
                p = Path("reports")
                p.mkdir(exist_ok=True)
                test_file = p / ".health_check"
                test_file.write_text("ok")
                test_file.unlink()
                health.report_writable = True
            except Exception:
                health.report_writable = False
                issues.append("报告存储不可写")

        # ── QMT ──
        if profile.get("qmt"):
            health.qmt_checked = True
            try:
                from xtquant import xtdata
                health.qmt_connected = True
            except Exception:
                health.qmt_connected = False
                issues.append("QMT断开")
        else:
            health.skipped_checks.append("QMT")

        # ── L2数据新鲜度 ──
        if profile.get("l2"):
            if self.last_l2_time:
                health.l2_data_age_seconds = (datetime.now() - self.last_l2_time).total_seconds()
            if health.l2_data_age_seconds > 30:
                issues.append("L2数据断流>30s")
        else:
            health.l2_data_age_seconds = 0
            health.skipped_checks.append("L2")

        # ── 数据库 ──
        if profile.get("db"):
            health.db_checked = True
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute("SELECT 1")
                conn.close()
                health.db_ok = True
            except Exception:
                health.db_ok = False
                issues.append("数据库异常")
        else:
            health.db_ok = True
            health.skipped_checks.append("DB")

        # ── Market Provider ──
        if profile.get("market_provider"):
            health.skipped_checks.append("MarketProvider(SKIPPED)")

        # ── Position Sync ──
        if profile.get("position_sync"):
            health.skipped_checks.append("PositionSync(SKIPPED)")

        # ── 综合判断 ──
        if not issues:
            health.overall = "HEALTHY"
        elif len(issues) <= 2:
            health.overall = "WARNING"
        else:
            health.overall = "CRITICAL"

        return health

    def mark_l2_update(self):
        self.last_l2_time = datetime.now()

    def mark_l1_update(self):
        self.last_l1_time = datetime.now()
