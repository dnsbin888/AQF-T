"""
Risk Exit Adapter — E2 (DEC-027 Frozen)
========================================
将已有 Risk 判断结果转换为 ExitOrder，不创造新逻辑。

接入范围 (E2 冻结):
  1. KillSwitch Exit — 最高优先级，覆盖所有
  2. Drawdown Limit  — 组合回撤超限
  3. Regime Break    — 情绪周期恶化
  4. Risk Stop       — 持仓亏损超限

不加入 (V2):
  ATR/移动止损/止盈/分仓/AI
"""
from typing import Optional
from exit.exit_order import ExitOrder
from exit.exit_reason import ExitReason


class RiskExitAdapter:
    """
    风险退出适配器 — 只转换, 不判断

    输入: Risk 层已有状态 (KillSwitch / Drawdown / Regime / Position)
    输出: ExitOrder 列表 (统一格式)
    """

    def adapt(self,
              killswitch_active: bool = False,
              killswitch_reason: str = "",
              drawdown_exceeded: bool = False,
              drawdown_pct: float = 0,
              regime_phase: str = "",
              positions: dict = None) -> list[ExitOrder]:
        """
        转换所有风险状态为 ExitOrder

        Args:
            killswitch_active: 熔断是否触发
            killswitch_reason: 熔断原因
            drawdown_exceeded: 组合回撤是否超限
            drawdown_pct: 当前回撤%
            regime_phase: 当前Regime阶段
            positions: {symbol: {shares, avg_cost, current_price, loss_pct}}
        Returns:
            ExitOrder 列表 (可能为空)
        """
        orders = []

        # 1. KillSwitch — 最高优先级, 全部清仓
        if killswitch_active:
            if positions:
                for symbol, pos in positions.items():
                    orders.append(ExitOrder.kill_switch(
                        symbol=symbol,
                        quantity=pos.get("shares", 0),
                        reason=killswitch_reason or "KillSwitch triggered",
                    ))
            return orders  # KillSwitch触发时跳过其他检查，直接返回

        # 2. Drawdown — 组合级, 所有持仓按比例减仓
        if drawdown_exceeded:
            reduce_pct = min(1.0, abs(drawdown_pct) / 0.15)  # 回撤越大卖越多
            if positions:
                for symbol, pos in positions.items():
                    qty = int(pos.get("shares", 0) * reduce_pct / 100) * 100
                    if qty >= 100:
                        orders.append(ExitOrder(
                            symbol=symbol,
                            trigger_type="risk_stop",
                            trigger_rule=ExitReason.DRAWDOWN_LIMIT.value,
                            priority=ExitOrder.from_risk(symbol, ExitReason.DRAWDOWN_LIMIT, qty).priority,
                            quantity=qty,
                            quantity_pct=round(reduce_pct, 2),
                            reason=f"组合回撤{drawdown_pct:.1%}",
                            evidence={"drawdown_pct": drawdown_pct, "reduce_pct": reduce_pct},
                        ))

        # 3. Regime Break — 退潮期强制清仓
        if regime_phase == "退潮期" and positions:
            for symbol, pos in positions.items():
                orders.append(ExitOrder.from_risk(
                    symbol=symbol,
                    reason=ExitReason.REGIME_BREAK,
                    quantity=pos.get("shares", 0),
                    quantity_pct=1.0,
                    evidence={"regime": regime_phase, "action": "full_exit"},
                ))

        # 4. Risk Stop — 持仓级, 硬止损分层 (DEC-028-REFINED)
        if positions:
            for symbol, pos in positions.items():
                loss_pct = pos.get("loss_pct", 0)
                is_leader = pos.get("is_leader", False)
                hard_stop = -0.10 if is_leader else -0.08  # 龙头10%, 普通8%
                if loss_pct < hard_stop:
                    orders.append(ExitOrder.from_risk(
                        symbol=symbol,
                        reason=ExitReason.HARD_STOP,
                        quantity=pos.get("shares", 0),
                        quantity_pct=1.0,
                        evidence={
                            "entry_price": pos.get("avg_cost", 0),
                            "current_price": pos.get("current_price", 0),
                            "loss_pct": round(loss_pct, 3),
                            "limit": hard_stop,
                            "is_leader": is_leader,
                        },
                    ))

        return orders

    def check_position_risk(self, avg_cost: float, current_price: float,
                            max_loss_pct: float = -0.08) -> Optional[dict]:
        """
        单票风险检测 — 给 Position Monitor 调用

        Returns: None (安全) 或 risk_info dict (触发)
        """
        if avg_cost <= 0 or current_price <= 0:
            return None
        loss_pct = (current_price - avg_cost) / avg_cost
        if loss_pct < max_loss_pct:
            return {
                "triggered": True,
                "loss_pct": round(loss_pct, 3),
                "avg_cost": avg_cost,
                "current_price": current_price,
                "max_loss_pct": max_loss_pct,
            }
        return None
