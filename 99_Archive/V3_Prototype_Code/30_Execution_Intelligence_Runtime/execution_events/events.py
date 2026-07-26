"""
AQF-T Execution Events — 交易事件类型定义
扩展 V3.2.0 Event Bus
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from event_bus.event_bus import EventBus, EventType as BaseEventType

bus = EventBus()


class EventType(BaseEventType):
    """V3.3.0 新增执行层事件"""
    ORDER_CREATED = "OrderCreatedEvent"
    EXECUTION_RESULT = "ExecutionEvent"
    PORTFOLIO_UPDATED = "PortfolioUpdatedEvent"
    POSITION_CHANGED = "PositionChangedEvent"
    PERFORMANCE = "PerformanceEvent"
    FEEDBACK = "FeedbackEvent"
