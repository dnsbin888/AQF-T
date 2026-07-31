"""
ExitOrder — 统一卖出指令 (DEC-027 Frozen)
==========================================
Risk Exit 和 Strategy Exit 统一输出此格式。
Exit Decision 合并后走 Risk → Execution 管道。
"""
from dataclasses import dataclass, field
from datetime import datetime
from exit.exit_reason import ExitReason, ExitPriority


@dataclass
class ExitOrder:
    """统一卖出指令 — Entry Pipeline 的 TradingSignal 对等体"""
    symbol: str
    trigger_type: str           # "risk_stop" | "strategy_exit" | "kill_switch"
    trigger_rule: str           # ExitReason.value — 具体触发规则
    priority: int               # 100=KillSwitch, 80=Risk, 50=Strategy, 30=Manual
    action: str = "SELL"
    quantity: int = 0           # 卖出股数
    quantity_pct: float = 1.0   # 卖出比例 (0-1, 默认全卖)
    reason: str = ""
    evidence: dict = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    @classmethod
    def from_risk(cls, symbol: str, reason: ExitReason, quantity: int,
                  quantity_pct: float = 1.0, evidence: dict = None) -> "ExitOrder":
        """Risk Exit — 优先级80, 不可被策略覆盖"""
        return cls(
            symbol=symbol,
            trigger_type="risk_stop",
            trigger_rule=reason.value,
			priority=ExitPriority.RISK,
            quantity=quantity,
            quantity_pct=quantity_pct,
            reason=f"Risk: {reason.value}",
            evidence=evidence or {"reason": reason.value},
        )

    @classmethod
    def from_strategy(cls, symbol: str, reason: ExitReason, quantity: int,
                      quantity_pct: float = 1.0, evidence: dict = None) -> "ExitOrder":
        """Strategy Exit — 优先级50, 可被Risk覆盖"""
        return cls(
            symbol=symbol,
            trigger_type="strategy_exit",
            trigger_rule=reason.value,
			priority=ExitPriority.STRATEGY,
            quantity=quantity,
            quantity_pct=quantity_pct,
            reason=f"Strategy: {reason.value}",
            evidence=evidence or {"reason": reason.value},
        )

    @classmethod
    def kill_switch(cls, symbol: str, quantity: int, reason: str = "") -> "ExitOrder":
        """KillSwitch — 优先级100, 最高"""
        return cls(
            symbol=symbol,
            trigger_type="kill_switch",
            trigger_rule=ExitReason.KILLSWITCH.value,
			priority=ExitPriority.KILLSWITCH,
            quantity=quantity,
            quantity_pct=1.0,
            reason=f"KillSwitch: {reason}",
            evidence={"reason": reason},
        )
