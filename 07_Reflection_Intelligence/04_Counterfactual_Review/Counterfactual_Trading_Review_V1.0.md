# AQF-T Counterfactual Trading Review V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: 07_Reflection_Intelligence / 04_Counterfactual_Review

---

## 1. Purpose

Post-trade "what if" analysis. Connects to V2.9 Counterfactual Engine. Answers: "What could I have done differently?"

## 2. Counterfactual Scenarios

```json
{
  "review_id": "CFR_20260728_001",
  "actual": { "entry": "09:45", "exit": "14:30_stop", "return": -3.0, "position_pct": 30 },
  
  "alternatives": [
    { "scenario": "Exit at 14:00", "return": -1.5, "reason": "Captured intraday high before crash" },
    { "scenario": "Wait for confirmation", "return": 0, "reason": "Wouldn't have entered without 2-board confirm" },
    { "scenario": "Half position (15%)", "return": -1.5, "reason": "Same loss%, half capital at risk" }
  ],
  
  "best_alternative": { "action": "Half position", "return": -1.5, "lesson": "Reduce initial size when confidence < 0.85" }
}
```

## 3. Connection

Counterfactual Review → TradingEpisode.reflection → Pattern Extractor → Knowledge Router

## 4. Limitation

Reviews are proposals. Human governs what becomes knowledge (C-002).
