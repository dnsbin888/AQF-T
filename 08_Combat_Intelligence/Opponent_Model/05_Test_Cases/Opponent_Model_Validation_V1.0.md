# AQF-T Opponent Model Validation V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## OP-TEST-001: Institution Detection
Input: Large blocks, steady all-day, gentle price impact, building over days. Expected: Institution.confidence>0.70, intent=Accumulating, sell_pressure low.

## OP-TEST-002: Hot Money Exit Signal
Input: 09:35 burst, sharp price, holding period ending, volume spike. Expected: Hot_Money.confidence>0.70, intent=Distributing, distribution_probability high.

## OP-TEST-003: Quant Active Detection
Input: Frequent small orders, symmetric buy/sell, >50% cancel rate, intraday only. Expected: Quant.confidence>0.70, trap_probability elevated.

## OP-TEST-004: Retail FOMO
Input: Tiny scattered orders, lagged entry after price already moved +5%, chasing pattern. Expected: Retail.confidence>0.70, intent=Chasing. Decision: conf−0.10, risk+10%.

## OP-TEST-005: Low Confidence → Ignore
Input: Mixed signals, dominant_participant confidence < 0.60. Expected: Opponent signal weight → 0. Decision ignores Opponent.
