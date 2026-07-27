# AQF-T State Vector Definition Specification V1.0

Version: V1.0.0
Status: FINAL DESIGN — Engineering Specification
Module: World Model Intelligence
Phase: AQF-T V2.9.0
Author: AQF-T Chief Architect
Date: 2026-07-27

---

## 1. Document Control

### 1.1 Purpose

本文档定义 AQF-T World Model 中最基础的数据结构：**Market State Vector（市场状态向量）**。

Market State Vector 是 AQF-T 对 A 股市场环境进行统一数字化表达的核心对象。

它不是交易信号。它不是预测结果。

它是：

```
市场真实状态 → 数字化表示 → World Model认知基础 → Belief State推理
→ Regime识别 → Scenario Simulation → Decision Intelligence
```

整个 AQF-T 智能体系建立在统一 Market State Representation 之上。

---

## 2. Architecture Position

### 2.1 Position in AQF-T Architecture

AQF-T World Model 数据流：

```
External Market → Data Collection Layer → Feature Engineering Layer
→ Market State Vector Engine → Belief State Engine → Regime Model
→ Scenario Simulation Engine → Decision Intelligence → Execution System
```

Market State Vector 位于：AI Brain → World Model → Market State Representation

属于：**Market Cognitive Foundation Layer**

---

## 3. Design Principles

### 3.1 Principle 1 — 不预测价格，描述环境

传统量化：K线 → 指标 → 买卖信号

AQF-T：市场状态 → 市场认知 → 概率判断 → 决策

系统首先回答：**当前市场处于什么环境？** 而不是：明天涨还是跌？

### 3.2 Principle 2 — 面向 A 股实际环境

适配：沪深市场、游资生态、中小私募、个人量化系统

重点捕捉：情绪周期、涨停生态、资金流向、主线强度、龙头状态、市场风险

### 3.3 Principle 3 — 可计算

每一个状态必须有数据来源、计算方法、更新频率、标准化方法。

禁止"市场感觉"、"人工判断"作为核心输入。

---

## 4. Market State Vector Overview

AQF-T Market State Vector：

```
S(t) = {
    Price_State, Volume_State, Liquidity_State, Sentiment_State,
    Capital_State, Risk_State, Microstructure_State,
    Regime_State, External_State
}
```

共 9 大状态维度。

---

## 5. State Vector Structure

### 5.1 Overall Schema

```json
{
    "timestamp": "",
    "market": "A_SHARE",
    "price_state": {},
    "volume_state": {},
    "liquidity_state": {},
    "sentiment_state": {},
    "capital_state": {},
    "risk_state": {},
    "microstructure_state": {},
    "regime_state": {},
    "external_state": {},
    "confidence": 0.0,
    "version": "V1.0"
}
```

---

## 6. State Dimension Definition

### 6.1 Price State（价格状态）

**Purpose**: 描述市场趋势方向。

**Data Source**: QMT行情 / Tick数据 / 日线 / 分钟线

| 字段 | 含义 | 类型 |
|------|------|------|
| trend_direction | 趋势方向 | float |
| momentum_score | 动量强度 | float |
| ma_alignment | 均线结构 | float |
| volatility | 价格波动 | float |
| breakout_strength | 突破强度 | float |

**Calculation**:

- `trend = (MA20 - MA60) / MA60`
- `momentum = (close_today - close_N) / close_N`

**Update Frequency**: 日线每日更新，分钟5分钟更新。

---

### 6.2 Volume State（成交状态）

**Purpose**: 识别市场参与程度。

| 字段 | 说明 |
|------|------|
| volume_ratio | 量比 |
| turnover_rate | 换手率 |
| volume_expansion | 成交扩张 |
| volume_contraction | 成交萎缩 |

**Calculation**: `Volume_Ratio = Current Volume / Average Volume(N)`

---

### 6.3 Liquidity State（流动性状态）

**Purpose**: 判断是否适合交易。

| 字段 | 说明 |
|------|------|
| market_turnover | 市场成交额 |
| bid_ask_depth | 盘口深度 |
| spread | 买卖价差 |
| liquidity_score | 流动性评分 |

**Data Source**: Level-2（买卖五档、委托量、成交速度）

---

### 6.4 Sentiment State（情绪状态）

这是 AQF-T 区别于普通量化系统的重要模块，用于模拟游资情绪周期。

| 字段 | 说明 |
|------|------|
| limit_up_count | 涨停数量 |
| limit_down_count | 跌停数量 |
| max_board_height | 最高连板高度 |
| broken_board_rate | 炸板率 |
| emotion_score | 情绪评分 |

**Emotion Score Formula**:

```
Emotion Score = 涨停数量 × 2 - 跌停数量 × 3 + 最高连板 × 5 - 炸板率 × 20
```

**Interpretation**:

| 评分 | 阶段 |
|------|------|
| 低 | 冰点 |
| 中低 | 回暖 |
| 高 | 高潮 |
| 下降 | 退潮 |

---

### 6.5 Capital State（资金状态）

**Purpose**: 描述市场资金方向、强弱和攻击意愿。

A 股市场的重要特征：价格不是唯一驱动因素。资金流决定热点持续性、龙头高度、板块生命力。

| 字段 | 说明 | 数据来源 |
|------|------|----------|
| northbound_flow | 北向资金变化 | 公开数据 |
| main_fund_flow | 主力资金流 | Level-2/资金数据 |
| sector_rotation | 板块轮动强度 | 行情数据 |
| hot_money_activity | 游资活跃度 | 涨停数据 |
| capital_concentration | 资金集中度 | 市场统计 |

**Capital Strength Score**:

```
Capital_Strength = 0.25 × Main_Fund_Flow + 0.20 × Northbound_Flow
                 + 0.25 × Sector_Rotation + 0.30 × Hot_Money_Activity
```

范围：0 ~ 100

| Score | 含义 |
|-------|------|
| 80-100 | 资金高度活跃 |
| 60-80 | 资金积极 |
| 40-60 | 正常 |
| 20-40 | 资金谨慎 |
| 0-20 | 资金退潮 |

---

### 6.6 Risk State（风险状态）

**Purpose**: 风险状态拥有最高优先级。符合 AQF-T Constitution：Risk Fortress 优先于收益优化。

| 字段 | 说明 |
|------|------|
| market_drawdown | 市场回撤 |
| volatility_risk | 波动风险 |
| liquidity_risk | 流动性风险 |
| sentiment_crash_risk | 情绪崩溃风险 |
| system_risk | 系统风险 |

**Risk Score**:

```
Risk_Score = 0.25 × Drawdown_Risk + 0.25 × Volatility_Risk
           + 0.20 × Liquidity_Risk + 0.30 × Sentiment_Risk
```

范围：0-100

| Score | 等级 |
|-------|------|
| 0-30 | Low |
| 30-60 | Medium |
| 60-80 | High |
| 80-100 | Extreme |

---

### 6.7 Microstructure State（微观结构状态）

**Purpose**: 利用 Level-2 数据。这是 AQF-T 区别于普通个人量化的重要优势。

**Data Source**: 国金证券 QMT — Level-2 行情、买卖盘口、委托流、成交明细

| 字段 | 说明 |
|------|------|
| order_imbalance | 委托不平衡 |
| large_order_ratio | 大单比例 |
| active_buy_ratio | 主动买入比例 |
| queue_strength | 封单强度 |
| market_pressure | 买卖压力 |

**Order Imbalance Formula**:

```
Order_Imbalance = (Bid_Volume - Ask_Volume) / (Bid_Volume + Ask_Volume)
```

范围：[-1, 1]

---

### 6.8 Regime State（市场体制状态）

**Purpose**: 连接 Market State 与 Regime Model。

```json
{
    "current_regime": "",
    "transition_probability": {},
    "regime_confidence": 0.0
}
```

**Regime Types**:

| ID | 类型 |
|----|------|
| 0 | Neutral |
| 1 | Accumulation 吸筹 |
| 2 | Expansion 扩张 |
| 3 | Mania 狂热 |
| 4 | Distribution 派发 |
| 5 | Panic 恐慌 |
| 6 | Recovery 恢复 |

**Example**:

```json
{ "current_regime": "Expansion", "confidence": 0.82 }
```

---

### 6.9 External State（外部状态）

**Purpose**: 捕捉外部环境变化。

| 字段 | 说明 |
|------|------|
| global_market | 全球市场 |
| us_market | 美股 |
| commodity | 大宗商品 |
| currency | 汇率 |
| policy_signal | 政策信号 |

外部状态不是主要交易依据，默认权重 ≤10%，避免外部市场噪声影响 A 股判断。

---

## 7. Complete Market State Vector

```python
class MarketStateVector:
    timestamp: datetime
    price_state: { trend_direction, momentum_score, volatility }
    volume_state: { volume_ratio, turnover_rate }
    liquidity_state: { liquidity_score }
    sentiment_state: { emotion_score, limit_up_count, board_height }
    capital_state: { capital_strength }
    risk_state: { risk_score }
    microstructure_state: { order_imbalance }
    regime_state: { regime }
    external_state: { global_factor }
    confidence: float  # state_confidence
```

---

## 8. State Normalization

不同数据尺度必须统一。AQF-T 采用 **Min-Max Normalization**:

```
X_norm = (X - X_min) / (X_max - X_min)
```

输出范围：0-1

**Extreme Handling**: 异常值（如极端成交量）采用 Winsorization，限制 99%分位。

---

## 9. State Confidence Engine

Market State 不是绝对真实，需要置信度。

**Confidence Formula**:

```
Confidence = 0.4 × Data_Quality + 0.3 × Model_Stability + 0.3 × Signal_Consistency
```

**Confidence Usage**:

| Confidence | 系统行为 |
|------------|----------|
| >0.8 | 正常决策 |
| 0.6-0.8 | 降低仓位 |
| <0.6 | 禁止激进交易 |

---

## 10. Time Scale Design

AQF-T 采用多周期状态：

| 尺度 | 周期 | 用途 |
|------|------|------|
| Short Term | 1min / 5min / 15min | 日内交易、Level-2分析 |
| Medium Term | Daily / Weekly | 波段、趋势 |
| Long Term | Monthly / Quarterly | Regime判断 |

**Multi-Time Fusion**:

```
Market_State = 0.5 × Short + 0.3 × Medium + 0.2 × Long
```

---

## 11. Market State Update Mechanism

### 11.1 Purpose

Market State Vector 不是静态数据。市场状态持续变化：

```
过去状态 S(t-1) → 新市场观测 O(t) → 状态更新 Engine → 当前状态 S(t)
```

### 11.2 State Update Architecture

```
Market Data → Observation Processor → Feature Aggregation
→ State Update Engine → Market State Vector
                              ├→ Belief State Engine
                              └→ Regime Model
```

### 11.3 Update Formula

AQF-T 采用动态状态更新模型：

```
S(t) = α × Observation(t) + (1-α) × S(t-1)
```

### 11.4 Dynamic Alpha

| 市场环境 | α | 说明 |
|----------|----|------|
| Normal Market | 0.3 | 状态平稳 |
| High Volatility | 0.6 | 快速响应 |
| Extreme Event | 0.8 | 快速切换风险状态 |

---

## 12. State Transition Detection

### 12.1 Purpose

识别市场状态是否发生变化。

### 12.2 Transition Score

```
Transition_Score = Σ |S(t) - S(t-1)| × Weight
```

### 12.3 Transition Level

| Score | 状态 |
|-------|------|
| 0-20 | 稳定 |
| 20-50 | 变化 |
| 50-80 | 明显切换 |
| 80-100 | 重大变化 |

---

## 13. State Storage Design

### 13.1 Storage Purpose

保存当前市场状态、历史状态、状态变化轨迹。用于 Memory System、Pattern Retrieval、Scenario Simulation。

### 13.2 Database Schema

表名：`market_state_vector`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| timestamp | DATETIME | 时间 |
| market | VARCHAR | 市场 |
| price_state | JSON | 价格状态 |
| volume_state | JSON | 成交状态 |
| liquidity_state | JSON | 流动性 |
| sentiment_state | JSON | 情绪 |
| capital_state | JSON | 资金 |
| risk_state | JSON | 风险 |
| microstructure_state | JSON | 微观结构 |
| regime_state | JSON | 体制 |
| external_state | JSON | 外部 |
| confidence | FLOAT | 置信度 |
| version | VARCHAR | 版本 |

---

## 14. Python Data Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

@dataclass
class MarketStateVector:
    timestamp: datetime
    market: str
    price_state: Dict
    volume_state: Dict
    liquidity_state: Dict
    sentiment_state: Dict
    capital_state: Dict
    risk_state: Dict
    microstructure_state: Dict
    regime_state: Dict
    external_state: Dict
    confidence: float
    version: str = "V1.0"
```

---

## 15. Interface Definition

### 15.1 Input Interface

```json
{
    "price_data": {},
    "volume_data": {},
    "level2_data": {},
    "fund_flow": {},
    "sentiment_data": {}
}
```

### 15.2 Output Interface

```json
{
    "timestamp": "2026-07-27 09:35:00",
    "market_state": {
        "sentiment_score": 72,
        "risk_score": 25,
        "regime": "Expansion",
        "confidence": 0.86
    }
}
```

---

## 16. API Specification

### 16.1 Get Current State

```
GET /api/v1/world-model/state/current
```

Response:

```json
{ "regime": "Expansion", "emotion_score": 75, "risk_score": 22, "confidence": 0.88 }
```

### 16.2 Get Historical State

```
GET /api/v1/world-model/state/history
```

参数: `start_time`, `end_time`, `frequency`

---

## 17. Integration With AI Brain

Market State Vector 是 AI Brain 的统一输入：

| Engine | 输入 | 输出 |
|--------|------|------|
| Prediction Engine | Market State + Features | Future Probability |
| Sentiment Engine | Sentiment State + Capital State | Emotion Evaluation |
| Risk Intelligence | Risk State + Microstructure | Risk Score |
| Fusion Engine | All Model Outputs + Market State | Final Decision Probability |

---

## 18. Integration With Decision Intelligence

Decision Intelligence 不直接读取原始数据：

```
Raw Market Data → Feature Layer → Market State Vector → Belief State → Decision Engine
```

原因：降低噪声，提高解释性。

---

## 19. Integration With Memory System

Memory System 保存 Market State Snapshot + Market Outcome，形成历史经验案例。

例如：2025-09 Expansion Regime，情绪 80，龙头高度 7 板 → 最终结果：退潮。未来遇到相似状态，系统检索。

---

## 20. Integration With Scenario Simulation

Scenario Engine 使用当前 S(t) 生成未来 S(t+n)：

| 场景 | 概率 |
|------|------|
| 情绪继续增强 | 45% |
| 高位退潮 | 35% |
| 震荡 | 20% |

---

*AQF-T State Vector Definition V1.0 — FINAL DESIGN*
