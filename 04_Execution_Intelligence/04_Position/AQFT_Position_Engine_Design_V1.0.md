# AQF-T Position Engine Design

Version: V1.0.0
Status: ARCHITECT REVIEW PASSED — Pending Execution Intelligence Freeze
Phase: V3.0 Implementation Era — Phase 0 Foundation
Module: 04_Execution_Intelligence / 04_Position
Created: 2026-07-28

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Position_Engine_Design_V1.0.md |
| Module | Execution Intelligence — Position Engine |
| System | AQF-T Autonomous Quant Intelligence Framework |
| Version | V1.0.0 |
| Parent | AQFT_Execution_Intelligence_Architecture_V1.0 |
| Upstream | Portfolio Manager V1.0 ✅ + World Model V2.9.0 ✅ |
| Downstream | Order Planner, Risk Runtime |
| Constitutions | C-001, C-002, C-003, C-004, C-005, C-006(candidate) |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |

---

## 1. Purpose & Position

### 1.1 What Position Engine Does

Position Engine 是 V3.0 的 **持仓生命管理智能层（Position Lifecycle Intelligence）**。

它回答：**"当前持有的仓位表现如何？应该维持、加仓、减仓还是退出？"**

| Portfolio Manager | Position Engine |
|-------------------|----------------|
| HOW MUCH capital | HOW is the position behaving |
| Allocate funds | Track and evaluate positions |
| Capital decision | Position health monitoring |

### 1.2 Architecture Position

```
Portfolio Manager → POSITION ENGINE → Order Planner
   (HOW MUCH)         (HOW IS IT)       (GENERATE ORDER)
```

### 1.3 Core Definition

```
Position Engine = Trading Position Lifecycle Intelligence
Position Engine ≠ Decision Maker
Position Engine ≠ Stock Selector
Position Engine ≠ Signal Generator
```

---

## 2. Position Authority Boundary (C-006 Candidate)

```
C-006: Position Authority Boundary

Position Engine MAY:
  ✅ Monitor position state
  ✅ Evaluate position health
  ✅ Propose position actions (Maintain/Add/Reduce/Exit)
  ✅ Track profit/loss evolution

Position Engine SHALL NOT:
  ❌ Create DecisionIntent
  ❌ Override RiskState
  ❌ Directly send orders
  ❌ Modify Immutable Core
  ❌ Generate market direction
  ❌ Independently open new positions
```

**[NEEDS ARCHITECT REVIEW]** — C-006 promotion to formal Constitution.

---

## 3. Relationship with Upstream Modules

### 3.1 From Portfolio Manager

```
CapitalAllocation { target_weight: 0.25, max_weight: 0.30 }
        │
        ▼
Position Engine:
  - Receives target allocation
  - Compares with current position
  - Calculates delta
  - Proposes position action
```

### 3.2 From World Model (Read-Only Context)

| Context | Usage |
|---------|-------|
| RegimeState R(t) | Position health: regime-appropriate? |
| EmotionPhase | Leader position: sentiment support? |
| MarketMicrostructure | Execution timing readiness |

### 3.3 From Execution Reports

```
ExecutionReport → Position Engine:
  - Update current quantity
  - Update average cost
  - Update unrealized PnL
```

---

## 4. Five Core Objects

### 4.1 PositionState

```json
{
  "position_id": "POS_SH603xxx_20260728",
  "symbol": "SH.603xxx",
  "quantity": 10000,
  "avg_cost": 25.50,
  "market_price": 26.20,
  "market_value": 262000,
  "unrealized_pnl_pct": 2.75,
  "holding_days": 5,
  "entry_reason": "Leader confirmed, Expansion regime",
  "entry_decision_id": "DEC_20260723_093000",
  "version": "V1.0"
}
```

### 4.2 PositionContext

```json
{
  "position_id": "POS_SH603xxx_20260728",
  "timestamp": "2026-07-28T10:00:00",
  "market_regime": "Expansion",
  "emotion_cycle": "Warming",
  "theme_strength": 0.76,
  "leader_status": "Hold_7board",
  "risk_level": "Medium",
  "sector_momentum": "Strengthening",
  "source": "World Model + AI Brain"
}
```

### 4.3 PositionHealth

```json
{
  "position_id": "POS_SH603xxx_20260728",
  "health_score": 78,
  "health_level": "Healthy",
  "components": {
    "trend_score": 82,
    "emotion_score": 75,
    "liquidity_score": 80,
    "risk_score": 72
  },
  "warnings": [],
  "version": "V1.0"
}
```

### 4.4 PositionAction (Proposal Only)

```json
{
  "position_id": "POS_SH603xxx_20260728",
  "proposed_action": "Maintain",
  "reason": "Health 78 (Healthy), Regime Expansion, Leader intact",
  "conditions": [
    "If leader breaks → downgrade to ReduceCandidate",
    "If emotion shifts to Recession → ExitCandidate"
  ],
  "requires_risk_approval": false,
  "version": "V1.0"
}
```

### 4.5 PositionRecord (To Memory)

```json
{
  "position_id": "POS_SH603xxx_20260728",
  "lifecycle_events": [
    { "date": "2026-07-23", "event": "ENTRY", "quantity": 3000, "price": 24.80 },
    { "date": "2026-07-25", "event": "ADD", "quantity": 4000, "price": 25.30 },
    { "date": "2026-07-27", "event": "ADD", "quantity": 3000, "price": 25.80 }
  ],
  "status": "ACTIVE",
  "total_pnl_realized": 0,
  "total_pnl_unrealized_pct": 2.75
}
```

---

## 5. Six-State Position Machine

```
                    ENTRY
                      │
                      ▼
                 New Position
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Growing      Stable      Warning
          │           │           │
          ▼           ▼           ▼
      Increase     Maintain     Reduce
          │           │           │
          └───────────┼───────────┘
                      ▼
                   Critical
                      │
                      ▼
                     Exit
```

| State | Condition | Action |
|-------|-----------|--------|
| New | Just entered, < 3 days | Monitor, no action |
| Growing | Health ≥ 80, trend strengthening | Maintain or AddCandidate |
| Stable | Health 60-80, no change signals | Maintain |
| Warning | Health 40-60, early weakness | ReduceCandidate |
| Critical | Health < 40, leader broken, risk spiking | ExitCandidate |
| Exit | Position closed | Record → Memory |

---

## 6. Position Health Scoring

### 6.1 Health Formula

```
Health_Score = 
  Trend_Score     × 0.30 +
  Emotion_Score   × 0.25 +
  Liquidity_Score × 0.20 +
  Risk_Score      × 0.25

Where each sub-score ∈ [0, 100]
```

### 6.2 Health Levels

| Score | Level | Position State | Action Bias |
|:-----:|-------|:-------------:|-------------|
| ≥ 80 | Healthy | Growing / Stable | Maintain or AddCandidate |
| 60-80 | Stable | Stable | Maintain |
| 40-60 | Warning | Warning | ReduceCandidate |
| < 40 | Critical | Critical | ExitCandidate |

---

## 7. A-Share Leader Position Lifecycle

```
启动期 (Launch)
  Health: 65-75
  State: New → Growing
  Action: Trial position, small size
  Condition: Leader 2-board confirmed

确认期 (Confirmation)
  Health: 75-85
  State: Growing → Stable
  Action: Add to confirmation size
  Condition: Sector follows, volume healthy

加速期 (Acceleration)
  Health: 85-95
  State: Growing
  Action: Core position hold
  Condition: Emotion climax, broad participation

高潮期 (Peak)
  Health: 80-90 (elevated risk)
  State: Stable
  Action: Protect profit, trailing stop
  Condition: Leader at 7+ board

分歧期 (Divergence)
  Health: 50-70
  State: Warning
  Action: Reduce, lock profit
  Condition: 炸板率 rising, mid-tier stocks falling

退潮期 (Recession)
  Health: < 40
  State: Critical
  Action: Exit
  Condition: Leader broken, emotion crashed
```

---

## 8. Limit-Up Position Special States

| Signal | Position Health Impact | Proposed Action |
|--------|:---------------------:|-----------------|
| 封单稳定 + 换手健康 + 梯队完整 | +10 to Trend | Maintain |
| 封单下降 > 30% | −15 to Liquidity | ReduceCandidate |
| 炸板 (天地板) | −30 to Emotion, −30 to Risk | ExitCandidate (urgent) |
| 中位股A杀扩散 | −20 to Emotion | ReduceCandidate |
| 龙头断板 + 情绪骤降 | −40 to Emotion, −30 to Trend | ExitCandidate |

---

## 9. Risk Runtime Interaction

```
Position Engine: PositionAction { "proposed": "AddCandidate" }
        │
        ▼
Risk Runtime: RiskAssessment { "score": 85, "level": "Extreme" }
        │
        ▼
Risk Veto: BLOCK. Max allowed: Maintain.
        │
        ▼
Final PositionDecision: "Maintain" (downgraded from AddCandidate)
```

**Position Engine proposes. Risk Runtime disposes.**

---

## 10. Position Delta Calculation

```
Target_Position (from Portfolio Manager): 30%
Current_Position:                         25%
─────────────────────────────────────────────
Delta:                                    +5%

IF Delta > 0 AND Health ≥ 60 AND Risk OK:
  → AddCandidate
IF Delta < 0:
  → ReduceCandidate
IF Delta ≈ 0:
  → Maintain
```

---

## 11. Failure Handling

| Failure | Action |
|---------|--------|
| QMT position mismatch > 5% | Pause. Flag PositionDrift. Reconcile. |
| Health score drops > 20 in 1 day | Immediate review. Downgrade to Warning. |
| Leader broken while position active | Downgrade to Critical. Propose ExitCandidate. |
| Risk veto blocks proposed action | Accept downgrade. Log. |

---

## 12. Feedback to Memory

```
PositionRecord → Memory System:
  - Full lifecycle events
  - Entry/Add/Reduce/Exit timestamps
  - PnL realized and unrealized
  - Health score trajectory
  - Risk interactions

Purpose:
  - Pattern: Which positions perform best in which regimes?
  - Knowledge: When to exit early vs hold through volatility?
```

---

## 13. Constitution Compliance

| Constitution | Status | Evidence |
|-------------|:------:|----------|
| C-001: Intelligence Ownership | ✅ | Monitors positions, proposes actions, generates no direction |
| C-002: Immutable Core | ✅ | Reads S(t)/B(t)/R(t), never writes |
| C-003: QMT Boundary | ✅ | Outputs to Order Planner, never directly to QMT |
| C-004: Strategy Boundary | ✅ | Consumes StrategyPlan context, does not modify |
| C-005: Portfolio Boundary | ✅ | Receives CapitalAllocation, does not override |
| C-006 (candidate) | ✅ | All MAY/SHALL NOT embedded in §2 |

---

## 14. Engineering Requirement

| Constraint | Value |
|------------|-------|
| Position health evaluation | < 50ms |
| Max monitored positions | 50 |
| State machine transitions | Deterministic |
| Health score update frequency | 5 min or on significant event |

```
04_Execution_Intelligence/04_Position/
├── position_state.py
├── position_context.py
├── health_scorer.py
├── state_machine.py
├── action_proposer.py
├── limit_up_monitor.py
├── position_recorder.py
└── __init__.py
```

---

## 15. Testing Requirement

- New position → health score calculated correctly
- Health < 40 → Critical → ExitCandidate
- Risk Extreme → AddCandidate blocked → Maintain
- Leader broken → immediate Critical
- Delta calculation: target > current → AddCandidate

---

## 16. Freeze Criteria

1. 6-state machine validated
2. Health scoring formula defined
3. A-Share leader lifecycle mapped
4. Limit-up special states defined
5. Risk veto interaction specified
6. All Constitutions C-001 through C-006 verified
7. PositionEngine proposes, Risk disposes

---

## Source References

| Section | Source |
|---------|--------|
| 1-3 | Architect P0-005 Specification |
| 4-5 | Execution Intelligence Architecture V1.0 §6 + Position theory |
| 6-8 | A-Share trading practice |
| 9 | Risk Runtime V2.8.6 + Constitution C-001 |
| 10-15 | Portfolio Manager V1.0 + Execution Architecture V1.0 |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | C-006 promotion to formal Constitution — approve? | §2 |
| 2 | Health score weights (0.30/0.25/0.20/0.25) — confirm? | §6 |
| 3 | Health threshold boundaries (80/60/40) — appropriate? | §6 |
| 4 | Leader lifecycle stages: 6 stages sufficient? | §7 |

---

*AQF-T Position Engine Design V1.0 — ENGINEERING DRAFT*  
*V3.0 Phase 0. Position Lifecycle Intelligence. Proposes, does not dispose.*  
*No original design. All content from Architect specifications.*
