# AQFT Environment Model Design V3.0.0


# AQF-T 市场环境模型设计


Version:

V3.0.0


Status:

Engineering Design


Classification:

AQF-T World Model 环境认知层设计文件


Date:

2026-07-26


---

# 第一章 模块定位


## 1.1 为什么需要 Environment Model


Market World Model 回答：

"市场现在是什么状态？"


Environment Model 回答：

"这个状态属于什么环境？"



## 1.2 State ≠ Environment


两个市场状态可能数值相近，但属于完全不同的环境。


示例：

指数上涨 + 成交放大


世界 A：牛市启动，资金流入，风险低

世界 B：熊市反弹，机构派发，风险高


状态相似，世界不同。错误的判断导致错误的策略。



## 1.3 在 World Model 中的位置


Market World Model (State) → Environment Model (Context) ← 本文件 → Scenario Engine → Counterfactual Engine



---

# 第二章 模块架构


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



---

# 第三章 Layer 1: Market Regime Environment


## 3.1 市场周期


```
Bull Expansion     →  趋势向上 + 资金流入 + 波动降低
Bull Mature        →  趋势向上 + 分歧增加 + 波动上升
Distribution       →  趋势走平 + 机构出货 + 量价背离
Bear Decline       →  趋势向下 + 资金流出 + 波动上升
Capitulation       →  恐慌抛售 + 流动性枯竭 + 极端波动
Accumulation       →  底部盘整 + 机构吸筹 + 波动降低
Recovery           →  趋势转好 + 信心恢复 + 温和上涨
```



## 3.2 与 Regime Detector 的关系


复用 Market World Model 的 Regime Detector（World-001 ~ World-010）。

Environment Model 在此之上增加**周期位置判断**和**阶段转换概率**。



---

# 第四章 Layer 2: Macro Environment


## 4.1 宏观世界向量


```
MacroWorldVector:

  inflation: (deflation | low | moderate | high | hyper)
  interest_rate: (falling | stable | rising | peak)
  currency: (weakening | stable | strengthening)
  gdp_cycle: (expansion | peak | contraction | trough)
  policy_cycle: (tightening | neutral | easing | emergency)
  global_risk: 0-100
  credit_cycle: (expanding | stable | contracting)
```



## 4.2 宏观环境解释


不是简单数据，而是环境语义：


2024 示例：

China: Policy Support + US Rate High + Global Liquidity Tight + AI Theme Expansion



---

# 第五章 Layer 3: Capital Environment


## 5.1 资金世界


```
CapitalFlowWorld:

  institution_flow:
    direction: (inflow | neutral | outflow)
    intensity: 0-1
    sector_focus: [sector_ids]

  north_bound:
    direction: (inflow | neutral | outflow)
    amount_rank: percentile

  margin_trading:
    balance_trend: (increasing | stable | decreasing)
    leverage_level: 0-1

  retail_flow:
    direction: (inflow | neutral | outflow)
    sentiment_driven: 0-1

  quant_flow:
    activity_level: 0-1
    strategy_type: (trend | mean_reversion | arbitrage)

  corporate_flow:
    buyback: 0-1
    ipo_pace: 0-1
```



## 5.2 资金环境类型


- 机构吸筹世界 — Institution↑ Retail↓ Liquidity↑ Volatility↓
- 散户狂热世界 — Retail↑ Institution↓ Volume↑ Risk↑
- 量化主导世界 — Quant↑ Spread↓ Volatility↓
- 资金撤退世界 — All↓ Liquidity↓ Risk↑
- 外资流入世界 — North↑ Currency↑ BlueChip↑



---

# 第六章 Layer 4: Policy Environment


## 6.1 政策世界


```
PolicyWorld:

  monetary:
    stance: (tightening | neutral | easing)
    rate_direction: (-1 | 0 | +1)
    liquidity_operation: (drain | neutral | inject)

  fiscal:
    stance: (austerity | neutral | stimulus)
    infra_spending: 0-1
    tax_policy: (increase | neutral | reduce)

  regulatory:
    financial: (tightening | neutral | liberalizing)
    sector_specific: {sector_id: policy_stance}

  geo_political:
    stability: 0-100
    trade_relation: (conflict | neutral | cooperation)
```



## 6.2 政策环境类型


- Neutral — 中性政策
- Stimulus — 政策刺激（流动性注入 + 财政扩张）
- Restriction — 政策收紧（去杠杆 + 监管强化）
- Emergency — 紧急干预（市场异常 + 临时措施）
- Transition — 政策转向（预期变化 + 不确定性高）



---

# 第七章 Layer 5: Environment Memory


## 7.1 环境记忆


回答核心问题：

"历史上有没有出现过类似的世界？"



## 7.2 检索流程


Current Environment → Environment Encoder → Vector Search → Similar Historical Worlds → Output Comparison



## 7.3 输出示例


```
当前环境:
  政策刺激 + 流动性改善 + AI 主题

历史类似世界:
  1. 2015 创业板行情 — 相似度 0.78
     平均上涨 28%, 最大回撤 35%, 持续 180 天

  2. 2020 疫情后科技 — 相似度 0.82
     平均上涨 45%, 最大回撤 22%, 持续 240 天

  3. 2023 AI 行情 — 相似度 0.91
     平均上涨 32%, 最大回撤 18%, 持续 120 天

综合参考:
  expected_return: +25~45%
  expected_drawdown: 18~35%
  expected_duration: 120~240 天
  risk_level: Medium-High
```



---

# 第八章 Environment Encoder


## 8.1 环境编码


将五层环境信息编码为统一向量：


Regime + Macro + Capital + Policy + Sentiment → Environment Embedding (512-dim)



## 8.2 用途


- 环境相似度检索
- Scenario Engine 输入
- Agent 环境感知
- Risk 环境风险评估



---

# 第九章 与 Scenario Engine 的接口


Environment Model 输出 → Scenario Engine 输入


```
Environment Model 输出:
  current_regime: "Bull_Expansion"
  macro_vector: [...]
  capital_state: "Institution_Accumulating"
  policy_stance: "Stimulus"
  similar_histories: [...]

Scenario Engine 使用:
  "在 Bull_Expansion + Stimulus 环境中，
   未来 20 天可能出现哪些情景？"
```



---

# 第十章 数据流


```
Market World Model → State Vector
                           ↓
Regime Detector → Macro Data → Capital Data → Policy Data → Sentiment Data
                           ↓
                   Environment Encoder
                           ↓
                  Environment Embedding (512-dim)
                           ↓
              ┌────────────┼────────────┐
              │            │            │
        Regime Class   Env Memory    Risk Context
              │            │            │
              └────────────┼────────────┘
                           ↓
                   Scenario Engine
```



---

# 第十一章 验证标准


- Regime 识别准确率: ≥ 85%
- Macro Environment 分类: ≥ 80%
- Capital Flow 方向判断: ≥ 75%
- 历史相似环境检索 Top-3 相关度: ≥ 0.75
- Environment Embedding 同环境聚类纯度: ≥ 0.80



---

# 第十二章 设计冻结声明


本文件定义 AQF-T Environment Model V3.0.0。


Environment Model 是 World Model 的"高层语义理解层"。

它回答："当前市场处于什么样的世界中？"以及"历史上是否有类似的世界？"


这是连接 Market State → Scenario Generation → Counterfactual Reasoning 的关键认知桥梁。



Version:

V3.0.0


Status:

Engineering Design


END OF AQFT ENVIRONMENT MODEL DESIGN
