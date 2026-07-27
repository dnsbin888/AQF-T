# AQF-T Experience Knowledge Router V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: 06_Experience_Intelligence / 04_Knowledge_Router

---

## 1. Purpose

Promotes validated ExperiencePatterns to Knowledge. Not all patterns qualify.

## 2. Promotion Criteria

| Criterion | Threshold |
|-----------|:---------:|
| Sample size | N ≥ 100 |
| Confidence | ≥ 0.80 |
| Cross-regime validated | At least 2 regimes |
| Temporal stability | Test/Train ≥ 0.85 |
| No recent contradiction | 0 contradictions in 90 days |

## 3. KnowledgeCandidate

```json
{
  "candidate_id": "KC_20260728_001",
  "pattern_id": "PAT_Expansion_Warming_LeaderEnter",
  "promotion_ready": true,
  "knowledge": "In Expansion+Warming, LeaderMomentum ENTER succeeds 78% with avg +5.2% over 5d",
  "limitations": "Valid only when Risk<60. Fails in Distribution.",
  "requires_human_approval": false
}
```

## 4. Demotion

Knowledge contradicted by 3+ recent episodes → demoted back to Pattern for re-evaluation.

## 5. Governance

Knowledge updates are **Proposals**. Evolution System evaluates. Human approves for deployment (C-002).
