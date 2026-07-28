"""
Dragon Strategy — 龙头战法
引用: V2.8.6 04_Strategy/AQFT_Strategy_Design_V2.8.6.md (Dragon章节)
      6项龙头判定 + 3种买入模式 + 5种卖出条件
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DragonSignal:
    symbol: str
    is_dragon: bool
    board_count: int
    sector_limit_up_count: int
    seal_ratio: float
    longhu_seats: int
    auction_amount: float
    float_market_cap: float
    action: str = "HOLD"
    reason: str = ""


class DragonStrategy:
    """
    龙头战法 — 直接实现 V2.8.6 04_Strategy 的设计

    引用自 V2.8.6 04_Strategy:
      - 龙头判定6条件 (第3.2节)
      - 三买入模式: 首板打板/二板接力/弱转强 (第3.2节)
      - 五卖出条件: 炸板/竞价转弱/题材退潮/连板中断/异动 (第3.2节)
      - 参数默认值 (第8章参数表)
    """

    # 参数全部来自 V2.8.6 04_Strategy 第8章参数表
    def __init__(self,
                 min_board: int = 3,           # 默认3, 范围2-5
                 min_sector_up: int = 5,
                 seal_threshold: float = 0.05,  # 默认5%, 范围3-10%
                 min_longhu_seats: int = 2,
                 min_auction: float = 5000,    # 万元
                 max_float_cap: float = 50):    # 亿元
        self.min_board = min_board
        self.min_sector_up = min_sector_up
        self.seal_threshold = seal_threshold
        self.min_longhu_seats = min_longhu_seats
        self.min_auction = min_auction
        self.max_float_cap = max_float_cap

    def is_dragon(self, ctx: dict) -> DragonSignal:
        """
        6项龙头判定条件 — V2.8.6 04_Strategy §3.2
        满足≥3项即为龙头
        """
        conditions = [
            ctx.get("board_count", 0) >= self.min_board,
            ctx.get("sector_limit_up_count", 0) >= self.min_sector_up,
            ctx.get("seal_ratio", 0) >= self.seal_threshold,
            ctx.get("longhu_seats", 0) >= self.min_longhu_seats,
            ctx.get("auction_amount", 0) >= self.min_auction and ctx.get("float_market_cap", 999) <= self.max_float_cap,
            ctx.get("gap_up_pct", 0) >= 0.05 and ctx.get("volume_ratio", 0) > 1.5,
        ]
        met = sum(conditions)

        return DragonSignal(
            symbol=ctx.get("symbol", ""),
            is_dragon=(met >= 3),
            board_count=ctx.get("board_count", 0),
            sector_limit_up_count=ctx.get("sector_limit_up_count", 0),
            seal_ratio=ctx.get("seal_ratio", 0),
            longhu_seats=ctx.get("longhu_seats", 0),
            auction_amount=ctx.get("auction_amount", 0),
            float_market_cap=ctx.get("float_market_cap", 999),
            reason=f"{met}/6 条件满足" if met >= 3 else f"仅{met}/6, 不够",
        )

    def entry_signal(self, ctx: dict, sentiment_phase: str) -> Optional[DragonSignal]:
        """
        三买入模式 — V2.8.6 04_Strategy §3.2
        情绪周期过滤: 退潮/冰点不参与 — V2.8.6 04_Strategy §4 适配矩阵
        """
        dragon = self.is_dragon(ctx)
        if not dragon.is_dragon:
            return None
        if sentiment_phase in ("退潮期", "冰点期"):
            return None

        # 模式1: 首板打板
        if ctx.get("board_count", 0) == 1 and ctx.get("is_early_session", False) and ctx.get("theme_heat", 0) > 0.7:
            dragon.action = "BUY"
            dragon.reason = "首板打板"

        # 模式2: 二板接力 (竞价高开3-7%)
        elif ctx.get("board_count", 0) == 1 and 0.03 <= ctx.get("gap_up_pct", 0) <= 0.07 and not ctx.get("炸板", False):
            dragon.action = "BUY"
            dragon.reason = "二板接力"

        # 模式3: 弱转强 (前日炸板 + 竞价翻红 + 量比>3)
        elif ctx.get("prev_炸板", False) and ctx.get("gap_up_pct", 0) > 0 and ctx.get("intraday_turn_red", False) and ctx.get("volume_ratio", 0) > 3:
            dragon.action = "BUY"
            dragon.reason = "弱转强"

        return dragon

    def exit_signal(self, ctx: dict) -> Optional[str]:
        """五卖出条件 — V2.8.6 04_Strategy §3.2"""
        if ctx.get("炸板_minutes", 0) > 10:
            return "炸板>10分钟"
        if ctx.get("gap_down_pct", 0) > 0.03:
            return "竞价低开>3%"
        if ctx.get("sector_limit_up_count", 99) < 3:
            return "题材涨停<3家"
        if not ctx.get("is_limit_up", False) and ctx.get("board_count", 0) >= 2:
            return "连板中断"
        if ctx.get("pct_10d", 0) > 0.80:
            return "10日涨幅>80%异动"
        return None
