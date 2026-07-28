# AQF-T Market Replay Engine V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — V3.1

---

## 1. Purpose

Let AQF-T go back in time. Not simple backtesting — full cognitive replay.

```
Historical Market Data → Replay → World Model → Belief → Decision → Outcome → Evaluation
```

## 2. Replay Constraints (Critical)

**NO future information leakage.** AQF-T at time T sees ONLY data available up to T. Each bar processed sequentially.

## 3. ReplayRecord

```json
{
  "replay_id": "REPLAY_20260728_001",
  "period": "2023-01-01_to_2024-12-31",
  "scenario": "Full_Market_Cycle",
  "decision_count": 847,
  "metrics": { "decision_accuracy": 0.68, "regime_accuracy": 0.74, "avg_confidence_calibration_error": 0.09 }
}
```

## 4. What Replay Measures

Not just PnL. It measures: Decision Accuracy, Regime Classification Correctness, Belief Drift, Confidence Calibration Error, Error Attribution Accuracy, Knowledge Improvement Rate.

## 5. vs Traditional Backtest

Traditional: Price→Strategy→Return. AQF-T: Market→Belief→Decision→Action→Outcome→Reflection.
