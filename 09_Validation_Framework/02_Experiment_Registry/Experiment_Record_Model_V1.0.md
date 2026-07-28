# AQF-T Experiment Record Model V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — V3.1

---

## 1. ExperimentRecord

```json
{
  "experiment_id": "EXP_20260728_001",
  "hypothesis": "换手板比一字板更适合作为龙头候选",
  "target_module": "LimitUp_Intelligence",
  "baseline": "Traditional_Breakout_Strategy",
  "method": "Historical_Replay_2018_2026",
  "dataset": "A_Share_LimitUp_Data",
  "metric": { "win_rate": 0.62, "sharpe": 1.45, "max_drawdown": -0.18 },
  "baseline_metric": { "win_rate": 0.48, "sharpe": 0.82, "max_drawdown": -0.32 },
  "result": "SUPPORTED",
  "confidence": 0.85,
  "decision": "KEEP_AND_ENHANCE"
}
```

## 2. Five Questions (MC-003)

Every experiment answers: What to validate? Why validate? Based on what? How to validate? When does it fail?

## 3. Decision Outcomes

SUPPORTED → Knowledge confidence ↑ | REJECTED → Knowledge confidence ↓ | INCONCLUSIVE → More data needed

## 4. Lifecycle

HYPOTHESIS → REGISTERED → RUNNING → ANALYZED → DECIDED → ARCHIVED
