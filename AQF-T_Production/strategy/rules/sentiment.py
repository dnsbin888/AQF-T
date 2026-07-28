"""
Sentiment Engine — 情绪周期判断
引用: V2.8.6 03_AI_Brain/AQFT_AI_Brain_Design_V2.8.6.md (Sentiment Engine章节)
      情绪值公式 + 四阶段模型 + 题材热度公式
"""
from dataclasses import dataclass


@dataclass
class SentimentReport:
    phase: str              # 冰点期/回暖期/高潮期/退潮期
    score: float            # 情绪值
    limit_up_count: int
    limit_down_count: int
    max_board_height: int
    炸板率: float
    north_flow: float
    recommend_position: float
    recommend_strategy: str


class SentimentEngine:
    """
    游资情绪周期引擎
    直接实现 V2.8.6 03_AI_Brain Sentiment Engine 的设计

    引用自 V2.8.6 03_AI_Brain §4:
      - 情绪值公式: 涨停×2 - 跌停×3 + 连板×5 + 北向×10
      - 四阶段: 冰点(<20)→回暖(20-50)→高潮(50-80)→退潮(>80)
      - 情绪极值: <15极度恐慌(低吸), >85过度狂热(止盈)
      - 炸板率>50%: 暂停所有买入
    """

    def evaluate(self, ctx: dict) -> SentimentReport:
        up = ctx.get("limit_up_count", 0)
        down = ctx.get("limit_down_count", 0)
        height = ctx.get("max_board_height", 0)
        炸板率 = ctx.get("炸板率", 0)
        north = ctx.get("north_bound_net", 0)

        # V2.8.6 03_AI_Brain §4.4 情绪值公式
        score = up * 2 - down * 3 + height * 5
        if north > 10:
            score += 10
        elif north < -10:
            score -= 10

        phase = self._classify(score, 炸板率, down, height)
        strategy, position = self._recommend(phase, score)

        return SentimentReport(
            phase=phase, score=score,
            limit_up_count=up, limit_down_count=down,
            max_board_height=height, 炸板率=炸板率,
            north_flow=north,
            recommend_position=position,
            recommend_strategy=strategy,
        )

    def _classify(self, score: float, 炸板率: float, down: int, height: int) -> str:
        """V2.8.6 03_AI_Brain §4.3 四阶段判断"""
        if down > 30 and height <= 2:
            return "冰点期"
        if height >= 7 and 炸板率 < 0.30:
            return "高潮期"
        if 炸板率 > 0.40 or down > 50:
            return "退潮期"
        if score > 80:
            return "高潮期"
        if score > 20:
            return "回暖期"
        return "冰点期"

    def _recommend(self, phase: str, score: float) -> tuple[str, float]:
        """V2.8.6 04_Strategy §4 适配矩阵"""
        if phase == "高潮期":
            return "Dragon+Trend", 0.70
        if phase == "回暖期":
            return "Dragon+Sentiment", 0.50
        if phase == "冰点期":
            return "VolumePrice试错", 0.20
        return "Defensive空仓", 0.10
