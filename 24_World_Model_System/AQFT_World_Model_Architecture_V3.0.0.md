# AQFT World Model Architecture V3.0.0


# AQF-T 世界模型认知架构设计


Version:

V3.0.0


Status:

Cognitive Architecture Design


Classification:

AQF-T 世界模型宪法级设计文件


Date:

2026-07-26


---

# 第一章 设计动机


## 1.1 为什么需要世界模型


传统量化系统：

Market Data → Factor → Strategy → Execution



问题：

系统只知道"过去发生了什么"，不理解"现在处于什么世界"，无法推演"未来可能怎样"。



AQF-T World Model 的目标：

从 Price Predictor 升级为 Market Reality Simulator



## 1.2 核心跃迁


| 传统系统 | AQF-T World Model |
|---------|-------------------|
| 预测涨跌 | 理解市场状态 |
| 单一路径推演 | 多世界分支模拟 |
| 线性因果 | 反事实推理 |
| 无记忆 | 模拟经验积累 |
| 黑箱输出 | 可解释状态空间 |



---

# 第二章 在 AQF-T 中的定位


## 2.1 架构位置


```
Data Runtime → AI Brain → Agent Intelligence (23)
                              ↓
                    World Model (24) ← 本文件
                              ↓
                  Counterfactual Engine
                              ↓
                    Decision Intelligence
                              ↓
                 Risk / Strategy / Execution
```



## 2.2 与 P4 Evolution 的关系


P4 Learning → P4 Knowledge → P4 Decision → World Model → P4 Governance


World Model 是 P4 自进化系统的"认知核心"。



---

# 第三章 核心哲学


## 3.1 三大原则


### Reality Modeling — 建模市场现实

市场不是价格序列。市场是动态状态空间。


### Scenario Generation — 生成未来可能

不是预测一个结果。而是生成多个可能的未来世界分支。


### Counterfactual Reasoning — 理解不同选择的后果

"如果我当时做了不同的选择，结果会怎样？"



---

## 3.2 与传统预测的本质区别


传统：Input → Model → Output (UP/DOWN)

AQF-T：State → World Model → Multiple Futures → Reasoning → Optimal Action



---

# 第四章 五层总体架构


```
                 AQF-T WORLD MODEL V3.0.0

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



---

# 第五章 Layer 1: Market State Representation


## 5.1 市场状态向量


S(t) = [


### Price State

价格水平 / 趋势强度 / 支撑阻力


### Liquidity State

成交量 / 买卖价差 / 市场深度 / 资金流向


### Volatility State

历史波动率 / 隐含波动 / 波动率曲面


### Capital Flow State

主力资金 / 散户资金 / 北向资金 / 融资融券


### Institution Behavior

机构持仓变化 / 大宗交易 / 期权异动


### Retail Emotion

散户情绪 / 社交媒体热度 / 搜索趋势


### Policy Environment

货币政策 / 财政政策 / 监管变化 / 国际关系


### Macro Context

GDP / CPI / PMI / 利率 / 汇率


### Sector Rotation

行业轮动 / 风格切换 / 主题热度


### Market Regime

牛市 / 熊市 / 震荡 / 危机 / 复苏

]



---

## 5.2 状态编码器


State Encoder: Raw Data → Market State Vector


输出维度：可配置（默认 256-dim embedding）



---

# 第六章 Layer 2: Market Dynamics Model


## 6.1 市场动力学


市场不是静止的，状态随时间演化。


动力学方程：

S(t+1) = f( S(t), A(t), E(t) )


其中：

- S(t) — 当前市场状态
- A(t) — Agent 行为（买入/卖出/持仓）
- E(t) — 外部事件（政策/黑天鹅/资金冲击）



---

## 6.2 环境模型


回答核心问题：现在市场处于什么世界？


Regime Types：

- Bull Market World — 牛市环境
- Bear Market World — 熊市环境
- Liquidity Crisis World — 流动性危机
- Policy Stimulus World — 政策刺激
- AI Bubble World — AI 泡沫
- Rate Cut World — 降息周期
- Black Swan World — 黑天鹅事件



---

# 第七章 Layer 3: Scenario Simulation


## 7.1 情景生成


不是预测单一未来，而是生成多个可能的未来世界分支。


Given: 当前市场状态 S(t)


Generate:

Scenario A: Continuing Trend

Scenario B: Reversal

Scenario C: Sideways

Scenario D: Volatility Explosion

Scenario E: Liquidity Evaporation



## 7.2 情景概率


每个 Scenario 附带：

- probability — 发生概率
- confidence — 置信度
- impact — 对持仓的影响
- risk_level — 风险等级



---

# 第八章 Layer 4: Counterfactual Engine


## 8.1 定位


这是 AQF-T 区分于所有传统量化系统的核心。


传统：如果买入会怎样？（单一路径回测）

AQF-T：如果当时做出不同选择，世界会如何演化？（反事实推理）



## 8.2 反事实问题类型


- 如果降低仓位 20%，最大回撤会减少多少？
- 如果提前 3 天退出，收益曲线如何变化？
- 如果风险阈值提高，哪些亏损交易会避免？
- 如果资金流反转，策略何时失效？
- 如果在 2024-02 流动性危机中使用当前策略，结果如何？



## 8.3 反事实推理流程


Observed History → Build World Model → Create Counterfactual Branch → Simulate Alternative → Compare Outcomes → Learn Lesson



---

# 第九章 Layer 5: Simulation Memory


## 9.1 定位


没有记忆的世界模型只是预测器。


Simulation Memory 负责：

- 保存每一次模拟的结果
- 保存反事实推理的经验
- 形成可检索的"市场经验库"



## 9.2 记忆结构


### Historical Experiences

真实发生过的事件和结果


### Synthetic Scenarios

AI 生成的极端情景


### Decision Outcomes

每次决策的结果记录


### Counterfactual Results

反事实推演的经验



## 9.3 记忆检索


Agent 调用：


"过去类似环境中：

- 发生了什么？
- 当时采取什么策略？
- 结果如何？
- 风险是什么？"



---

# 第十章 数据模型


## 10.1 MarketState 定义


```
MarketState:
  timestamp: UTC
  regime: Bull | Bear | Sideway | Crisis
  liquidity: 0-1
  volatility: 0-1
  sentiment: 0-1 (Fear ↔ Greed)
  capital_flow: 0-1 (Outflow ↔ Inflow)
  policy_factor: 0-1
  sector_state: vector
  embedding: 256-dim vector
```



---

## 10.2 SimulationResult 定义


```
SimulationResult:
  scenario_id: UUID
  initial_state: MarketState
  action: BUY | SELL | HOLD
  horizon: timesteps
  future_states: [MarketState]
  probability: 0-1
  risk_score: 0-100
  confidence: 0-1
```



---

# 第十一章 与 Agent 系统的交互接口


## 11.1 Agent → World Model



Request:

```
agent.simulate(
  state: CurrentMarketState,
  action: ProposedAction,
  horizon: 20
)
```



Response:

```
[
  Scenario A: 60% probability, Risk 20, Bull continues
  Scenario B: 25% probability, Risk 55, Reversal
  Scenario C: 15% probability, Risk 80, Volatility explosion
]
```



---

## 11.2 Counterfactual 接口


```
agent.counterfactual(
  "What if we reduced position by 20% in the last drawdown?"
)

→ Max drawdown reduced by 35%
→ Total return reduced by 8%
→ Sharpe ratio improved by 0.3
```



---

# 第十二章 验证体系


## 12.1 世界模型验证


- State Representation Quality — 状态向量能否区分不同市场环境
- Dynamics Prediction Accuracy — 状态转移预测准确率
- Scenario Coverage — 情景生成是否覆盖关键风险事件
- Counterfactual Plausibility — 反事实推演是否符合市场逻辑



## 12.2 持续验证


每次交易后：

Actual Outcome vs Predicted Scenarios → Feedback → Model Improvement



---

# 第十三章 演化路线


| 版本 | 能力 | 状态 |
|------|------|------|
| V3.0.0 | World Model Architecture | 🔄 Design |
| V3.1.0 | State Representation + Dynamics | ⏳ |
| V3.2.0 | Scenario Simulation + Counterfactual | ⏳ |
| V3.3.0 | Simulation Memory + Agent Integration | ⏳ |
| V4.0.0 | AGI Decision Layer | 🎯 |



---

# 第十四章 与其他模块的关系


| 模块 | 关系 |
|------|------|
| 23_Agent_System | Agent 调用 World Model 进行情景模拟 |
| 22_Evolution | World Model 的经验反馈给 Learning Engine |
| 20_Simulation | World Model 提供市场环境给 Simulation |
| 16_AI_Runtime | AI 预测结果输入 World Model 作为先验 |
| 05_Risk | 反事实推演帮助 Risk 评估极端情景 |



---

# 第十五章 设计冻结声明


本文件定义 AQF-T World Model V3.0.0 认知架构。


World Model 不是预测器，而是市场现实模拟器。


它使 AQF-T 具备：

State → Understand → Simulate → Counterfactual → Remember → Decide


的完整认知闭环。


这是 AQF-T 从 Quantitative Trading System 向 Autonomous Market Intelligence System 跃迁的关键节点。



Version:

V3.0.0


Status:

Cognitive Architecture Design


END OF AQF-T WORLD MODEL ARCHITECTURE
