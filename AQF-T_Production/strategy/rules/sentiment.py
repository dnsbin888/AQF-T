"""
Sentiment Engine — 情绪周期判断 (游资核心)
"""
from dataclasses import dataclass


@dataclass
class SentimentReport:
    phase: str                  # 冰点期 / 回暖期 / 高潮期 / 退潮期
    score: float                # 情绪值
    limit_up_count: int         # 涨停家数
    limit_down_count: int       # 跌停家数
    max_board_height: int       # 最高连板
   炸板率: float                # 炸板率
    north_flow: float           # 北向净流入(亿)
    recommend_position: float   # 建议仓位
    recommend_strategy: str     # 建议策略


class SentimentEngine:
    """游资情绪周期引擎"""

    def evaluate(self, ctx: dict) -> SentimentReport:
        up = ctx.get("limit_up_count", 0)
        down = ctx.get("limit_down_count", 0)
        height = ctx.get("max_board_height", 0)
       炸板率 = ctx.get("炸板率", 0)
        north = ctx.get("north_bound_net", 0)  # 亿

        # 情绪值公式 (V2.8.6 03_AI_Brain)
        score = up * 2 - down * 3 + height * 5
        if north > 10:
            score += 10
        elif north < -10:
            score -= 10

        # 四阶段判断
        phase = self._classify(score, 炸板率, down, height)

        # 策略+仓位建议
        strategy, position = self._recommend(phase, score)

        return SentimentReport(
            phase=phase, score=score,
            limit_up_count=up, limit_down_count=down,
            max_board_height=height, 炸板率=炸板率,
            north_flow=north,
            recommend_position=position,
            recommend_strategy=strategy,
        )

    def _classify(self, score: float,炸板率: float, down: int, height: int) -> str:
        if down > 30 and height <= 2:
            return "冰点期"
        if height >= 7 and炸板率 < 0.30:
            return "高潮期"
        if 炸板率 > 0.40 or (down > 50):
            return "退潮期"
        if score > 80:
            return "高潮期"
        if score > 20:
            return "回暖期"
        return "冰点期"

    def _recommend(self, phase: str, score: float) -> tuple[str, float]:
        if phase == "高潮期":
            return "Dragon+Trend 重仓龙头", 0.70
        if phase == "回暖期":
            return "Dragon+Sentiment 逐步加仓", 0.50
        if phase == "冰点期":
            return "VolumePrice 试错首板", 0.20
        return "Defensive 空仓/轻仓", 0.10   # 退潮期
