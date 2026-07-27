# AQF-T Portfolio Manager Design

Version: V1.0.0
Status: ARCHITECT REVIEW PASSED — Pending Execution Intelligence Freeze
Phase: V3.0 Implementation Era — Phase 0 Foundation
Module: 04_Execution_Intelligence / 03_Portfolio
Created: 2026-07-28

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Portfolio_Manager_Design_V1.0.md |
| Module | Execution Intelligence — Portfolio Manager |
| System | AQF-T Autonomous Quant Intelligence Framework |
| Version | V1.0.0 |
| Parent | AQFT_Execution_Intelligence_Architecture_V1.0 |
| Upstream | Decision Intelligence V2.9.1 ✅ + Strategy Runtime V1.0 |
| Downstream | Position Engine, Risk Runtime |
| Constitutions | C-001, C-002, C-003, C-004, C-005(candidate) |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |

---

## 1. Purpose & Position

### 1.1 What Portfolio Manager Does

Portfolio Manager 是 V3.0 的 **资金配置智能层（Capital Allocation Intelligence）**。

它回答：**"多个交易机会同时出现时，资金应该如何分配？"**

| Decision Intelligence | Strategy Runtime | Portfolio Manager |
|----------------------|-----------------|-------------------|
| WHAT to do | HOW to do it | HOW MUCH to allocate |
| "ENTER AI 龙头" | "LeaderMomentum, 3-slice" | "25% allocation, priority 1" |
| Direction | Method | Capital |

### 1.2 Architecture Position

```
Decision Intelligence ──→ Strategy Runtime ──→ PORTFOLIO MANAGER ──→ Position Engine
       (WHAT)                  (HOW)                (HOW MUCH)            (TRACK)
```

### 1.3 Core Definition

```
Portfolio Manager = Capital Allocation Intelligence
Portfolio Manager ≠ Decision Maker
Portfolio Manager ≠ Alpha Generator
Portfolio Manager ≠ Market Predictor
```

---

## 2. Portfolio Authority Boundary (C-005 Candidate)

```
C-005: Portfolio Authority Boundary

Portfolio Manager MUST:
  ✅ Consume DecisionIntent
  ✅ Consume StrategyPlan
  ✅ Generate CapitalAllocation
  ✅ Respect RiskConstraint
  ✅ Balance Portfolio Exposure
  ✅ Report AllocationOutcome

Portfolio Manager MUST NOT:
  ❌ Generate Market Direction
  ❌ Create Trading Signal
  ❌ Override Decision
  ❌ Modify Immutable Core
  ❌ Bypass Risk Runtime
  ❌ Directly Submit Order
```

**[NEEDS ARCHITECT REVIEW]** — C-005 promotion to formal Constitution.

---

## 3. Relationship with Decision Intelligence

```
Decision Intelligence → DecisionIntent { action: "ENTER", confidence: 0.82 }
        │
        ▼
Portfolio Manager reads:
  - What action is requested
  - How confident is the decision
  - What regime are we in
  - What risk level is assigned

Portfolio Manager DOES NOT:
  - Second-guess the decision
  - Override the direction
  - Modify the confidence
```

---

## 4. Relationship with Strategy Runtime

```
Strategy Runtime → StrategyPlan { strategy_type, suggested_size, entry_method }
        │
        ▼
Portfolio Manager considers:
  - Suggested size as reference
  - May scale down based on portfolio constraints
  - May defer if capital insufficient

Portfolio Manager DOES NOT:
  - Change the strategy type
  - Modify the entry method
```

---

## 5. Input Contracts

### 5.1 DecisionIntent (From Decision Intelligence)

```json
{
  "decision_id": "DEC_20260728_093500",
  "symbol": "SH.603xxx",
  "action": "ENTER",
  "confidence": 0.82,
  "regime": "Expansion",
  "risk_level": "Medium",
  "reason": ["AI theme confirmed", "Leader 2-board", "Capital inflow"]
}
```

### 5.2 StrategyPlan (From Strategy Runtime)

```json
{
  "plan_id": "PLAN_20260728_093500",
  "strategy_type": "LeaderMomentum",
  "suggested_size_pct": 0.30,
  "entry_mode": "sliced_3"
}
```

### 5.3 PortfolioState (Current)

```json
{
  "total_capital": 1000000,
  "available_cash": 450000,
  "current_exposure_pct": 0.55,
  "max_exposure_pct": 0.70,
  "sector_exposure": { "AI": 0.30, "新能源": 0.15, "消费": 0.10 },
  "position_count": 5,
  "risk_budget_remaining_pct": 0.15
}
```

---

## 6. Output Contracts

### 6.1 CapitalAllocation

```json
{
  "allocation_id": "ALLOC_20260728_093500",
  "decision_id": "DEC_20260728_093500",
  "plan_id": "PLAN_20260728_093500",
  "symbol": "SH.603xxx",

  "target_weight": 0.25,
  "max_weight": 0.30,
  "entry_budget": 250000,
  "priority": 1,

  "status": "APPROVED",
  "reason": "High confidence + Regime support + Risk budget available",

  "constraints_applied": {
    "max_single_position": 0.30,
    "max_sector_exposure": 0.40,
    "correlation_penalty_applied": false
  },

  "version": "V1.0"
}
```

### 6.2 PortfolioDecision (Per Opportunity)

| Decision | Condition |
|----------|-----------|
| APPROVE | Risk budget available, correlation OK, priority fits |
| REDUCE | Scale down due to exposure limit or correlation concern |
| REJECT | Risk budget exhausted, or confidence too low |
| DEFER | Queue for next cycle (capital temporarily insufficient) |

---

## 7. Portfolio Object Model

```
PortfolioState
├── total_capital
├── available_cash
├── current_exposure_pct
├── max_exposure_pct (from Risk Runtime)
├── sector_exposure: { sector: weight }
├── positions: [Position]
└── risk_budget_remaining_pct
```

---

## 8. Capital Allocation Engine

### 8.1 Allocation Pipeline

```
[1] Receive: DecisionIntent + StrategyPlan
        │
[2] Check: Is Risk budget available?
        │  NO → REJECT or DEFER
        ▼
[3] Calculate: Target weight based on confidence + regime + risk
        │
[4] Check: Correlation with existing positions?
        │  HIGH → REDUCE (concentration penalty)
        ▼
[5] Check: Sector exposure within limit?
        │  OVER → REDUCE
        ▼
[6] Output: CapitalAllocation
```

### 8.2 Allocation Formula

```
Target_Weight = Base_Weight × Confidence_Factor × Regime_Factor × Risk_Discount

Where:
  Base_Weight:      StrategyPlan.suggested_size_pct
  Confidence_Factor: min(1.0, DecisionIntent.confidence / 0.80)
  Regime_Factor:     Expansion=1.0, Recovery=0.8, Neutral=0.5,
                     Distribution=0.3, Panic=0.1
  Risk_Discount:     1.0 - (Risk_Score / 200)
```

**[NEEDS ARCHITECT REVIEW]** — Allocation formula weights.

---

## 9. Exposure Management

### 9.1 Exposure Limits by Regime (from Risk Runtime)

| Regime | Max Total Exposure | Max Single Position | Max Sector |
|--------|:-----------------:|:-------------------:|:----------:|
| Expansion | 70% | 30% | 40% |
| Recovery | 60% | 25% | 35% |
| Neutral | 50% | 20% | 30% |
| Distribution | 30% | 15% | 20% |
| Panic | 10% | 5% | 10% |

**Portfolio Manager reads these from Risk Runtime. Does not set them.**

### 9.2 Exposure Calculation

```
Available_Exposure = Max_Total_Exposure - Current_Exposure

IF Available_Exposure ≤ 0:
  → All new ENTER/INCREASE: REJECT
  → Only REDUCE/EXIT processed
```

---

## 10. Multi-Opportunity Resolution

### 10.1 Conflict Scenario

```
Simultaneous DecisionIntents:
  D1: ENTER AI_Leader, confidence=0.82, strategy=LeaderMomentum
  D2: ENTER 新能源_Leader, confidence=0.72, strategy=LeaderMomentum
  D3: ENTER 机器人_Leader, confidence=0.55, strategy=TrendBreakout

Available capital: 150,000 (15% of portfolio)
Total requested: 250,000 (D1:100k, D2:100k, D3:50k)
```

### 10.2 Resolution Rules

```
[1] Rank by: confidence × regime_factor
    D1: 0.82 × 1.0 = 0.82  → Priority 1
    D2: 0.72 × 1.0 = 0.72  → Priority 2
    D3: 0.55 × 1.0 = 0.55  → Priority 3

[2] Allocate in priority order until capital exhausted:
    D1: Full (100k)
    D2: Full (100k) → Capital exhausted after D1+D2
    D3: DEFER (no capital remaining)

[3] Output: APPROVE(D1), APPROVE(D2), DEFER(D3)
```

---

## 11. Risk Budget Integration

```
Risk Runtime provides:
  - Max total exposure
  - Max single position
  - Max sector exposure
  - Max drawdown limit
  - Risk score

Portfolio Manager:
  - Reads all constraints
  - Applies them during allocation
  - NEVER overrides Risk limits
  - If Risk score spikes mid-session → freeze new allocations
```

---

## 12. A-Share Position Model

### 12.1 Position Tiers

| Tier | Weight Range | Purpose | When |
|------|:-----------:|---------|------|
| 试错仓 (Trial) | 5-10% | 验证机会 | 首板确认期 |
| 确认仓 (Confirm) | 10-20% | 趋势确认 | 二板成功, 板块联动 |
| 主仓 (Core) | 20-30% | 主升阶段 | Expansion+Warming, 龙头确认 |
| 加仓 (Add) | +5-10% | 加速期 | 超预期, 情绪高潮 |
| 退出仓 (Exit) | →0% | 减仓清仓 | 退潮信号, Risk升高 |

### 12.2 Position Tier → Regime Mapping

| Tier | Expansion | Neutral | Distribution | Panic |
|------|:--------:|:-------:|:-----------:|:-----:|
| 试错仓 | ✅ | ✅ | ❌ | ❌ |
| 确认仓 | ✅ | ✅ | ❌ | ❌ |
| 主仓 | ✅ | ❌ | ❌ | ❌ |
| 加仓 | ✅ | ❌ | ❌ | ❌ |
| 退出仓 | ✅ | ✅ | ✅ | ✅ |

---

## 13. Portfolio Lifecycle

```
Pre-Market:
  [1] Load current positions from QMT (via Position Engine)
  [2] Load Risk constraints from Risk Runtime
  [3] Calculate available exposure

During Trading:
  [4] Receive DecisionIntent + StrategyPlan
  [5] Run allocation pipeline
  [6] Output CapitalAllocation → Position Engine

Post-Trade:
  [7] Update PortfolioState
  [8] Report AllocationOutcome → Memory System

End-of-Day:
  [9] Reconcile with QMT positions
  [10] Generate daily portfolio report
```

---

## 14. Feedback Loop

```
CapitalAllocation → Position Engine → Order Planner → QMT → ExecutionReport
                                                              │
                                                              ▼
                                                      AllocationOutcome
                                                              │
                                                     ┌────────┴────────┐
                                                     ▼                 ▼
                                               Memory System     Evolution System
                                               (Episode)         (allocation quality)
```

---

## 15. Failure Handling

| Failure | Action |
|---------|--------|
| Risk budget exhausted | REJECT all new ENTER/INCREASE |
| QMT position mismatch | Pause allocations. Reconcile first. |
| Single sector > 40% | REDUCE any new allocation to that sector |
| Correlation > 0.80 with existing | REDUCE (concentration penalty -50%) |
| Available cash < minimum order | DEFER all new allocations |

---

## 16. Constitution Compliance

| Constitution | Status | Evidence |
|-------------|:------:|----------|
| C-001: Intelligence Ownership | ✅ | Portfolio allocates capital, generates no direction |
| C-002: Immutable Core | ✅ | Reads S(t)/B(t)/R(t), never writes |
| C-003: QMT Boundary | ✅ | Outputs to Position Engine, never directly to QMT |
| C-004: Strategy Boundary | ✅ | Consumes StrategyPlan, does not modify |
| C-005 (candidate) | ✅ | All MUST/MUST NOT embedded in §2 |

---

## Source References

| Section | Source |
|---------|--------|
| 1-2 | Architect P0-004 Specification |
| 3-4 | Strategy Runtime V1.0 + Decision Intelligence V2.9.1 |
| 5-6 | Execution Intelligence Architecture V1.0 §6 |
| 7-11 | Portfolio theory + Risk Runtime V2.8.6 |
| 12 | A-share position practice |
| 13-15 | Execution Intelligence Architecture V1.0 §8 |
| 16 | C-001/C-002/C-003/C-004 |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | C-005 promotion to formal Constitution — approve? | §2 |
| 2 | Allocation formula weights (confidence/regime/risk factors) — confirm? | §8 |
| 3 | Correlation penalty threshold: 0.80 → -50% — appropriate? | §15 |
| 4 | Position tier model: 5 tiers sufficient for V3.0 MVP? | §12 |

---

*AQF-T Portfolio Manager Design V1.0 — ENGINEERING DRAFT*  
*V3.0 Phase 0 Foundation. Capital Allocation Intelligence. Not Alpha Generator.*  
*No original design. All content from Architect specifications.*
