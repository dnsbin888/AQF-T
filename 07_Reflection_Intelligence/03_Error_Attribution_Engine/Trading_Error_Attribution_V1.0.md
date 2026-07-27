# AQF-T Trading Error Attribution Engine V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: 07_Reflection_Intelligence / 03_Error_Attribution

---

## 1. Purpose

Attributes outcome deviation to the correct source. Avoids "lost money = bad decision" logic.

## 2. Error Taxonomy

| Error Type | Example | Belongs To |
|-----------|---------|-----------|
| Regime Misclassification | Thought Expansion, was Distribution | World Model |
| Belief Error | Overconfident on trend strength | Belief Engine |
| Timing Error | Entered too early (pre-confirmation) | Strategy Runtime |
| Execution Error | High slippage due to market order | Order Planner |
| External Shock | Unexpected regulation/black swan | None (uncontrollable) |
| Risk Underestimation | Risk scored Low, drawdown was High | Risk Intelligence |

## 3. Attribution Logic

```
IF regime_correct AND belief_correct AND execution_ok AND external_factor:
  → Good Decision, Bad Outcome (external)
  
IF regime_correct AND belief_wrong:
  → Belief Error (not Regime Error)
  
IF regime_wrong (and everything else based on wrong regime):
  → Regime Error (root cause)
```

## 4. Output

```json
{
  "error_attribution": {
    "primary_error": "external_shock",
    "secondary_errors": [],
    "decision_quality": "GOOD",
    "recommendation": "No system change. External event."
  }
}
```
