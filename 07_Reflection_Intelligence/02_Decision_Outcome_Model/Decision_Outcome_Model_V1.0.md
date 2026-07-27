# AQF-T Decision Outcome Model V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: 07_Reflection_Intelligence / 02_Decision_Outcome_Model

---

## 1. DecisionOutcome Object

```json
{
  "outcome_id": "DO_20260728_001",
  "episode_id": "EP_20260728_001",
  "decision_id": "DEC_20260728_093500",

  "decision_context": {
    "action": "ENTER", "confidence": 0.82,
    "regime": "Expansion", "emotion": "Warming", "theme": "AI"
  },

  "expected": { "target_return_pct": 8.0, "holding_days": 5, "max_drawdown_pct": -5.0 },
  "actual": { "return_pct": -3.0, "holding_days": 2, "max_drawdown_pct": -5.0, "exit_reason": "stop_loss" },

  "deviation": { "return_gap_pct": -11.0, "holding_gap_days": -3, "primary_cause": "regulatory_surprise" },

  "attribution": {
    "decision_quality": "GOOD",
    "outcome_quality": "BAD",
    "regime_correct": true, "belief_correct": true,
    "execution_ok": true, "external_factor": "unexpected_regulation"
  },

  "learning": { "what_to_update": null, "confidence_adjustment": null, "pattern_signal": "Good_Decision_Bad_Outcome" }
}
```

## 2. Decision Quality Matrix

| Decision | Outcome | Label | Action |
|----------|---------|-------|--------|
| Good | Good | Reinforce | Pattern confidence + |
| Good | Bad | Accept | Don't degrade (external factor) |
| Bad | Good | **Warn** | Don't reinforce (luck) |
| Bad | Bad | Learn | Pattern confidence − |

## 3. Lifecycle

OPEN(position active) → CLOSED → EVALUATED → ATTRIBUTED → LEARNED → ARCHIVED
