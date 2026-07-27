# AQF-T Session Phase Model V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: World Model — Market Clock / Session Phase

---

## 1. SessionPhaseState

```json
{
  "trading_date": "2026-07-28",
  "timestamp": "14:52:00",
  "session_phase": "ClosePricing",
  "minutes_from_open": 322,
  "minutes_to_close": 8,
  "market_behavior": "Tail_Pricing",
  "liquidity_profile": "Declining",
  "volatility_profile": "Elevated",
  "signal_weight": 0.70,
  "risk_modifier": 0.20,
  "historical_probability": { "tail_reversal": 0.32, "breakout_reliable": 0.45 }
}
```

## 2. Five Phases

| Phase | Time | Behavior | Signal Wt | Risk Δ | Execution |
|-------|------|----------|:---------:|:------:|:---------:|
| Auction | 09:15-25 | 预期形成 | 0.00 | — | ❌ Blocked |
| OpenDrive | 09:30-10:00 | 方向确认 | 1.20 | 0% | ✅ Max signal |
| MorningTrend | 10:00-11:30 | 趋势验证 | 1.00 | +5% | ✅ Normal |
| Afternoon | 13:00-14:30 | 资金重选 | 0.90 | +10% | ✅ Conservative |
| ClosePricing | 14:30-15:00 | 次日定价 | 0.70 | +20% | ⚠️ Restricted |

## 3. Phase Transitions

Auction→OpenDrive(09:25) | OpenDrive→MorningTrend(10:00) | MorningTrend→Afternoon(11:30→13:00 lunch) | Afternoon→ClosePricing(14:30) | ClosePricing→Closed(15:00)
