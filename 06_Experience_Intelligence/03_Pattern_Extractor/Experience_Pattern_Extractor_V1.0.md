# AQF-T Experience Pattern Extractor V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: 06_Experience_Intelligence / 03_Pattern_Extractor

---

## 1. Purpose

Mines recurring patterns from TradingEpisodes. Answers: "What conditions consistently produce good/bad outcomes?"

## 2. Extraction Pipeline

```
Episodes (N≥30 similar) → Cluster by [Regime+Emotion+Action] → Statistical test → ExperiencePattern
```

## 3. Pattern Object

```json
{
  "pattern_id": "PAT_Expansion_Warming_LeaderEnter",
  "condition": { "regime": "Expansion", "emotion": "Warming", "action": "ENTER", "strategy": "LeaderMomentum" },
  "statistics": { "episodes": 127, "success_rate": 0.78, "avg_return_5d_pct": 5.2, "avg_quality": 0.85 },
  "confidence": 0.82, "status": "active"
}
```

## 4. Pattern Types

- **Success Pattern**: High win rate → reinforce
- **Failure Pattern**: Low win rate → avoid or adjust
- **Execution Pattern**: Quality consistently good/bad → improve order strategy
- **Regime Pattern**: Strategy works in Expansion but fails in Distribution

## 5. Validation

N≥30, p<0.05 vs random, temporal stability check. Weekly batch processing.
