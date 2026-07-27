# AQF-T QMT Adapter Interface Design

Version: V1.0.0
Status: ENGINEERING DRAFT — Awaiting Architect Review
Phase: V3.0 Implementation Era — Phase 0 Foundation
Module: 04_Execution_Intelligence / 06_QMT
Created: 2026-07-28

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_QMT_Adapter_Interface_Design_V1.0.md |
| Module | Execution Intelligence — QMT Adapter |
| System | AQF-T Autonomous Quant Intelligence Framework |
| Version | V1.0.0 |
| Parent | AQFT_Execution_Intelligence_Architecture_V1.0 |
| Upstream | Order Planner V1.0 ✅ |
| Downstream | MiniQMT (xtdata + xttrader) → Broker |
| Constitutions | C-001, C-002, C-003, C-007, C-008(candidate) |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |

---

## 1. Purpose & Position

### 1.1 What QMT Adapter Does

QMT Adapter 是 AQF-T 的 **唯一执行翻译层（Execution Translation Layer）**。

它是 AQF-T Intelligence 与真实市场之间的**最后一道边界**。

| AQF-T Brain | QMT Adapter |
|-------------|-------------|
| WHAT to trade | HOW to translate to QMT |
| WHY to trade | WHEN to send |
| Intelligence | Execution |

### 1.2 Architecture Position

```
Order Planner → QMT ADAPTER → xttrader → Broker → Exchange
                    │
                    ├── xtdata (行情读取 — 唯一下行通道)
                    └── ExecutionReport → Memory
```

### 1.3 Core Definition

```
QMT Adapter = Execution Translation Layer
QMT Adapter ≠ Strategy Engine
QMT Adapter ≠ Signal Generator
QMT Adapter ≠ Risk Engine
QMT Adapter ≠ Position Controller
QMT Adapter ≠ Second Brain
```

---

## 2. QMT Adapter Boundary (C-008 Candidate)

```
C-008: Execution Adapter Boundary

QMT Adapter SHALL:
  ✅ Translate OrderRequest → QMT order_stock()
  ✅ Execute only Risk-approved orders
  ✅ Return ExecutionReport (facts, not opinions)
  ✅ Query account/position state
  ✅ Monitor connection health
  ✅ Handle connection recovery

QMT Adapter SHALL NOT:
  ❌ Create trading intent
  ❌ Modify DecisionIntent
  ❌ Override Risk Runtime
  ❌ Change Portfolio Allocation
  ❌ Generate strategy signals
  ❌ Judge market conditions
  ❌ Bypass Intelligence Chain
```

**[NEEDS ARCHITECT REVIEW]** — C-008 promotion to formal Constitution.

---

## 3. Four Core Responsibilities

### 3.1 Order Translation

```
AQF-T OrderRequest → QMT Adapter → xttrader.order_stock()

Example:
  OrderRequest { symbol: "600519.SH", side: "BUY", quantity: 100, price: 1850.00 }
  → xttrader.order_stock(code="600519.SH", order_type=<xtconstant.STOCK_BUY>, 
                         price=1850.00, volume=100, strategy_name="AQFT", remark="DEC_xxx")
```

### 3.2 Execution Communication

```
Send → Acknowledge → Fill/Cancel/Reject → Report

States tracked:
  PENDING → SUBMITTED → ACKNOWLEDGED → PARTIAL_FILLED → FILLED
                                     → REJECTED
                                     → CANCELLED
```

### 3.3 Account Observation

```
Query broker state:
  - Account cash / available_cash / market_value / total_asset
  - Positions: symbol, quantity, avg_cost, market_price, unrealized_pnl
  - Orders: pending, filled, cancelled

Return: BrokerAccountSnapshot (facts only, no interpretation)
```

### 3.4 Failure Handling

| Failure | QMT Action | AQF-T Notification |
|---------|-----------|-------------------|
| Connection lost | Auto-reconnect every 30s | ExecutionUnavailable |
| Order rejected | Capture reject_reason | ExecutionReport(REJECTED) |
| Partial fill | Report filled quantity | Position Engine recalculates |
| Timeout (>30s no ack) | Query order status | ExecutionReport(TIMEOUT) |
| xttrader crash | Reinitialize session | ExecutionUnavailable → Alert |

---

## 4. Five Core Objects

### 4.1 QMTConnectionState

```json
{
  "status": "CONNECTED",
  "last_heartbeat": "2026-07-28T10:00:00",
  "session_id": "QMT_SES_20260728",
  "reconnect_attempts": 0,
  "xtdata_connected": true,
  "xttrader_connected": true
}
```

States: INIT → CONNECTED → DEGRADED(one channel down) → DISCONNECTED → RECOVERING

### 4.2 BrokerAccountSnapshot

```json
{
  "account_id": "AQFT_PRIMARY",
  "timestamp": "2026-07-28T10:00:00",
  "cash": 450000.00,
  "available_cash": 380000.00,
  "frozen_cash": 70000.00,
  "market_value": 550000.00,
  "total_asset": 1000000.00,
  "positions": [
    {
      "symbol": "SH.603xxx",
      "quantity": 10000,
      "avg_cost": 25.50,
      "market_price": 26.20,
      "unrealized_pnl_pct": 2.75
    }
  ]
}
```

### 4.3 QMTOrderCommand (AQF-T → QMT)

```json
{
  "order_id": "ORD_20260728_100000_S1",
  "symbol": "SH.600519",
  "side": "BUY",
  "quantity": 100,
  "price": 1850.00,
  "order_type": "LIMIT",
  "time_in_force": "DAY",
  "strategy_name": "AQFT",
  "remark": "DEC_20260728_093500_S1"
}
```

### 4.4 QMTExecutionEvent (QMT → AQF-T)

```json
{
  "order_id": "ORD_20260728_100000_S1",
  "status": "FILLED",
  "filled_quantity": 100,
  "filled_price": 1849.50,
  "reject_reason": null,
  "timestamp": "2026-07-28T10:00:03"
}
```

### 4.5 ExecutionReport (To Intelligence Layer)

```json
{
  "order_id": "ORD_20260728_100000_S1",
  "plan_id": "EP_20260728_100000",
  "decision_id": "DEC_20260728_093500",
  "status": "FILLED",
  "filled_quantity": 100,
  "average_price": 1849.50,
  "slippage_bps": -0.3,
  "latency_ms": 15,
  "timestamp": "2026-07-28T10:00:03",
  "version": "V1.0"
}
```

---

## 5. Interface Contract

### 5.1 Order Submission

```python
def submit_order(order: QMTOrderCommand) -> OrderAck:
    """
    Translate AQF-T OrderRequest → QMT xttrader.
    Returns immediately with ack (order_id + status).
    Actual fill delivered via callback.
    """
```

### 5.2 Order Cancellation

```python
def cancel_order(order_id: str) -> bool:
    """Cancel pending order. Returns True if cancelled."""
```

### 5.3 Status Query

```python
def query_order(order_id: str) -> QMTExecutionEvent: ...
def query_position(symbol: str) -> Position: ...
def query_account() -> BrokerAccountSnapshot: ...
```

### 5.4 Callback Registration

```python
def on_fill(callback: Callable[[ExecutionReport], None]): ...
def on_order_status(callback: Callable[[QMTExecutionEvent], None]): ...
def on_connection_change(callback: Callable[[QMTConnectionState], None]): ...
```

---

## 6. Lifecycle Management

```
INIT        → Load config, validate credentials
              │
CONNECTING  → Login xtdata + xttrader
              │
CONNECTED   → Ready. Accept OrderRequests.
              │
              ├── DISCONNECTED → Auto-reconnect (30s intervals)
              │                   After 5min: Alert human
              │
              └── SHUTDOWN → Cancel all pending. Logout. Flush.
```

---

## 7. Security Constraints

| Rule | Description |
|------|-------------|
| No credential storage in code | Use config file with OS-level permissions |
| One session per account | Prevent duplicate orders |
| Order audit log | Every order → timestamped log entry |
| Position reconciliation | Daily: compare AQF-T vs QMT positions. Mismatch → block. |
| Risk hard gate | Account-level position limit enforced at QMT level |

---

## 8. Constitution Compliance

| Constitution | Status | Evidence |
|-------------|:------:|----------|
| C-001: Intelligence Ownership | ✅ | Translates orders. Zero trading intent. |
| C-002: Immutable Core | ✅ | Reads account state. Never writes S(t)/B(t)/R(t). |
| C-003: QMT Boundary | ✅ | Only module that calls xttrader. Only module that calls xtdata. |
| C-007: Order Execution Boundary | ✅ | Receives OrderRequest from Order Planner. Does not modify. |
| C-008 (candidate) | ✅ | All SHALL/SHALL NOT embedded in §2 |

---

## 9. Testing Requirement

- CONNECTED → submit_order → FILLED → ExecutionReport → Memory
- DISCONNECTED → auto-reconnect → CONNECTED
- REJECTED order → ExecutionReport with reject_reason
- Partial fill → correct filled_quantity in report
- Position mismatch detected → reconciliation triggered

---

## 10. Freeze Criteria

1. 5 core objects defined with lifecycle
2. 4 responsibilities clearly bounded
3. C-001/C-002/C-003/C-007 verified
4. C-008 candidate defined
5. Connection lifecycle: INIT→CONNECTED→DISCONNECTED→RECOVERING
6. Failure scenarios handled (disconnect, reject, partial, timeout)
7. Zero intelligence: no signal, no strategy, no risk, no decision
8. Security: credential isolation, audit log, reconciliation

---

## Source References

| Section | Source |
|---------|--------|
| 1-2 | Architect P0-007 Specification |
| 3-4 | QMT Integration Principle V1.0 (C-003) |
| 5-6 | Order Planner V1.0 + MiniQMT API |
| 7-8 | C-001/C-002/C-003/C-007 |
| 9-10 | V3.0 Requirements |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | C-008 promotion to formal Constitution — approve? | §2 |
| 2 | Auto-reconnect: 30s interval → 5min human alert — appropriate? | §6 |
| 3 | Position reconciliation frequency: daily or continuous? | §7 |
| 4 | xtdata for market data: QMT Adapter or separate Data Adapter? | §1 |

---

*AQF-T QMT Adapter Interface Design V1.0 — ENGINEERING DRAFT*  
*V3.0 Phase 0 — Final Module. Execution Translation Layer. Zero Intelligence.*  
*AQF-T owns intelligence. QMT owns execution.*  
*No original design. All content from Architect specifications.*
