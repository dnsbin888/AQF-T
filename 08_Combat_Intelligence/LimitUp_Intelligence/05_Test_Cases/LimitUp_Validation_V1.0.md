# AQF-T Limit-Up Validation V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## LU-TEST-001: 换手板识别
Input: 09:45, 首次封板, 换手8.5%, 封单0.85, 0次炸板, OpenDrive. Expected: BoardType=换手板, conf+0.10, LeaderCandidate.

## LU-TEST-002: 烂板警告
Input: 封单<0.60, 炸板2次, 换手>20%. Expected: BoardType=烂板, Risk HIGH, conf−0.20, Avoid.

## LU-TEST-003: 回封板时间差异
Case A: 10:00回封. Case B: 14:50回封. Expected: A conf > B conf, A risk < B risk.

## LU-TEST-004: 天地板
Input: 涨停→跌停. Expected: Risk EXTREME, Exit immediate.

## LU-TEST-005: F006激活
Input: Mania regime + 高位板(≥7) + SealDecay. Expected: F006 active, conf−0.20, risk+15, 仓位减半.
