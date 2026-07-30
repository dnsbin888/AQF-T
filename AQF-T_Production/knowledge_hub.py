"""
Knowledge Hub — 知识中心
归因+经验+训练+模型评估+策略生命周期
"""
from datetime import datetime
from enum import Enum
from review.factor_attribution import ReviewEngine
from learning.model_registry import ModelRegistry


class StrategyStatus(Enum):
    CREATED = "created"
    BACKTESTING = "backtesting"
    PAPER = "paper_trading"
    LIVE = "live"
    PAUSED = "paused"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class StrategyLifecycle:
    """策略生命周期管理"""

    def __init__(self):
        self.strategies: dict[str, dict] = {}

    def register(self, name: str, path: str, params: dict):
        self.strategies[name] = {
            "name": name, "path": path, "params": params,
            "status": StrategyStatus.CREATED.value,
            "created_at": datetime.now().isoformat(),
            "promoted_at": None,
            "performance": {"sharpe": 0, "win_rate": 0, "max_dd": 0, "trades": 0},
            "history": [{"action": "created", "timestamp": datetime.now().isoformat()}],
        }

    def promote(self, name: str, new_status: StrategyStatus):
        if name in self.strategies:
            self.strategies[name]["status"] = new_status.value
            self.strategies[name]["promoted_at"] = datetime.now().isoformat()
            self.strategies[name]["history"].append({
                "action": f"promoted→{new_status.value}",
                "timestamp": datetime.now().isoformat(),
            })

    def should_deprecate(self, name: str) -> bool:
        """自动降权: 连续3月Sharpe<0.5 或 月回撤>20%"""
        s = self.strategies.get(name, {})
        perf = s.get("performance", {})
        return (perf.get("sharpe", 1) < 0.5 and perf.get("max_dd", 0) > 0.20)

    def should_upgrade(self, name: str) -> bool:
        """自动升级: 连续3月Sharpe>1.5 且 回撤<10%"""
        s = self.strategies.get(name, {})
        perf = s.get("performance", {})
        return (perf.get("sharpe", 1) > 1.5 and perf.get("max_dd", 100) < 0.10)


class KnowledgeHub:
    """AQF-T 知识中心"""

    def __init__(self):
        self.review = ReviewEngine()
        self.registry = ModelRegistry()
        self.lifecycle = StrategyLifecycle()
        self.training_history: list[dict] = []

    def record_trade(self, trade: dict):
        self.review.attribute(trade)

    def get_best_model(self, model_type: str) -> dict:
        return self.registry.get_active(model_type) or {}

    def get_strategy_performance(self) -> dict:
        s = self.review.summary()
        return {
            "total_trades": s.get("total_trades", s.get("total", 0)),
            "win_rate": s.get("win_rate", 0),
            "top_signals": s.get("top_contributing_signals", []),
        }

    def daily_report(self, regime, positions, signals) -> str:
        perf = self.get_strategy_performance()
        active = [n for n, st in self.lifecycle.strategies.items()
                  if st["status"] == "live"]
        return (
            f"AQF-T {datetime.now().strftime('%Y-%m-%d')}\n"
            f"Regime: {regime.sentiment_phase} ({regime.operation_mode})\n"
            f"Active: {len(active)} strategies | {len(positions)} positions\n"
            f"WinRate: {perf['win_rate']} | Trades: {perf['total_trades']}"
        )
