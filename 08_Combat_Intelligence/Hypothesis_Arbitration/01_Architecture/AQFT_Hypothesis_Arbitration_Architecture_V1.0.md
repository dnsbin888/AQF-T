# AQF-T Hypothesis Arbitration Architecture

Version: V1.0.0 | Status: ARCHITECT REVIEW PASSED — Phase 2 Complete V1.2 | Module: 08_Combat_Intelligence
Created: 2026-07-28

---

## Design Evidence

| Item | Value |
|------|-------|
| Core Concept | Evidence-weighted hypothesis fusion (仲裁, not 辩论) |
| Evidence Level | A (Bayesian fusion) + B (multi-source arbitration) |
| Research ID | R-P2-004 |
| Applicable Scope | AQF-T Combat Intelligence Layer |
| Failure Boundary | All hypotheses Unknown → No Decision |
| Original Extension | Narrative Generation + Conflict Matrix (AQF-T D-Level) |

---

## 1. Purpose

P2-004 ≠ Multi-Agent Debate. It is **Cognitive Arbitration** — fusing LimitUp/Opponent/Quant hypotheses into a single, unified DecisionContext.

```
P2-001/002/003 Hypotheses → Arbitration → DecisionContext → Decision Engine
```

Arbitration fuses evidence. It does NOT create new hypotheses (C-014).

## 2. Four-Stage Pipeline

**Stage 1 — Evidence Collection**: Gather all hypotheses → Evidence Pool

**Stage 2 — Consistency Check**: All agree? Partially conflict? All contradict?

**Stage 3 — Conflict Resolution**: Evidence-weighted fusion (A+×0.50 + A×0.30 + B×0.15 + C×0.05). NOT voting.

**Stage 4 — Narrative Generation**: Unified market narrative → DecisionContext

## 3. Conflict Matrix

| Situation | Result |
|-----------|--------|
| All agree | Confidence ↑, Full execution |
| 2 support, 1 oppose | Conservative execution |
| All conflict | WAIT |
| All Unknown | No Decision |

## 4. Output: DecisionContext

OverallConfidence, OverallRisk, SupportingEvidence, ContradictingEvidence, PrimaryNarrative, AlternativeNarratives, RecommendedExecution, ConfidenceCalibration.

## 5. C-014 Candidate

Arbitration may fuse and interpret hypotheses. Shall NOT create new hypotheses without evidence. Shall NOT override Risk Engine.

## 6. Deliverables

```
08_Combat_Intelligence/Hypothesis_Arbitration/
├── 01_Architecture/          ← This document
├── 02_Arbitration_Engine/
├── 03_Conflict_Resolution/
├── 04_Decision_Context/
└── 05_Test_Cases/
```

*Phase 2 Final Module. Completes Combat Intelligence.*
