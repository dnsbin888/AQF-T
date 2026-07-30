"""
RelativeStrength — 相对强度 (P1 Pattern)
==========================================
全部规则, 零AI. 回答: "个股vs大盘/板块/龙头, 谁更强?"

公式:
  RS_market  = 个股5日涨幅 / 大盘5日涨幅
  RS_sector  = 个股5日涨幅 / 板块5日涨幅
  RS_leader  = 个股5日涨幅 / 龙头5日涨幅
  综合: RS_score = (RS_market + RS_sector + RS_leader) / 3

输入: akshare数据 或 模拟ctx
输出: Candidate evidence字段 + rs_score (0-1)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RelativeStrengthSignal:
    symbol: str
    rs_score: float            # 0-1 综合相对强度
    rs_market: float           # vs大盘
    rs_sector: float           # vs板块
    rs_leader: float           # vs龙头
    stock_5d_return: float     # 个股5日涨幅
    market_5d_return: float    # 大盘5日涨幅
    sector_5d_return: float    # 板块5日涨幅
    leader_5d_return: float    # 龙头5日涨幅
    outperforms_market: bool   # 跑赢大盘?
    outperforms_sector: bool   # 跑赢板块?
    evidence: dict = None


class RelativeStrength:
    """
    相对强度 — 纯规则评分

    使用方法:
      rs = RelativeStrength()
      signal = rs.evaluate(ctx)
      # signal.rs_score → 0-1, 接入Pipeline候选排序加权
    """

    def evaluate(self, ctx: dict) -> RelativeStrengthSignal:
        """
        ctx字段:
          symbol: str
          stock_5d_return: float     个股5日涨幅 (小数, 0.05=5%)
          market_5d_return: float    大盘(上证)5日涨幅
          sector_5d_return: float    所属板块5日涨幅
          leader_5d_return: float    板块龙头5日涨幅
        """
        symbol = ctx.get("symbol", "")
        stock_5d = ctx.get("stock_5d_return", 0)
        market_5d = ctx.get("market_5d_return", 0.001)
        sector_5d = ctx.get("sector_5d_return", 0.001)
        leader_5d = ctx.get("leader_5d_return", 0.001)

        # 相对强度 (分母避免除零)
        rs_market = stock_5d / max(abs(market_5d), 0.001)
        rs_sector = stock_5d / max(abs(sector_5d), 0.001)
        rs_leader = stock_5d / max(abs(leader_5d), 0.001)

        # 归一化到0-1: tanh(x/2)*0.5+0.5, 中心0.5=持平
        rs_market_norm = self._norm(rs_market)
        rs_sector_norm = self._norm(rs_sector)
        rs_leader_norm = self._norm(rs_leader)

        # 综合: 均值
        rs_score = (rs_market_norm + rs_sector_norm + rs_leader_norm) / 3

        return RelativeStrengthSignal(
            symbol=symbol,
            rs_score=round(rs_score, 3),
            rs_market=round(rs_market_norm, 3),
            rs_sector=round(rs_sector_norm, 3),
            rs_leader=round(rs_leader_norm, 3),
            stock_5d_return=round(stock_5d, 4),
            market_5d_return=round(market_5d, 4),
            sector_5d_return=round(sector_5d, 4),
            leader_5d_return=round(leader_5d, 4),
            outperforms_market=rs_market > 1.0,
            outperforms_sector=rs_sector > 1.0,
            evidence={
                "rs_market": round(rs_market_norm, 3),
                "rs_sector": round(rs_sector_norm, 3),
                "rs_leader": round(rs_leader_norm, 3),
                "stock_5d": round(stock_5d, 4),
                "outperforms_market": rs_market > 1.0,
                "outperforms_sector": rs_sector > 1.0,
            }
        )

    @staticmethod
    def _norm(x: float) -> float:
        """tanh归一化: 中心0=0.5, 正→>0.5, 负→<0.5"""
        import math
        return math.tanh(x / 2.0) * 0.5 + 0.5
