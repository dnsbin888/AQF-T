"""
Timing XGB — 维度2: L2择时
数据: L2逐笔成交 + 十档盘口 + 委托队列 + 大单统计
模型: XGBoost
"""
from dataclasses import dataclass


@dataclass
class TimingSignal:
    symbol: str
    timing: str         # NOW / WAIT
    confidence: float   # 0-1
    reason: str


class TimingPredictor:
    """
    维度2: 择时 (XGBoost)

    数据: L2逐笔成交 + 十档盘口 + 委托队列 + 大单统计
    标签: 未来30/60分钟收益率 (二分类: NOW/WAIT)
    输出: NOW / WAIT + 置信度
    """

    def __init__(self, model_path: str = ""):
        self.model_path = model_path
        self.model = None  # 待训练后加载

    def predict(self, l2_features: dict) -> TimingSignal:
        """
        择时判断

        生产环境: model.predict(l2_features)
        开发环境: 规则降级
        """
        if self.model:
            return self._model_predict(l2_features)
        return self._rule_predict(l2_features)

    def _model_predict(self, l2_features: dict) -> TimingSignal:
        """XGBoost 模型预测"""
        prob = 0.70  # placeholder
        return TimingSignal(
            symbol=l2_features.get("symbol", ""),
            timing="NOW" if prob > 0.60 else "WAIT",
            confidence=abs(prob - 0.5) * 2,
            reason=f"XGBoost prob={prob:.2f}",
        )

    def _rule_predict(self, l2_features: dict) -> TimingSignal:
        """规则降级 (模型不可用时)"""
        big_buy = l2_features.get("net_big_flow", 0)
        seal_ratio = l2_features.get("seal_ratio", 0)
        dd = l2_features.get("ddy", 0)

        # L2信号: 大单净流入 + DDY>0(筹码集中) + 封单稳固
        score = 0
        if big_buy > 0:
            score += 1
        if seal_ratio > 5:
            score += 1
        if dd > 0:
            score += 1

        if score >= 2:
            return TimingSignal(
                symbol=l2_features.get("symbol", ""),
                timing="NOW", confidence=0.65,
                reason=f"L2规则: {score}/3信号满足",
            )
        return TimingSignal(
            symbol=l2_features.get("symbol", ""),
            timing="WAIT", confidence=0.50,
            reason=f"L2规则: 仅{score}/3信号",
        )
