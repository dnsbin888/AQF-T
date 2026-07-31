"""
Strategy Exit Adapter — E3 (DEC-028-REFINED Frozen)
=====================================================
将已有策略信号转换为统一 ExitOrder。不改 Dragon / Pattern / Risk。

E3 接入:
  1. BREAK_EXIT      — 炸板退出 (Dragon: 炸板>10分钟)
  2. LEADER_END      — 龙头结束 (LeaderLifeCycle→INVALID)
  3. PATTERN_INVALID — 持仓依据失效 (任何核心Pattern失效)

不出:
  ATR/MA/Alpha SELL/TimeStop → V2
"""
from typing import Optional
from exit.exit_order import ExitOrder
from exit.exit_reason import ExitReason


class StrategyExitAdapter:
    """
    策略退出适配器 — 只转换, 不判断

    输入: Dragon信号 / Pattern状态 / 持仓上下文
    输出: ExitOrder 列表 (统一格式, priority=50)
    """

    def evaluate(self,
                 positions: dict,
                 pattern_state: dict = None,
                 ctx: dict = None) -> list[ExitOrder]:
        """
        评估所有持仓的策略退出条件

        Args:
            positions: {symbol: {shares, avg_cost, current_price, sector, ...}}
            pattern_state: {symbol: {pattern_name: status, ...}}
            ctx: 市场上下文 (炸板/龙头等Dragon信号字段)
        Returns:
            ExitOrder 列表
        """
        orders = []
        if not positions:
            return orders

        ctx = ctx or {}
        pattern_state = pattern_state or {}

        for symbol, pos in positions.items():
            pstate = pattern_state.get(symbol, {})

            # 1. BREAK_EXIT — 炸板退出 (游资核心)
            break_order = self._check_break_exit(symbol, pos, ctx)
            if break_order:
                orders.append(break_order)

            # 2. LEADER_END — 龙头生命周期结束
            leader_order = self._check_leader_end(symbol, pos, pstate)
            if leader_order:
                orders.append(leader_order)

            # 3. PATTERN_INVALID — 持仓依据失效
            invalid_order = self._check_pattern_invalid(symbol, pos, pstate)
            if invalid_order:
                orders.append(invalid_order)

        return orders

    # ── 1. BREAK_EXIT ──

    def _check_break_exit(self, symbol: str, pos: dict,
                          ctx: dict) -> Optional[ExitOrder]:
        """
        炸板退出 — Dragon exit_signal 等价逻辑 (不修改Dragon)

        条件: 炸板_minutes > 10 (游资共识: 炸板卖一半, 尾盘不板卖全部)
        E3 当前: 炸板>10分钟触发全卖
        """
        break_minutes = ctx.get("炸板_minutes", 0)

        if break_minutes > 10:
            return ExitOrder(
                symbol=symbol,
                trigger_type="strategy_exit",
                trigger_rule=ExitReason.BREAK_EXIT.value,
                priority=50,
                quantity=pos.get("shares", 0),
                quantity_pct=1.0,
                reason=f"炸板>{break_minutes}分钟",
                evidence={
                    "trigger_source": "strategy",
                    "pattern": "PositionAnchor",
                    "炸板_minutes": break_minutes,
                    "board_status": ctx.get("board_status", ""),
                },
            )
        return None

    # ── 2. LEADER_END ──

    def _check_leader_end(self, symbol: str, pos: dict,
                          pstate: dict) -> Optional[ExitOrder]:
        """
        龙头生命周期结束 — AQF-T独有闭环

        条件: LeaderLifeCycle 从 VALIDATED/ACTIVE → INVALID/END

        这是 AQF-T 比固定止损高级的地方:
          龙头识别 → 持仓 → 龙头确认消失 → 退出
        """
        leader_status = pstate.get("LeaderLifeCycle", "")

        if leader_status in ("END", "INVALID", "DEPRECATED"):
            return ExitOrder(
                symbol=symbol,
                trigger_type="strategy_exit",
                trigger_rule=ExitReason.LEADER_END.value,
                priority=50,
                quantity=pos.get("shares", 0),
                quantity_pct=1.0,
                reason=f"龙头生命周期结束: {leader_status}",
                evidence={
                    "trigger_source": "strategy",
                    "pattern": "LeaderLifeCycle",
                    "previous_state": "VALIDATED",
                    "current_state": leader_status,
                },
            )
        return None

    # ── 3. PATTERN_INVALID ──

    def _check_pattern_invalid(self, symbol: str, pos: dict,
                               pstate: dict) -> Optional[ExitOrder]:
        """
        持仓依据失效 — 任何核心 Pattern 不再满足

        条件: 买入时依赖的 Pattern 状态变为 INVALID/DEPRECATED

        核心 Pattern 列表 (DEC-027):
          PositionAnchor / LadderScore / LeaderLifeCycle / EmotionCycle
          SectorFlow / RelativeStrength
        """
        core_patterns = [
            "PositionAnchor", "LadderScore", "LeaderLifeCycle",
            "EmotionCycle", "SectorFlow", "RelativeStrength",
        ]

        for pattern_name in core_patterns:
            status = pstate.get(pattern_name, "")
            if status in ("INVALID", "DEPRECATED"):
                return ExitOrder(
                    symbol=symbol,
                    trigger_type="strategy_exit",
                    trigger_rule=ExitReason.PATTERN_INVALID.value,
                    priority=50,
                    quantity=pos.get("shares", 0),
                    quantity_pct=1.0,
                    reason=f"Pattern失效: {pattern_name}={status}",
                    evidence={
                        "trigger_source": "strategy",
                        "invalid_pattern": pattern_name,
                        "current_state": status,
                        "all_patterns": {
                            k: v for k, v in pstate.items()
                            if k in core_patterns
                        },
                    },
                )
        return None

    # ── 单票风险检测 (辅助, 不改E2) ──

    def position_context(self, symbol: str, pos: dict,
                         pstate: dict) -> dict:
        """
        获取持仓上下文 — 供 Risk Exit 使用

        Returns:
            {"is_leader": bool, "is_break_board": bool, "patterns": {...}}
        """
        is_leader = pstate.get("LeaderLifeCycle", "") in ("VALIDATED", "ACTIVE")
        return {
            "symbol": symbol,
            "is_leader": is_leader,
            "hard_stop_pct": -0.10 if is_leader else -0.08,
            "patterns": {
                k: v for k, v in pstate.items()
                if k in ("PositionAnchor", "LadderScore", "LeaderLifeCycle",
                         "EmotionCycle", "SectorFlow", "RelativeStrength")
            },
        }
