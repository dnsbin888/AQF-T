"""
ExitPipeline — 持仓生命周期管理 (DEC-027 Frozen, E1 Skeleton)
==============================================================
E1: 骨架 — trigger → validate → priority resolve → ExitOrder
E2: Risk Exit 接入
E3: Strategy Exit 接入
E4: Exit Evidence 验证

与 Entry Pipeline 平级，不互相侵入。
SELL > BUY — 当 Exit 和 Entry 冲突时，Exit 优先。
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from exit.exit_order import ExitOrder
from exit.exit_reason import ExitPriority


@dataclass
class ExitResult:
    """ExitPipeline 运行结果"""
    date: str = ""
    orders: list = field(default_factory=list)    # 最终 ExitOrder 列表
    rejected: list = field(default_factory=list)   # 被否决的 ExitOrder
    merged_count: int = 0                          # 合并数量
    total_triggers: int = 0
    total_orders: int = 0
    errors: list = field(default_factory=list)


class ExitPipeline:
    """
    持仓退出管道 — 和 Entry Pipeline 平级

    E1骨架职责:
      1. 接收 ExitOrder (来自 Risk / Strategy)
      2. 按优先级排序 (KillSwitch > Risk > Strategy)
      3. 同标的高优先级覆盖低优先级
      4. 输出最终 ExitOrder 列表
      5. 发布 POSITION_UPDATED 事件

    E2/E3才接入真实的 Risk/Strategy 触发逻辑。
    """

    def __init__(self):
        self._pending_exits: list[ExitOrder] = []
        self._pending_entries: list = []  # 未成交 Entry Order (用于冲突处理)

    # ── E1: 核心逻辑 ──

    def submit(self, order: ExitOrder):
        """接收 ExitOrder (来自任何触发源)"""
        self._pending_exits.append(order)

    def set_pending_entries(self, entries: list):
        """设置未成交 Entry Order — 用于冲突处理"""
        self._pending_entries = entries

    def resolve(self) -> ExitResult:
        """
        优先级裁决 + 合并

        E1逻辑:
          1. 按 priority 降序排列
          2. 同标的: 高优先级覆盖低优先级
          3. 同优先级: 取 quantity_pct 最大的
          4. 取消冲突的 Entry Order (SELL > BUY)
        """
        result = ExitResult(date=datetime.now().strftime("%Y-%m-%d"))

        if not self._pending_exits:
            return result

        result.total_triggers = len(self._pending_exits)

        # 按优先级降序
        sorted_exits = sorted(self._pending_exits, key=lambda o: -o.priority)

        # 同标的取最高优先级
        seen: dict[str, ExitOrder] = {}
        rejected = []
        for order in sorted_exits:
            if order.symbol not in seen:
                seen[order.symbol] = order
            else:
                existing = seen[order.symbol]
                if order.priority > existing.priority:
                    rejected.append(existing)
                    seen[order.symbol] = order
                elif order.priority == existing.priority:
                    # 同优先级取 quantity_pct 最大的
                    if order.quantity_pct > existing.quantity_pct:
                        rejected.append(existing)
                        seen[order.symbol] = order
                    else:
                        rejected.append(order)
                else:
                    rejected.append(order)

        result.orders = list(seen.values())
        result.rejected = rejected
        result.merged_count = result.total_triggers - len(result.orders)
        result.total_orders = len(result.orders)

        # ── SELL > BUY 冲突处理 ──
        cancelled_entries = []
        exit_symbols = {o.symbol for o in result.orders}
        for entry in self._pending_entries:
            if entry.get("symbol") in exit_symbols and entry.get("status") != "FILLED":
                entry["status"] = "CANCELLED_BY_EXIT"
                entry["cancel_reason"] = "Exit pipeline override"
                cancelled_entries.append(entry)

        # ── 发布事件 ──
        for order in result.orders:
            self._publish_exit(order)

        # ── 清空待处理 ──
        self._pending_exits = []
        self._pending_entries = []

        return result

    # ── Event Bus ──

    def _publish_exit(self, order: ExitOrder):
        """发布 EXIT_TRIGGERED + POSITION_UPDATED 事件"""
        try:
            from core.event_bus import bus, EVENTS
            bus.publish("EXIT_TRIGGERED", {
                "symbol": order.symbol,
                "trigger_type": order.trigger_type,
                "trigger_rule": order.trigger_rule,
                "priority": order.priority,
                "quantity_pct": order.quantity_pct,
                "reason": order.reason,
                "timestamp": order.timestamp,
            }, source="exit_pipeline")
        except ImportError:
            pass

    # ── 状态查询 ──

    def status(self) -> dict:
        return {
            "pending_exits": len(self._pending_exits),
            "pending_entries": len(self._pending_entries),
        }


# ── Event Bus 事件类型注册 ──
# 在主 core/event_bus.py 的 EVENTS dict 中添加:
#   "EXIT_TRIGGERED":    "ExitTriggeredEvent",
#   "POSITION_UPDATED":  "PositionUpdatedEvent",
