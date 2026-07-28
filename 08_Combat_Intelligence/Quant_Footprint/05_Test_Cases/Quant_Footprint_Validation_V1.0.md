# AQF-T Quant Footprint Validation V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## QF-TEST-001: Momentum Ignition Detection
Input: cancel_ratio 0.62, small_burst orders, bid_ask symmetry 0.75, holding<500ms. Expected: F2 HIGH, conf−0.08, TWAP.

## QF-TEST-002: Passive Liquidity (Safe)
Input: 双边挂单稳定, 点差小, 撤单率<10%. Expected: F1 HIGH, Risk↓, LIMIT.

## QF-TEST-003: Spoofing-like Hypothesis
Input: 挂单-快速撤单模式, 诱导成交. Expected: F4 HIGH, conf−0.15, WAIT. Output uses "consistent with" language (never "this is spoofing").

## QF-TEST-004: No L2 Data
Input: L2 unavailable. Expected: activity=NONE, footprint ignored.

## QF-TEST-005: Opponent + Footprint Fusion
Input: Institution.conf=0.82 + Footprint=DOMINANT(0.91). Expected: conf−0.05, risk+10%. Recognition that institution signal may be confounded by algo dominance.
