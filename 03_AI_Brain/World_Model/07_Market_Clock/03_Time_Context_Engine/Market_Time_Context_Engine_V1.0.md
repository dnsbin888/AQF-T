# AQF-T Market Time Context Engine V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: World Model — Market Clock / Time Context Engine

---

## 1. Purpose

Computes the temporal context for any given market moment. Answers: "Given this time of day, what should I know about this signal?"

## 2. MarketClockContext Output

```json
{
  "session_phase": "OpenDrive",
  "minutes_from_open": 5,
  "liquidity_state": "Peak",
  "volatility_state": "Elevated_Declining",
  "historical_behavior": {
    "breakout_reliability": 0.78,
    "false_signal_probability": 0.12,
    "avg_volume_profile": "Highest in first 30min"
  },
  "adjustments": { "confidence": 0.10, "risk": 0.00, "position_bias": "Full" }
}
```

## 3. Phase-Aware Historical Statistics

Each phase maintains independent stats: breakout reliability, false signal rate, avg volume profile, reversal probability. These feed into MarketClockContext and update over time via Experience feedback.

## 4. Failure Pattern Integration

```
ClosePricing + F005(Late-Day Chase) → risk_modifier +0.20, signal_weight ×0.70
OpenDrive + F001(Fake Breakout) → require 2-bar confirmation before weight boost
```
