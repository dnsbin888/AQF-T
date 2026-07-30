"""
Market Regime Engine — 市场状态引擎
所有策略的"总开关" — 每天第一个运行, 输出统一市场状态
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class MarketRegime:
    """全市场状态 — 所有策略读取"""

    # 情绪维度
    sentiment_phase: Literal["冰点期", "回暖期", "高潮期", "退潮期"]
    sentiment_score: float              # 情绪值

    # 结构维度
    limit_up_count: int                 # 涨停家数
    limit_down_count: int               # 跌停家数
    board_ladder: dict                  # {2板:N, 3板:N, 4板:N, 5+板:N}
    promotion_rate: float               # 首板→二板晋级率
    zhatban_rate: float                 # 炸板率

    # 资金维度
    north_bound_direction: Literal["流入", "流出", "中性"]
    north_bound_amount: float           # 北向净流入(亿)
    margin_trend: Literal["上升", "下降", "平稳"]

    # 综合决策
    operation_mode: Literal["aggressive", "normal", "cautious", "defensive", "stop"]
    path_a_allowed: bool                # 回封板是否允许
    path_b_allowed: bool                # 半路是否允许
    max_position_pct: float             # 全局仓位上限
    recommended_path: str = ""          # 推荐路径
    regime_confidence: float = 1.0      # 环境置信度 (GPT Q1: 0-1, 影响仓位倍率)
    regime_multiplier: float = 1.0      # 仓位倍率 (GPT V1.1: 高潮1.0/回暖0.8/冰点0.3/退潮0)

    timestamp: str = ""


class MarketRegimeEngine:
    """
    市场状态引擎 — 系统每天第一个运行的模块

    输入: 全市场统计数据 (涨停/跌停/梯队/北向/炸板率)
    输出: MarketRegime → 所有策略读取

    决策逻辑:
      退潮 → stop (两条路都禁止)
      冰点 → cautious (仅B2题材扩散, 轻仓)
      回暖 → normal (A+B, 中等仓位)
      高潮 → aggressive (A+B, 满仓)
    """

    def evaluate(self, market_stats: dict) -> MarketRegime:
        # ── 情绪值 ──
        up = market_stats.get("limit_up_count", 0)
        down = market_stats.get("limit_down_count", 0)
        height = market_stats.get("max_board_height", 0)
        zhatban = market_stats.get("zhatban_rate", market_stats.get("炸板率", 0))
        north = market_stats.get("north_bound_net", 0)

        score = up * 2 - down * 3 + height * 5
        if north > 10:
            score += 10
        elif north < -10:
            score -= 10

        # ── 四阶段 ──
        if down > 30 and height <= 2:
            phase = "冰点期"
        elif height >= 7 and zhatban < 0.30:
            phase = "高潮期"
        elif zhatban > 0.40 or down > 50:
            phase = "退潮期"
        elif score > 80:
            phase = "高潮期"
        elif score > 20:
            phase = "回暖期"
        else:
            phase = "冰点期"

        # ── 梯队 ──
        ladder = market_stats.get("board_ladder", {})
        promotion = market_stats.get("promotion_rate", 0)

        # ── 北向 ──
        if north > 10:
            nb_dir = "流入"
        elif north < -10:
            nb_dir = "流出"
        else:
            nb_dir = "中性"

        # ── 融资 ──
        margin_chg = market_stats.get("margin_balance_change", 0)
        if margin_chg > 0.02:
            margin_t = "上升"
        elif margin_chg < -0.02:
            margin_t = "下降"
        else:
            margin_t = "平稳"

        # ── 综合决策 ──
        mode, path_a, path_b, max_pos, recommended = self._decide(
            phase, score, zhatban, promotion
        )

        # ── 环境置信度 (GPT Q1) ──
        confidence = self._compute_confidence(phase, score, zhatban, promotion)

        return MarketRegime(
            sentiment_phase=phase,
            sentiment_score=round(score, 0),
            limit_up_count=up,
            limit_down_count=down,
            board_ladder=ladder,
            promotion_rate=round(promotion, 2),
            zhatban_rate=round(zhatban, 2),
            north_bound_direction=nb_dir,
            north_bound_amount=round(north, 1),
            margin_trend=margin_t,
            operation_mode=mode,
            path_a_allowed=path_a,
            path_b_allowed=path_b,
            max_position_pct=max_pos,
            regime_confidence=confidence,
            regime_multiplier=self.get_regime_multiplier(phase),
            recommended_path=recommended,
            timestamp=datetime.now().isoformat(),
        )

    def _compute_confidence(self, phase: str, score: float,
                            zhatban: float, promotion: float) -> float:
        """
        环境置信度 (GPT Q1)

        衡量环境判断的确定性:
          - 指标远离边界 → 高置信
          - 指标接近边界 → 低置信

        返回: 0-1, 用于仓位倍率调节
          > 0.8: 正常仓位
          0.6-0.8: 70% 仓位
          < 0.6: 50% 仓位
        """
        confidence = 0.5  # 基准

        # 远离退潮边界 (炸板率低、跌停少 → 更确定)
        if zhatban < 0.20:
            confidence += 0.15
        elif zhatban < 0.30:
            confidence += 0.10
        elif zhatban > 0.50:
            confidence -= 0.10

        # 晋级率高 → 情绪判断更确定
        if promotion > 0.40:
            confidence += 0.15
        elif promotion > 0.25:
            confidence += 0.10
        elif promotion < 0.10:
            confidence -= 0.10

        # 情绪值远离边界
        if score > 100:
            confidence += 0.10
        elif score < -50:
            confidence -= 0.10

        # 退潮期确定性更高 (明确的危险信号)
        if phase == "退潮期":
            confidence += 0.10

        return round(max(0.0, min(1.0, confidence)), 2)

    def _decide(self, phase: str, score: float, zhatban: float,
                promotion: float) -> tuple:
        """
        综合决策 — 所有策略的总开关

        Returns: (mode, path_a, path_b, max_pos, recommended)
        regime_multiplier 按 GPT V1.1: 高潮1.0/回暖0.8/冰点0.3/退潮0
        """
        if phase == "退潮期":
            return ("stop", False, False, 0.0, "空仓")

        if phase == "冰点期":
            if promotion > 0.20:
                return ("cautious", False, True, 0.20, "B2题材扩散")
            return ("defensive", False, False, 0.10, "观望")

        if phase == "高潮期":
            if zhatban < 0.20:
                return ("aggressive", True, True, 0.70, "A+B全开")
            return ("normal", True, True, 0.50, "A+B")

        if phase == "回暖期":
            if promotion > 0.30:
                return ("normal", True, True, 0.50, "A+B")
            return ("normal", True, False, 0.30, "A优先")

        return ("normal", True, True, 0.50, "A+B")

    @staticmethod
    def get_regime_multiplier(phase: str) -> float:
        """仓位倍率 (GPT V1.1): 高潮1.0/回暖0.8/冰点0.3/退潮0"""
        multipliers = {
            "退潮期": 0.0,
            "冰点期": 0.30,
            "回暖期": 0.80,
            "高潮期": 1.0,
        }
        return multipliers.get(phase, 0.50)
