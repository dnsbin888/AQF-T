"""
E3 Strategy Exit — 4 acceptance tests (DEC-028-REFINED)
========================================================
Test 1: BREAK_EXIT 炸板退出
Test 2: LEADER_END 龙头结束
Test 3: PATTERN_INVALID 依据失效
Test 4: Risk > Strategy 优先级
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from exit.strategy_exit_adapter import StrategyExitAdapter
from exit.exit_pipeline import ExitPipeline
from exit.exit_order import ExitOrder
from exit.exit_reason import ExitReason


def test_break_exit():
    """Test 1: 炸板>10分钟 → BREAK_EXIT"""
    adapter = StrategyExitAdapter()
    positions = {"000001": {"shares": 3000, "avg_cost": 10.0, "current_price": 9.5}}
    ctx = {"炸板_minutes": 12, "board_status": "炸板"}
    orders = adapter.evaluate(positions, ctx=ctx)
    assert len(orders) == 1, f"Expected 1 order, got {len(orders)}"
    o = orders[0]
    assert o.trigger_rule == ExitReason.BREAK_EXIT.value, f"Expected BREAK_EXIT, got {o.trigger_rule}"
    assert o.priority == 50
    assert o.evidence["炸板_minutes"] == 12
    assert o.quantity_pct == 1.0
    print("  [PASS] Test 1: BREAK_EXIT")


def test_leader_end():
    """Test 2: LeaderLifeCycle INVALID → LEADER_END"""
    adapter = StrategyExitAdapter()
    positions = {"600519": {"shares": 500, "avg_cost": 1850.0, "current_price": 1840.0}}
    pstate = {"600519": {"LeaderLifeCycle": "INVALID"}}
    orders = adapter.evaluate(positions, pattern_state=pstate)
    assert len(orders) >= 1, f"Expected at least 1 order, got {len(orders)}"
    # LEADER_END + PATTERN_INVALID both trigger (LeaderLifeCycle在核心Pattern列表)
    leader = [o for o in orders if o.trigger_rule == ExitReason.LEADER_END.value]
    assert len(leader) >= 1, f"Expected LEADER_END in orders, got {[o.trigger_rule for o in orders]}"
    assert leader[0].evidence["pattern"] == "LeaderLifeCycle"
    assert leader[0].evidence["current_state"] == "INVALID"
    print("  [PASS] Test 2: LEADER_END")


def test_pattern_invalid():
    """Test 3: PositionAnchor INVALID → PATTERN_INVALID"""
    adapter = StrategyExitAdapter()
    positions = {"000002": {"shares": 2000, "avg_cost": 15.0, "current_price": 14.5}}
    pstate = {"000002": {"PositionAnchor": "INVALID", "LeaderLifeCycle": "VALIDATED"}}
    orders = adapter.evaluate(positions, pattern_state=pstate)
    assert len(orders) == 1
    o = orders[0]
    assert o.trigger_rule == ExitReason.PATTERN_INVALID.value
    assert o.evidence["invalid_pattern"] == "PositionAnchor"
    print("  [PASS] Test 3: PATTERN_INVALID")


def test_risk_over_strategy():
    """Test 4: Risk HARD_STOP + Strategy BREAK_EXIT → Risk 覆盖 Strategy"""
    from exit.risk_exit_adapter import RiskExitAdapter

    ep = ExitPipeline()
    risk_adapter = RiskExitAdapter()
    strategy_adapter = StrategyExitAdapter()

    positions = {"000001": {"shares": 3000, "avg_cost": 10.0, "current_price": 9.1,
                            "loss_pct": -0.09}}
    ctx = {"炸板_minutes": 12}
    pstate = {"000001": {"PositionAnchor": "VALIDATED"}}

    # Risk Exit (pri=80)
    risk_orders = risk_adapter.adapt(
        killswitch_active=False,
        positions=positions,
    )
    for o in risk_orders:
        ep.submit(o)

    # Strategy Exit (pri=50)
    strategy_orders = strategy_adapter.evaluate(positions, ctx=ctx, pattern_state=pstate)
    for o in strategy_orders:
        ep.submit(o)

    result = ep.resolve()
    assert result.total_orders == 1, f"Expected 1 winner, got {result.total_orders}"
    winner = result.orders[0]
    assert winner.trigger_type == "risk_stop", f"Risk should win, got {winner.trigger_type}"
    assert winner.trigger_rule == ExitReason.HARD_STOP.value
    print("  [PASS] Test 4: Risk > Strategy")


def test_position_context():
    """Bonus: 龙头票止损10% vs 普通票8%"""
    adapter = StrategyExitAdapter()
    pos = {"shares": 1000, "avg_cost": 10.0, "current_price": 9.5}
    ctx_leader = adapter.position_context("000001", pos, {"LeaderLifeCycle": "VALIDATED"})
    ctx_normal = adapter.position_context("000002", pos, {"PositionAnchor": "VALIDATED"})
    assert ctx_leader["hard_stop_pct"] == -0.10, f"Leader should be 10%, got {ctx_leader['hard_stop_pct']}"
    assert ctx_normal["hard_stop_pct"] == -0.08, f"Normal should be 8%, got {ctx_normal['hard_stop_pct']}"
    print("  [PASS] Bonus: Leader 10% vs Normal 8%")


if __name__ == "__main__":
    print("\n  E3 Strategy Exit — Acceptance Tests\n")
    tests = [
        test_break_exit,
        test_leader_end,
        test_pattern_invalid,
        test_risk_over_strategy,
        test_position_context,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  [FAIL] {t.__name__}: {e}")
    print(f"\n  Results: {passed}/{len(tests)} passed, {failed} failed")
