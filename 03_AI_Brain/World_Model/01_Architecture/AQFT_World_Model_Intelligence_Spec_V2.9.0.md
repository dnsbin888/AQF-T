# AQFT World Model Intelligence Specification

Version: V2.9.0
Status: FROZEN — V2.9.0 World Model Architecture Freeze
Phase: V2.9 Intelligence Era — World Model
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_World_Model_Intelligence_Spec_V2.9.0.md |
| Module | World Model — Architecture |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V2.9.0 |
| Parent | AQF-T V2.8.6 Architecture Freeze |
| Children | Market State Space, Belief State Engine, Regime Model, Scenario Simulation, Interface Spec |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | AQFT_World_Model_Architecture_V3.0.0 + 6 companion docs |

---

## 1. Purpose

### 1.1 Design Objective

将 AQF-T 从 **Price Predictor（价格预测器）** 升级为 **Market Reality Simulator（市场现实模拟器）**。

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 1]

World Model 回答三个核心问题：

| 问题 | 对应层 |
|------|--------|
| 市场现在处于什么状态？ | Layer 1: Market State Representation |
| 市场为什么会这样？ | Layer 2: Market Dynamics Model |
| 未来可能发生什么？ | Layer 3-5: Scenario / Counterfactual / Memory |

### 1.2 Core Transformation

| 传统系统 | AQF-T World Model |
|---------|-------------------|
| 预测涨跌 | 理解市场状态 |
| 单一路径推演 | 多世界分支模拟 |
| 线性因果 | 反事实推理 |
| 无记忆 | 模拟经验积累 |
| 黑箱输出 | 可解释状态空间 |

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 1.2]

---

## 2. Scope

### 2.1 In Scope

- Market State Representation（市场状态表征）
- Market Dynamics Modeling（市场动力学建模）
- Environment Context Recognition（环境语境识别）
- Scenario Generation & Simulation（场景生成与模拟）
- Counterfactual Reasoning（反事实推理）
- Simulation Memory & Experience（模拟记忆与经验积累）

### 2.2 Out of Scope

- ❌ 交易执行
- ❌ 高频撮合
- ❌ 超大型机构级计算
- ❌ 万亿参数金融大模型
- ❌ 另类数据超级平台

### 2.3 Target Environment

**Personal Workstation + QMT + L2 Data + Local AI Models**

服务于：游资交易者 / 中小私募 / 个人量化系统

[Source: AQF-T Constitution V2.8.6 + Market Simulation Design Chapter 1]

---

## 3. Architecture Position

### 3.1 In AQF-T System

```
Data Runtime → AI Brain → Agent Intelligence (23)
                              ↓
                    World Model (24) ← 本模块
                              ↓
                  Counterfactual Engine
                              ↓
                    Decision Intelligence
                              ↓
                 Risk / Strategy / Execution
```

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 2.1]

### 3.2 Relationship with AI Brain

AI Brain 负责 **"预测未来"**。World Model 负责 **"理解现在"**。

```
AI Brain Prediction Engine
          ↑
Market State Space (World Model)
          ↓
Current Market Understanding
```

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 2 + AI Brain Design V2.8.6]

### 3.3 Relationship with P4 Evolution

```
P4 Learning → P4 Knowledge → P4 Decision → World Model → P4 Governance
```

World Model 是 P4 自进化系统的认知核心。

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 2.2]

---

## 4. World Model Philosophy

### 4.1 Three Core Principles

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 3.1]

**Principle 1: Reality Modeling — 建模市场现实**

市场不是价格序列。市场是动态状态空间。

**Principle 2: Scenario Generation — 生成未来可能**

不是预测一个结果，而是生成多个可能的未来世界分支。

**Principle 3: Counterfactual Reasoning — 理解不同选择的后果**

"如果我当时做了不同的选择，结果会怎样？"

### 4.2 Market as Dynamic System

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 3.2 + `AQFT_Market_State_Space_Design_V1.0`]

```
传统：Input → Model → Output (UP/DOWN)
AQF-T：State → World Model → Multiple Futures → Reasoning → Optimal Action
```

### 4.3 Environment Context Awareness

[Source: `AQFT_Environment_Model_Design_V3.0.0` — Chapter 1]

两个市场状态可能数值相近，但属于完全不同的环境。

> 示例：指数上涨 + 成交放大。世界A：牛市启动，资金流入，风险低。世界B：熊市反弹，机构派发，风险高。

状态相似，世界不同。Environment Model 负责区分。

---

## 5. Overall Architecture — Five Layers

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 4]

```
                 AQF-T WORLD MODEL V2.9.0
                         ↑
              Decision Intelligence
                         ↑
         Layer 5: Simulation Memory
                         ↑
         Layer 4: Counterfactual Engine
                         ↑
         Layer 3: Scenario Simulation
                         ↑
         Layer 2: Market Dynamics Model
                         ↑
         Layer 1: Market State Representation
                         ↑
            Data / Agent / Environment
```

| Layer | Name | Function | V2.9 Module |
|-------|------|----------|-------------|
| L1 | Market State Representation | 9-dimension state vector S(t) | 02_State_Model ✅ |
| L2 | Market Dynamics Model | State transition P(S_{t+1}\|S_t,A_t,E_t) | 03_Belief ⏳ + 04_Regime ⏳ |
| L3 | Scenario Simulation | Multi-future world tree generation | 05_Simulation ⏳ |
| L4 | Counterfactual Engine | "What if I chose differently?" | 05_Simulation ⏳ |
| L5 | Simulation Memory | Experience accumulation & retrieval | 05_Simulation ⏳ |

---

## 6. Module Relationship

### 6.1 V2.9.0 Sub-modules

```
01_Architecture/   ← 本文件 — Intelligence Spec
        ↓
02_State_Model/    ✅ Market State Space + State Vector
        ↓
03_Belief_Model/   ⏳ Belief State Engine (hidden state inference)
        ↓
04_Regime_Model/   ⏳ Regime Model (market phase classification)
        ↓
05_Simulation/     ⏳ Scenario Simulation + Counterfactual + Memory
        ↓
06_Interface/      ⏳ World Model API
```

### 6.2 External Dependencies

| Upstream | Provides |
|----------|----------|
| Data Runtime | Market data, L2 data, fund flow |
| AI Brain | Model predictions, sentiment signals |

| Downstream | Consumes |
|------------|----------|
| Decision Intelligence | World state, scenarios, counterfactuals |
| Strategy Runtime | Market regime, risk assessment |
| Evolution System | Performance feedback, learning signals |

---

## 7. Core Components

[Source: `AQFT_World_Model_Market_Simulation_Design_V3.0.0` — Chapter 3 + `AQFT_Market_World_Model_Design_V3.0.0`]

### 7.1 Market Model

```
market_world_model/
├── state_encoder/          # 原始数据 → 状态向量
├── regime_detector/        # 市场环境识别
├── dynamics_model/         # 状态转移建模
├── causal_graph/           # 市场因果图
├── market_memory/          # 市场状态记忆
└── world_state_manager/    # 世界状态管理器
```

### 7.2 Environment Model

```
environment_model/
├── regime_environment/      # 市场周期环境
├── macro_environment/       # 宏观政策环境
├── capital_environment/     # 资金流环境
├── policy_environment/      # 制度政策环境
├── sentiment_environment/   # 市场情绪环境
├── environment_encoder/     # 环境向量编码
└── environment_memory/      # 环境历史记忆
```

### 7.3 Scenario Simulation Engine

核心对象：Scenario Universe Ω = {W₁, W₂, W₃, ..., Wₙ}

每一个 W_i 代表一个未来市场世界。不预测唯一未来 — 生成多条可能路径。

### 7.4 Counterfactual Intelligence

核心问题："如果我当时做了不同的选择，结果会怎样？"

这是 AQF-T 区别于所有传统量化系统的认知能力。

### 7.5 Simulation Memory

从 Data Memory 到 Experience Memory：

```
交易决策 → 结果发生 → 反事实分析 → 经验提取 → 记忆形成 → 未来决策优化
```

---

## 8. Data Flow

[Source: Composite from all Blueprint docs]

```
Market Data (QMT + L2)
        ↓
Feature Engineering
        ↓
Market State Vector S(t) ──────── [L1: 02_State_Model ✅]
        ↓
Belief State Engine ────────────── [L2: 03_Belief_Model ⏳]
        ↓
Regime Model ───────────────────── [L2: 04_Regime_Model ⏳]
        ↓
Scenario Simulation ────────────── [L3: 05_Simulation ⏳]
        ↓
Counterfactual Reasoning ───────── [L4: 05_Simulation ⏳]
        ↓
Simulation Memory ──────────────── [L5: 05_Simulation ⏳]
        ↓
Decision Intelligence
        ↓
Strategy / Risk / Execution
```

---

## 9. State Model Relationship

[Source: `AQFT_Market_State_Space_Design_V1.0.md` + `AQFT_State_Vector_Definition_V1.0.md`]

**V2.9.0 已完成**:

- Market State Space: 9-dimension state space S(t) = [S₁...S₉]
- State Vector: Full schema, Python dataclass, API, storage

State Model 是 World Model 的认知基础。所有上层模块（Belief、Regime、Simulation）都建立在 S(t) 之上。

---

## 10. Belief Model Relationship

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 5]

Belief State Engine 负责从可观测的 Market State 推断不可直接观测的隐状态（hidden state）。

- 输入：S(t) + Observations(t)
- 输出：Belief State B(t) with confidence
- 方法：[NEEDS ARCHITECT REVIEW] — Bayesian Filtering / Particle Filter / VAE 待 ChatGPT 确定

---

## 11. Regime Model Relationship

[Source: `AQFT_Market_World_Model_Design_V3.0.0` — Chapter 4]

10 Regime Types defined in Blueprint (World-001 to World-010).

Regime 分类映射到 AQF-T V2.9 简化版 7 体制：

| ID | 名称 | 特征 |
|----|------|------|
| R0 | Neutral | Sideways, Low Volume |
| R1 | Accumulation | 吸筹 |
| R2 | Expansion | 扩张 |
| R3 | Mania | 狂热 |
| R4 | Distribution | 派发 |
| R5 | Panic | 恐慌 |
| R6 | Recovery | 恢复 |

Regime 识别流程：Market Data → Feature Extraction → State Encoder → Regime Classifier → Regime ID + Confidence

---

## 12. Simulation Relationship

[Source: `AQFT_Scenario_Simulation_Engine_Design_V3.0.0` + `AQFT_Counterfactual_Intelligence_Engine_Design_V3.0.0`]

### Scenario Simulation

```
Current World + Environment + Dynamics → Future World Tree → Scenario Universe
```

核心：不是预测单一未来，而是生成 Scenario Universe。

### Counterfactual Reasoning

```
Actual World → Counterfactual Clone → "What if I chose differently?" → Alternative Outcome
```

这是 AQF-T 实现自主学习的关键认知能力。

---

## 13. Decision Intelligence Relationship

[Source: `AQFT_AGI_Decision_Architecture_Design_V3.0.0`]

Decision Intelligence 不直接读取原始数据。它接收 World Model 的认知输出：

```
World Model → State + Regime + Scenarios + Counterfactuals → Decision Engine
```

决策公式：U(A) = Expected Return - Risk Penalty + Knowledge Gain - Uncertainty Cost

---

## 14. Engineering Boundary

### 14.1 Target Scale

| 维度 | 上限 |
|------|------|
| 并发标的 | ≤ 50 |
| 数据频率 | Tick ~ Daily |
| 模型参数 | ≤ 100M |
| 推理延迟 | ≥ 100ms（非高频） |
| 存储 | Local PostgreSQL + Time-series DB |
| 计算 | Single Workstation (CPU + 1 GPU) |

### 14.2 Explicitly NOT Designing For

- ❌ 毫秒级高频交易
- ❌ 分布式计算集群
- ❌ 千亿参数模型
- ❌ 机构级另类数据平台
- ❌ Citadel / Renaissance 级基础设施

---

## 15. Interface Requirement

### 15.1 World Model Input

From Data Runtime: price, volume, L2 order book, fund flow, sentiment data.

### 15.2 World Model Output

To Decision Intelligence + AI Brain + Strategy Runtime:

- Market State S(t)
- Belief State B(t)
- Current Regime + confidence
- Scenario forecasts
- Counterfactual analysis

### 15.3 API Design (Preliminary)

```
GET  /api/v1/world-model/state/current
GET  /api/v1/world-model/state/history
POST /api/v1/world-model/simulate
POST /api/v1/world-model/counterfactual
```

**[NEEDS ARCHITECT REVIEW]** — Full API specification deferred to 06_Interface module.

---

## 16. Testing Requirement

### 16.1 Unit Testing

- Each layer (L1-L5) independently testable
- State computation correctness
- Regime classification accuracy
- Scenario generation validity

### 16.2 Historical Replay

- Cover: Bull / Bear / Sideways / Emotion Climax / Emotion Crash
- Cover: at least 3 complete A-share cycles (2015, 2018, 2020-2022, 2024)

### 16.3 Integration Testing

- End-to-end: Market State → Belief → Regime → Scenario → Decision
- Interface contract validation

### 16.4 Scenario Stress Testing

- Extreme events (2015 crash, 2020 COVID, 2024 policy shock)
- Regime transitions (Mania → Panic, Distribution → Accumulation)

---

## 17. Freeze Criteria

World Model Intelligence Spec V2.9.0 冻结条件：

1. **Architecture Review Passed** — 与 Constitution V2.8.6 一致
2. **All 6 sub-modules completed** — 01 through 06 all at FINAL DESIGN
3. **Interface consistency** — 输入/输出契约对齐 AI Brain + Decision
4. **Engineering readiness** — 数据结构、API、类设计明确到可编码
5. **A-share applicability** — 游资/中小私募/个人量化适用性确认
6. **No institutional scope creep** — 未引入大型机构基础设施

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-4 | `AQFT_World_Model_Architecture_V3.0.0` |
| 5 | `AQFT_World_Model_Architecture_V3.0.0` Ch.4 + `AQFT_Market_Simulation_Design_V3.0.0` Ch.3 |
| 6-7 | `AQFT_Market_World_Model_Design_V3.0.0` + `AQFT_Environment_Model_Design_V3.0.0` |
| 8 | Composite from all Blueprint docs |
| 9 | `AQFT_Market_State_Space_Design_V1.0.md` (V2.9 completed) |
| 10-11 | `AQFT_World_Model_Architecture_V3.0.0` Ch.5 + `AQFT_Market_World_Model_Design_V3.0.0` Ch.4 |
| 12 | `AQFT_Scenario_Simulation_Engine_Design_V3.0.0` + `AQFT_Counterfactual_Intelligence_Engine_Design_V3.0.0` |
| 13 | `AQFT_AGI_Decision_Architecture_Design_V3.0.0` |
| 14-17 | Inferred from Blueprint principles + V2.9 Design Principles |

---

## Architect Review Resolution (2026-07-27)

| # | Item | Decision |
|---|------|----------|
| 1 | Belief Engine algorithm | Deferred to Implementation. Architecture is model-agnostic. |
| 2 | Full API specification | Deferred to 06_Interface module. |
| 3 | Scenario generation method | Deferred to 05_Simulation module. |
| 4 | Compute budget | **Confirmed**: Personal Workstation, local GPU optional, CPU-friendly. No distributed/supercomputer. |
| 5 | Embedding dimension | Deferred to V2.9.2 Memory System. |

**Architect Review: PASSED ✅**

---

*AQF-T World Model Intelligence Specification V2.9.0 — ENGINEERING DRAFT*  
*Source: 7 Blueprint documents from 24_World_Model_System/*  
*No original design added. All content traceable to V3.0.0 Blueprint.*
