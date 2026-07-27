# AQF-T C-007: Order Execution Boundary

Version: V1.0.0
Status: ✅ FROZEN — Constitution-Level
Date: 2026-07-28
Source: P0-006 Order Planner Design V1.0

---

## Core Definition

**Order Planner = Execution Intelligence. Optimizes execution, not trading decisions.**

---

## MAY

| Rule | Description |
|------|-------------|
| ✅ Generate OrderRequest | From approved PositionAction |
| ✅ Split orders into slices | Reduce market impact |
| ✅ Optimize execution timing | VWAP/TWAP/Limit/Market selection |
| ✅ Manage order lifecycle | Created→Submitted→Ack→Fill→Terminated |
| ✅ Handle partial fills | Recalculate delta, continue or cancel |

---

## SHALL NOT

| Rule | Description |
|------|-------------|
| ❌ Create trading intent | 属于 Decision Intelligence |
| ❌ Change capital allocation | 属于 Portfolio Manager |
| ❌ Override Risk decision | Risk has veto. Cancel on Extreme. |
| ❌ Modify Strategy | 违反 C-004 |
| ❌ Bypass QMT Adapter | 违反 C-003 |
| ❌ Generate market direction | 属于 World Model |

---

## Risk Hierarchy

```
Risk Veto > Order Execution

IF Risk = Extreme during active execution:
  → Cancel ALL pending slices
  → Do NOT submit new orders
  → Report RiskInterrupt
```

---

*AQF-T C-007 Order Execution Boundary — Constitution-Level. FROZEN.*
