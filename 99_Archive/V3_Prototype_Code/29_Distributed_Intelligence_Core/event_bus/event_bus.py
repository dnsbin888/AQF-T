"""
AQF-T Event Bus — 分布式智能系统的神经系统
基于内存 Pub/Sub（生产环境替换为 Redis/NATS）
"""
import threading
import time
from datetime import datetime
from collections import defaultdict
from typing import Callable, Any

EventCallback = Callable[[dict], None]


class EventBus:
    """AQF-T 事件总线 — 所有服务通过此总线异步通信"""

    def __init__(self):
        self._subscribers: dict[str, list[EventCallback]] = defaultdict(list)
        self._event_log: list[dict] = []
        self._lock = threading.Lock()

    def publish(self, event_type: str, data: Any, source: str = "") -> dict:
        """发布事件到总线"""
        event = {
            "type": event_type,
            "data": data,
            "source": source,
            "timestamp": datetime.now().isoformat(),
        }
        with self._lock:
            self._event_log.append(event)
            if len(self._event_log) > 10000:
                self._event_log = self._event_log[-5000:]

        # 异步通知所有订阅者
        for callback in self._subscribers.get(event_type, []):
            try:
                threading.Thread(target=callback, args=(event,), daemon=True).start()
            except Exception as e:
                print(f"[EventBus] callback error for {event_type}: {e}")

        return event

    def subscribe(self, event_type: str, callback: EventCallback):
        """订阅事件类型"""
        self._subscribers[event_type].append(callback)
        print(f"[EventBus] subscribed: {event_type}")

    def get_history(self, event_type: str = "", limit: int = 50) -> list[dict]:
        """获取事件历史"""
        events = self._event_log
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return events[-limit:]

    def get_stats(self) -> dict:
        """总线统计"""
        return {
            "total_events": len(self._event_log),
            "event_types": list(self._subscribers.keys()),
            "subscriber_count": sum(len(v) for v in self._subscribers.values()),
        }


# 全局事件总线实例
bus = EventBus()


# ── 预定义事件类型 ──
class EventType:
    MARKET_DATA = "MarketEvent"
    WORLD_STATE = "WorldStateEvent"
    AGENT_CONSENSUS = "AgentConsensusEvent"
    DECISION = "DecisionEvent"
    RISK_DECISION = "RiskDecisionEvent"
    EXECUTION = "ExecutionEvent"
    MEMORY = "MemoryEvent"
    LEARNING = "LearningEvent"
    ALERT = "AlertEvent"
