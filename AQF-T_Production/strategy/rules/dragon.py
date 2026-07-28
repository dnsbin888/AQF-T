"""
Dragon Strategy — 龙头战法
A股游资核心策略
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DragonSignal:
    symbol: str
    is_dragon: bool
    board_count: int                    # 连板数
    sector_limit_up_count: int          # 题材涨停家数
    seal_ratio: float                   # 封单/流通市值
    longhu_seats: int                   # 龙虎榜游资席位
    auction_amount: float               # 竞价封单(万)
    float_market_cap: float             # 流通市值(亿)
    action: str = "HOLD"               # BUY / SELL / HOLD
    reason: str = ""


class DragonStrategy:
    """龙头战法"""

    def __init__(self,
                 min_board: int = 3,
                 min_sector_up: int = 5,
                 seal_threshold: float = 0.05,
                 min_longhu_seats: int = 2,
                 min_auction: float = 5000,
                 max_float_cap: float = 50):
        self.min_board = min_board
        self.min_sector_up = min_sector_up
        self.seal_threshold = seal_threshold
        self.min_longhu_seats = min_longhu_seats
        self.min_auction = min_auction
        self.max_float_cap = max_float_cap

    def is_dragon(self, ctx: dict) -> DragonSignal:
        """
        龙头判定 — 6项条件满足≥3即为龙头
        """
        board_count = ctx.get("board_count", 0)
        sector_up = ctx.get("sector_limit_up_count", 0)
        seal_ratio = ctx.get("seal_ratio", 0)
        longhu_seats = ctx.get("longhu_seats", 0)
        auction_amount = ctx.get("auction_amount", 0)
        float_cap = ctx.get("float_market_cap", 999)

        conditions = [
            board_count >= self.min_board,
            sector_up >= self.min_sector_up,
            seal_ratio >= self.seal_threshold,
            longhu_seats >= self.min_longhu_seats,
            auction_amount >= self.min_auction and float_cap <= self.max_float_cap,
            ctx.get("gap_up_pct", 0) >= 0.05 and ctx.get("volume_ratio", 0) > 1.5,
        ]

        is_dragon = sum(conditions) >= 3

        return DragonSignal(
            symbol=ctx.get("symbol", ""),
            is_dragon=is_dragon,
            board_count=board_count,
            sector_limit_up_count=sector_up,
            seal_ratio=seal_ratio,
            longhu_seats=longhu_seats,
            auction_amount=auction_amount,
            float_market_cap=float_cap,
            reason=f"Conditions met: {sum(conditions)}/6" if is_dragon else "Not enough conditions",
        )

    def entry_signal(self, ctx: dict, sentiment_phase: str) -> Optional[DragonSignal]:
        """买入信号"""
        dragon = self.is_dragon(ctx)
        if not dragon.is_dragon:
            return None

        # 情绪周期过滤
        if sentiment_phase in ("退潮期", "冰点期"):
            return None

        # 首板打板: 早盘快速拉升触板 + 题材热度>0.7
        if (ctx.get("board_count", 0) == 1 and
                ctx.get("is_early_session", False) and
                ctx.get("theme_heat", 0) > 0.7):
            dragon.action = "BUY"
            dragon.reason = "首板打板: 早盘触板+题材热度高"

        # 二板接力: 竞价高开3-7% + 30分钟不炸板
        elif (ctx.get("board_count", 0) == 1 and
                ctx.get("gap_up_pct", 0) >= 0.03 and
                ctx.get("gap_up_pct", 0) <= 0.07 and
                not ctx.get("炸板", False)):
            dragon.action = "BUY"
            dragon.reason = "二板接力: 竞价高开+不炸板"

        # 弱转强: 前日炸板 + 竞价高开+15min翻红+量比>3
        elif (ctx.get("prev_炸板", False) and
                ctx.get("gap_up_pct", 0) > 0 and
                ctx.get("intraday_turn_red", False) and
                ctx.get("volume_ratio", 0) > 3):
            dragon.action = "BUY"
            dragon.reason = "弱转强: 前日炸板+竞价翻红+放量"

        return dragon

    def exit_signal(self, ctx: dict) -> Optional[str]:
        """卖出信号 — 返回原因或None"""
        if ctx.get("炸板_minutes", 0) > 10:
            return "炸板>10分钟"
        if ctx.get("gap_down_pct", 0) > 0.03:
            return "竞价低开>3%"
        if ctx.get("sector_limit_up_count", 99) < 3:
            return "题材涨停<3家"
        if not ctx.get("is_limit_up", False) and ctx.get("board_count", 0) >= 2:
            return "连板中断"
        if ctx.get("pct_10d", 0) > 0.80:
            return "10日涨幅>80%, 异动风险"
        return None
