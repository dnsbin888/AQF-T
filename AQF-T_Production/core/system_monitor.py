"""
Infrastructure Monitor — 系统健康监控
生产必须有: QMT状态/L2延迟/DB/模型加载/CPU/内存
"""
import psutil
import sqlite3
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class SystemHealth:
    qmt_connected: bool = False
    l2_data_age_seconds: float = 999    # L2数据新鲜度
    l1_data_age_seconds: float = 999
    db_ok: bool = False
    models_loaded: dict = None           # {model_name: bool}
    cpu_pct: float = 0
    memory_pct: float = 0
    disk_free_gb: float = 0
    event_bus_queue_size: int = 0
    overall: str = "UNKNOWN"             # HEALTHY / WARNING / CRITICAL

    def to_dict(self) -> dict:
        return {
            "qmt": "OK" if self.qmt_connected else "DOWN",
            "l2_age": f"{self.l2_data_age_seconds:.1f}s",
            "l1_age": f"{self.l1_data_age_seconds:.1f}s",
            "db": "OK" if self.db_ok else "FAIL",
            "models": self.models_loaded or {},
            "cpu": f"{self.cpu_pct:.0f}%",
            "memory": f"{self.memory_pct:.0f}%",
            "disk": f"{self.disk_free_gb:.0f}GB",
            "overall": self.overall,
        }


class SystemMonitor:
    """基础设施健康监控"""

    def __init__(self, db_path: str = "data/aqft.db"):
        self.db_path = db_path
        self.last_l2_time: Optional[datetime] = None
        self.last_l1_time: Optional[datetime] = None

    def check(self, mode: str = "paper") -> SystemHealth:
        health = SystemHealth()
        is_live = (mode == "live")

        # QMT连接 (仅Live模式检查)
        if is_live:
            try:
                from xtquant import xtdata
                health.qmt_connected = True
            except Exception:
                health.qmt_connected = False
        else:
            health.qmt_connected = True  # Paper/Simulator: 跳过

        # L2数据新鲜度
        if self.last_l2_time:
            health.l2_data_age_seconds = (datetime.now() - self.last_l2_time).total_seconds()
        elif not is_live:
            health.l2_data_age_seconds = 0  # Paper模式: 无需L2

        # 数据库 (仅Live模式检查)
        if is_live:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute("SELECT 1")
                conn.close()
                health.db_ok = True
            except Exception:
                health.db_ok = False
        else:
            health.db_ok = True  # Paper/Simulator: 跳过

        # 模型加载状态
        health.models_loaded = {
            "lgbm_trend": False,
            "xgb_timing": False,
        }

        # CPU/内存
        health.cpu_pct = psutil.cpu_percent()
        health.memory_pct = psutil.virtual_memory().percent
        health.disk_free_gb = psutil.disk_usage("/").free / (1024**3)

        # 综合判断
        issues = []
        if is_live and not health.qmt_connected:
            issues.append("QMT断开")
        if is_live and health.l2_data_age_seconds > 30:
            issues.append("L2数据断流>30s")
        if is_live and not health.db_ok:
            issues.append("数据库异常")
        if health.memory_pct > 85:
            issues.append("内存不足")

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
