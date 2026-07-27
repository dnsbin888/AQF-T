# AQF-T Participant State Model V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## 1. ParticipantState Object

```json
{
  "timestamp": "2026-07-28T10:00:00",
  "symbol": "SH.603xxx",
  "dominant_participant": "Hot_Money",
  "participants": [
    { "type": "Hot_Money", "confidence": 0.78, "intent": "Relay", "intent_probability": 0.72,
      "holding_style": "Lock_3_5_Days", "expected_action": "Continue_Holding" },
    { "type": "Institution", "confidence": 0.45, "intent": "Accumulating", "intent_probability": 0.55 },
    { "type": "Quant", "confidence": 0.30, "intent": "Intraday_Flip", "intent_probability": 0.60 },
    { "type": "Retail", "confidence": 0.65, "intent": "Chasing", "intent_probability": 0.70 }
  ],
  "opponent_pressure": { "buy_pressure": 65, "sell_pressure": 35, "distribution_probability": 0.25,
                         "continuation_probability": 0.68, "trap_probability": 0.12 }
}
```

## 2. Participant Types

| Type | Typical Size | Speed | Holding Period | Key Behavior |
|------|:-----------:|:-----:|:-------------:|-------------|
| Institution | Large | Slow | Weeks-Months | Build→Hold→Distribute |
| Hot Money | Medium | Fast | 1-5 Days | Launch→Relay→Exit |
| Quant | Variable | Ultra-Fast | Intraday | Mechanical flipping |
| Retail | Small | Late | Variable | Chase/Panic |
| Mixed | — | — | — | Cannot determine |

## 3. Intent States

Accumulating | Holding | Rotating | Distributing | Panic_Selling. Each with intent_probability (never 1.0).
