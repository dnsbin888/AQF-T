# AQF-T Order Planner Design

Version: V1.0.0
Status: ARCHITECT REVIEW PASSED — Pending Execution Intelligence Freeze
Phase: V3.0 Implementation Era — Phase 0 Foundation
Module: 04_Execution_Intelligence / 05_Order
Created: 2026-07-28

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Order_Planner_Design_V1.0.md |
| Module | Execution Intelligence — Order Planner |
| System | AQF-T Autonomous Quant Intelligence Framework |
| Version | V1.0.0 |
| Parent | AQFT_Execution_Intelligence_Architecture_V1.0 |
| Upstream | Position Engine V1.0 + Portfolio Manager V1.0 + Risk Runtime |
| Downstream | QMT Adapter → xttrader |
| Constitutions | C-001~C-006, C-007(candidate) |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |

---

## 1. Purpose & Position

### 1.1 What Order Planner Does

Order Planner 是 V3.0 的 **订单执行规划器（Order Execution Planner）**。

它回答：**"安全且高效地将已批准的仓位决策转换为实际订单。"**

| Position Engine | Order Planner |
|----------------|--------------|
| HOW is the position? | HOW to send the order? |
| Proposes position action | Generates execution plan |
| Health monitoring | Execution optimization |

### 1.2 Architecture Position

```
Position Engine → ORDER PLANNER → QMT Adapter → xttrader
   (WHAT to trade)    (HOW to send)   (translate)   (execute)
```

### 1.3 Core Definition

```
Order Planner = Order Execution Intelligence
Order Planner ≠ Trading Decision Maker
Order Planner ≠ Signal Generator
Order Planner ≠ Risk Assessor
```

---

## 2. Order Authority Boundary (C-007 Candidate)

```
C-007: Order Execution Boundary

Order Planner MAY:
  ✅ Generate ExecutionPlan
  ✅ Split orders into slices
  ✅ Optimize execution timing
  ✅ Manage order lifecycle
  ✅ Handle partial fills

Order Planner SHALL NOT:
  ❌ Create trading intent
  ❌ Change capital allocation
  ❌ Override Risk decision
  ❌ Modify strategy
  ❌ Bypass QMT Adapter
  ❌ Generate market direction
```

**[NEEDS ARCHITECT REVIEW]** — C-007 promotion to formal Constitution.

---

## 3. Five Core Objects

### 3.1 OrderIntent (Input)

```json
{
  "order_intent_id": "OI_20260728_100000",
  "source": "Position Engine",
  "position_id": "POS_SH603xxx_20260728",
  "symbol": "SH.603xxx",
  "side": "BUY",
  "target_quantity": 10000,
  "reason": "AddCandidate approved. Delta +5%.",
  "priority": "P1",
  "risk_approved": true,
  "risk_approval_id": "RISK_20260728_100000",
  "version": "V1.0"
}
```

### 3.2 ExecutionPlan (Core Output)

```json
{
  "plan_id": "EP_20260728_100000",
  "order_intent_id": "OI_20260728_100000",
  "symbol": "SH.603xxx",
  "side": "BUY",
  "total_quantity": 10000,
  "execution_style": "staged",
  "time_window_seconds": 1800,
  "price_constraint": {
    "max_price": 26.50,
    "max_slippage_pct": 1.0
  },
  "slices": [
    {
      "slice_id": 1,
      "quantity": 3000,
      "order_type": "LIMIT",
      "price_offset_pct": -0.5,
      "timeout_seconds": 300
    },
    {
      "slice_id": 2,
      "quantity": 3000,
      "order_type": "LIMIT",
      "trigger": "slice_1_filled",
      "timeout_seconds": 300
    },
    {
      "slice_id": 3,
      "quantity": 4000,
      "order_type": "MARKET",
      "trigger": "slice_2_filled",
      "timeout_seconds": 300
    }
  ],
  "risk_constraint": {
    "pause_if_risk_spike": true,
    "cancel_if_risk_extreme": true
  },
  "version": "V1.0"
}
```

### 3.3 OrderSlice

| Field | Description |
|-------|-------------|
| slice_id | Sequence number |
| quantity | Shares in this slice |
| order_type | LIMIT / MARKET |
| price_offset_pct | For LIMIT orders |
| trigger | Immediate / after_previous_fill / on_condition |
| timeout_seconds | Auto-cancel if unfilled |

### 3.4 OrderRequest (To QMT Adapter)

```json
{
  "order_id": "ORD_20260728_100000_S1",
  "plan_id": "EP_20260728_100000",
  "symbol": "SH.603xxx",
  "side": "BUY",
  "quantity": 3000,
  "price": 26.07,
  "order_type": "LIMIT",
  "timestamp": "2026-07-28T10:00:00",
  "version": "V1.0"
}
```

### 3.5 ExecutionReport (From QMT)

```json
{
  "order_id": "ORD_20260728_100000_S1",
  "status": "FILLED",
  "filled_quantity": 3000,
  "average_price": 26.05,
  "slippage_bps": -1.5,
  "latency_ms": 12,
  "timestamp": "2026-07-28T10:00:03",
  "version": "V1.0"
}
```

---

## 4. Four Execution Modes

### 4.1 Market Entry

```
PositionAction: Enter/Add
  → Single order, immediate
  → Order type: MARKET or LIMIT (near bid)
  → Slicing: none
  → Use: Routine entry, small quantity
```

### 4.2 Staged Entry

```
PositionAction: Enter/Add (large size)
  → Multiple slices
  → Slice 1: confirmation (30%)
  → Slice 2: momentum (30%)
  → Slice 3: completion (40%)
  → Use: Leader position building
  → Conditions: each slice triggers next on fill
```

### 4.3 Limit-Up Queue

```
A-Share Special: 涨停买入

  → Price = limit_up_price (hardcoded by exchange)
  → Order type: LIMIT at limit-up price
  → Queue behavior: submit, wait in queue
  → Monitor: 封单强度 changes
  → IF 封单骤降 > 50%: Cancel pending, re-evaluate
  → IF 炸板: Cancel all, alert Position Engine
  → Do NOT blindly chase limit-up
```

### 4.4 Emergency Exit

```
Risk State: Extreme
  → Priority: P0 (highest)
  → Order type: MARKET (speed > price)
  → Slicing: none (exit fully)
  → Cancel all other pending orders for this symbol
  → Execute immediately
```

---

## 5. Order Lifecycle

```
Created → Submitted → Acknowledged → Partial_Fill → Filled
                │              │
                ▼              ▼
            Rejected       Cancelled
                │              │
                └──────┬───────┘
                       ▼
                   Terminated
```

| State | Description |
|-------|-------------|
| Created | OrderRequest generated, not yet sent |
| Submitted | Sent to QMT, awaiting ack |
| Acknowledged | QMT confirmed receipt |
| Partial_Fill | Partially executed |
| Filled | Fully executed |
| Rejected | QMT rejected (price/quantity/rule) |
| Cancelled | Cancelled by AQF-T or QMT |
| Terminated | Final state |

---

## 6. Failure Safety

### F1: QMT Unavailable

```
IF QMT connection lost:
  → Status: ExecutionPaused
  → Pending orders: Hold (do not cancel blindly)
  → New orders: Queue locally (max 60s)
  → After 60s: Alert + escalate to human
```

### F2: Partial Fill

```
IF filled < requested after timeout:
  → Status: PartialFill
  → Action: Cancel remainder. Report to Position Engine.
  → Remaining delta: recalculated in next cycle.
```

### F3: Price Drift

```
IF market price drifts > max_slippage_pct from limit:
  → Do NOT chase price
  → Cancel pending LIMIT orders
  → Report PriceDrift to Position Engine
```

### F4: Risk Spike During Execution

```
IF Risk score crosses Extreme during active execution:
  → Cancel ALL pending slices immediately
  → Do NOT submit new orders
  → Report RiskInterrupt to Position Engine
  → Priority: Risk Veto > Execution Request (C-001)
```

---

## 7. Risk Runtime Boundary

```
Order Planner DOES:
  ✅ Receive Risk approval before planning
  ✅ Monitor Risk state during execution
  ✅ Cancel orders on Risk Extreme signal

Order Planner DOES NOT:
  ❌ Assess risk independently
  ❌ Override Risk veto
  ❌ Continue execution after Risk blocks
```

---

## 8. QMT Adapter Interface

```python
class OrderPlanner_to_QMT:
    """Order Planner → QMT Adapter contract."""

    def submit_order(order: OrderRequest) -> OrderAck: ...
    def cancel_order(order_id: str) -> bool: ...
    def query_order_status(order_id: str) -> OrderStatus: ...
    def on_fill(callback: Callable[[ExecutionReport], None]): ...
```

**Order Planner outputs OrderRequest. QMT Adapter translates to xttrader calls.**

---

## 9. Performance Budget

| Constraint | Value |
|------------|-------|
| Plan generation latency | < 50ms |
| Order submission latency | < 10ms (to QMT Adapter) |
| Max concurrent plans | 10 |
| Max slices per plan | 10 |
| CPU | < 5% |
| Memory | < 300MB |
| Schedule Level | P0 (orders) / P1 (plan generation) |

---

## 10. Constitution Compliance

| Constitution | Status | Evidence |
|-------------|:------:|----------|
| C-001: Intelligence Ownership | ✅ | Generates orders, not trading direction |
| C-002: Immutable Core | ✅ | Reads context, never writes core state |
| C-003: QMT Boundary | ✅ | Outputs to QMT Adapter, never xttrader directly |
| C-004: Strategy Boundary | ✅ | Consumes approved position actions |
| C-005: Portfolio Boundary | ✅ | Respects capital allocation limits |
| C-006: Position Boundary | ✅ | Acts on PositionAction, not independently |
| C-007 (candidate) | ✅ | All MAY/SHALL NOT embedded in §2 |

---

## 11. Testing Requirement

- Full fill → ExecutionReport status=FILLED → Position Engine updated
- Partial fill → Cancel remainder → Position Engine recalculates delta
- Risk Extreme mid-execution → All pending slices cancelled
- QMT unavailable → Queue locally, alert after 60s
- Limit-up queue → Monitor 封单, cancel on 炸板

---

## 12. Freeze Criteria

1. 4 execution modes defined (Market/Staged/LimitUp/Emergency)
2. 5 core objects with lifecycle
3. 4 failure scenarios handled
4. Risk boundary: cancel on Extreme, never override
5. C-001~C-007 verified
6. QMT Adapter interface clean (OrderRequest in, ExecutionReport out)
7. Performance budget within V3.0 constraints

---

## Source References

| Section | Source |
|---------|--------|
| 1-2 | Architect P0-006 Specification |
| 3-4 | Execution Intelligence Architecture V1.0 §6 |
| 5-6 | Position Engine V1.0 + Risk Runtime V2.8.6 |
| 7-8 | QMT Integration Principle V1.0 (C-003) |
| 9 | VERIFY-007 Performance Budget |
| 10-12 | C-001~C-006 + V3.0 Requirements |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | C-007 promotion to formal Constitution — approve? | §2 |
| 2 | Staged entry: 3-slice split (30/30/40) — configurable? | §4 |
| 3 | QMT unavailable: 60s local queue → alert — appropriate timeout? | §6 |
| 4 | Limit-up queue: auto-cancel on 封单骤降 > 50% — threshold correct? | §4 |

---

*AQF-T Order Planner Design V1.0 — ENGINEERING DRAFT*  
*V3.0 Phase 0. Order Execution Intelligence. Optimizes execution, not trading.*  
*No original design. All content from Architect specifications.*
