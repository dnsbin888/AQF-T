"""
Predictor LGB — 维度1: Alpha趋势预测
数据: 日K线 + 100因子
模型: LightGBM
"""
from dataclasses import dataclass


@dataclass
class AlphaSignal:
    symbol: str
    direction: str       # BUY / SELL / HOLD
    probability: float   # 0-1
    expected_return: float
    confidence: float


class AlphaPredictor:
    """
    维度1: 趋势预测 (LightGBM)

    数据: 日K线 + 100因子
    标签: 未来N日收益率
    输出: 方向 + 概率
    """

    def __init__(self, model_path: str = ""):
        self.model_path = model_path
        self.model = None  # 待训练后加载

    def predict(self, features: dict) -> AlphaSignal:
        """
        预测趋势方向

        生产环境: model.predict(features)
        开发环境: 规则降级
        """
        if self.model:
            return self._model_predict(features)
        return self._rule_predict(features)

    def _model_predict(self, features: dict) -> AlphaSignal:
        """LightGBM 模型预测"""
        # model.predict(feature_vector) → probability
        prob = 0.65  # placeholder
        return AlphaSignal(
            symbol=features.get("symbol", ""),
            direction="BUY" if prob > 0.55 else ("SELL" if prob < 0.45 else "HOLD"),
            probability=prob,
            expected_return=0.0,
            confidence=abs(prob - 0.5) * 2,
        )

    def _rule_predict(self, features: dict) -> AlphaSignal:
        """规则降级 (模型不可用时)"""
        # 简化趋势判断
        ma5 = features.get("ma_5", 0)
        ma20 = features.get("ma_20", 0)
        volume_ratio = features.get("volume_ratio", 1.0)

        if ma5 > ma20 and volume_ratio > 1.2:
            direction, prob = "BUY", 0.65
        elif ma5 < ma20:
            direction, prob = "SELL", 0.60
        else:
            direction, prob = "HOLD", 0.50

        return AlphaSignal(
            symbol=features.get("symbol", ""),
            direction=direction,
            probability=prob,
            expected_return=0.0,
            confidence=abs(prob - 0.5) * 2,
        )
