# AQF-T Execution Event Model

Version: V1.0.0
Status: ENGINEERING DRAFT — Phase 1
Module: 05_Observation_Intelligence / 02_Execution_Event
Created: 2026-07-28

---

## 1. Purpose

Records the complete lifecycle of every order: what was intended, what was sent, what actually happened.

## 2. ExecutionRecord

```json
{
  "execution_id": "EXEC_20260728_100000",
  "decision_id": "DEC_20260728_093500",
  "plan_id": "EP_20260728_100000",
  "order_id": "ORD_20260728_100000_S1",
  "symbol": "SH.603xxx",

  "intended": { "quantity": 10000, "price_limit": 26.50, "order_type": "LIMIT", "time_window_s": 300 },
  "actual": { "filled_quantity": 10000, "avg_price": 26.45, "slippage_bps": -1.9, "latency_ms": 15, "fills": 3 },
  "timeline": [
    { "time": "10:00:00.000", "event": "SUBMITTED" },
    { "time": "10:00:00.015", "event": "ACKNOWLEDGED" },
    { "time": "10:00:02.340", "event": "PARTIAL_FILLED", "detail": { "qty": 5000, "px": 26.44 } },
    { "time": "10:00:02.890", "event": "PARTIAL_FILLED", "detail": { "qty": 3000, "px": 26.46 } },
    { "time": "10:00:04.120", "event": "FILLED", "detail": { "qty": 2000, "px": 26.45 } }
  ],
  "context": { "regime_at_execution": "Expansion", "risk_at_execution": "Low" }
}
```

## 3. Lifecycle

SUBMITTED → ACKNOWLEDGED → PARTIAL_FILLED → FILLED | REJECTED | CANCELLED | TIMEOUT

## 4. Storage

Every ExecutionRecord → Observation Store → Memory System (Episode)
