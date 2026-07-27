# AQFT Market State Space Design Specification

## AQF-T World Model Intelligence System

Version: V1.0.0
Status: FINAL DESIGN
Target Phase: V2.9.0 World Model Intelligence
Design Authority: AQF-T Chief Architect

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Market_State_Space_Design_V1.0.md |
| Module | World Model — Market State Space |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent Module | AQFT_World_Model_Intelligence_Spec_V2.9.0 |
| Child Module | AQFT_State_Vector_Definition_V1.0 |
| Status | FINAL DESIGN |
| Target Phase | V2.9.0 World Model Intelligence |
| Design Authority | AQF-T Chief Architect |
| Implementation Target | Engineering Specification Before Coding |

---

## 1. Purpose

### 1.1 Design Objective

AQFT Market State Space 模块用于定义 AQF-T World Model 对 A 股市场环境进行统一认知的基础状态空间。

该模块解决以下核心问题：

传统量化系统通常直接从价格、成交量、指标生成交易信号：

```
Market Data → Feature → Signal → Trade
```

存在：市场状态不可解释、策略无法理解环境变化、牛熊转换响应滞后、情绪周期无法系统表达、模型容易在市场结构变化时失效。

AQF-T 引入 Market State Space：

```
Raw Market Observation → Market State Space → Belief State → Regime Recognition → Decision Intelligence
```

目标：将 A 股市场从"数据集合"转换为"可被 AI 理解的动态环境状态"。

---

## 2. Scope

### 2.1 Module Scope

Market State Space 负责：

**输入：**
- 市场行情数据
- Level-2 数据
- 资金流数据
- 情绪数据
- 宏观环境数据
- 策略运行反馈数据

**输出：** 统一市场状态 Market State S(t)

供 AI Brain、Strategy Runtime、Risk Intelligence、Decision Intelligence、Evolution System 使用。

### 2.2 Non-Scope

本模块不负责：
- ❌ 交易执行
- ❌ 高频撮合
- ❌ 超大型机构级计算
- ❌ 万亿参数金融大模型
- ❌ 另类数据超级平台

**AQF-T 定位：** Professional Individual Quant System + Small Private Fund Level Intelligence

**运行环境：** Personal Workstation + QMT + L2 Data + Local AI Models

---

## 3. Architecture Position

### 3.1 World Model Architecture

```
                 World Model
                      │
        ┌─────────────┴─────────────┐
        │                           │
Market State Space          Environment Model
        │
        ↓
State Vector
        │
        ↓
Belief State Engine
        │
        ↓
Regime Model
        │
        ↓
Scenario Simulation
        │
        ↓
Decision Intelligence
```

### 3.2 Relationship With AI Brain

AI Brain 负责"预测未来"，World Model 负责"理解现在"。

```
AI Brain Prediction Engine
          ↑
Market State Space
          ↓
Current Market Understanding
```

---

## 4. Core Design Philosophy

### 4.1 Market As Dynamic System

AQF-T 不将市场定义为 Price Sequence，而定义为 Dynamic Adaptive System。

市场状态：

```
S(t) = f(O(t), M(t), R(t), E(t))
```

其中：
- S(t): 市场状态
- O(t): 市场观测
- M(t): 市场微观结构
- R(t): 风险状态
- E(t): 市场情绪

---

## 5. Market State Space Overall Design

AQF-T Market State Space 采用九维状态模型。

**State Space Definition:** `S(t) = [S1, S2, S3, ..., S9]`

| Dimension | Name | Purpose |
|-----------|------|---------|
| S1 | Price Structure State | 价格趋势结构 |
| S2 | Volume Liquidity State | 成交与流动性 |
| S3 | Capital Flow State | 主力资金状态 |
| S4 | Market Emotion State | A股情绪周期 |
| S5 | Theme Rotation State | 题材轮动 |
| S6 | Microstructure State | L2微观结构 |
| S7 | Risk State | 风险环境 |
| S8 | Market Regime State | 市场阶段 |
| S9 | External Environment State | 外部环境 |

---

## 6. State Dimension Detailed Design

### 6.1 S1 Price Structure State

**目标：** 描述价格趋势和结构。

**输入：** 收盘价、均线系统、趋势强度、波动率

**核心指标：** Trend Strength、Momentum、Deviation、Structure Break

**输出：** S1 ∈ [-1, 1]

含义：-1 强下降 / 0 震荡 / +1 强上涨

### 6.2 S2 Volume Liquidity State

**目标：** 描述市场交易活跃程度。

**输入：** 成交额、换手率、量价关系、流动性指标

**输出：** S2 Liquidity Score

用于判断行情持续性、判断资金承接能力。

### 6.3 S3 Capital Flow State

**Design Objective:** 描述市场资金运动方向、强度和持续性。

A股市场具有明显的资金驱动特征，尤其适用于：游资交易体系、题材炒作周期、龙头接力模式、主线资金识别。

**Input Data:** 市场成交额、个股资金流、板块资金流、主力净流入、大单成交、L2 主动买卖数据

**State Variables:**

`S3 = f(Capital_flow, Intensity, Persistence)`

| Variable | Description |
|----------|-------------|
| Net Flow | 净资金流向 |
| Flow Intensity | 资金强度 |
| Flow Persistence | 持续时间 |
| Sector Migration | 板块迁移方向 |

**Output:** S3 ∈ [-1, 1]

| Value | Meaning |
|-------|---------|
| >0.7 | 强资金流入 |
| 0~0.7 | 温和流入 |
| -0.7~0 | 流出 |
| <-0.7 | 大规模撤退 |

### 6.4 S4 Market Emotion State

**A股特色核心状态** — 这是 AQF-T 与普通量化系统的重要区别。

传统量化：Price + Volume

AQF-T：Price + Capital + Emotion Cycle + Participant Behavior

**Emotion State Definition:**

`S4 = f(LimitUp, LimitDown, 連板, 炸板率, MarketHeight, Turnover)`

**Core Indicators — 涨停生态：** 涨停数量、首板数量、二板数量、高标高度、龙头持续性。

**情绪温度模型：**

```
EmotionScore = 2×Lu - 3×Ld + 5×H + 10×F
```

| Symbol | Meaning |
|--------|---------|
| Lu | 涨停数量 |
| Ld | 跌停数量 |
| H | 连板高度 |
| F | 资金强度 |

**Emotion Regime Mapping:**

| Score | State | Trading Meaning |
|-------|-------|-----------------|
| <20 | 冰点 | 控仓试错 |
| 20-50 | 回暖 | 寻找主线 |
| 50-80 | 高潮 | 龙头强化 |
| >80 | 过热 | 防止退潮 |

**Output:** S4 ∈ [0, 100]

该状态直接输入：Sentiment Engine、Strategy Runtime、Risk Runtime。

### 6.5 S5 Theme Rotation State

**Objective:** 识别 A 股题材生命周期。

**State Variables:**

| Variable | Meaning |
|----------|---------|
| Theme Strength | 题材强度 |
| Breadth | 扩散程度 |
| Continuity | 持续性 |
| Leader Status | 龙头状态 |
| Capital Attention | 资金关注度 |

**Theme Lifecycle:**

```
启动期 → 发酵期 → 高潮期 → 分化期 → 退潮期 → 新主题切换
```

**Output:** S5 = Theme Vector

```json
{ "AI": 0.82, "新能源": 0.35, "消费": 0.21 }
```

### 6.6 S6 Microstructure State

**Objective:** 利用 Level-2 数据描述市场短周期行为。

AQF-T 已有 QMT 接口 + L2 数据源。因此该维度重点服务：短线交易、游资模式、买卖点优化。

**Input:** 委托队列、买卖盘深度、主动成交、大单行为、撤单行为

**Core Features:**

| Feature | Purpose |
|---------|---------|
| Order Imbalance | 买卖力量差 |
| Large Order Ratio | 大单占比 |
| Queue Pressure | 排队压力 |
| Active Buy Ratio | 主动买入强度 |

**State Output:** S6 ∈ [-1, 1]

+1: 主动买盘强 / 0: 平衡 / -1: 主动卖压

### 6.7 S7 Risk State

**Objective:** 建立市场风险感知。

**Risk Variables:** 波动率、最大回撤、市场宽度、流动性下降、极端事件。

**Risk Score:** `S7 = Risk(t)` 范围 0-100

| Score | Meaning |
|-------|---------|
| 0-30 | 低风险 |
| 30-60 | 正常 |
| 60-80 | 风险升高 |
| 80+ | 极端风险 |

### 6.8 S8 Market Regime State

**Objective:** 连接 Regime Model。Market State Space 不直接做最终判断，而提供状态输入。

**Regime Categories:**

R1 Neutral / R2 Accumulation / R3 Expansion / R4 Mania / R5 Distribution / R6 Panic / R7 Recovery

**Output:**

```json
{ "regime": "Expansion", "confidence": 0.82 }
```

### 6.9 S9 External Environment State

**Objective:** 描述外部影响。范围控制：不建立机构级宏观系统，仅使用个人系统可获得数据。

**Input:** 大盘指数、海外市场方向、汇率、商品趋势、政策事件。

**Output:** S9 External Environment Vector

---

## 7. Market State Space Mathematical Definition

### 7.1 State Vector

```
S(t) = [S1, S2, S3, S4, S5, S6, S7, S8, S9]
```

### 7.2 Dynamic Update

市场状态随时间变化：

```
S(t+1) = F(S(t), O(t))
```

其中：S(t) 当前市场状态、O(t) 新观测数据、F 状态转移函数。

### 7.3 Confidence

每个状态必须携带 State Value + Confidence + Timestamp。

```json
{ "state": "Emotion", "value": 72, "confidence": 0.86, "timestamp": "2026-07-27 09:35" }
```

---

## 8. Data Model

### 8.1 Market State Object Definition

Market State Space 输出统一状态对象：

```json
{
  "market_state_id": "MS_20260727_093500001",
  "timestamp": "2026-07-27 09:35:00",
  "market": "CN_A_SHARE",
  "state_vector": {
    "price_structure": 0.72,
    "liquidity": 0.65,
    "capital_flow": 0.81,
    "emotion": 68,
    "theme_rotation": {
      "AI": 0.76,
      "Energy": 0.42
    },
    "microstructure": 0.58,
    "risk": 32,
    "regime": "Expansion",
    "external_environment": 0.45
  },
  "confidence": 0.84
}
```

### 8.2 State Storage Model

AQF-T 本地量化环境采用轻量化存储。不设计大规模分布式数据库、云端金融数据湖、机构级数据平台。

采用：Local Database + Feature Storage + Model Cache

### 8.3 Recommended Storage

| Data Type | Storage |
|-----------|---------|
| 日行情 | PostgreSQL / SQLite |
| Tick/L2 | 时序数据库 |
| Feature | Feature Store |
| Model Output | JSON + Database |
| Historical State | Vector Storage |

---

## 9. Interface Definition

### 9.1 Upstream Interface

Market State Space 接收 Data Runtime：

```python
MarketDataInput()
```

```json
{
  "price": {},
  "volume": {},
  "orderbook": {},
  "capital_flow": {},
  "emotion_data": {}
}
```

### 9.2 Downstream Interface

输出给：

**1. Belief State Engine** — `update_market_state()`:

```json
{ "state_vector": {}, "confidence": 0.85 }
```

**2. AI Brain Fusion Engine** — `get_market_context()`:

```json
{ "regime": "Expansion", "emotion": 72, "risk": 28 }
```

**3. Strategy Runtime** — 调整策略行为。例如 Expansion 允许趋势策略提高权重，Panic 禁止高风险策略。

**4. Risk Runtime** — 风险约束。示例：

```json
{ "risk_level": "HIGH", "position_limit": 0.3 }
```

---

## 10. Dependency Definition

### 10.1 Upstream Dependencies

| Module | Purpose |
|--------|---------|
| Data Runtime | 数据输入 |
| Data Engineering | 数据清洗 |
| Feature Engineering | 特征计算 |
| AI Brain | 模型输出 |

### 10.2 Downstream Dependencies

| Module | Usage |
|--------|-------|
| Belief State Engine | 状态推理 |
| Regime Model | 市场阶段识别 |
| Decision Intelligence | 决策 |
| Evolution System | 学习反馈 |

### 10.3 Dependency Graph

```
Data Runtime → Feature Engineering → Market State Space → State Vector
→ Belief State Engine → Regime Model → Decision Intelligence
```

---

## 11. Engineering Requirement

### 11.1 Implementation Principle

目标：从设计直接进入代码实现。

要求：模块化、可测试、可替换、可扩展。

### 11.2 Software Structure

```
world_model/
├── market_state/
├── state_calculator/
├── feature_mapping/
├── state_storage/
├── interface/
└── tests/
```

### 11.3 Core Classes

```python
class MarketStateSpace:
    def update_state(self, market_data):
        pass
    def calculate_dimension(self):
        pass
    def get_state(self):
        pass

class StateDimension:
    name: str
    value: float
    confidence: float
    timestamp: str
```

### 11.4 Runtime Requirement

运行频率：非高频。设计目标：个人量化系统。

| Frequency | Usage |
|-----------|-------|
| 日级 | 市场环境判断 |
| 分钟级 | 短线调整 |
| Tick级 | L2微观辅助 |

不追求毫秒级交易。

---

## 12. Testing Requirement

### 12.1 Unit Test

测试每个状态维度计算。

例如 Emotion State：输入涨停50、跌停5、连板高度8 → 输出 Emotion Score。

### 12.2 Historical Replay Test

使用 A 股历史周期。覆盖：牛市、熊市、震荡、情绪高潮、情绪退潮。

### 12.3 Scenario Test

测试市场状态变化：高潮 → 退潮 → 冰点，状态是否正确变化。

### 12.4 Integration Test

验证完整链路：Market State → Belief Engine → Decision Engine → Strategy。

---

## 13. Freeze Criteria

Market State Space Design V1.0 达到以下条件后冻结。

**Architecture Review** — 通过：与 World Model 一致、与 Constitution 一致、与 AI Brain 一致。

**Interface Review** — 确认：输入接口明确、输出接口明确、无循环依赖。

**Engineering Review** — 确认：可编码、数据结构明确、类设计明确。

**Trading Applicability Review** — 确认符合：✅ 游资交易场景 ✅ 中小私募 ✅ 个人量化系统 ✅ QMT环境 ✅ L2数据。不包含：❌ 超算模拟 ❌ 高频基础设施。

---

## 14. Final Design Summary

AQFT Market State Space 是 AQF-T World Model 的核心认知基础。

它将传统 `Market Data → Signal → Trade` 升级为：

```
Market Observation → Market State Space → Belief State → Market Regime
→ Decision Intelligence → Trading Action
```

核心价值：**不是预测市场。而是让 AI 理解市场当前处于什么状态。**

最终服务：**AQF-T Financial Intelligence Operating System。**

---

*AQF-T Market State Space Design V1.0 — FINAL DESIGN*
