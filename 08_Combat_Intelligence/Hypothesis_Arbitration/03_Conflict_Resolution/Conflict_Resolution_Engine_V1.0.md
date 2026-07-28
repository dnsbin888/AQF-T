# AQF-T Conflict Resolution Engine V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## Design Evidence

| Item | Value |
|------|-------|
| Core Concept | Evidence-weighted conflict detection + resolution |
| Evidence Level | A (conflict detection theory) + C (A股经验) |

---

## 1. Conflict Matrix

| Scenario | Example | Result |
|----------|---------|--------|
| All Agree | Leader + Institution + Passive | Confidence↑, Full |
| 2 Support, 1 Oppose | Leader + Institution + Momentum | Conservative, Half size |
| 2 Oppose, 1 Support | Leader + Distribution + Spoofing | Reduce position |
| All Conflict | Bearish + Distribution + Spoofing | WAIT |
| All Unknown | All conf<0.50 | No Decision |

## 2. Conflict Score

ConflictScore = 1.0 − ConsistencyScore. HIGH conflict (>0.5) → auto confidence reduction ×0.7.

## 3. Resolution Rules

Conflict but one hypothesis has evidence A+ → A+ hypothesis gets priority (MC-010: higher evidence quality). Conflict and all evidence B/C → automatic conservative bias. Conflict and Risk HIGH → WAIT.

## 4. Examples

**Leader(0.81) + Institution(0.72) + Passive(0.75)**: All agree → consistency 0.88 → Strong. Full ENTER.

**Leader(0.81) + Distribution(0.68) + Momentum(0.72)**: Mixed → conflict 0.45 → Conservative. Half size, TWAP.
