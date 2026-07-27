# AQF-T Execution Drift Detection

Version: V1.0.0
Status: ENGINEERING DRAFT — Phase 1
Module: 05_Observation_Intelligence / 04_Drift_Detection
Created: 2026-07-28

---

## 1. Purpose

Detects when actual execution deviates from the ExecutionPlan. Answers: "Did reality match the plan?"

## 2. Drift Types

| Type | Check | Threshold |
|------|-------|:---------:|
| Quantity Drift | `|filled - intended| / intended` | > 20% → Alert |
| Price Drift | `|avg_price - limit_price| / limit_price` | > 1% → Alert |
| Timing Drift | `actual_duration - planned_duration` | > 2× planned → Alert |
| Completion Drift | partial fill after timeout | → Alert |

## 3. DriftAlert

```json
{
  "execution_id": "EXEC_20260728_100000",
  "drift_detected": true,
  "drift_type": "Quantity_Drift",
  "intended_quantity": 10000, "actual_quantity": 3500,
  "drift_pct": 65.0,
  "likely_cause": "Liquidity_insufficient",
  "recommendation": "Position Engine recalculate delta"
}
```

## 4. Handling

DriftAlert → Position Engine (recalculate) + Risk Runtime (check if safe) + Memory (record pattern). Drift Detection does NOT auto-correct — it notifies.
