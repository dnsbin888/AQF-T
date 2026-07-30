"""
Event LLM — 维度4: 事件分析
数据: 公告/新闻/政策/龙虎榜/社交媒体
方法: DeepSeek/Qwen API 解析非结构化文本
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EventSignal:
    has_event: bool
    direction: str        # POSITIVE / NEGATIVE / NEUTRAL
    urgency: str          # HIGH / MEDIUM / LOW
    impact_score: float   # 0-1
    summary: str
    source: str
    timestamp: str


class EventEngine:
    """
    维度4: 事件分析引擎
    使用 LLM API 解析非结构化文本

    输入: 公告/新闻/政策/龙虎榜/社交媒体
    输出: 事件信号 + 影响方向 + 紧急程度
    """

    def __init__(self, use_api: bool = False):
        self.use_api = use_api

    def analyze(self, symbol: str, texts: list[str]) -> EventSignal:
        """
        分析事件文本
        生产环境: 调用 DeepSeek/Qwen API
        开发环境: 规则匹配
        """
        if self.use_api:
            return self._api_analyze(symbol, texts)
        return self._rule_analyze(symbol, texts)

    def _api_analyze(self, symbol: str, texts: list[str]) -> EventSignal:
        """调用 LLM API (DeepSeek/Qwen)"""
        # 伪代码 — 实盘时替换为真实API调用
        # response = deepseek.chat(prompt=f"分析以下新闻对{symbol}的影响: {texts}")
        return EventSignal(
            has_event=bool(texts),
            direction="NEUTRAL",
            urgency="LOW",
            impact_score=0.0,
            summary=f"待API分析: {len(texts)}条信息",
            source="LLM_API",
            timestamp=datetime.now().isoformat(),
        )

    def _rule_analyze(self, symbol: str, texts: list[str]) -> EventSignal:
        """规则匹配 (API不可用时的降级方案)"""
        if not texts:
            return EventSignal(
                has_event=False, direction="NEUTRAL", urgency="LOW",
                impact_score=0.0, summary="无事件", source="rule",
                timestamp=datetime.now().isoformat(),
            )

        combined = " ".join(texts)

        # 关键词匹配
        positive = ["增持", "回购", "业绩预增", "中标", "政策支持", "利好", "涨停"]
        negative = ["减持", "亏损", "退市", "处罚", "调查", "利空", "跌停", "暴雷"]
        urgent = ["停牌", "立案", "暴雷", "退市", "紧急"]

        pos_count = sum(1 for w in positive if w in combined)
        neg_count = sum(1 for w in negative if w in combined)
        urg_count = sum(1 for w in urgent if w in combined)

        if pos_count > neg_count:
            direction = "POSITIVE"
        elif neg_count > pos_count:
            direction = "NEGATIVE"
        else:
            direction = "NEUTRAL"

        urgency = "HIGH" if urg_count > 0 else ("MEDIUM" if neg_count > 2 else "LOW")
        impact = min(1.0, (pos_count + neg_count) * 0.2)

        return EventSignal(
            has_event=True,
            direction=direction,
            urgency=urgency,
            impact_score=impact,
            summary=f"规则匹配: 正面{pos_count} 负面{neg_count} 紧急{urg_count}",
            source="rule",
            timestamp=datetime.now().isoformat(),
        )

    def should_override(self, event: EventSignal) -> Optional[dict]:
        """
        事件是否应该覆盖模型决策 (GPT V1.1: 增加 evidence 字段)

        返回: None(不覆盖) / {"action": "REDUCE", "evidence": ...} /
              {"action": "BLOCK", "evidence": ...}
        """
        if event.urgency == "HIGH" and event.direction == "NEGATIVE":
            return {
                "action": "BLOCK",
                "evidence": {
                    "trigger": "HIGH urgency + NEGATIVE direction",
                    "urgency": event.urgency,
                    "direction": event.direction,
                    "impact_score": event.impact_score,
                    "summary": event.summary,
                    "reason": "historical drawdown correlation — urgent negative events",
                }
            }
        if event.direction == "NEGATIVE" and event.impact_score > 0.5:
            return {
                "action": "REDUCE",
                "evidence": {
                    "trigger": "NEGATIVE + impact>0.5",
                    "direction": event.direction,
                    "impact_score": event.impact_score,
                    "summary": event.summary,
                    "reason": "negative sentiment with significant impact",
                }
            }
        return None
