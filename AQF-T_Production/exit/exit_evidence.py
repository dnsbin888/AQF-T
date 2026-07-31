"""
Exit Evidence Schema — DEC-027 Frozen
======================================
每笔卖出记录完整生命周期: 买前 → 持仓中 → 触发 → 执行 → 买后 → 反事实
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExitEvidence:
    """卖出证据包 — position_before → trigger → decision → execution → position_after"""
    symbol: str
    exit_reason: str            # ExitReason.value

    # 卖出前持仓快照
    position_before: dict = field(default_factory=dict)
    # {"shares": 3000, "avg_cost": 10.0, "market_value": 28500, "pnl_pct": -0.05}

    # 触发条件快照
    trigger: dict = field(default_factory=dict)
    # {"type": "hard_stop", "priority": 80, "loss_pct": -0.082, "trigger_price": 9.20}

    # 决策信息
    decision: dict = field(default_factory=dict)
    # {"action": "SELL", "quantity": 1500, "quantity_pct": 0.5, "batch": 1}

    # 执行结果
    execution: dict = field(default_factory=dict)
    # {"fill_price": 9.18, "slippage_bps": 2.2, "fee": 4.83, "status": "FILLED"}

    # 卖出后持仓
    position_after: dict = field(default_factory=dict)
    # {"shares": 1500, "avg_cost": 10.0, "remaining_pct": 0.5}

    # 反事实 (V2)
    counterfactual: dict = field(default_factory=dict)
    # {"if_held_N_days": -0.12, "if_sold_all": -0.08}

    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "exit_reason": self.exit_reason,
            "position_before": self.position_before,
            "trigger": self.trigger,
            "decision": self.decision,
            "execution": self.execution,
            "position_after": self.position_after,
            "counterfactual": self.counterfactual,
            "timestamp": self.timestamp,
        }
