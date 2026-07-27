# AQF-T Participant Behavior Inference Engine V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## 1. Inference Model

Behavior-based, not identity-based. Infers participant type from observable patterns, not from seat database.

## 2. Observable Signals

| Signal | Institution | Hot Money | Quant | Retail |
|--------|:----------:|:---------:|:----:|:------:|
| Order Size | Large blocks | Medium chunks | Small frequent | Tiny scattered |
| Speed | Slow accumulation | Fast concentrated | Ultra-fast | Lagged |
| Time Pattern | All-day steady | 09:35-10:30 burst | Continuous | Late session |
| Impact on Price | Gentle | Sharp | Reversal-prone | Follow-through weak |
| Holding Signal | Position building over days | Lock-up 3-5 days | No overnight | FOMO entry |

## 3. Intent Probability

P(Intent|Signals) = behavior_match × 0.35 + timing_match × 0.25 + size_match × 0.25 + consistency × 0.15. Output always probability, never certainty.

## 4. OpponentPressure Score

Pressure = buy_pressure − sell_pressure, normalized to 0-100. Distribution probability from holding period mismatch + volume profile. Trap probability from divergence between price direction and participant intent.
