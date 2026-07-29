"""
Model Registry — 模型版本管理
记录: 日期/数据范围/参数/回测结果/状态
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class ModelRegistry:
    """模型注册中心"""

    def __init__(self, registry_path: str = "models/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.models = self._load()

    def _load(self) -> dict:
        if self.registry_path.exists():
            return json.loads(self.registry_path.read_text(encoding="utf-8"))
        return {"models": {}, "history": []}

    def _save(self):
        self.registry_path.write_text(json.dumps(self.models, ensure_ascii=False, indent=2))

    def register(self, model_id: str, model_type: str, version: str,
                 file_path: str, metadata: dict) -> dict:
        """注册新模型"""
        entry = {
            "model_id": model_id,
            "model_type": model_type,       # LGBM / XGBoost
            "version": version,
            "file_path": file_path,
            "training_date": metadata.get("training_date", ""),
            "data_start": metadata.get("data_start", ""),
            "data_end": metadata.get("data_end", ""),
            "features": metadata.get("features", []),
            "hyperparams": metadata.get("hyperparams", {}),
            "backtest": {
                "ic": metadata.get("ic", 0),
                "icir": metadata.get("icir", 0),
                "sharpe": metadata.get("sharpe", 0),
                "max_drawdown": metadata.get("max_drawdown", 0),
                "auc": metadata.get("auc", 0),
            },
            "status": "registered",          # registered/testing/active/deprecated
            "registered_at": datetime.now().isoformat(),
            "promoted_at": None,
            "promoted_by": None,
        }
        self.models["models"][model_id] = entry
        self.models["history"].append({
            "action": "register", "model_id": model_id,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()
        return entry

    def promote(self, model_id: str, approver: str = "system") -> dict:
        """模型上线: registered → active"""
        if model_id not in self.models["models"]:
            return {"error": f"模型 {model_id} 不存在"}

        # 下线旧版本
        model_type = self.models["models"][model_id]["model_type"]
        for mid, m in self.models["models"].items():
            if m["model_type"] == model_type and m["status"] == "active":
                m["status"] = "deprecated"

        self.models["models"][model_id]["status"] = "active"
        self.models["models"][model_id]["promoted_at"] = datetime.now().isoformat()
        self.models["models"][model_id]["promoted_by"] = approver
        self.models["history"].append({
            "action": "promote", "model_id": model_id,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()
        return self.models["models"][model_id]

    def rollback(self, model_id: str) -> dict:
        """回滚: active → deprecated"""
        if model_id not in self.models["models"]:
            return {"error": f"模型 {model_id} 不存在"}

        model_type = self.models["models"][model_id]["model_type"]
        self.models["models"][model_id]["status"] = "deprecated"

        # 恢复上一个active版本
        prev = None
        for mid, m in self.models["models"].items():
            if m["model_type"] == model_type and m["status"] == "deprecated" and mid != model_id:
                if prev is None or m["registered_at"] > prev["registered_at"]:
                    prev = m

        if prev:
            prev_id = prev["model_id"]
            self.models["models"][prev_id]["status"] = "active"

        self.models["history"].append({
            "action": "rollback", "model_id": model_id,
            "restored": prev["model_id"] if prev else None,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()
        return self.models["models"].get(model_id, {})

    def get_active(self, model_type: str) -> Optional[dict]:
        """获取当前活跃模型"""
        for m in self.models["models"].values():
            if m["model_type"] == model_type and m["status"] == "active":
                return m
        return None

    def list_all(self) -> list[dict]:
        """列出所有模型"""
        return [
            {"model_id": m["model_id"], "type": m["model_type"],
             "version": m["version"], "status": m["status"],
             "ic": m["backtest"]["ic"], "sharpe": m["backtest"]["sharpe"]}
            for m in self.models["models"].values()
        ]
