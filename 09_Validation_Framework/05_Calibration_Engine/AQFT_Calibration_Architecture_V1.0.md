# AQF-T Calibration Engine Architecture V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — V3.1 | Module: 09_Validation_Framework/05_Calibration
Created: 2026-07-28

---

## Design Evidence

| Item | Value |
|------|-------|
| Core Concept | Statistical calibration of confidence to probability |
| Evidence Level | **A+** (Guo et al. Calibration, Bayesian Decision Theory, Platt Scaling) |
| Research ID | R-V3.1-005 |
| Applicable Scope | All AQF-T confidence outputs |
| Failure Boundary | Regime shift — recalibration needed on structural market change |

---

## 1. Purpose

**Confidence ≠ Probability.** System says 80%. Does that mean ~80% success? Calibration Engine transforms "AI confidence" into "statistically verified probability."

## 2. Core Principle (C-015 Candidate)

Confidence is prediction reliability, NOT trading profit prediction. Must separate: Prediction Accuracy ≠ Trading Profit.

## 3. Calibration Pipeline

```
Confidence Output → Outcome Matching → Calibration Analysis → Correction → Calibrated Confidence
```

**Stage 1 — Collect**: All module predictions (LimitUp, Opponent, Quant, Arbitration, Decision).

**Stage 2 — Match**: Prediction vs actual outcome.

**Stage 3 — Analyze**: Reliability Diagram, Brier Score, Expected Calibration Error (ECE).

**Stage 4 — Correct**: Raw confidence → calibration function → calibrated confidence.

## 4. Buy Before Build — Four Methods (Evidence A+)

| Method | Evidence | Best For |
|--------|:------:|----------|
| Platt Scaling | A | Binary classification |
| Isotonic Regression | A | Non-parametric, non-linear markets |
| Bayesian Calibration | A+ | AQF-T World Model integration |
| Temperature Scaling | A | Deep learning model calibration |

**Phase 1 recommendation: Isotonic + Bayesian.** Do NOT invent calibration algorithms.

## 5. Core Objects

**ConfidenceRecord**: prediction, confidence_score, actual_event, outcome.

**CalibrationState**: raw_confidence, calibrated_confidence, historical_accuracy, sample_size, confidence_interval, reliability_score.

## 6. Decision Impact

Before: "Confidence 82%" → After: "Raw 82%, Historical 71% (386 samples), ECE 0.06, Adjusted 74%, Reliability HIGH"

## 7. Connection

LimitUp/Opponent/Quant → Calibration → Reflection (P1-003) → Knowledge Update (C-009/MC-010).

## 8. Deliverables

```
09_Validation_Framework/05_Calibration_Engine/
├── 01_Architecture/  ← This document
├── 02_Confidence_Model/
├── 03_Calibration_Method/
├── 04_Decision_Interface/
└── 05_Test_Cases/
```

*V3.1-005. From AI judgment to scientific measurement.*
