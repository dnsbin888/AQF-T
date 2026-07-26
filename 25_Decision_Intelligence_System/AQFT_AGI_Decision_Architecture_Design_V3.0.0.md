# AQFT Decision Intelligence Design V3.6.0


# AQF-T 决策智能系统详细设计


Version: V3.6.0 | Status: Detailed Engineering Design
Date: 2026-07-26

> 参考: TradingGroup Decision Agent + HedgeAgents 会议机制 + FinRL-X 权重中心化


---

# 第一章 定位


Decision Intelligence 是 AQF-T 的最高决策层。融合 World Model + Multi-Agent + Risk 的输出，选择最优行动。

```
World Model(认知) + Agent Council(分析) → Decision Engine(选择) → Action
```

---

# 第二章 决策流水线


```
Input: World State + Agent Consensus + Risk Assessment + Experience Memory
       │
       ▼
  Scenario Evaluation (来自 World Model: 当前环境下各Scenario的概率+风险)
       │
       ▼
  Action Generation (六级行动空间: Observe/Hold/Increase/Reduce/Hedge/Exit)
       │
       ▼
  Counterfactual Verification (如果选择A vs 选择B, 后果差异?)
       │
       ▼
  Decision Optimization (U(A) = Return - Risk + Knowledge - Uncertainty)
       │
       ▼
  Output: Optimal Action + Confidence + Reasoning Trace
```

---

# 第三章 预期效用决策


借鉴经济学决策理论:

```
A* = argmax E[U(A)]

U(A) = Expected Return - Risk Penalty + Knowledge Gain - Uncertainty Cost

其中:
  Expected Return: Scenario概率 × Scenario收益
  Risk Penalty: Risk Score × Risk厌恶系数
  Knowledge Gain: 选择此行动能学到多少(探索vs利用)
  Uncertainty Cost: 预测不确定性惩罚(高不确定性→偏向保守)
```

---

# 第四章 游资决策特化


## 4.1 情绪周期覆盖

```
情绪周期 → 决策倾向:
  冰点期: Observe优先, 试错小仓
  回暖期: Increase优先, Dragon策略激活
  高潮期: Hold+Increase, 重仓龙头
  退潮期: Reduce+Exit优先, 禁止新开仓
```

## 4.2 涨停板特殊决策

```
持有涨停股时:
  封单强度 > 5% + 题材热度 > 0.7 → Hold
  封单骤降 > 50% + 炸板 → Exit (市价卖出)
  连板≥11 + 异动警告 → Reduce (减仓50%)
```

---

# 第五章 决策审计


每条决策记录:

```
DecisionRecord:
  decision_id: UUID
  world_state_snapshot: MarketWorldState
  agent_votes: {agent_name: vote}
  scenarios_considered: [ScenarioResult]
  counterfactual_comparisons: [CounterfactualResult]
  chosen_action: Action
  expected_value: float
  reasoning_trace: [str]        # 人类可读的推理链
  confidence: float
  outcome: (回填)实际结果
  lesson: (回填)经验教训
```

---

# 第六章 API


| 端点 | 方法 | 功能 |
|------|:---:|------|
| POST /decision/evaluate | POST | 决策评估 |
| GET /decision/history | GET | 决策历史 |
| GET /decision/{id}/trace | GET | 决策推理链 |
| GET /decision/performance | GET | 决策绩效 |

---

# 第七章 设计冻结声明


本文件定义 AQF-T Decision Intelligence V3.6.0。

借鉴 TradingGroup Decision Agent + HedgeAgents 会议融合 + FinRL-X 权重中心化 + 经济学预期效用理论。

游资特化: 情绪周期覆盖 + 涨停板特殊决策 + 完整决策审计。

Version: V3.6.0 | Status: Detailed Engineering Design
END OF AQFT DECISION INTELLIGENCE DESIGN
