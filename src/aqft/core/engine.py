"""
AQF-T Runtime Engine — 系统主引擎
负责模块加载、服务编排、生命周期管理
"""
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger("aqft.engine")


@dataclass
class SystemStatus:
    """系统运行状态"""
    name: str = "AQF-T"
    version: str = "3.1.0"
    mode: str = "development"
    modules: dict = field(default_factory=dict)
    uptime: float = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "mode": self.mode,
            "modules": self.modules,
            "uptime": self.uptime,
        }


class AQFTEngine:
    """AQF-T 主引擎 — 系统唯一入口"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/system.yaml"
        self.status = SystemStatus()
        self._modules: dict = {}
        logger.info(f"AQF-T Engine V{self.status.version} initializing...")

    def load_config(self) -> dict:
        """加载系统配置"""
        import yaml

        path = Path(self.config_path)
        if not path.exists():
            logger.warning(f"Config not found: {self.config_path}, using defaults")
            return {}

        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self.status.mode = config.get("system", {}).get("mode", "development")
        logger.info(f"Config loaded: mode={self.status.mode}")
        return config

    def start(self) -> SystemStatus:
        """启动系统"""
        logger.info("=" * 60)
        logger.info("  AQF-T Autonomous Quantitative Fusion Trading System")
        logger.info(f"  Version: {self.status.version}")
        logger.info(f"  Mode: {self.status.mode}")
        logger.info("=" * 60)

        config = self.load_config()

        # 按顺序加载模块
        module_order = [
            "data", "ai_brain", "strategy",
            "risk", "execution", "world_model",
            "decision", "agent"
        ]

        for name in module_order:
            mod_cfg = config.get("modules", {}).get(name, {})
            if mod_cfg.get("enabled", True):
                self.status.modules[name] = "initialized"
                logger.info(f"  [{name:15s}] initialized")

        # Risk 模块特殊处理
        if config.get("modules", {}).get("risk", {}).get("kill_switch_active", True):
            logger.info("  [risk            ] kill_switch ACTIVE")

        logger.info("-" * 60)
        logger.info("  AQF-T Intelligence Console ONLINE")
        logger.info(f"  http://{config.get('server', {}).get('host', '127.0.0.1')}:{config.get('server', {}).get('port', 8080)}")
        logger.info("-" * 60)

        return self.status

    def stop(self):
        """停止系统"""
        logger.info("AQF-T Engine stopping...")
        for name in self.status.modules:
            self.status.modules[name] = "stopped"
            logger.info(f"  [{name:15s}] stopped")
        logger.info("AQF-T Engine stopped.")

    def get_status(self) -> dict:
        """获取系统状态"""
        return self.status.to_dict()


# 全局引擎实例
_engine: Optional[AQFTEngine] = None


def get_engine() -> AQFTEngine:
    """获取全局引擎实例"""
    global _engine
    if _engine is None:
        _engine = AQFTEngine()
    return _engine
