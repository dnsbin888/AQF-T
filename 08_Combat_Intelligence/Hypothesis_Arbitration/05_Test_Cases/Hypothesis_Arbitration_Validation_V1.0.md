# AQF-T Hypothesis Arbitration Validation V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## ARB-TEST-001: All Agree
Input: Leader(0.81) + Institution(0.72) + Passive(0.75). Expected: consistency HIGH, conflict LOW, Strong BUY, Full ENTER.

## ARB-TEST-002: Mixed — 2 Support, 1 Oppose
Input: Leader(0.81) + Institution(0.72) + Momentum(0.72). Expected: conflict 0.45, Conservative, Half size, TWAP.

## ARB-TEST-003: All Conflict
Input: Leader(0.81) + Distribution(0.68) + Spoofing(0.65). Expected: WAIT. All conflict → No execution.

## ARB-TEST-004: All Unknown
Input: LimitUp(conf<0.50) + Opponent(conf<0.50) + Quant(NONE). Expected: No Decision. Unknown threshold met.

## ARB-TEST-005: Evidence Quality Priority
Input: Leader(C,0.75) + Institution(B,0.60) + Quant(A+,0.55). Expected: A+ hypothesis weight highest despite lower raw confidence. Evidence quality > raw score (MC-010).
