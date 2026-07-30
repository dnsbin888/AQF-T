"""
SectorFlow — 板块资金流向 (P1 Pattern)
========================================
全部规则, 零AI. 回答: "今天哪个板块最强? 资金是否开始切换?"

公式:
  sector_flow_score = 涨停家数变化*0.30 + 资金净流入强度*0.30 + 涨跌幅*0.20 + 成交量变化*0.20

输入: akshare板块数据 或 模拟ctx
输出: Candidate evidence字段 + sector_flow_score (0-1)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SectorFlowSignal:
    symbol: str
    sector: str
    sector_flow_score: float       # 0-1 板块强度
    limit_up_change: float         # 涨停家数变化率
    fund_flow_intensity: float     # 资金净流入强度
    sector_pct_change: float       # 板块涨跌幅
    volume_change: float           # 成交量变化率
    is_sector_leader: bool         # 是否板块龙头
    evidence: dict = None


class SectorFlow:
    """
    板块资金流向 — 纯规则评分

    使用方法:
      sf = SectorFlow()
      signal = sf.evaluate(ctx)
      # signal.sector_flow_score → 0-1, 接入Pipeline候选评分
    """

    def evaluate(self, ctx: dict) -> SectorFlowSignal:
        """
        ctx字段:
          sector: str                  板块名称
          sector_limit_up_change: float  涨停家数变化率 (今日/5日均值 - 1)
          sector_fund_flow: float        资金净流入(亿)
          sector_fund_flow_avg: float    5日平均资金净流入
          sector_pct: float              板块涨跌幅%
          sector_volume_change: float    成交量变化率
          symbol: str
          is_leader: bool                是否板块龙头
        """
        symbol = ctx.get("symbol", "")
        sector = ctx.get("sector", "未知")

        # 涨停家数变化率 (0-1, 变化越大越好)
        limit_up_change = ctx.get("sector_limit_up_change", 0)
        limit_up_score = self._normalize_change(limit_up_change)

        # 资金净流入强度 = 今日净流入 / max(5日均值, 1)
        fund_flow = ctx.get("sector_fund_flow", 0)
        fund_avg = max(abs(ctx.get("sector_fund_flow_avg", 1)), 1)
        fund_intensity = fund_flow / fund_avg
        fund_score = self._clamp(fund_intensity, -2, 3) / 3  # normalize to 0-1 range

        # 板块涨跌幅 (0-1)
        sector_pct = ctx.get("sector_pct", 0)
        pct_score = self._clamp(sector_pct / 5.0, -2, 2) / 2 + 0.5

        # 成交量变化率 (0-1)
        volume_change = ctx.get("sector_volume_change", 0)
        volume_score = self._normalize_change(volume_change)

        # 综合: 权重按spec
        score = (
            limit_up_score * 0.30 +
            fund_score * 0.30 +
            pct_score * 0.20 +
            volume_score * 0.20
        )

        is_leader = ctx.get("is_leader", False)

        return SectorFlowSignal(
            symbol=symbol,
            sector=sector,
            sector_flow_score=round(min(max(score, 0), 1), 3),
            limit_up_change=round(limit_up_change, 3),
            fund_flow_intensity=round(fund_intensity, 3),
            sector_pct_change=round(sector_pct, 3),
            volume_change=round(volume_change, 3),
            is_sector_leader=is_leader,
            evidence={
                "sector": sector,
                "limit_up_change": round(limit_up_change, 3),
                "fund_intensity": round(fund_intensity, 3),
                "sector_pct": round(sector_pct, 2),
                "volume_change": round(volume_change, 3),
            }
        )

    @staticmethod
    def _normalize_change(change: float) -> float:
        """变化率归一化: 0→0.5, 正→>0.5, 负→<0.5"""
        return SectorFlow._clamp(change / 2.0 + 0.5, 0, 1)

    @staticmethod
    def _clamp(val: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, val))
