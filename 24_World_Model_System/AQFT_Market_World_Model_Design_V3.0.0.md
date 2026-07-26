# AQFT Market World Model Design V3.0.0


# AQF-T 市场世界模型核心设计


Version:

V3.0.0


Status:

Engineering Design


Classification:

AQF-T 世界模型第一核心子模块设计文件


Date:

2026-07-26


---

# 第一章 模块定位


## 1.1 定义


Market World Model = AQF-T 对市场现实的内部认知模型


负责：

- 市场状态理解
- 市场机制建模
- 状态转移预测
- 环境识别


它不是预测器，而是 AQF-T 的"市场世界观"。



## 1.2 在 World Model 五层中的位置


本模块覆盖 Layer 1 + Layer 2：

Layer 1: State Representation — State Encoder
Layer 2: Dynamics Model — Dynamics Engine + Causal Graph


上层依赖：

Scenario Simulation → 依赖本模块的状态转移输出

Counterfactual Engine → 依赖本模块的因果图



---

# 第二章 模块架构


```
market_world_model/

├── state_encoder/          # 原始数据 → 状态向量
├── regime_detector/        # 市场环境识别
├── dynamics_model/         # 状态转移建模
├── causal_graph/           # 市场因果图
├── market_memory/          # 市场状态记忆
└── world_state_manager/    # 世界状态管理器
```



---

# 第三章 Market World State


## 3.1 市场世界状态对象


```
MarketWorldState:

  timestamp: UTC

  market_regime:
    trend_state: Bull | Bear | Neutral
    phase: Early | Mid | Late | Transition
    confidence: 0-1

  liquidity_state:
    money_flow: 0-1 (Outflow ↔ Inflow)
    market_depth: 0-1 (Shallow ↔ Deep)
    turnover: 0-1 (Low ↔ High)
    spread: 0-1 (Tight ↔ Wide)

  participant_state:
    institution: (accumulating | distributing | neutral)
    retail: (fearful | greedy | neutral)
    quant: (trend_following | mean_reversion | neutral)

  emotion_state:
    fear_index: 0-100
    greed_index: 0-100
    confidence_index: 0-100
    panic_level: 0-100

  macro_state:
    policy_direction: (tightening | neutral | easing)
    economic_cycle: (expansion | peak | contraction | trough)
    global_risk: 0-100

  risk_state:
    volatility: 0-100
    drawdown_risk: 0-100
    tail_probability: 0-100
    systemic_risk: 0-100

  embedding:
    vector: [768]
    version: str
```



---

# 第四章 Regime Recognition Engine


## 4.1 定位


判断当前处于哪个市场世界。



## 4.2 Market Regime Universe


| Regime ID | 名称 | 特征 |
|-----------|------|------|
| World-001 | 牛市扩散 | Trend UP + Liquidity HIGH + Greed |
| World-002 | 牛市加速 | Trend UP + Liquidity HIGH + FOMO |
| World-003 | 牛市尾部 | Trend UP + Divergence + Distribution |
| World-004 | 熊市初期 | Trend DOWN + Liquidity DROP + Fear |
| World-005 | 熊市恐慌 | Trend DOWN + Liquidity DRY + Panic |
| World-006 | 熊市筑底 | Trend FLAT + Accumulation + Low Confidence |
| World-007 | 流动性收缩 | Liquidity DROP + Volatility UP |
| World-008 | 政策驱动 | Policy CHANGE + Sector Rotation |
| World-009 | 风险释放 | Volatility SPIKE + Drawdown |
| World-010 | 震荡等待 | Sideways + Low Volume + Neutral |



## 4.3 Regime 识别流程


Market Data → Feature Extraction → State Encoder → Regime Classifier → Regime ID + Confidence



---

# 第五章 Market Dynamics Model


## 5.1 状态转移


$$
P(S_{t+1} \mid S_t, A_t, E_t)
$$


其中：

- S_t — 当前市场世界状态
- A_t — Agent 行为向量
- E_t — 外部事件向量



## 5.2 输出


不是"明天涨/跌"，而是未来状态分布：


上涨世界 55%

震荡世界 30%

风险世界 15%



## 5.3 Dynamics 学习


学习来源：

- 历史状态转移数据
- World Model 模拟经验
- 反事实推演反馈



---

# 第六章 Causal Market Graph


## 6.1 市场因果图


```
政策 (Policy)
    ↓
流动性 (Liquidity)
    ↓
资金流 (Capital Flow)
    ↓              ↓
行业轮动        市场情绪
(Sector)        (Sentiment)
    ↓              ↓
个股价格 ←──→ 市场指数
(Price)       (Index)
```



## 6.2 因果边


每条边包含：

- direction — 因果方向
- strength — 因果强度 (0-1)
- lag — 时滞 (天)
- confidence — 置信度


示例：

Policy → Liquidity: strength=0.82, lag=3d, confidence=0.91



## 6.3 因果图用途


Counterfactual Engine 依赖此图：

"如果政策没有收紧，流动性会如何？"


Causal Graph → Do-calculus → Counterfactual State



---

# 第七章 API 设计


## 7.1 获取当前世界状态


```
GET /world/state/current


Response:
  regime: "liquidity_expansion"
  confidence: 0.87
  risk_level: 32
  embedding_version: "v3.0.0"
```



## 7.2 推演未来


```
POST /world/simulate


Request:
  state: MarketWorldState
  action: ProposedAction
  horizon: 20


Response:
  scenarios:
    - name: "trend_continue"
      probability: 0.62
      states: [...]
      risk: 25
    - name: "volatility_spike"
      probability: 0.18
      states: [...]
      risk: 68
```



## 7.3 反事实查询


```
POST /world/counterfactual


Request:
  query: "What if position reduced 20% at T-5?"
  baseline: historical_state_sequence


Response:
  alternative_path: [...]
  comparison:
    max_drawdown: -35%
    return_diff: -8%
    sharpe_diff: +0.3
```



---

# 第八章 与现有模块连接


## 8.1 与 23 Agent System


Agent → World Model Query → State + Scenarios → Decision


Agent 在做任何决策前，先调用 World Model 获取当前世界状态和未来情景。



## 8.2 与 18 Risk Runtime


World Model 输出 Future Risk Distribution → Risk Engine 评估极端情景



## 8.3 与 22 Evolution


Simulation Result → Experience Memory → World Model Improvement



## 8.4 与 16 AI Runtime


AI Prediction 作为 World Model 的先验输入，World Model 的 State Embedding 反馈给 AI Runtime



---

# 第九章 数据流


```
External Data → State Encoder → MarketWorldState
                                    ↓
                           Regime Detector
                                    ↓
                            Dynamics Model
                                    ↓
                    ┌───────────────┼───────────────┐
                    │               │               │
              Scenario Gen    Counterfactual    Risk Estimate
                    │               │               │
                    └───────────────┼───────────────┘
                                    ↓
                            Decision Support
```



---

# 第十章 验证标准


- Regime Recognition Accuracy: ≥ 85%（区分 10 种市场世界）
- State Transfer Prediction: Top-3 Scenario 覆盖 ≥ 90% 实际情况
- Causal Edge Validation: 因果强度误差 ≤ 0.15
- Embedding Quality: 同 Regime 相似度 ≥ 0.8



---

# 第十一章 设计冻结声明


本文件定义 AQF-T Market World Model V3.0.0 核心设计。


Market World Model 是 World Model 五层架构的基础层，定义 AQF-T 如何理解市场现实。


后续 Scenario / Counterfactual / Memory 层的设计均依赖本模块。



Version:

V3.0.0


Status:

Engineering Design


END OF AQFT MARKET WORLD MODEL DESIGN
