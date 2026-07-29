"""
Learning Plugin Interface — 插件化接口
Decision不知道底层是LightGBM还是Transformer
只调用: Predict() / Explain() / Train() / Evaluate()
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Prediction:
    value: float
    confidence: float
    explanation: str      # SHAP: "MA5贡献+30%, 北向贡献+20%"


@dataclass
class Evaluation:
    ic: float
    icir: float
    sharpe: float
    max_drawdown: float
    auc: float


class LearningPlugin(ABC):
    """所有模型必须实现此接口 — Decision不知道底层是谁"""

    @abstractmethod
    def predict(self, features: dict) -> Prediction:
        """预测 — 屏蔽模型差异"""
        ...

    @abstractmethod
    def explain(self, features: dict) -> str:
        """解释 — SHAP/特征重要性, 可审计"""
        ...

    @abstractmethod
    def train(self, data, labels) -> dict:
        """训练 — 返回metrics"""
        ...

    @abstractmethod
    def evaluate(self, data, labels) -> Evaluation:
        """评估 — 标准化指标"""
        ...

    @property
    @abstractmethod
    def model_type(self) -> str:
        """模型类型标识"""
        ...


# 实现示例: LightGBM / XGBoost / CatBoost 都实现此接口
# Decision只需: plugin.predict(features) → Prediction
# 不需要知道 plugin 是 LGBM 还是 Transformer
