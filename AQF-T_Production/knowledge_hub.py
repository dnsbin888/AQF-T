"""
Knowledge Hub — 知识中心
归因+经验+训练+模型评估+绩效+Model Registry
"""
from datetime import datetime
from review.factor_attribution import ReviewEngine
from learning.model_registry import ModelRegistry


class KnowledgeHub:
    """AQF-T 知识中心 — 所有经验/训练/评估的统一入口"""

    def __init__(self):
        self.review = ReviewEngine()
        self.registry = ModelRegistry()
        self.training_history: list[dict] = []
        self.strategy_scores: dict[str, dict] = {}

    def record_trade(self, trade: dict):
        """记录交易 → 归因 → 经验"""
        self.review.attribute(trade)

    def record_training(self, model_id: str, metrics: dict):
        """记录训练历史"""
        self.training_history.append({
            "model_id": model_id,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
        })

    def get_best_model(self, model_type: str) -> dict:
        """获取当前最优模型"""
        return self.registry.get_active(model_type) or {}

    def get_strategy_performance(self) -> dict:
        """策略绩效总览"""
        summary = self.review.summary()
        return {
            "total_trades": summary["total_trades"],
            "win_rate": summary["win_rate"],
            "avg_win": summary["avg_win"],
            "avg_loss": summary["avg_loss"],
            "top_signals": summary["top_contributing_signals"],
            "success_cases": summary["success_cases"],
            "failure_cases": summary["failure_cases"],
        }

    def get_experience(self, regime: str = "", limit: int = 20) -> list[dict]:
        """按市场环境检索经验"""
        cases = []
        if regime:
            for t in self.review.trades:
                if hasattr(t, 'entry_signals'):
                    cases.append(t)
        return cases[-limit:]

    def daily_report(self, market_regime, positions, signals) -> str:
        """生成日报告"""
        perf = self.get_strategy_performance()
        return f"""
AQF-T Daily Report {datetime.now().strftime('%Y-%m-%d')}
─────────────────────────────────────
Regime: {market_regime.sentiment_phase} ({market_regime.operation_mode})
Positions: {len(positions)} | Signals: {len(signals)}
Win Rate: {perf['win_rate']} | Trades: {perf['total_trades']}
Top Signal: {perf['top_signals'][0] if perf['top_signals'] else 'N/A'}
─────────────────────────────────────
"""
