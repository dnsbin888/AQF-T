# AQF-T C-006: Position Authority Boundary

Version: V1.0.0
Status: ✅ FROZEN — Constitution-Level
Date: 2026-07-28
Source: P0-005 Position Engine Design V1.0

---

## Core Definition

**Position Engine understands holding. It does not create trading.**

---

## MAY

| Rule | Description |
|------|-------------|
| ✅ Observe position state | Track quantity, cost, PnL |
| ✅ Evaluate position health | Trend/Emotion/Liquidity/Risk scoring |
| ✅ Generate position recommendations | Maintain/AddCandidate/ReduceCandidate/ExitCandidate |
| ✅ Track lifecycle events | Entry/Add/Reduce/Exit → Memory |

---

## SHALL NOT

| Rule | Description |
|------|-------------|
| ❌ Create trading intention | 属于 Decision Intelligence |
| ❌ Modify DecisionIntent | 违反 C-001 |
| ❌ Override Risk Runtime | Risk has veto authority |
| ❌ Directly submit orders | 违反 C-003 |
| ❌ Modify Immutable Core | 违反 C-002 |
| ❌ Generate market direction | 属于 World Model |

---

## Core Principle

**Position Engine proposes. Risk Runtime disposes.**

---

*AQF-T C-006 Position Authority Boundary — Constitution-Level. FROZEN.*
