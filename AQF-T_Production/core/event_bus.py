"""
Event Bus — 事件总线
所有模块通过事件通信, 解耦
"""
from collections import defaultdict
from datetime import datetime
from typing import Callable, Any
import threading


class Event:
    """统一事件格式"""
    def __init__(self, event_type: str, data: Any, source: str = ""):
        self.type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
        }


class EventBus:
    """AQF-T 事件总线 — 发布/订阅"""

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._history: list[Event] = []
        self._lock = threading.Lock()

    def publish(self, event_type: str, data: Any, source: str = "") -> Event:
        event = Event(event_type, data, source)
        with self._lock:
            self._history.append(event)
            if len(self._history) > 10000:
                self._history = self._history[-5000:]

        for cb in self._subscribers.get(event_type, []):
            try:
                threading.Thread(target=cb, args=(event,), daemon=True).start()
            except Exception as e:
                print(f"[EventBus] {event_type} callback error: {e}")
        return event

    def subscribe(self, event_type: str, callback: Callable):
        self._subscribers[event_type].append(callback)

    def recent(self, event_type: str = "", limit: int = 50) -> list[Event]:
        events = self._history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]


# 全局实例
bus = EventBus()


# 事件类型
EVENTS = {
    "MARKET_REGIME":   "MarketRegimeEvent",    # 市场状态更新
    "SIGNAL_A":        "SignalEvent_PathA",     # 回封板信号
    "SIGNAL_B":        "SignalEvent_PathB",     # 半路/接力信号
    "RISK_DECISION":   "RiskDecisionEvent",     # 风控审批
    "ORDER_CREATED":   "OrderCreatedEvent",     # 订单生成
    "ORDER_FILLED":    "OrderFilledEvent",      # 订单成交
    "ORDER_REJECTED":  "OrderRejectedEvent",    # 订单拒绝
    "DAILY_REPORT":    "DailyReportEvent",      # 日终报告
    "KILL_SWITCH":     "KillSwitchEvent",       # 紧急熔断
}
