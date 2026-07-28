# AQF-T Statistical Validation Model V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — V3.1

---

## 1. Five Methods (Evidence Level: A)

**Bootstrap**: Resample returns 1000×. Is performance stable or one lucky run?

**Monte Carlo**: Randomize decisions. Is AQF-T better than random?

**Walk-Forward**: Train on past, test on future. No look-ahead bias.

**Out-of-Sample**: Separate train/validate/test periods. Cover different regimes.

**Calibration Curve**: System says 80% confidence → actual success rate? Perfect calibration: confidence=actual.

## 2. Calibration Output

```json
{
  "module": "Decision_Engine",
  "calibration": [
    { "confidence_bin": "0.7-0.8", "predicted_rate": 0.75, "actual_rate": 0.68, "error": 0.07, "status": "OVERCONFIDENT" },
    { "confidence_bin": "0.6-0.7", "predicted_rate": 0.65, "actual_rate": 0.63, "error": 0.02, "status": "CALIBRATED" }
  ],
  "overall_calibration_error": 0.06
}
```

## 3. Action

Error > 0.10 → recalibrate confidence. Error < 0.05 → well-calibrated. Overconfident → reduce confidence multiplier.
