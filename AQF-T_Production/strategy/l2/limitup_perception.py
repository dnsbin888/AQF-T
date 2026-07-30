"""
LimitUp Perception — 涨停感知 (回封板核心)
实现: 炸板分类 + 板块地位 + 回封确认
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ZhaBanAnalysis:
    symbol: str
    is_healthy: bool             # True=洗盘型, False=诱多型
    type: str                    # "洗盘型" | "诱多型"
    score: int                   # 满足条件数
    can_wait: bool               # 是否值得等回封


@dataclass
class BoardStatus:
    symbol: str
    position_score: float        # 板块地位 0-1
    is_main_theme: bool          # 是否主线 (>0.7)
    theme_name: str
    sector_limit_up_count: int
    follower_count: int          # 跟风涨停数


@dataclass
class ReSealQuality:
    symbol: str
    volume_score: float          # 缩量分 (0/0.5/1)
    time_score: float            # 快速分 (0/0.5/1)
    linkage_score: float         # 联动分 (0/0.5/1)
    total_score: float           # 综合 (>0.7→进场)
    can_enter: bool


class LimitUpPerception:
    """涨停感知引擎 — 实现回封板量化判断"""

    # ── 炸板分类 ──

    def classify_break(self, ctx: dict) -> ZhaBanAnalysis:
        """
        炸板分类: 洗盘型 vs 诱多型
        洗盘型≥3 → 等回封 / 诱多型≥2 → 放弃
        """
        conditions_healthy = [
            ctx.get("break_drop_pct", 0) <= 0.05,               # ① 炸板后横盘≤5点
            ctx.get("white_above_yellow", False),                 # ② 白线在黄线上方
            ctx.get("buy_absorption", False),                     # ③ 买盘持续承接
            ctx.get("big_order_on_break", False),                 # ④ 炸板瞬间大单接货
            ctx.get("board_count", 0) <= 5,                       # ⑤ 非高位(连板≤5)
        ]
        conditions_trap = [
            ctx.get("break_drop_pct", 0) > 0.07,                  # ① 直线下坠>7点
            not ctx.get("white_above_yellow", True),              # ② 白线在黄线下方
            not ctx.get("buy_absorption", True),                  # ③ 无买盘承接
            ctx.get("board_count", 0) >= 7,                       # ④ 高位(连板≥7)
        ]

        healthy_count = sum(conditions_healthy)
        trap_count = sum(conditions_trap)

        if healthy_count >= 3:
            return ZhaBanAnalysis(
                symbol=ctx.get("symbol", ""), is_healthy=True,
                type="洗盘型", score=healthy_count, can_wait=True
            )
        elif trap_count >= 2:
            return ZhaBanAnalysis(
                symbol=ctx.get("symbol", ""), is_healthy=False,
                type="诱多型", score=trap_count, can_wait=False
            )
        return ZhaBanAnalysis(
            symbol=ctx.get("symbol", ""), is_healthy=False,
            type="不确定", score=0, can_wait=False
        )

    # ── 板块地位 ──

    def evaluate_board_status(self, ctx: dict) -> BoardStatus:
        """
        板块地位量化
        >0.7 主线 / 0.4-0.7 次线 / <0.4 杂毛
        """
        up_count = ctx.get("sector_limit_up_count", 0)
        follower = ctx.get("follower_count", 0)
        theme_days = ctx.get("theme_days", 0)

        # 涨停家数分
        if up_count >= 10:    count_score = 1.0
        elif up_count >= 5:   count_score = 0.7
        elif up_count >= 3:   count_score = 0.4
        else:                 count_score = 0.0

        # 联动分
        if follower >= 3:     link_score = 1.0
        elif follower >= 1:   link_score = 0.5
        else:                 link_score = 0.0

        # 阶段分
        if theme_days <= 1:   stage_score = 1.0    # 新题材启动
        elif theme_days <= 3: stage_score = 0.8    # 持续
        elif theme_days <= 5: stage_score = 0.3    # 末期
        else:                 stage_score = 0.0    # 退潮

        position_score = max(count_score, link_score, stage_score)

        return BoardStatus(
            symbol=ctx.get("symbol", ""),
            position_score=round(position_score, 2),
            is_main_theme=(position_score > 0.7),
            theme_name=ctx.get("theme_name", ""),
            sector_limit_up_count=up_count,
            follower_count=follower,
        )

    # ── 回封确认 ──

    def evaluate_reseal(self, ctx: dict) -> ReSealQuality:
        """
        回封3标准量化
        综合 > 0.7 → 进场
        """
        # ① 缩量回封
        reseal_vol = ctx.get("reseal_1min_vol", 0)
        first_vol = ctx.get("first_seal_1min_vol", 1)
        vol_ratio = reseal_vol / max(first_vol, 1)
        if vol_ratio < 0.7:     volume_score = 1.0
        elif vol_ratio < 1.0:   volume_score = 0.5
        else:                   volume_score = 0.0

        # ② 快速回封
        reseal_time_min = ctx.get("break_to_reseal_min", 99)
        if reseal_time_min < 5:      time_score = 1.0
        elif reseal_time_min < 10:   time_score = 0.5
        elif reseal_time_min < 15:   time_score = 0.25
        else:                        time_score = 0.0

        # ③ 联动
        linkage = ctx.get("linkage_count", 0)
        if linkage >= 2:       linkage_score = 1.0
        elif linkage >= 1:     linkage_score = 0.5
        else:                  linkage_score = 0.0

        total = (volume_score + time_score + linkage_score) / 3

        return ReSealQuality(
            symbol=ctx.get("symbol", ""),
            volume_score=volume_score,
            time_score=time_score,
            linkage_score=linkage_score,
            total_score=round(total, 2),
            can_enter=(total > 0.7),
        )

    # ── 综合判断 ──

    def should_enter(self, ctx: dict) -> tuple[bool, str, float]:
        """
        回封板最终决策: 能不能进?

        条件链:
          板块地位 > 0.4 (非杂毛)
          AND 炸板 = 洗盘型
          AND 回封 ≥ 2/3标准
        """
        # Step 1: 板块地位
        board = self.evaluate_board_status(ctx)
        if board.position_score < 0.4:
            return False, f"杂毛, 板块地位={board.position_score:.1f}", 0.0

        # Step 2: 炸板分类
        break_result = self.classify_break(ctx)
        if not break_result.can_wait:
            return False, f"诱多型炸板, 不参与", 0.0

        # Step 3: 回封确认
        reseal = self.evaluate_reseal(ctx)
        if not reseal.can_enter:
            return False, f"回封质量不足={reseal.total_score:.1f}", 0.0

        # 综合置信度
        confidence = (
            board.position_score * 0.30 +
            (break_result.score / 5) * 0.20 +
            reseal.total_score * 0.50
        )

        position_pct = 0.15 if board.is_main_theme else 0.08

        return True, f"回封确认, 仓位={position_pct:.0%}", confidence
