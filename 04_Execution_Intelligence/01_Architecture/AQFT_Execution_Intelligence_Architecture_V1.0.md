# AQF-T Execution Intelligence Layer Architecture

Version: V1.0.0
Status: ENGINEERING DRAFT — Awaiting Architect Review
Phase: V3.0 Implementation Era — Phase 0 Foundation
Module: 04_Execution_Intelligence
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Execution_Intelligence_Architecture_V1.0.md |
| Module | Execution Intelligence Layer — Architecture |
| System | AQF-T Autonomous Quant Intelligence Framework |
| Version | V1.0.0 |
| Phase | V3.0 Phase 0 — Foundation |
| Upstream | Decision Intelligence V2.9.1 ✅ + Risk Runtime V2.8.6 |
| Downstream | QMT Adapter → xttrader → Broker |
| Constitutions | C-001 (Intelligence Ownership), C-002 (Immutable Core), C-003 (QMT Boundary) |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |

---

## 1. Purpose

### 1.1 What Execution Intelligence Does

Execution Intelligence Layer 是 AQF-T 的 **交易神经系统（Trading Nervous System）**。

V2.9 完成的是：AQF-T 如何思考（Understand → Reason → Decide → Remember → Evolve）。

Execution Intelligence 完成的是：**AQF-T 如何行动（Decide → Plan → Execute → Observe）**。

```
V2.9 (已完成):           V3.0 Execution Intelligence:
  Understand                Decide → (this layer) → Execute
  Reason                         │
  Decide              ┌──────────┼──────────┐
  Remember            ▼          ▼          ▼
  Evolve           Plan       Execute    Observe
```

### 1.2 Core Definition

**Execution Intelligence 是 Decision Intent 到 Market Action 的安全转换层。**

它不产生交易方向。它实现交易方向。

### 1.3 What Execution Intelligence Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 策略系统 | Decision 的执行翻译器 |
| 信号系统 | 订单计划生成器 |
| 自动交易机器人 | 受治理的执行管道 |
| QMT 增强模块 | QMT 的上层抽象 |
| 第二个大脑 | 大脑的手足 |

---

## 2. Scope

### 2.1 In Scope

- Decision → Execution Plan 转换 (Strategy Runtime)
- 组合与仓位管理 (Portfolio Manager + Position Engine)
- 订单计划生成 (Order Planner)
- 执行成本优化 (Execution Optimizer)
- QMT 接口适配 (QMT Adapter)
- 执行结果观察与反馈 (Execution Report → Memory)

### 2.2 Out of Scope

- ❌ 市场判断 (World Model)
- ❌ 交易方向选择 (Decision Intelligence)
- ❌ 策略信号生成 (AI Brain)
- ❌ 独立的风险评估 (Risk Runtime — 本层消费 Risk，不产生 Risk)
- ❌ QMT 策略引擎 (禁用)

### 2.3 Target Scale

Personal workstation. QMT local client. Single account. ≤50 concurrent instruments. All execution CPU-friendly.

---

## 3. Architecture Position

### 3.1 V3.0 完整智能闭环

```
                    Market Environment
                           │
                           ▼
              ┌─────────────────────────┐
              │     AQF-T BRAIN          │  V2.9 ✅
              │                          │
              │  World Model             │  Understand
              │  Reasoning Engine        │  Reason
              │  Decision Intelligence   │  Decide
              │  Memory System           │  Remember
              │  Evolution System        │  Evolve
              └────────────┬────────────┘
                           │ DecisionIntent
                           ▼
              ┌─────────────────────────┐
              │  TRADING NERVOUS SYSTEM  │  V3.0 ← 本模块
              │                          │
              │  Strategy Runtime        │  Translate
              │  Portfolio Manager       │  Allocate
              │  Position Engine         │  Track
              │  Risk Runtime            │  Constrain
              └────────────┬────────────┘
                           │ ExecutionPlan
                           ▼
              ┌─────────────────────────┐
              │  EXECUTION INTELLIGENCE  │  V3.0 ← 本模块
              │                          │
              │  Order Planner           │  Generate
              │  Execution Optimizer     │  Optimize
              │  QMT Adapter             │  Adapt
              └────────────┬────────────┘
                           │ OrderRequest
                           ▼
              ┌─────────────────────────┐
              │       QMT / BROKER       │
              │  xttrader → 券商柜台     │
              └────────────┬────────────┘
                           │ ExecutionReport
                           ▼
              ┌─────────────────────────┐
              │   OBSERVATION LOOP       │
              │  Memory ← Evolution      │
              └─────────────────────────┘
```

### 3.2 Layer Responsibility

| Layer | Question | Output | Intelligence? |
|-------|----------|--------|:------------:|
| AQF-T Brain | What to do? | DecisionIntent | ✅ Yes |
| Trading Nervous System | How to do it? | ExecutionPlan | ❌ No |
| Execution Intelligence | How to optimize? | OrderRequest | ❌ No |
| QMT/Broker | Execute | Fill | ❌ No |

---

## 4. Constitutional Constraints

### 4.1 C-001: Intelligence Ownership

```
AQF-T owns intelligence. QMT owns execution.

Execution Layer SHALL NOT:
  - Judge market conditions
  - Select stocks
  - Generate trading direction
  - Modify position logic
  - Override Decision output
```

[Source: `AQFT_QMT_Integration_Principle_V1.0.md`]

### 4.2 C-002: Immutable Core

```
The following objects SHALL NOT be modified by Execution Layer:

  - MarketState S(t)
  - BeliefState B(t)
  - RegimeState R(t)
  - RiskState
  - DecisionRecord (read only after Decision publishes)
```

[Source: VERIFY-006 Constitution Compliance — Immutable Core Rule]

### 4.3 C-003: QMT Boundary

```
QMT SHALL:
  ✅ Receive Order Intent
  ✅ Send Order
  ✅ Query Status (position, fill, capital)
  ✅ Return Execution Result

QMT SHALL NOT:
  ❌ Generate Signal
  ❌ Adjust Strategy
  ❌ Override Risk
  ❌ Make independent trading decisions
```

[Source: `AQFT_QMT_Integration_Principle_V1.0.md`]

---

## 5. Three-Layer Architecture

### 5.1 Layer 1: Trading Nervous System

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| Strategy Runtime | Decision → Execution Logic | DecisionRecord | TradingIntent |
| Portfolio Manager | 组合层控制：总仓位/行业暴露/风格暴露/资金 | TradingIntent + Portfolio State | Allocation Plan |
| Position Engine | 实时状态：Current/Target/Delta | Allocation Plan + Market Data | Position State |
| Risk Runtime | 最后交易边界。Risk Veto Authority | Position State | Risk Decision |

### 5.2 Layer 2: Execution Intelligence

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| Order Planner | 交易计划生成：切片/时机/条件 | TradingIntent + Position State + Risk OK | ExecutionPlan |
| Execution Optimizer | 降低成本：VWAP/TWAP/Limit | ExecutionPlan + Market Microstructure | Optimized Orders |
| QMT Adapter | Schema 转换：AQF-T → QMT API | Optimized Orders | xttrader calls |

### 5.3 Layer 3: Observation

| Component | Responsibility |
|-----------|---------------|
| Execution Report | 成交/滑点/延迟/状态 → Memory System |
| Performance Feedback | Execution quality → Evolution System |

---

## 6. Core Object Definitions

### 6.1 DecisionIntent

```json
{
  "decision_id": "DEC_20260727_093500",
  "timestamp": "2026-07-27T09:35:00",
  "symbol": "SH.603xxx",
  "action": "Increase",
  "target_position": 0.30,
  "confidence": 0.82,
  "regime": "Expansion",
  "risk_limit": {
    "max_position": 0.50,
    "max_single_order": 0.10
  },
  "reasoning_summary": "Expansion+Warming, Leader confirmed, Risk Low",
  "source": "Decision Intelligence DI-003",
  "version": "V1.0"
}
```

**Lifecycle:** Create (Decision) → Validate (Risk) → Plan (Strategy) → Execute (Order Planner) → Observe (Execution Report) → Archive (Memory)

**Authority:** Decision Intelligence is sole Creator. Execution Layer reads, does not modify.

### 6.2 ExecutionPlan

```json
{
  "plan_id": "PLAN_20260727_093500",
  "decision_id": "DEC_20260727_093500",
  "execution_mode": "sliced",
  "total_quantity_pct": 0.20,
  "slices": [
    {
      "slice_id": 1,
      "quantity_pct": 0.10,
      "timing": "immediate",
      "condition": "liquidity_normal",
      "order_type": "limit",
      "price_offset": "-0.5%"
    },
    {
      "slice_id": 2,
      "quantity_pct": 0.10,
      "timing": "after_slice_1_fill",
      "condition": "leader_strength_maintained",
      "order_type": "market"
    }
  ],
  "constraints": {
    "max_slippage_pct": 1.0,
    "max_duration_minutes": 30,
    "cancel_if_risk_triggered": true
  },
  "version": "V1.0"
}
```

**Lifecycle:** Create (Strategy Runtime) → Optimize (Execution Optimizer) → Execute (QMT Adapter) → Complete/Expire

### 6.3 OrderRequest

```json
{
  "order_id": "ORD_20260727_093500_001",
  "plan_id": "PLAN_20260727_093500",
  "account": "AQFT_PRIMARY",
  "symbol": "SH.603xxx",
  "side": "BUY",
  "quantity": 10000,
  "price_type": "LIMIT",
  "price": 25.50,
  "expiry_seconds": 300,
  "version": "V1.0"
}
```

### 6.4 ExecutionReport

```json
{
  "order_id": "ORD_20260727_093500_001",
  "status": "FILLED",
  "filled_quantity": 10000,
  "average_price": 25.48,
  "slippage_bps": -2.0,
  "latency_ms": 15,
  "timestamp": "2026-07-27T09:35:03",
  "version": "V1.0"
}
```

**Lifecycle:** Create (QMT Adapter on fill) → Log (Runtime) → Store (Memory System) → Analyze (Evolution)

---

## 7. Authority Matrix

| Object | Owner | Write | Read | Immutable? |
|--------|:-----:|:-----:|:----:|:----------:|
| MarketState S(t) | World Model | World Model | All | ✅ |
| BeliefState B(t) | Belief Engine | Belief Engine | All | ✅ |
| RegimeState R(t) | Regime Engine | Regime Engine | All | ✅ |
| RiskState | Risk Runtime | Risk Runtime | All | ✅ |
| DecisionRecord | Decision Intelligence | Decision | All | ✅ |
| DecisionIntent | Decision Intelligence | Decision | Strategy, Portfolio, Position, Risk | ❌ (updatable by Decision) |
| ExecutionPlan | Strategy Runtime | Strategy Runtime | Order Planner, Risk | ❌ |
| OrderRequest | QMT Adapter | QMT Adapter | Runtime, Risk | ❌ (transient) |
| ExecutionReport | QMT Adapter | QMT Adapter (create on fill) | Memory, Evolution, Runtime | ✅ (after fill) |

---

## 8. Failure Safety Design

### 8.1 QMT Unavailable

```
IF QMT connection lost:
  → Status: ExecutionUnavailable
  → Action: Stop new orders. Hold existing positions.
  → Alert: Log + notify (Critical)
  → Recovery: Auto-reconnect every 30s. Manual resume after 5 min.
```

### 8.2 Partial Fill

```
IF filled_qty < requested_qty AND time > expiry:
  → Status: PartialFill
  → Action: Cancel remainder. Log discrepancy.
  → Report: ExecutionDrift → Risk check.
```

### 8.3 Risk Triggered During Execution

```
IF Risk score crosses threshold mid-execution:
  → Status: RiskInterrupt
  → Action: Cancel all pending slices. Do NOT submit new orders.
  → Priority: Risk Veto > Execution Request (Constitution Ch.7)
```

### 8.4 Execution Drift

```
IF |target_position - actual_position| > 5% AND duration > 30min:
  → Alert: ExecutionDrift warning
  → Action: Pause. Human review recommended.
```

---

## 9. Memory & Evolution Interface

### 9.1 Execution → Memory

```
ExecutionReport → Episodic Memory:
  - Decision made
  - Plan executed
  - Fill result (price, quantity, slippage, latency)
  - Market context at execution time

Purpose: Future retrieval for execution quality analysis
```

### 9.2 Execution → Evolution

```
Execution quality metrics → Evolution System:
  - Slippage trend (improving or degrading?)
  - Execution latency trend
  - Fill rate (partial vs full)
  - Cost relative to VWAP

Evolution MAY propose:
  - Optimizer parameter changes
  - Slicing strategy adjustments

Evolution SHALL NOT:
  - Directly modify Order Planner logic (C-002)
  - Auto-deploy changes (Human Approval required)
```

---

## 10. Object Lifecycle

```
DecisionIntent:
  Created → Validated(Risk) → Planned(Strategy) → Executed(QMT) → Archived(Memory)

ExecutionPlan:
  Created → Optimized → Executing → Completed/Expired/Cancelled → Archived

OrderRequest:
  Created → Submitted → Acknowledged → Partial/Filled/Rejected → Reported

ExecutionReport:
  Created(on fill) → Logged → Stored(Memory) → Analyzed(Evolution)
```

---

## 11. Interface Contracts

### 11.1 Upstream (from AQF-T Brain)

| From | To | Data |
|------|----|------|
| Decision Intelligence | Strategy Runtime | DecisionIntent |
| World Model | Strategy Runtime | S(t), B(t), R(t) (read-only context) |
| Risk Runtime | Strategy Runtime | RiskDecision (APPROVE/ADJUST/REJECT) |

### 11.2 Downstream (to QMT)

| From | To | Data |
|------|----|------|
| QMT Adapter | xttrader | OrderRequest → order_stock() |
| xttrader | QMT Adapter | Fill → ExecutionReport |

### 11.3 Feedback (to Memory/Evolution)

| From | To | Data |
|------|----|------|
| QMT Adapter | Memory System | ExecutionReport |
| Execution Optimizer | Evolution System | Execution quality metrics |

---

## 12. Engineering Requirement

### 12.1 Constraints

| Constraint | Value |
|------------|-------|
| Order planning latency | < 50ms |
| QMT Adapter latency overhead | < 5ms |
| Max concurrent orders | 20 |
| Max slices per plan | 10 |
| Risk check per order | Mandatory (pre-submit) |
| All execution CPU-friendly | Yes |

### 12.2 Code Structure

```
04_Execution_Intelligence/
├── 01_Architecture/           ← This document
├── 02_Strategy_Runtime/        (P0-003)
├── 03_Portfolio/               (P0-004)
├── 04_Position/                (P0-005)
├── 05_Order/                   (P0-006)
├── 06_QMT/                     (P0-007)
└── tests/
```

---

## 13. Testing Requirement

### 13.1 Unit Tests

- DecisionIntent → ExecutionPlan conversion
- OrderRequest → QMT API format translation
- ExecutionReport parsing from QMT fill
- Risk gate: rejected DecisionIntent → no ExecutionPlan created

### 13.2 Integration Tests

- Full chain: DecisionIntent → ExecutionPlan → OrderRequest → (mock) QMT → ExecutionReport → Memory
- QMT unavailable → ExecutionUnavailable → no orders submitted
- Risk trigger mid-execution → all pending orders cancelled
- Partial fill → correct drift detection

---

## 14. QMT Adapter Interface (Preliminary)

```python
class QMTAdapter:
    """Minimal QMT interface. No intelligence."""

    def connect(account: str) -> ConnectionStatus: ...
    def disconnect(): ...

    def submit_order(order: OrderRequest) -> OrderAck: ...
    def cancel_order(order_id: str) -> bool: ...

    def query_position(symbol: str) -> Position: ...
    def query_account() -> AccountState: ...

    def on_fill(callback: Callable[[ExecutionReport], None]): ...
    def on_order_status(callback: Callable[[OrderStatus], None]): ...

    def is_connected() -> bool: ...
    def health_check() -> HealthStatus: ...
```

---

## 15. Freeze Criteria

1. **Constitution C-001/C-002/C-003 verified** — No intelligence in Execution Layer
2. **4 core objects defined** — DecisionIntent, ExecutionPlan, OrderRequest, ExecutionReport
3. **Authority Matrix complete** — Every object has unique Owner
4. **Failure safety defined** — QMT unavailable, partial fill, risk trigger, execution drift
5. **Memory/Evolution interfaces defined** — Execution result → Memory → Evolution
6. **Risk Veto preserved** — Risk check mandatory before every order submission
7. **QMT is replaceable** — Adapter pattern confirmed
8. **Decision traceability** — Every fill traceable to DecisionIntent → DecisionRecord

---

## Source References

| Section | Source |
|---------|--------|
| 1-3 | Architect P0-001 Boundary Definition |
| 4 | AQFT_QMT_Integration_Principle_V1.0 (C-001/C-002/C-003) |
| 5-6 | Architect P0-002 Architecture specification |
| 7 | VERIFY-004 Access Control Matrix |
| 8 | AR-01 Autonomous Runtime §12 Fault Handling |
| 9-11 | Decision Intelligence V2.9.1 + Memory System V2.9.2 |
| 12-15 | V2.9 Design Principles + V3.0 Requirements |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | ExecutionPlan slicing strategy: fixed 3-slice or dynamic? | §6 |
| 2 | QMT reconnection: 30s auto-retry → 5min manual resume — appropriate? | §8 |
| 3 | Execution drift threshold: 5% deviation — confirm? | §8 |
| 4 | Slippage optimization: VWAP vs TWAP vs Passive — default? | §5 |

---

*AQF-T Execution Intelligence Architecture V1.0 — ENGINEERING DRAFT*  
*V3.0 Phase 0 Foundation. First layer of the Trading Nervous System.*  
*No original design. All content from Architect specifications.*
