# AQF-T Knowledge Lifecycle Management Architecture

Version: V1.0.0 | Status: ENGINEERING DRAFT — V3.1 Final | Module: Knowledge_System/Knowledge_Lifecycle
Created: 2026-07-28

---

## Design Evidence

| Item | Value |
|------|-------|
| Core Concept | Knowledge lifecycle governance — from discovery to retirement |
| Evidence Level | A/B (Bayesian updating, concept drift, data lifecycle) + D (AQF-T conditional knowledge) |
| Research ID | R-V3.1-006 |

---

## 1. Purpose

V3.1's final module. Closes the loop: **Learn → Validate → Promote → Decay → Retire.**

Knowledge is NOT truth. Knowledge is a **validated hypothesis with a confidence score and an expiry date.**

## 2. Core Principles

| # | Principle |
|---|-----------|
| P1 | Knowledge is Hypothesis — never permanent truth |
| P2 | Knowledge Must Have Confidence — with sample N, regime, decay |
| P3 | Knowledge Can Die — expired knowledge must stop influencing decisions |

## 3. Seven-State Lifecycle

```
DISCOVERED → VALIDATING → CONFIRMED → ACTIVE → DECAYING → RETIRED → ARCHIVED
```

| State | Meaning | Decision Influence |
|-------|---------|:------------------:|
| DISCOVERED | From Reflection/Failure/Experience | ❌ None |
| VALIDATING | In Validation Framework | ❌ None |
| CONFIRMED | Passed min validation (N>100, consistency OK) | ⚠️ Low weight |
| ACTIVE | Fully validated, Regime-conditional | ✅ Full weight |
| DECAYING | Success rate declining / regime mismatch / stale | ⚠️ Reduced weight |
| RETIRED | No longer used. Kept for research. | ❌ None |
| ARCHIVED | Historical record only | ❌ None |

## 4. Knowledge Decay Engine

`KnowledgeWeight(t) = InitialConfidence × ValidationFactor × TimeDecay × RegimeMatch`

Decay triggers: success rate decline, market regime change, time since last validation > threshold.

## 5. KnowledgeEntity Object

```json
{
  "knowledge_id": "K_F005_LateDayChase",
  "source": "MEM-003_Failure_Library",
  "type": "Pattern",
  "evidence_level": "C",
  "confidence": 0.76,
  "validation_count": 428,
  "applicable_regime": ["High_Emotion", "Climax"],
  "created": "2025-06-15",
  "last_validated": "2026-07-01",
  "decay_factor": 0.94,
  "status": "ACTIVE"
}
```

## 6. Promotion & Retirement

Promotion: Experience→Pattern→Validation(N>100)→Knowledge→Decision Influence (never override rules, C-016).

Retirement: success rate < threshold + regime mismatch + time decay → RETIRED. Preserved for research.

## 7. C-016 Candidate

C-016-1: Knowledge cannot directly modify Core Decision Rules (influence only). C-016-2: Every Knowledge has provenance. C-016-3: Expired Knowledge cannot influence Decision.

## 8. Connection

Reflection→Memory→Calibration→Knowledge Lifecycle→World Model→Decision

---

*V3.1-006. Knowledge Lifecycle. V3.1 Final Module.*
