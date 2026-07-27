# AQF-T C-008: QMT Adapter Authority Boundary

Version: V1.0.0
Status: ✅ FROZEN — Constitution-Level
Date: 2026-07-28
Source: P0-007 QMT Adapter Interface Design V1.0

---

## Core Definition

**QMT Adapter = Execution Translation Layer. Translates intent to action. Zero intelligence.**

---

## SHALL

| Rule | Description |
|------|-------------|
| ✅ Receive OrderCommand | From Order Planner |
| ✅ Translate to QMT API | xttrader.order_stock() |
| ✅ Return ExecutionEvent | Facts only, no interpretation |
| ✅ Query account/position | BrokerAccountSnapshot |
| ✅ Monitor connection health | QMTConnectionState |
| ✅ Handle connection recovery | Auto-reconnect 30s, alert 5min |

---

## SHALL NOT

| Rule | Description |
|------|-------------|
| ❌ Generate trading signal | 属于 AI Brain |
| ❌ Modify DecisionIntent | 违反 C-001 |
| ❌ Adjust position target | 属于 Portfolio Manager |
| ❌ Override Risk | Risk has veto authority |
| ❌ Create strategy | 违反 C-004 |
| ❌ Change order objective | 属于 Order Planner |

---

## Risk Hierarchy

```
Risk Runtime veto > QMT Adapter execution.
IF Risk=Extreme during active execution:
  → Cancel pending orders
  → Report ExecutionInterrupt
```

---

*AQF-T C-008 QMT Adapter Boundary — Constitution-Level. FROZEN.*
