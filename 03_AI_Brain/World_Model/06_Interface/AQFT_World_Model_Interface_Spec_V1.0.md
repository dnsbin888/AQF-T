# AQF-T World Model Interface Specification

Version: V1.0.0
Status: FROZEN — V2.9.0 World Model Architecture Freeze
Phase: V2.9 Intelligence Era — World Model
Module: 06_Interface
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_World_Model_Interface_Spec_V1.0.md |
| Module | World Model — Interface Specification |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_World_Model_Intelligence_Spec_V2.9.0 |
| Dependencies | 01-05 All World Model sub-modules (all at REVIEW PASSED) |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source | All V2.9 World Model modules + AI Brain/Strategy/Risk/Data V2.8.6 |

---

## 1. Purpose

### 1.1 What Interface Spec Defines

World Model Interface 定义 World Model 如何成为 AQF-T 的 **统一市场认知服务层**。

它不是普通 REST API 文档。它定义：

- World Model 内部模块间的数据契约
- World Model 对外部系统（AI Brain / Decision / Strategy / Risk / Data）的服务接口
- 消息格式、数据 Schema、调用协议
- 运行时约束与安全边界

### 1.2 What Interface Spec Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 交易执行 API | 市场认知服务接口 |
| QMT 订单接口 | 状态查询与分析接口 |
| 券商接口 | 内部模块间契约 |
| HTTP-only 文档 | 协议无关的逻辑接口定义 |

---

## 2. Scope

### 2.1 In Scope

- World Model 内部数据流接口（State → Belief → Regime → Simulation）
- World Model → AI Brain 接口
- World Model → Decision Intelligence 接口
- World Model → Strategy Runtime 接口
- World Model → Risk Runtime 接口
- Data Runtime → World Model 接口
- 消息/数据 Schema 定义
- 运行时约束

### 2.2 Out of Scope

- ❌ 交易执行 API（属于 06_Execution）
- ❌ QMT / 券商接口实现
- ❌ 网络协议细节（HTTP/gRPC 选择属于 Implementation）
- ❌ 数据库 ORM 层

---

## 3. Architecture Position

### 3.1 World Model in AQF-T System

```
                    ┌─────────────────────┐
                    │    Data Runtime      │
                    └──────────┬──────────┘
                               │ raw data
                               ▼
┌──────────────────────────────────────────────────┐
│                  WORLD MODEL                      │
│                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  State   │→│  Belief  │→│  Regime  │        │
│  │  Model   │ │  Engine  │ │  Model   │        │
│  └──────────┘  └──────────┘  └──────────┘        │
│        │                            │             │
│        └────────────┬───────────────┘             │
│                     ▼                              │
│            ┌──────────────┐                       │
│            │  Simulation   │                       │
│            └──────────────┘                       │
│                     │                              │
└─────────────────────┼──────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │  AI Brain │ │ Decision │ │ Strategy │
    │           │ │  Intel.  │ │ Runtime  │
    └──────────┘ └──────────┘ └──────────┘
                                    │
                              ┌──────────┐
                              │   Risk   │
                              │ Runtime  │
                              └──────────┘
                                    │
                              ┌──────────┐
                              │Execution │
                              │ Runtime  │
                              └──────────┘
```

---

## 4. Interface Philosophy

### 4.1 Design Principles

**Principle 1: World Model is a Service, Not a Library**

World Model 作为独立认知服务运行，不嵌入到调用方代码中。

**Principle 2: Read-Only for Consumers**

Strategy、Risk、Execution 读取 World Model 输出，但不写入。World Model 的状态只能由 Market Data 和内部推理更新。

**Principle 3: Confidence Everywhere**

每个 World Model 输出都携带置信度。下游模块根据置信度决定使用策略。

**Principle 4: Synchronous Query + Asynchronous Update**

- 状态查询：同步（毫秒级）
- 模拟运行：异步（秒级）
- 内部状态更新：事件驱动

---

## 5. Internal World Model Interface

### 5.1 Data Flow Chain

```
[Data Input] → [State Model] → [Belief Engine] → [Regime Model] → [Simulation]
                     │               │                │                │
                     ▼               ▼                ▼                ▼
                  S(t)            B(t)             R(t)          Scenarios
```

### 5.2 Interface Contracts

| From | To | Data | Format | Frequency |
|------|----|------|--------|-----------|
| Data Runtime | State Model | Raw market data | JSON/MarketDataInput | Per tick/bar |
| State Model | Belief Engine | MarketStateVector S(t) | Python object / JSON | 5 min |
| Belief Engine | Regime Model | BeliefState B(t) | Python object / JSON | 5 min |
| Regime Model | Simulation | RegimeState R(t) | Python object / JSON | On change |
| Simulation | Memory | ScenarioRecord | JSON | Per simulation run |

### 5.3 Internal Schema

```python
# State Model → Belief Engine
class StateToBelief:
    market_state: MarketStateVector    # 9-dim S(t)
    ai_signals: Dict                   # AI Brain outputs
    prior_belief: Optional[BeliefState] # B(t-1)

# Belief Engine → Regime Model
class BeliefToRegime:
    belief_state: BeliefState          # B(t)
    market_state: MarketStateVector    # S(t) for context
    transition_indicators: Dict        # regime shift signals

# Regime Model → Simulation
class RegimeToSimulation:
    regime_state: RegimeState          # R(t)
    belief_state: BeliefState          # B(t)
    market_state: MarketStateVector    # S(t)
    simulation_config: Dict            # horizon, method, count
```

---

## 6. AI Brain Interface

### 6.1 Direction: AI Brain → World Model

| From AI Brain Engine | To World Model | Data |
|---------------------|----------------|------|
| Prediction Engine | State Model | Trend direction, probability |
| Sentiment Engine | State Model + Belief Engine | Emotion phase, score |
| Risk Intelligence | Belief Engine + Regime Model | Risk score, warnings |

### 6.2 Direction: World Model → AI Brain

| From World Model | To AI Brain | Data | Purpose |
|-----------------|-------------|------|---------|
| State Model | Fusion Engine | MarketContext{S(t), R(t)} | Context for weight adjustment |
| Regime Model | Fusion Engine | Regime + confidence | Dynamic weight selection |
| Simulation | Prediction Engine | Scenario forecasts | Alternative future reference |

### 6.3 Fusion Engine Context API

```python
# World Model → AI Brain Fusion Engine
GET /world-model/context

Response:
{
  "market_state": { S(t) },
  "current_regime": "Expansion",
  "regime_confidence": 0.82,
  "emotion_phase": "Warming",
  "risk_level": "Medium",
  "scenario_summary": "Expansion likely to continue (P=45%)"
}
```

[Source: `AQFT_AI_Brain_Design_V2.8.6.md` — Chapter 6 & 10]

---

## 7. Decision Intelligence Interface

### 7.1 World Model → Decision Intelligence

```
Decision Intelligence receives:

  [1] MarketState S(t)      — What is the market now?
  [2] BeliefState B(t)      — What does AI believe?
  [3] RegimeState R(t)      — What phase are we in?
  [4] ScenarioReport        — What could happen next?
  [5] Confidence scores     — How reliable is each?
```

### 7.2 Decision Context Object

```python
class DecisionContext:
    timestamp: datetime

    market_state: MarketStateVector
    belief_state: BeliefState
    regime: RegimeState

    scenarios: List[Scenario]
    top_scenario: Scenario

    risk_assessment: RiskAssessment
    overall_confidence: float

    # Summary for Decision Engine
    summary: str  # Human-readable context
```

### 7.3 API

```python
GET /world-model/decision-context
POST /world-model/simulate-for-decision
  Body: { decision_options: [Action1, Action2, ...] }
  Response: { per_option_scenarios: [...], recommendation_context: {...} }
```

---

## 8. Strategy Interface

### 8.1 World Model → Strategy Runtime

Strategy 使用 World Model 进行 **策略行为约束**，而非生成交易信号。

| World Model Output | Strategy Usage |
|-------------------|----------------|
| Regime R(t) | 允许/禁止策略类型 |
| Emotion Phase | 调整策略参数（激进/保守） |
| Scenario Report | 多情景仓位规划参考 |
| Risk Context | 仓位上限约束 |

### 8.2 Strategy Constraint API

```python
GET /world-model/strategy-constraint

Response:
{
  "regime": "Expansion",
  "allowed_strategies": ["trend", "leader"],
  "restricted_strategies": ["dip_buy"],
  "position_limit": 0.70,
  "sentiment_override": null,
  "risk_flags": []
}
```

**[NEEDS ARCHITECT REVIEW]** — Exact constraint schema to be aligned with Strategy Runtime implementation.

---

## 9. Risk Interface

### 9.1 World Model → Risk Runtime

Risk Runtime 使用 World Model 进行 **风险环境感知**。

| World Model Output | Risk Usage |
|-------------------|------------|
| Regime R(t) | 风险等级覆盖 |
| Risk Scenario | 极端风险预警 |
| Belief Confidence | 模型不确定性 → 提高风险边际 |
| Simulation Tail Risk | 尾部风险预估值 |

### 9.2 Risk Context API

```python
GET /world-model/risk-context

Response:
{
  "regime_risk_level": "Medium",
  "tail_risk_probability": 0.05,
  "tail_risk_severity": "Extreme",
  "belief_confidence": 0.77,
  "volatility_regime": "Normal",
  "liquidity_risk": "Low",
  "regime_override": null
}
```

[Source: `AQFT_Risk_Design_V2.8.6.md`]

---

## 10. Data Runtime Interface

### 10.1 Data Runtime → World Model

```
Data Runtime provides:
  - Market tick data (price, volume)
  - L1/L2 order book snapshots
  - Kline data (1min, 5min, daily)
  - Fund flow data
  - Sentiment aggregates

World Model subscribes:
  SUB market_data.{symbol}.{frequency}
  SUB fund_flow.{market}
  SUB sentiment.{market}
```

### 10.2 Input Schema

```json
{
  "market_data": {
    "symbol": "SH.000001",
    "timestamp": "2026-07-27T09:35:00",
    "price": { "open": 3450.0, "high": 3465.0, "low": 3445.0, "close": 3460.0 },
    "volume": { "total": 125000000, "turnover_rate": 0.85 },
    "l2_data": { "bid_volume": {}, "ask_volume": {}, "order_imbalance": 0.12 },
    "fund_flow": { "main_net": 50000000, "northbound": 20000000 }
  },
  "sentiment": {
    "limit_up_count": 65,
    "limit_down_count": 8,
    "max_board_height": 7,
    "炸板率": 0.22
  }
}
```

---

## 11. Message / Data Schema

### 11.1 Unified Response Envelope

All World Model API responses follow:

```json
{
  "status": "ok",
  "timestamp": "2026-07-27T09:35:00",
  "data": { },
  "confidence": 0.82,
  "warnings": [],
  "version": "V2.9.0"
}
```

### 11.2 Error Response

```json
{
  "status": "error",
  "timestamp": "...",
  "error_code": "WM_DATA_STALE",
  "message": "Market data older than 5 minutes",
  "data": null
}
```

### 11.3 Key Data Types

| Type | Defined In | Description |
|------|-----------|-------------|
| `MarketStateVector` | 02_State_Model | 9-dim state vector |
| `BeliefState` | 03_Belief_Model | 5-dim belief with confidence |
| `RegimeState` | 04_Regime_Model | 7-regime classification |
| `Scenario` | 05_Simulation | Single future world path |
| `ScenarioReport` | 05_Simulation | Multi-scenario analysis |
| `DecisionContext` | 06_Interface (here) | Aggregated context for decision |

---

## 12. Runtime Requirement

### 12.1 Performance

| Operation | Target Latency | Max Latency |
|-----------|:-------------:|:-----------:|
| Get current state | < 10ms | 50ms |
| Get belief state | < 10ms | 50ms |
| Get regime | < 5ms | 20ms |
| Get decision context | < 50ms | 200ms |
| Run simulation (async) | < 5s | 30s |
| Run counterfactual (async) | < 10s | 60s |

### 12.2 Availability

- World Model runs as local service (same machine as AQF-T core)
- No external network dependency for core queries
- Graceful degradation when data is stale: return last known state + `warning: data_stale`

### 12.3 Concurrency

- Read queries: concurrent (stateless)
- State updates: serialized (ordered by timestamp)
- Simulations: queued (max 3 concurrent)

---

## 13. Security & Governance

### 13.1 Read-Only for Consumers

Strategy、Risk、Execution 只能读取 World Model 输出。

**禁止**下游模块直接写入 World Model 内部状态。

唯一写入路径：Data Runtime → State Model → internal chain.

### 13.2 Audit Trail

所有 World Model 状态变更记录：

- Timestamp
- Source (数据驱动 / 推理更新 / 手动覆盖)
- Old value → New value
- Confidence change

### 13.3 Manual Override Governance

允许人工覆盖 Regime 判断，但必须：

1. 记录覆盖原因
2. 标记为 `manual_override: true`
3. 下游模块接收到 `manual_override` 标记后可选择是否采纳
4. 覆盖有时间限制（默认 1 trading day，需显式续期）

### 13.4 Constitution Compliance

[Source: `AQFT_System_Constitution_V2.8.6_FINAL.md`]

- World Model 输出不直接触发交易
- 所有交易必须经过 Strategy → Risk → Execution 审核链
- World Model 置信度 < 0.6 时，Risk Runtime 应自动提高风险等级

---

## 14. Testing Requirement

### 14.1 Unit Tests

- Each interface endpoint: valid input → valid output
- Error handling: stale data, missing fields, invalid parameters
- Schema validation: response matches defined schema

### 14.2 Integration Tests

- Full chain: Data → State → Belief → Regime → Simulation → Decision Context
- AI Brain receives valid context from World Model
- Strategy receives valid constraint from World Model
- Risk receives valid risk context from World Model

### 14.3 Contract Tests

- Interface schema versioning: V1.0 backward compatibility
- Breaking change detection: schema diff on each commit

### 14.4 Performance Tests

- 100 concurrent read queries → all < 50ms
- Simulation queue: 5 concurrent → no timeout

---

## 15. Freeze Criteria

1. **All internal interfaces defined** — State→Belief→Regime→Simulation chain complete
2. **All external interfaces defined** — AI Brain / Decision / Strategy / Risk / Data
3. **Schema consistency** — Data types align with all 5 sub-modules
4. **Security boundaries clear** — Read-only consumers, audit trail, manual override governance
5. **Performance targets specified** — Latency, concurrency, availability
6. **No trading execution APIs** — Clean separation from 06_Execution
7. **Constitution compliant** — World Model is cognitive service, not trading engine

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-4 | Synthesized from AQF-T Architecture + World Model Intelligence Spec |
| 5 | All 5 completed V2.9 World Model modules |
| 6 | `AQFT_AI_Brain_Design_V2.8.6.md` Ch.6, 10 |
| 7 | `AQFT_AGI_Decision_Architecture_Design_V3.0.0` |
| 8 | `AQFT_Strategy_Design_V2.8.6.md` |
| 9 | `AQFT_Risk_Design_V2.8.6.md` |
| 10 | `AQFT_Data_Runtime_Design_V2.8.6.md` |
| 11-15 | Inferred from V2.9 Design Principles + Constitution |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Strategy constraint exact schema — align with Strategy Runtime implementation | §8 |
| 2 | Manual override governance: maximum override duration? | §13 |
| 3 | Transport protocol choice (in-process / localhost HTTP / gRPC) | §12 |
| 4 | Simulation async result delivery mechanism (callback / polling / event) | §12 |

---

*AQF-T World Model Interface Specification V1.0 — ENGINEERING DRAFT*  
*Source: All V2.9 World Model modules + AI Brain / Strategy / Risk / Data V2.8.6*  
*No original design added. All interfaces derived from existing module specifications.*
