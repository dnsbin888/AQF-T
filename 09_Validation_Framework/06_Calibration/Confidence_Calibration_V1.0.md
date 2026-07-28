# AQF-T Confidence Calibration V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — V3.1

---

## 1. Purpose (MC-010 aligned)

System says Confidence=0.82. Does that actually mean 82% success rate?

## 2. Calibration Pipeline

```
Decision + Confidence → Record actual outcome → Compare predicted vs actual → Calibrate
```

## 3. Knowledge Confidence Lifecycle

Initial Confidence (design estimate) → Validation Result (historical data) → Updated Confidence (calibrated). Well-calibrated → increase weight in Decision. Overconfident → reduce weight + flag.

## 4. Connection to Memory

Calibrated confidence → Knowledge Memory updates. Under-calibrated confidence → Pattern flagged for review. Well-calibrated → Knowledge promoted.

## 5. Constitution

C-009: Calibration adjusts confidence weights. Never modifies Decision Rules. MC-010: Validation overrides initial design estimates.
