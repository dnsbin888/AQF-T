# AQF-T Strategy Runtime Design

Version: V1.0.0
Status: ENGINEERING DRAFT — Awaiting Architect Review
Phase: V3.0 Implementation Era — Phase 0 Foundation
Module: 04_Execution_Intelligence / 02_Strategy_Runtime
Created: 2026-07-28

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Strategy_Runtime_Design_V1.0.md |
| Module | Execution Intelligence — Strategy Runtime |
| System | AQF-T Autonomous Quant Intelligence Framework |
| Version | V1.0.0 |
| Parent | AQFT_Execution_Intelligence_Architecture_V1.0 |
| Upstream | Decision Intelligence V2.9.1 ✅ |
| Downstream | Portfolio Manager, Position Engine, Risk Runtime |
| Constitutions | C-001, C-002, C-003, C-004(candidate) |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |

---

## 1. Purpose & Position

### 1.1 What Strategy Runtime Does

Strategy Runtime 是 V3.0 的 **策略执行规划器（Strategy Execution Planner）**。

它回答：**"已经决定要行动了，用什么方案来执行这个决定？"**

| Decision Intelligence | Strategy Runtime |
|----------------------|-----------------|
| WHAT to do | HOW to do it |
| "Increase AI exposure" | "Leader Momentum template, 3-slice entry" |
| Direction | Method |
| Decision Maker | Decision Executor Planner |

### 1.2 Architecture Position

```
Decision Intelligence (Decide)
        │ DecisionIntent
        ▼
┌───────────────────────────┐
│    STRATEGY RUNTIME        │  ← 本模块
│                            │
│  [1] Receive DecisionIntent│
│  [2] Select Strategy Tmpl  │
│  [3] Generate StrategyPlan │
│  [4] Apply Risk Constraint │
│  [5] Output to Portfolio   │
└────────────┬──────────────┘
             │ StrategyPlan
             ▼
     Portfolio Manager
```

---

## 2. Strategy Runtime Role

### 2.1 Core Definition

```
Strategy Runtime = Decision Executor Planner
Strategy Runtime ≠ Decision Maker
Strategy Runtime ≠ Market Signal Generator
Strategy Runtime ≠ Second Brain
```

### 2.2 What Strategy Runtime MUST Do

| MUST | Description |
|------|-------------|
| Consume DecisionIntent | 唯一输入来源 |
| Generate StrategyPlan | 输出执行方案 |
| Respect RiskConstraint | 接受 Risk 约束 |
| Report StrategyOutcome | 反馈执行结果 |
| Support NO ACTION | 空仓等待也是策略 |
| Support multi-strategy | 多模板并行 |

### 2.3 What Strategy Runtime MUST NOT Do

| MUST NOT | Reason |
|----------|--------|
| Generate Market Direction | 属于 Decision Intelligence |
| Override DecisionIntent | 违反 C-001 |
| Modify Immutable Core | 违反 C-002 |
| Bypass Decision Intelligence | 违反 Intelligence Chain |
| Judge market conditions | 属于 World Model |
| Allocate capital independently | 属于 Portfolio Manager |
| Veto Risk decisions | 属于 Risk Runtime |

---

## 3. Intelligence Boundary (C-004 Candidate)

```
C-004: Strategy Runtime Boundary

Strategy Runtime SHALL:
  ✅ Consume DecisionIntent
  ✅ Generate ExecutionPlan Proposal  
  ✅ Respect RiskConstraint
  ✅ Report StrategyOutcome

Strategy Runtime SHALL NOT:
  ❌ Generate Market Direction
  ❌ Override DecisionIntent
  ❌ Modify Immutable Core
  ❌ Bypass Decision Intelligence
```

**[NEEDS ARCHITECT REVIEW]** — C-004 promotion to formal Constitution.

---

## 4. Input Contract

### 4.1 DecisionIntent (From Decision Intelligence)

```json
{
  "decision_id": "DEC_20260728_093500",
  "timestamp": "2026-07-28T09:35:00",
  "symbol": "SH.603xxx",
  "action": "ENTER",
  "confidence": 0.82,
  "regime": "Expansion",
  "emotion_phase": "Warming",
  "risk_level": "Medium",
  "target_position_pct": 0.30,
  "reason": [
    "AI theme confirmed",
    "Leader 2-board successful",
    "Capital inflow sustained"
  ],
  "constraints": {
    "max_position_pct": 0.50,
    "max_single_order_pct": 0.10,
    "risk_score_max": 60
  },
  "source": "Decision Intelligence DI-003",
  "version": "V1.0"
}
```

**Strategy Runtime reads DecisionIntent. Does NOT modify it.**

### 4.2 Additional Context (Read-Only)

| Context | Source | Usage |
|---------|--------|-------|
| RegimeState R(t) | World Model | Strategy template selection |
| EmotionPhase | AI Brain Sentiment | Entry aggressiveness |
| MarketMicrostructure | L2 Data (QMT) | Execution timing |

---

## 5. Output Contract

### 5.1 StrategyPlan

```json
{
  "plan_id": "PLAN_20260728_093500",
  "decision_id": "DEC_20260728_093500",
  "strategy_type": "LeaderMomentum",
  "symbol": "SH.603xxx",

  "entry_plan": {
    "mode": "sliced",
    "slices": [
      {
        "slice_id": 1,
        "label": "confirmation_entry",
        "quantity_pct": 0.10,
        "trigger": "Leader holds 2-board, volume > 5d_avg",
        "order_type": "limit",
        "price_offset_pct": -0.5
      },
      {
        "slice_id": 2,
        "label": "momentum_add",
        "quantity_pct": 0.10,
        "trigger": "Price breaks intraday high, sector follows",
        "order_type": "market"
      },
      {
        "slice_id": 3,
        "label": "trend_confirm",
        "quantity_pct": 0.10,
        "trigger": "Regime stays Expansion, Risk stays < Medium",
        "order_type": "limit"
      }
    ]
  },

  "exit_rule": {
    "primary": "Emotion shifts to Recession OR Risk exceeds 60",
    "secondary": "Leader stock 炸板 OR sector rotation signal",
    "hard_stop": "Position drawdown > 5% from entry"
  },

  "constraints_applied": {
    "max_position": 0.30,
    "risk_limit": "Medium",
    "regime_override": "Expansion only"
  },

  "version": "V1.0"
}
```

### 5.2 StrategyResult (Feedback to Memory)

```json
{
  "plan_id": "PLAN_20260728_093500",
  "decision_id": "DEC_20260728_093500",
  "status": "EXECUTED",
  "planned_position_pct": 0.30,
  "actual_position_pct": 0.28,
  "deviation_reason": "Slice 3 unfilled — risk check triggered",
  "performance": {
    "entry_avg_price": 25.50,
    "current_price": 26.20,
    "unrealized_pnl_pct": 2.75
  },
  "outcome": "PENDING"
}
```

---

## 6. Strategy Instance Model

```json
{
  "strategy_id": "STRAT_LeaderMomentum_v1",
  "name": "Leader Momentum Strategy",
  "type": "LeaderMomentum",
  "version": "V1.0",
  "status": "Active",

  "applicable_regimes": ["Expansion", "Recovery"],
  "applicable_emotions": ["Warming", "Climax"],
  "applicable_actions": ["ENTER", "INCREASE"],

  "entry_template": "sliced_3",
  "exit_rule": "emotion_recession_or_risk_high",
  "position_limit_pct": 0.30,

  "created_by": "AQF-T Architect",
  "last_validated": "2026-07-28"
}
```

---

## 7. Strategy Lifecycle

```
Created ──→ Validated ──→ Active ──→ Paused ──→ Retired
   │            │            │           │
   │            │            │           └── Performance degraded
   │            │            └── Market condition changed
   │            └── Backtest + Risk review passed
   └── Architect defines template
```

| State | Description | Action |
|-------|-------------|--------|
| Created | Template defined | Awaiting validation |
| Validated | Backtest + Risk review passed | Ready for activation |
| Active | In production | Available for Strategy Selection |
| Paused | Temporary suspension | No new plans generated |
| Retired | Permanently removed | Archived |

---

## 8. Strategy Types (V3.0 Initial)

### 8.1 Leader Momentum Strategy (龙头接力)

| Parameter | Value |
|-----------|-------|
| Applicable Regimes | Expansion, Recovery |
| Applicable Emotions | Warming, Climax |
| Entry Mode | Sliced (3 slices: confirmation → momentum → trend) |
| Exit Trigger | Emotion → Recession OR Risk → High |
| Position Limit | 30% |
| A-Share Rationale | 龙头确认后分批介入,情绪退潮即退出 |

### 8.2 Trend Breakout Strategy (趋势突破)

| Parameter | Value |
|-----------|-------|
| Applicable Regimes | Expansion |
| Applicable Emotions | Warming |
| Entry Mode | Breakout confirmation (2 slices) |
| Exit Trigger | Trend weakening OR volume declining |
| Position Limit | 25% |

### 8.3 Defense Strategy (防御)

| Parameter | Value |
|-----------|-------|
| Applicable Regimes | Distribution, Panic |
| Applicable Emotions | Recession, Ice |
| Entry Mode | N/A (only REDUCE / EXIT) |
| Exit Trigger | Immediate |
| Position Limit | 10% (or full exit) |

### 8.4 No-Action Strategy (空仓等待)

| Parameter | Value |
|-----------|-------|
| Applicable Regimes | Neutral |
| Applicable Emotions | Any (when no edge detected) |
| Entry Mode | N/A |
| Exit Trigger | N/A |
| Position Limit | 0% |

**No-Action is a valid strategy. It prevents forced trading.**

---

## 9. Strategy Selection

### 9.1 Selection Logic

```
Input: DecisionIntent { action, regime, emotion, symbol }

[1] Filter: Which strategies are Active AND applicable to this regime?
[2] Match: Which strategies support this action type (ENTER/INCREASE/REDUCE/EXIT)?
[3] Rank: By historical performance in similar regime+emotion conditions
[4] Select: Top-ranked strategy that satisfies RiskConstraint
[5] Generate: StrategyPlan from selected template
```

### 9.2 Selection Matrix

| Decision Action | Regime | Emotion | → Strategy |
|:--------------:|--------|---------|-----------|
| ENTER | Expansion | Warming | LeaderMomentum |
| ENTER | Recovery | Warming | LeaderMomentum |
| INCREASE | Expansion | Climax | LeaderMomentum |
| REDUCE | Distribution | Recession | Defense |
| EXIT | Panic | Ice | Defense |
| — | Neutral | Any | No-Action |

---

## 10. Multi-Strategy Coordination

When multiple DecisionIntents arrive simultaneously:

```
DecisionIntent_1: ENTER AI_Leader, 30%
DecisionIntent_2: ENTER 新能源_Leader, 20%

Coordination Rule:
  [1] Total exposure ≤ Portfolio limit (from Portfolio Manager)
  [2] If conflict: Higher confidence wins
  [3] If equal: Earlier timestamp wins
  [4] Remaining allocation queued for next cycle

Strategy Runtime DOES NOT arbitrate capital allocation.
  → Portfolio Manager handles this.
```

---

## 11. Capital Allocation Interface

Strategy Runtime generates StrategyPlan with `target_position_pct`. Capital allocation and fund availability checks are performed by Portfolio Manager (P0-004).

```
StrategyPlan (target_position_pct: 0.30)
        │
        ▼
Portfolio Manager: "Is 30% available given current exposure?"
        │
        ├── YES → Forward to Position Engine
        └── NO  → Scale down → Return adjusted plan
```

---

## 12. Position Interaction

```
StrategyPlan → Position Engine: "Target: 30%, Current: 10%"
        │
        ▼
Position Engine: "Delta: +20%. Feasible. Proceed."
        │
        ▼
Order Planner: Generate OrderRequests for +20%
```

---

## 13. Risk Constraint Handling

```
Before StrategyPlan generation:
  [1] Check: Is Risk score < DecisionIntent.constraints.risk_score_max?
  [2] Check: Is Regime applicable per strategy template?
  [3] If Risk triggered mid-execution: Cancel all pending slices.

Strategy Runtime does NOT veto Risk.
Strategy Runtime ACCEPTS Risk constraints.
```

---

## 14. Execution Handoff

```
StrategyPlan → Portfolio Manager (allocation check)
             → Position Engine (delta calculation)
             → Risk Runtime (final approval)
             → Order Planner (OrderRequest generation)
             → QMT Adapter (xttrader)
```

Strategy Runtime's responsibility ends at StrategyPlan generation. Downstream modules handle execution.

---

## 15. Feedback Collection

```
StrategyPlan → Execution → ExecutionReport
                                │
                                ▼
                        StrategyResult
                                │
                        ┌───────┴───────┐
                        ▼               ▼
                  Memory System    Evolution System
                  (Episode)        (performance analysis)
```

---

## 16. Failure Handling

| Failure | Action |
|---------|--------|
| No strategy matches DecisionIntent | Return "NoStrategyMatch". Log. Alert. |
| Risk constraint blocks all slices | Return empty plan with reason. |
| DecisionIntent confidence < 0.60 | Generate plan but flag "LowConfidence". |
| Strategy template validation expired | Pause strategy. Require re-validation. |
| Performance degrades 3 consecutive times | Flag for review. Recommend pause. |

---

## 17. Performance Monitoring

| Metric | Purpose |
|--------|---------|
| Plan-to-fill ratio | How much of planned position was actually filled? |
| Strategy win rate by regime | Which strategy works best in which market? |
| Slippage trend | Is execution quality improving? |
| Deviation frequency | How often does actual deviate from plan? |
| Strategy selection accuracy | Was the right strategy chosen for the context? |

Metrics feed into Evolution System for strategy weight adjustment.

---

## 18. Constitution Compliance

| Constitution | Status | Evidence |
|-------------|:------:|----------|
| C-001: Intelligence Ownership | ✅ | Strategy consumes DecisionIntent, generates no direction |
| C-002: Immutable Core | ✅ | Strategy reads S(t)/B(t)/R(t), never writes |
| C-003: QMT Boundary | ✅ | Strategy outputs to Portfolio, never directly to QMT |
| C-004: Strategy Boundary (candidate) | ✅ | All MUST/MUST NOT rules embedded in §2-3 |

---

## Source References

| Section | Source |
|---------|--------|
| 1-3 | Architect P0-003 Specification |
| 4-5 | Execution Intelligence Architecture V1.0 §6 |
| 6-10 | A-share trading practice + V2.8.6 Strategy Design |
| 11-14 | Execution Intelligence Architecture V1.0 §5 |
| 15-17 | Memory System V2.9.2 + Evolution System V2.8.6 |
| 18 | QMT Integration Principle V1.0 + C-001/C-002/C-003 |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | C-004 promotion to formal Constitution — approve? | §3 |
| 2 | Strategy template count: 4 initial (Leader/Trend/Defense/NoAction) — sufficient for V3.0 MVP? | §8 |
| 3 | Multi-strategy conflict rule: "Higher confidence wins" — confirm? | §10 |
| 4 | Performance degradation threshold: "3 consecutive times" — appropriate? | §16 |

---

*AQF-T Strategy Runtime Design V1.0 — ENGINEERING DRAFT*  
*V3.0 Phase 0 Foundation. Decision Executor Planner. Not a second brain.*  
*No original design. All content from Architect specifications.*
