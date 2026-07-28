# AQF-T Hypothesis Arbitration Engine V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## Design Evidence

| Item | Value |
|------|-------|
| Core Concept | Evidence-weighted fusion (not majority voting) |
| Evidence Level | A (Bayesian evidence combination) |
| Failure Boundary | All Unknown → No Decision |

---

## 1. Evidence Pool

```json
{
  "arbitration_id": "ARB_20260728_100000",
  "hypotheses": [
    { "source": "P2-001_LimitUp", "type": "LeaderCandidate", "conf": 0.81, "evidence_level": "C", "weight": 0.15 },
    { "source": "P2-002_Opponent", "type": "Institution_Accumulating", "conf": 0.72, "evidence_level": "B", "weight": 0.30 },
    { "source": "P2-003_Quant", "type": "Passive_Liquidity", "conf": 0.75, "evidence_level": "A", "weight": 0.50 }
  ],
  "consistency_score": 0.88,
  "conflict_score": 0.12
}
```

## 2. Fusion Formula

```
OverallConfidence = Σ(Hypothesis_i.conf × EvidenceWeight_i) / Σ(EvidenceWeight_i)

EvidenceWeight: A+ = 0.50, A = 0.30, B = 0.15, C = 0.05
```

NOT voting. Evidence quality determines influence.

## 3. Consistency Check

All hypotheses aligned (direction consistent) → consistency_score HIGH, conflict LOW. Mixed directions → consistency MEDIUM. Opposing directions → consistency LOW, conflict HIGH → conservative bias.

## 4. Unknown Handling

Any hypothesis with confidence < 0.50 → marked Unknown. All Unknown → No Decision. No forced classification.
