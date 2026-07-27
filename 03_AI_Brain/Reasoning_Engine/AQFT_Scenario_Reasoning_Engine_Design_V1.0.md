# AQF-T Scenario Reasoning Engine Design

Version: V1.0.0
Status: FROZEN — V2.9.3 Reasoning Engine Freeze
Phase: V2.9 Intelligence Era — Reasoning Engine
Module: Reasoning_Engine
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Scenario_Reasoning_Engine_Design_V1.0.md |
| Module | Reasoning Engine — Scenario Reasoning |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_Reasoning_Engine_Architecture_V2.9.3 |
| Upstream | World Model V2.9.0 ✅ + Causal V1.0 + Counterfactual V1.0 |
| Downstream | Decision Intelligence V2.9.1 |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Scenario Simulation V3.0.0 + Counterfactual V3.0.0 + Market Simulation V3.0.0 |

---

## 1. Purpose

### 1.1 What Scenario Reasoning Does

Scenario Reasoning Engine 回答：**"在当前所有认知条件下，未来最可能朝哪些方向演化？"**

| Engine | Question |
|--------|----------|
| Causal | Why is the market like this? |
| Counterfactual | What if key conditions change? |
| Scenario | Where could this go from here? |

### 1.2 Not Prediction — Structured Projection

Scenario Reasoning 不是预测未来。它基于当前 State + Belief + Regime + Memory 进行结构化路径投射。

---

## 2. Scope

- Scenario generation from current state
- Scenario evaluation (impact, probability, risk)
- Scenario ranking for decision support
- A-share specific scenario types

Out of scope: price prediction, trading strategy generation, unlimited simulation.

---

## 3. Architecture Position

In Reasoning Engine: Causal → Counterfactual → **Scenario** → Explainable → Decision

---

## 4. Scenario Reasoning Philosophy

**Principle 1: Multiple Paths, Not One Prediction** — Always output ≥3 scenarios.

**Principle 2: Probability-Weighted, Not Equal** — Each scenario has a probability and confidence.

**Principle 3: Actionable, Not Abstract** — Each scenario answers: "What does this mean for our decision?"

**Principle 4: Memory-Informed** — Historical similar scenarios inform probability estimates.

---

## 5. Scenario Object Model

```json
{
  "scenario_id": "SCEN_20260727_001",
  "name": "Bull Continuation",
  "type": "primary",
  "initial_condition": {
    "regime": "Expansion", "emotion": "Warming",
    "risk": "Low", "leader_status": "Strong_7board"
  },
  "trigger": "Leader holds + volume sustained",
  "evolution_path": [
    {"t+1": "Leader confirms 8-board, sector follows"},
    {"t+3": "Sentiment rises to Climax, breadth expands"},
    {"t+5": "Regime approaches Mania boundary"}
  ],
  "expected_impact": { "direction": "bullish", "magnitude": "+5-10%", "sectors": ["AI","Tech"] },
  "probability": 0.45, "confidence": 0.78,
  "risk_level": "Medium (overheat risk at t+5)",
  "key_monitor": ["leader_volume", "炸板率", "sentiment_score"]
}
```

---

## 6. Scenario Generation

Pipeline: Current State → Identify Key Drivers → Generate Paths (Dynamics + Memory + Causal) → Filter Plausible → Rank

Methods: Dynamics simulation (primary), Historical replay (reference), Causal projection (driver-based).

---

## 7. Scenario Evaluation

Each scenario scored on: direction + magnitude impact, probability, risk level, timeline clarity, decision relevance.

---

## 8. Probability Assessment

`P(Scenario) = f(Dynamics_Fit, Historical_Frequency, Causal_Coherence, Current_Momentum)`

| P > 40% | Primary — core decision reference |
| P 20-40% | Secondary — contingency planning |
| P 10-20% | Tail — awareness |
| P < 10% | Remote — noted |

---

## 9. Risk Opportunity Mapping

| Scenario | Opportunity | Risk | Action Implication |
|----------|------------|------|-------------------|
| Bull Continuation (45%) | +5-10% in AI/Tech | Overheat at t+5 | Increase, monitor sentiment |
| Consolidation (30%) | Rotation opportunity | False breakout | Hold, prepare rotation |
| Policy Shock (15%) | Defensive sectors | Broad drawdown | Reduce, increase cash |
| External Crisis (10%) | None | Systemic | Exit, full defense |

---

## 10. World Model Interface

Input: S(t), B(t), R(t), Simulation forecasts. Output: Scenario-informed belief updates.

---

## 11. Simulation Interface

Leverages World Model Simulation (05_Simulation) for trajectory projection. Scenario adds probability + impact assessment on top.

---

## 12. Memory Interface

Query similar past scenarios → calibrate probability. Store scenario-vs-actual for future accuracy improvement.

---

## 13. Decision Interface

```json
{
  "scenario_report": {
    "top_scenario": "Bull Continuation (45%) → Increase supported",
    "risk_scenario": "Policy Shock (15%) → Pre-hedge recommended",
    "overall_assessment": "Favorable risk/reward. Monitor leader + sentiment.",
    "confidence": 0.78
  }
}
```

---

## 14. Engineering Requirement

< 300ms for 5 scenarios. CPU-friendly. Max 5 scenarios per query.

Code: `scenario_generator | scenario_evaluator | probability_estimator | risk_opportunity_mapper`

---

## 15. Testing Requirement

Multiple scenarios generated from same state. Probabilities approximately sum to 1.0 (allowing for unknown residual). Historical accuracy tracked.

---

## 16. Freeze Criteria

Architecture passed. Scenario object complete. A-share scenario types defined. No price prediction. No strategy generation.

---

## Source References

Scenario Simulation V3.0.0 + Counterfactual V3.0.0 + Market Simulation V3.0.0. No original design.

---

## Items Requiring Architect Review

| # | Item |
|---|------|
| 1 | Max 5 scenarios — sufficient coverage? |
| 2 | Probability thresholds (40/20/10) — confirm? |
| 3 | Scenario-vs-actual accuracy feedback — Evolution or Memory? |

---

*AQF-T Scenario Reasoning Engine Design V1.0 — ENGINEERING DRAFT*
