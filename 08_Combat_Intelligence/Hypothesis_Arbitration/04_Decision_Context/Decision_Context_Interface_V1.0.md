# AQF-T Decision Context Interface V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## Design Evidence

| Item | Value |
|------|-------|
| Core Concept | Unified DecisionContext — single input to Decision Engine |
| Evidence Level | B (industry: unified decision interfaces) |

---

## 1. DecisionContext Object

```json
{
  "context_id": "DC_20260728_100000",
  "overall_confidence": 0.77,
  "overall_risk": 0.30,
  "primary_narrative": "Recovery + Leader confirmed + Institution accumulating + Passive liquidity → Favorable",
  "alternative_narratives": ["Quant active but passive — monitoring needed"],
  "supporting_evidence": ["LimitUp: LeaderCandidate(0.81)", "Opponent: Institution(0.72)", "Quant: Passive(0.75)"],
  "contradicting_evidence": [],
  "conflict_score": 0.12,
  "unknown_ratio": 0.00,
  "recommended_execution": "Full_ENTER_LIMIT",
  "confidence_calibration": { "raw": 0.82, "adjusted": 0.77, "adjustments": ["conflict_penalty: −0.00", "evidence_weight: +0.05"] }
}
```

## 2. Decision Engine Upgrade

`Before: Decision(S,B,R,Clock)` → `After: Decision(DecisionContext)` — DecisionContext is the SINGLE unified input. Decision Engine no longer reads P2-001/002/003 directly.

## 3. C-014

Arbitration may fuse and interpret hypotheses. Shall NOT create new hypotheses without evidence. Shall NOT override Risk Engine.
