# AQF-T Explainable Reasoning Engine Design

Version: V1.0.0
Status: FROZEN — V2.9.3 Reasoning Engine Freeze
Phase: V2.9 Intelligence Era — Reasoning Engine
Module: Reasoning_Engine
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Explainable_Reasoning_Engine_Design_V1.0.md |
| Module | Reasoning Engine — Explainable Reasoning |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_Reasoning_Engine_Architecture_V2.9.3 |
| Upstream | Causal + Counterfactual + Scenario Reasoning |
| Downstream | Decision Intelligence + Human-AI Governance |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Reasoning Architecture V2.9.3 + Human-AI Governance V3.0.0 + Constitution V2.8.6 |

---

## 1. Purpose

### 1.1 What Explainable Reasoning Does

Explainable Reasoning Engine 回答 AI 治理中最关键的问题：**"为什么系统形成这个判断？"**

[Source: Constitution V2.8.6 — Principle 4: Explainability + Principle 9: Human-AI Collaboration]

| Without Explainability | With Explainability |
|----------------------|-------------------|
| AI: "Increase, confidence 0.78" | AI: "Increase. Because: Expansion+Warming+LowRisk. Evidence: 3/4 engines agree. Historical: 72% success. Alternative: Hold also reasonable." |
| Human: "Why?" → Silence | Human: Can verify reasoning, challenge assumptions |

### 1.2 Why This Matters

可解释性不是可选功能。它是 AQF-T 作为 AI 增强决策系统的治理基础。不可解释的 AI = 不可治理的 AI。

---

## 2. Scope

In scope: evidence trace, reasoning chain, confidence decomposition, alternative explanations, uncertainty quantification, human review triggers.

Out of scope: natural language generation (uses structured templates, not free-form LLM), replacing human judgment.

---

## 3. Architecture Position

Final stage in Reasoning Pipeline: Causal → Counterfactual → Scenario → **Explainable** → Decision + Human Review

---

## 4. Explainability Philosophy

**Principle 1: Every Conclusion Has a Trace** — "Increase because X, Y, Z" — not "Increase."

**Principle 2: Confidence Is Decomposable** — Overall 0.78 = Engine agreement 0.85 × Evidence quality 0.90 × Historical match 0.80. Not a magic number.

**Principle 3: Alternatives Must Be Visible** — "Hold would be 0.55 utility — also defensible." Shows the system considered other options.

**Principle 4: Uncertainty Is Honest** — "Key uncertainty: sentiment may overheat in 3-5 days." Admits what it doesn't know.

---

## 5. Explanation Object Model

```json
{
  "explanation_id": "EXPL_20260727_093500",
  "question": "Should AQF-T increase AI exposure?",
  "conclusion": "Increase posture from 35% to 50%",
  "confidence": 0.78,

  "evidence": {
    "world_model": { "regime": "Expansion (0.82)", "emotion": "Warming (0.75)" },
    "ai_brain": { "prediction_up": 0.72, "sentiment_warming": 0.75, "risk_low": 0.85 },
    "memory": { "similar_episodes": 127, "success_rate": 0.72 },
    "causal": { "chain": "Policy→Liquidity→Sector→Index", "confidence": 0.82 }
  },

  "reasoning_chain": [
    "Step 1: Expansion regime confirmed → aggressive posture supported",
    "Step 2: Warming sentiment → positive momentum",
    "Step 3: Risk Low (28) → budget available",
    "Step 4: Causal analysis → rally has structural foundation, not purely speculative",
    "Step 5: Memory → 72% historical success in similar conditions",
    "Conclusion: Increase with confidence 0.78"
  ],

  "confidence_breakdown": {
    "engine_agreement": 0.85, "evidence_quality": 0.90,
    "historical_match": 0.80, "uncertainty_penalty": -0.05,
    "overall": 0.78
  },

  "alternatives": [
    { "action": "Hold", "utility": 0.55, "rationale": "Lower return but higher certainty. Defensible if risk tolerance lower." }
  ],

  "uncertainties": [
    "Sentiment approaching overheat (65/100). Monitor threshold 80.",
    "Leader stock at 7-board — fatigue risk increases each board.",
    "Policy follow-through not yet confirmed."
  ],

  "human_review": { "required": false, "reason": "Confidence > 0.70, Risk < 60", "escalation_triggers": ["sentiment > 80", "leader_炸板"] }
}
```

---

## 6. Evidence Trace

Every conclusion element must trace to a source:

| Claim | Source |
|-------|--------|
| "Expansion regime" | World Model Regime Engine, confidence 0.82 |
| "Warming sentiment" | AI Brain Sentiment Engine, score 65 |
| "Low risk" | Risk Intelligence, score 28 |
| "72% historical success" | Memory System, 127 episodes |

No unsourced claims. No "AI thinks."

---

## 7. Reasoning Chain Visualization

Structured trace: Step 1 (Context) → Step 2 (Evidence) → Step 3 (Analysis) → Step 4 (Causal) → Step 5 (Historical) → Conclusion + Confidence + Alternatives + Uncertainties + Watch Conditions.

---

## 8. Confidence Model

`Overall = Engine_Agreement × 0.35 + Evidence_Quality × 0.30 + Historical_Match × 0.25 + Uncertainty_Penalty × 0.10`

| > 0.80 | Strong — autonomous recommendation |
| 0.60-0.80 | Moderate — recommendation with caveats |
| 0.40-0.60 | Weak — human review recommended |
| < 0.40 | Insufficient — no autonomous recommendation |

---

## 9. Alternative Explanation

Counter-argument to current conclusion, e.g., "Hold is also reasonable: lower return (+2%) but higher certainty. Appropriate if risk tolerance lower or if leader stock concerns dominate."

---

## 10. Uncertainty Management

Known unknowns explicitly stated: "Sentiment may overheat (currently 65, threshold 80)", "Leader fatigue risk at high board count", "Policy follow-through pending."

Uncertainty level affects confidence: Low uncertainty → no penalty. Medium → -0.05. High → -0.15.

---

## 11. World Model Interface

Receives: State, Belief, Regime, Scenarios. Uses for: evidence anchoring, uncertainty identification.

---

## 12. Memory Interface

Receives: Historical similar cases with outcomes. Uses for: historical-match confidence component, alternative scenario reference.

---

## 13. Decision Interface

```json
{
  "explanation_report": {
    "conclusion": "Increase, confidence 0.78",
    "why": ["Expansion+Warming+LowRisk", "Causal foundation confirmed", "72% historical success"],
    "why_not_alternatives": "Hold: lower return. Reduce: inappropriate for regime.",
    "what_to_watch": ["Sentiment > 80", "Leader炸板", "Policy follow-through"],
    "human_review": false
  }
}
```

---

## 14. Human-AI Governance Interface

Auto-escalation triggers: Confidence < 0.60, Risk > 60, Full Exit decisions, Regime change detected, Pattern contradiction, Novel situation (no memory match).

Human override record: original + override + reason + timestamp + expiry.

---

## 15. Engineering Requirement

< 100ms. CPU-friendly. Structured templates. `explanation_generator | evidence_tracer | confidence_decomposer | uncertainty_quantifier | human_review_gate`

---

## 16. Freeze Criteria

Architecture passed. Explanation object complete. Evidence trace mandatory. Confidence decomposed. Alternatives visible. Uncertainty honest. Human review triggers defined. No black-box outputs.

---

## Source References

Reasoning Architecture V2.9.3 + Human-AI Governance V3.0.0 + Constitution V2.8.6 (Principles 4, 9). No original design.

---

## Items Requiring Architect Review

| # | Item |
|---|------|
| 1 | Confidence decomposition weights — confirm? |
| 2 | Auto-escalation thresholds appropriate? |
| 3 | Explanation template: structured enough vs too rigid? |

---

*AQF-T Explainable Reasoning Engine Design V1.0 — ENGINEERING DRAFT*
