# AQF-T Reflection Knowledge Interface V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: 07_Reflection_Intelligence / 05_Knowledge_Update_Interface

---

## 1. Purpose

Routes reflection outputs to Experience Intelligence (P1-002). Bridge between "what we learned" and "what the system remembers."

## 2. LearningProposal Object

```json
{
  "proposal_id": "LP_20260728_001",
  "source_episodes": ["EP_20260728_001", "EP_20260715_003", "EP_20260710_007"],
  "failure_type": "Regime_Misclassification",
  "pattern_evidence": "3 episodes: Expansion signal followed by Distribution within 2 days",
  "confidence": 0.72,
  "suggested_update": "Increase Regime transition sensitivity when Volume declines + Sentiment peaks",
  "target_module": "World_Model_Regime_Engine",
  "human_approval": "pending"
}
```

## 3. Routing

| Reflection Output | → Destination |
|-------------------|---------------|
| DecisionOutcome | TradingEpisode (P1-002) |
| ErrorAttribution | FailurePatternLibrary (MEM-003) |
| CounterfactualReview | Episode.reflection field |
| LearningProposal | Knowledge Router (P1-002) → Evolution |

## 4. Constitution

C-002: Proposals only. Human approves. Never auto-modify Immutable Core. C-009 candidate: Reflection may update Knowledge, may NOT directly modify Decision Logic.
