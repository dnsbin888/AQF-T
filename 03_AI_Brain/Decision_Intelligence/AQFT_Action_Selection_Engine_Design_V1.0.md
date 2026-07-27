# AQF-T Action Selection Engine Design

Version: V1.0.0
Status: FROZEN — V2.9.1 Decision Intelligence Freeze
Phase: V2.9 Intelligence Era — Decision Intelligence
Module: Decision_Intelligence
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Action_Selection_Engine_Design_V1.0.md |
| Module | Decision Intelligence — Action Selection Engine |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_Decision_Intelligence_Architecture_V2.9.1 |
| Upstream | Fusion Engine (evidence) + World Model (context) + Risk (constraint) |
| Downstream | Strategy Runtime → Risk Runtime → Execution Runtime |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Decision Architecture V3.0.0 + AI Brain Design V2.8.6 |

---

## 1. Purpose

### 1.1 What Action Selection Does

Action Selection Engine 是 Decision Intelligence 的 **执行决策器**。

它回答：**"在当前所有认知、约束和风险条件下，AQF-T 应该采取什么行动方向？"**

| Fusion Engine | Action Selection |
|--------------|-----------------|
| 综合证据 | 选择行动 |
| "证据表明……" | "因此，应该……" |
| Evidence integration | Action decision |

### 1.2 Action Selection ≠ Strategy

```
Action Selection:  "加仓" (Increase exposure)
Strategy Runtime:  "用趋势策略，选龙头股，分3批入场" (How specifically)

Action Selection:  "防御" (Defend)
Strategy Runtime:  "减仓50%，剩余仓位设止损-3%" (How specifically)
```

Action = Direction（方向）。Strategy = Method（方法）。

### 1.3 What Action Selection Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 买卖信号 (BUY/SELL) | 行动姿态 (Increase/Reduce) |
| 选股系统 | 方向选择 |
| 仓位计算器 | 约束内行动强度判定 |
| 替代 Strategy | Strategy 的指挥层 |

---

## 2. Scope

### 2.1 In Scope

- 7-level action space definition
- Utility-based action selection (U(A) optimization)
- Risk constraint integration
- Confidence-gated action output
- Regime-contextual action mapping
- Human governance interface
- Action reasoning trace

### 2.2 Out of Scope

- ❌ Specific trading strategy design
- ❌ Stock selection / portfolio construction
- ❌ Position sizing (that's Strategy + Risk)
- ❌ Order execution (that's Execution Runtime)
- ❌ Bypassing Risk approval

---

## 3. Architecture Position

### 3.1 In Decision Pipeline

```
Fusion Engine (Evidence)
        │
        ▼
┌───────────────────────┐
│ ACTION SELECTION      │  ← 本模块
│                       │
│ [1] Decision State    │
│ [2] Utility Eval      │
│ [3] Risk Gate         │
│ [4] Action Select     │
│ [5] Confidence Check  │
│ [6] Governance Gate   │
│ [7] Output            │
└───────────┬───────────┘
            │
            ▼
    Strategy Runtime
```

### 3.2 In AQF-T System

```
World Model → Fusion Engine → Action Selection → Strategy → Risk → Execution
```

Action Selection is the **final cognitive step before Strategy execution**.

---

## 4. Action Intelligence Philosophy

### 4.1 Core Principles

**Principle 1: Act on Evidence, Not Impulse**

每一次行动必须可追溯到融合证据。禁止无依据的交易冲动。

**Principle 2: Conservative Under Uncertainty**

不确定性高时，默认保守。Confidence < 0.60 → 不增加风险敞口。

**Principle 3: Regime Shapes Action**

同一证据在 Expansion 中触发 Increase，在 Panic 中可能只触发 Hold。

**Principle 4: Risk Has Veto**

Risk 可以否决任何行动。Action Selection 在 Risk Gate 之后才输出。

### 4.2 Expected Utility Decision

```
A* = argmax U(A)  subject to Risk_Constraint(A) = PASS

U(A) = Expected_Return - Risk_Penalty + Knowledge_Gain - Uncertainty_Cost
```

---

## 5. Action Space Definition

### 5.1 Seven-Level Action Space

| Level | Action | Meaning | Risk Exposure Change |
|:-----:|--------|---------|:-------------------:|
| 0 | Observe | 观察，不持仓 | 0 |
| 1 | Wait | 等待入场时机 | 0 (ready) |
| 2 | Prepare | 准备入场，确认条件 | 0→minimal |
| 3 | Enter | 入场，建立初始仓位 | 0→base |
| 4 | Hold | 维持现有仓位 | unchanged |
| 5 | Increase | 加仓 | base→full |
| 6 | Reduce | 减仓 | full→base→0 |
| 7 | Exit | 清仓退出 | →0 |

### 5.2 Action-State Machine

```
        Observe
           │
           ▼
         Wait ──────────────┐
           │                │
           ▼                │
        Prepare             │
           │                │
           ▼                │
         Enter ──→ Hold ──→ Increase
           │        │          │
           │        ▼          ▼
           └──→ Reduce ←── Reduce
                    │
                    ▼
                  Exit
```

---

## 6. Decision State Representation

### 6.1 Decision State Object

```json
{
  "decision_id": "DEC_20260727_093500",
  "timestamp": "2026-07-27T09:35:00",

  "input": {
    "fusion_evidence": { FusionOutput },
    "world_context": { "regime": "Expansion", "emotion": "Warming" },
    "current_position": { "exposure": 0.35, "max_allowed": 0.70 },
    "risk_assessment": { "score": 28, "level": "Low" }
  },

  "evaluation": {
    "candidate_actions": [
      { "action": "Increase", "utility": 0.72, "risk_ok": true },
      { "action": "Hold", "utility": 0.55, "risk_ok": true },
      { "action": "Enter", "utility": 0.48, "risk_ok": true },
      { "action": "Reduce", "utility": 0.15, "risk_ok": true }
    ],
    "selected": "Increase",
    "confidence": 0.78
  },

  "constraints_applied": [
    "Regime: Expansion → Increase/Hold allowed",
    "Risk: Low → no restriction",
    "Confidence: 0.78 → full execution within limit"
  ],

  "reasoning": "Expansion regime + Warming sentiment + Low risk → Increase posture appropriate"
}
```

---

## 7. Utility Function Model

### 7.1 Utility Formula

[Source: `AQFT_AGI_Decision_Architecture_Design_V3.0.0` — Chapter 3]

```
U(Action) = E[Return | Action] - Risk_Penalty + Knowledge_Gain - Uncertainty_Cost

Components:
  E[Return]:     Σ P(Scenario_i) × Expected_Return(Action, Scenario_i)
  Risk_Penalty:  Risk_Score × Risk_Aversion × Exposure(Action)
  Knowledge_Gain: Information value (exploration bonus for seldom-used actions)
  Uncertainty_Cost: Fusion_Uncertainty × Action_Aggressiveness
```

### 7.2 Utility per Action Type

| Action | Return Component | Risk Component | Knowledge | Uncertainty |
|--------|:---------------:|:-------------:|:---------:|:-----------:|
| Observe | 0 | 0 | High (learning) | 0 |
| Wait | 0 | 0 | Medium | 0 |
| Prepare | Low | Low | Medium | Low |
| Enter | Medium | Medium | Medium | Medium |
| Hold | Status quo | Status quo | Low | Low |
| Increase | High | High | Low | High |
| Reduce | Negative (give up upside) | Negative (reduce risk) | Low | Low |
| Exit | Most negative (give up all) | Most negative (eliminate risk) | Low | Low |

**[NEEDS ARCHITECT REVIEW]** — Knowledge_Gain term for Observe/Wait: appropriate for AQF-T? Or should exploration be handled by Evolution System?

---

## 8. Constraint Handling

### 8.1 Constraint Types

| Constraint | Source | Effect |
|------------|--------|--------|
| Regime constraint | World Model Regime | Allowed/blocked action types |
| Risk constraint | Risk Intelligence | Max exposure, blocked actions |
| Confidence constraint | Fusion Engine | Action scaling |
| Position constraint | Strategy Runtime | Current exposure → feasible actions |
| Governance constraint | Human-AI rules | Authorization required |

### 8.2 Constraint Application Order

```
[1] Regime: Which actions are allowed in this regime?
        ↓ (filter)
[2] Risk: Does Risk block any actions?
        ↓ (filter/scale)
[3] Confidence: Are we confident enough for this action?
        ↓ (scale confidence < 0.60 → cap at Hold)
[4] Position: What's feasible given current exposure?
        ↓ (filter)
[5] Governance: Does this action need human approval?
        ↓ (flag for review)
[6] Final Action Set → Utility Evaluation → Select A*
```

---

## 9. Risk Integration

### 9.1 Risk Gate

```
Action Candidate → Risk Gate → Approved / Scaled / Blocked
```

| Risk Level | Increase | Enter | Hold | Reduce | Exit |
|-----------|:--------:|:-----:|:----:|:------:|:----:|
| Low (0-30) | ✅ Full | ✅ Full | ✅ | ✅ | ✅ |
| Medium (30-60) | ⚠️ Scaled | ✅ | ✅ | ✅ | ✅ |
| High (60-80) | ❌ Blocked | ⚠️ Scaled | ✅ | ✅ | ✅ |
| Extreme (80+) | ❌ Blocked | ❌ Blocked | ⚠️ | ✅ | ✅ |

### 9.2 Risk Veto

Risk Runtime 可以在 Action Selection 输出后否决：

```
Action Selection: "Increase"
       ↓
Risk Runtime: "Risk Score 85. Veto. Max: Hold."
       ↓
Final Action: "Hold"
```

---

## 10. Human Governance

### 10.1 Authorization Thresholds

| Action | Auto-Approved | Human Review |
|--------|:------------:|:------------:|
| Observe, Wait, Prepare | ✅ | — |
| Enter (initial) | ✅ (Risk must be Low/Medium) | Risk High |
| Hold | ✅ | — |
| Increase (≤ 50% limit) | ✅ | Risk Medium+ |
| Increase (> 50% limit) | — | ✅ Required |
| Reduce | ✅ | — |
| Exit (partial) | ✅ | — |
| Exit (full portfolio) | — | ✅ Required |

### 10.2 Override Record

```json
{
  "original_action": "Increase",
  "override_action": "Hold",
  "override_by": "Human",
  "reason": "Earnings report pending — manual caution",
  "timestamp": "...",
  "expires": "2026-07-28T09:30:00"
}
```

---

## 11. Action Explanation

### 11.1 Reasoning Trace

每个 Action 输出必须携带：

```
WHY this action?
  → "Expansion regime + Warming sentiment → Aggressive posture supported"

WHY NOT alternatives?
  → "Exit rejected: regime supports holding. Reduce rejected: risk not elevated."

WHAT WOULD CHANGE THIS?
  → "If sentiment phase shifts to Recession OR risk score exceeds 60 → Reduce"
```

### 11.2 Explanation Template

```json
{
  "action": "Increase",
  "reasoning": [
    "Regime: Expansion → Increase/Hold supported",
    "Sentiment: Warming (score 65) → momentum favorable",
    "Risk: Low (score 28) → risk budget available",
    "Fusion confidence: 0.78 → full execution allowed"
  ],
  "alternatives": {
    "Hold": "Lower return, higher certainty. Appropriate if risk tolerance lower.",
    "Reduce": "Inappropriate for current regime unless risk signals change."
  },
  "watch_conditions": [
    "Sentiment phase → Recession: action should shift to Reduce",
    "Risk score → 60+: reduce position scale",
    "Regime → Distribution: exit all aggressive positions"
  ]
}
```

---

## 12. Feedback Loop

### 12.1 Action Outcome Tracking

```
Action(t) → Strategy(t) → Execution(t) → Outcome(t+n)
                                              │
                                              ▼
                                     Was the action correct?
                                              │
                                     ┌────────┴────────┐
                                     ▼                 ▼
                              Action Accuracy    Regime-Action Fit
                              by Regime          Optimization
```

### 12.2 Learning Metrics

| Metric | Improves |
|--------|----------|
| Action accuracy per regime | Regime-action mapping |
| Confidence calibration | Confidence gate thresholds |
| Override frequency | Governance thresholds |
| Action→outcome correlation | Utility function parameters |

---

## 13. Engineering Requirement

### 13.1 Constraints

| Constraint | Value |
|------------|-------|
| Decision latency | < 50ms (after Fusion complete) |
| Utility evaluation | < 10ms per candidate |
| Max candidate actions | 8 |
| Compute | CPU-friendly (simple utility calc) |

### 13.2 Code Structure

```
decision_intelligence/action_engine/
├── action_space.py             # 7-level action definitions
├── decision_state.py           # DecisionState object
├── utility_calculator.py       # U(A) computation
├── constraint_engine.py        # Multi-constraint application
├── risk_gate.py                # Risk check + veto
├── governance_gate.py          # Human authorization
├── action_selector.py          # A* = argmax U(A)
├── explanation_generator.py    # Reasoning trace
└── __init__.py
```

---

## 14. Testing Requirement

### 14.1 Unit Tests

- All 7 actions selectable given appropriate inputs
- Risk High: Increase blocked, Reduce allowed
- Confidence < 0.40: actions capped at Observe/Wait
- Regime Panic: Enter/Increase blocked

### 14.2 Scenario Tests

| Scenario | Expected Action |
|----------|----------------|
| Expansion + Warming + Low Risk | Increase |
| Expansion + Warming + High Risk | Hold or Reduce |
| Panic + Ice + Extreme Risk | Exit or Observe |
| Neutral + Mixed + Low Risk | Hold |
| Recovery + Warming + Medium Risk | Enter (cautious) |

### 14.3 Integration Tests

- Full chain: Fusion → Action → Strategy translation
- Risk veto: Action=Increase, Risk=Extreme → output=Hold
- Governance: full exit → human review flag set

---

## 15. Freeze Criteria

1. **Architecture Review Passed** — Correctly positioned after Fusion, before Strategy
2. **7-level action space complete** — Observe through Exit, state machine defined
3. **Utility function specified** — U(A) with 4 components
4. **Constraint pipeline ordered** — Regime → Risk → Confidence → Position → Governance
5. **Risk veto maintained** — Risk can override any action
6. **Human governance integrated** — Authorization thresholds clear
7. **Explanation mandatory** — Every action output carries reasoning trace
8. **No strategy design** — Action = direction, not method

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-4 | Decision Intelligence Architecture V2.9.1 |
| 5 | Extended from Decision Architecture V3.0.0 Ch.2 |
| 6-7 | Decision Architecture V3.0.0 Ch.2-3 |
| 8-9 | Constitution Ch.7 + Risk Design V2.8.6 |
| 10 | Constitution Ch.10 + Human-AI Collaboration V3.0.0 |
| 11 | Inferred from Explainability principle |
| 12 | Evolution System V2.8.6 |
| 13-15 | V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Knowledge_Gain term for Observe/Wait — exploration bonus or defer to Evolution? | §7 |
| 2 | Action space: 7 levels appropriate for A-share retail? Or simplify to 5? | §5 |
| 3 | Auto-approval thresholds: appropriate risk tolerance? | §10 |

---

*AQF-T Action Selection Engine Design V1.0 — ENGINEERING DRAFT*  
*Source: Decision Architecture V3.0.0 + AI Brain Design V2.8.6 + Constitution V2.8.6*  
*No original design added. All content traceable to existing AQF-T architecture.*
