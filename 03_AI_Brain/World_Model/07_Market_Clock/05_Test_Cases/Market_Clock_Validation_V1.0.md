# AQF-T Market Clock Validation V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: World Model — Market Clock / Test Cases

---

## MC-TEST-001: Same State, Different Time

Input: Regime=Recovery, Emotion=Improving, Liquidity=Rising. Case A: 09:35. Case B: 14:50.

Expected: Different confidence, risk, position bias between A and B.

## MC-TEST-002: Late-Day Chase Prevention

Input: 14:45, Breakout Signal, F005 Active.

Expected: Risk↑, Confidence↓, ENTER blocked or reduced to Prepare.

## MC-TEST-003: Early Leader Confirmation

Input: 09:45, Leader 2-board + Volume Expansion + Emotion Recovery.

Expected: OpenDrive weight boost. ENTER evaluation allowed.

## MC-TEST-004: Phase Transition

Input: 14:29:59→14:30:00. Phase transition Afternoon→ClosePricing.

Expected: Weight drops 0.90→0.70, Risk rises +10%→+20%, without discontinuity.

## MC-TEST-005: Auction Block

Input: 09:20, any signal. Phase=Auction.

Expected: NO EXECUTION. Signal weight=0.
