# AQF-T Decision Intelligence Architecture

Version: V2.9.1
Status: FROZEN — V2.9.1 Decision Intelligence Freeze
Phase: V2.9 Intelligence Era — Decision Intelligence
Module: Decision_Intelligence
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Decision_Intelligence_Architecture_V2.9.1.md |
| Module | Decision Intelligence — Action Brain |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V2.9.1 |
| Parent | AQF-T V2.9.0 World Model (FROZEN) |
| Upstream | World Model ✅ + AI Brain V2.8.6 + Agent Intelligence V3.0.0 |
| Downstream | Strategy Runtime → Risk Runtime → Execution Runtime |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | AQFT_AGI_Decision_Architecture_Design_V3.0.0 (V3.6.0) |

---

## 1. Purpose

### 1.1 What Decision Intelligence Does

Decision Intelligence 是 AQF-T 的 **Action Brain（行动大脑）**。

| World Model | Decision Intelligence |
|-------------|---------------------|
| "市场是什么样的？" | "我应该怎么做？" |
| Understanding | Action |
| Cognitive Layer | Decision Layer |
| What is happening? | What should AQF-T do? |

[Source: `AQFT_AGI_Decision_Architecture_Design_V3.0.0` — Chapter 1]

### 1.2 Core Leap

```
Traditional quant:   Data → Signal → Trade
AQF-T:               World Model → Agent Council → Decision Engine → Action
```

Decision Intelligence 融合 World Model（认知）+ Multi-Agent（分析）+ Risk（约束），选择最优行动。

### 1.3 What Decision Intelligence Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 交易策略生成器 | 行动方向选择器 |
| 买卖信号输出 | 决策框架 |
| 单模型判断 | 多引擎融合决策 |
| 黑箱输出 | 可审计推理链 |
| 替代 Strategy | Strategy 的上游指挥 |

---

## 2. Scope

### 2.1 In Scope

- Multi-engine fusion decision framework
- Action selection (direction, not method)
- Confidence-calibrated decision output
- Decision audit trail with reasoning chain
- Human-AI governance interface
- Risk-aware decision optimization
- Learning feedback from decision outcomes

### 2.2 Out of Scope

- ❌ Strategy implementation (belongs to 04_Strategy)
- ❌ Order execution (belongs to 06_Execution)
- ❌ Risk rule enforcement (belongs to 05_Risk)
- ❌ Single-model buy/sell signals
- ❌ Automated trading without human governance

---

## 3. Architecture Position

### 3.1 In AQF-T System

```
                 World Model (V2.9.0 FROZEN)
                 State + Belief + Regime + Simulation
                         │
              Agent Intelligence (P5-01)
              Multi-Agent Council
                         │
              ┌──────────┴──────────┐
              │  DECISION ENGINE   │  ← 本模块
              │  (Action Brain)    │
              └──────────┬──────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         Strategy     Risk       Human-AI
         Runtime     Runtime    Governance
              │          │          │
              └──────────┼──────────┘
                         ▼
                   Execution
```

### 3.2 Decision vs Strategy — Critical Distinction

```
Decision Intelligence:  "进攻" (Attack)
Strategy Runtime:       "用龙头战法" (Use Dragon Strategy)

Decision Intelligence:  "防御" (Defend)
Strategy Runtime:       "空仓或轻仓" (Go flat or light)

Decision = Direction (What to do)
Strategy = Method (How to do it)
```

---

## 4. Decision Intelligence Philosophy

### 4.1 Core Principles

**Principle 1: Multi-Engine Fusion — No Single Model Decision**

[Source: Constitution V2.8.6 + AI Brain Design V2.8.6]

决策输入来自多引擎融合，禁止单一模型决定交易。

**Principle 2: Confidence-Driven Output**

每个决策携带置信度。低置信度 → 自动降级或暂停。

**Principle 3: Explainable Every Step**

每个决策必须回答：Why? Based on what? What's the risk? What's the alternative?

**Principle 4: Human-in-the-Loop**

AI 建议，系统约束，人最终授权。

### 4.2 Expected Utility Framework

[Source: `AQFT_AGI_Decision_Architecture_Design_V3.0.0` — Chapter 3]

```
A* = argmax E[U(A)]

U(A) = Expected_Return - Risk_Penalty + Knowledge_Gain - Uncertainty_Cost

Where:
  Expected_Return  = Σ P(Scenario_i) × Return(Scenario_i, A)
  Risk_Penalty     = Risk_Score × Risk_Aversion_Coefficient
  Knowledge_Gain   = Information value of choosing A (explore vs exploit)
  Uncertainty_Cost = Penalty for high prediction uncertainty → bias conservative
```

---

## 5. Decision Pipeline

### 5.1 Five-Stage Pipeline

[Source: `AQFT_AGI_Decision_Architecture_Design_V3.0.0` — Chapter 2]

```
Stage 1: SCENARIO EVALUATION
  Input: World Model Scenarios (from 05_Simulation)
  Output: Probability-weighted scenario landscape
         │
         ▼
Stage 2: ACTION GENERATION
  Generate candidate actions from 6-level action space
         │
         ▼
Stage 3: COUNTERFACTUAL VERIFICATION
  "If choose A vs B, what differs?"
  Leverage World Model Counterfactual Engine
         │
         ▼
Stage 4: DECISION OPTIMIZATION
  Compute U(A) for each candidate
  Select A* = argmax U(A)
         │
         ▼
Stage 5: OUTPUT
  Action + Confidence + Reasoning Trace + Alternatives
```

### 5.2 Six-Level Action Space

| Level | Action | Description |
|:-----:|--------|-------------|
| 0 | Observe | 观察，不交易 |
| 1 | Hold | 持有现有仓位 |
| 2 | Increase | 加仓 |
| 3 | Reduce | 减仓 |
| 4 | Hedge | 对冲/防守 |
| 5 | Exit | 清仓退出 |

Note: These are **directional actions**, not specific trade orders. Strategy Runtime translates them into concrete methods.

---

## 6. Multi-Model Fusion Architecture

### 6.1 Fusion Engine Integration

[Source: `AQFT_AI_Brain_Design_V2.8.6.md` — Chapter 6 Fusion Engine]

```
Decision Input Sources:
        ┌─────────────────┐
        │ Prediction Engine│ → Trend direction + probability
        ├─────────────────┤
        │ Sentiment Engine │ → Emotion phase + theme strength
        ├─────────────────┤
        │ Risk Intelligence│ → Risk score + warnings
        ├─────────────────┤
        │ Experience Memory│ → Similar past situations
        ├─────────────────┤
        │ World Model      │ → State + Belief + Regime + Scenarios
        ├─────────────────┤
        │ Agent Council    │ → Multi-agent votes + reasoning
        └─────────────────┘
                 │
                 ▼
          Fusion Engine
                 │
                 ▼
          Decision Output
```

### 6.2 Fusion Weights

```
Fusion Score =
  Prediction Output  × 0.25 +
  Sentiment Signal   × 0.25 +
  World Model Context × 0.20 +
  Risk Assessment    × 0.20 +
  Experience Memory  × 0.10
```

### 6.3 Dynamic Weight Adjustment by Regime

| Regime | Prediction | Sentiment | World Model | Risk | Experience |
|--------|:----------:|:---------:|:-----------:|:----:|:----------:|
| Expansion | 0.30 | 0.25 | 0.20 | 0.15 | 0.10 |
| Mania | 0.20 | 0.30 | 0.20 | 0.20 | 0.10 |
| Panic | 0.10 | 0.15 | 0.20 | 0.45 | 0.10 |
| Neutral | 0.25 | 0.25 | 0.20 | 0.20 | 0.10 |

[Source: AI Brain Design V2.8.6 Ch.6.3 — adapted for Decision Intelligence]

---

## 7. Decision State Representation

### 7.1 Decision Object

```json
{
  "decision_id": "DEC_20260727_093500001",
  "timestamp": "2026-07-27T09:35:00",

  "world_context": {
    "regime": "Expansion",
    "emotion_phase": "Warming",
    "risk_level": "Medium",
    "top_scenario": "Expansion continues (P=45%)"
  },

  "engine_inputs": {
    "prediction": { "direction": "UP", "probability": 0.72 },
    "sentiment": { "phase": "Warming", "score": 65 },
    "risk_intelligence": { "score": 28, "level": "Low" },
    "experience": { "similar_cases": 12, "success_rate": 0.68 }
  },

  "agent_votes": {
    "market_agent": "Increase",
    "sentiment_agent": "Increase",
    "risk_agent": "Hold",
    "decision_agent": "Increase"
  },

  "candidate_actions": [
    { "action": "Increase", "utility": 0.72, "confidence": 0.78 },
    { "action": "Hold",    "utility": 0.55, "confidence": 0.85 },
    { "action": "Reduce",  "utility": 0.20, "confidence": 0.90 }
  ],

  "chosen_action": {
    "action": "Increase",
    "confidence": 0.78,
    "reasoning_trace": [
      "Expansion regime supports aggressive posture",
      "Sentiment warming confirms momentum",
      "Risk level low (28) — risk budget available",
      "3/4 agents vote Increase"
    ],
    "risk_constraint": "Position limit 70%, max single position 20%"
  },

  "alternatives": [
    "Hold: lower return but higher certainty (confidence 0.85)"
  ]
}
```

---

## 8. Action Selection Framework

### 8.1 Action-Context Mapping

| World Context | Default Posture | Aggressive Option | Conservative Option |
|--------------|:---------------:|:-----------------:|:-------------------:|
| Expansion + Warming + Low Risk | Increase | Increase (full) | Hold |
| Mania + Climax + Medium Risk | Hold | Increase (selective) | Reduce |
| Distribution + Recession + High Risk | Reduce | Hold | Exit |
| Panic + Ice + Extreme Risk | Exit | Reduce (hedge) | Exit (full) |
| Recovery + Warming + Medium Risk | Increase (cautious) | Increase | Observe |
| Neutral + Mixed + Low Risk | Hold | Increase (light) | Hold |

### 8.2 A-Share Retail Trader Specialization

[Source: `AQFT_AGI_Decision_Architecture_Design_V3.0.0` — Chapter 4]

**Emotion Cycle → Decision Bias:**

| Emotion Phase | Decision Tendency |
|--------------|-------------------|
| 冰点 (Ice) | Observe 优先，试错小仓 |
| 回暖 (Warming) | Increase 优先，Dragon 策略激活 |
| 高潮 (Climax) | Hold + Increase，重仓龙头 |
| 退潮 (Recession) | Reduce + Exit 优先，禁止新开仓 |

**Limit-Up Special Decisions:**

```
持有涨停股时:
  封单强度 > 5% AND 题材热度 > 0.7 → Hold
  封单骤降 > 50% OR 炸板 → Exit (市价卖出)
  连板 ≥ 11 AND 异动警告 → Reduce (-50%)
```

---

## 9. Confidence Management

### 9.1 Confidence Formula

```
Decision_Confidence = f(
  Engine_Agreement,        # Do engines agree?
  Scenario_Clarity,        # Is one scenario dominant?
  Risk_Buffer,             # How much risk budget remains?
  Historical_Similarity,   # Have we seen this before?
  Data_Freshness           # Is input data current?
)
```

### 9.2 Confidence Gates

| Confidence | Action Allowed |
|:----------:|---------------|
| > 0.80 | Full execution |
| 0.60–0.80 | Execute with reduced position |
| 0.40–0.60 | Hold only (no new positions) |
| < 0.40 | Observe only (no action) |

### 9.3 Conflict Resolution

When engines disagree (e.g., Prediction=Increase, Risk=Exit):

```
IF Risk_Score > 70:
  → Risk override: max posture = Hold (Constitution: Risk priority)
ELSE IF Sentiment = Recession AND Prediction = Increase:
  → Reduce confidence by 40%, bias toward Reduce
ELSE:
  → Weighted vote with confidence penalty
```

---

## 10. Risk-Aware Decision

### 10.1 Risk-Decision Integration

Decision Intelligence 不独立于 Risk Runtime。它是 Risk-aware 的：

```
Decision Engine → Proposed Action
       │
       ▼
Risk Runtime → Risk Assessment
       │
       ├── Risk OK → Action approved
       ├── Risk High → Action scaled down
       └── Risk Extreme → Action blocked
```

### 10.2 Risk Override Authority

[Source: Constitution V2.8.6 — Chapter 7: Risk Control Highest Authority]

Risk Runtime 对 Decision 输出拥有否决权。Risk Score > 80 时，Decision 输出自动降级为 Observe 或 Reduce。

---

## 11. Strategy Routing Interface

### 11.1 Decision → Strategy Translation

```
Decision Output: "Increase, confidence 0.78, Expansion regime"
        ↓
Strategy Runtime receives:
  - Action direction: Increase
  - Regime constraint: Expansion (trend + leader strategies allowed)
  - Position limit: 70%
  - Confidence: 0.78 → full position within limit
        ↓
Strategy selects: Trend Strategy (active) + Dragon Strategy (selective)
```

### 11.2 API

```python
POST /decision/evaluate
  Request: { world_context, engine_outputs, agent_votes }
  Response: DecisionOutput

GET /decision/current-posture
  Response: { action, confidence, constraints }
```

---

## 12. Human-AI Governance

### 12.1 Governance Model

[Source: Constitution V2.8.6 — Chapter 10 + Human-AI Collaboration V3.0.0]

```
AI Decision Engine:
  ✅ Analyze
  ✅ Compute
  ✅ Recommend

Human:
  ✅ Supervise
  ✅ Authorize (重大决策)
  ✅ Final responsibility
```

### 12.2 Authorization Thresholds

| Decision Type | Authorization |
|--------------|:------------:|
| Observe / Hold | Auto-approved |
| Increase (≤ 50% limit) | Auto-approved with Risk OK |
| Increase (> 50% limit) | Human review recommended |
| Reduce / Hedge | Auto-approved |
| Exit (partial) | Auto-approved |
| Exit (full portfolio) | Human review recommended |
| New strategy activation | Human approval required |

### 12.3 Manual Override

Human can override any decision. Override is recorded:

```json
{
  "original_decision": "Increase",
  "override": "Hold",
  "reason": "Manual: earnings report pending",
  "timestamp": "...",
  "expires": "2026-07-28"
}
```

---

## 13. Learning Feedback Loop

### 13.1 Decision Outcome Tracking

[Source: `AQFT_AGI_Decision_Architecture_Design_V3.0.0` — Chapter 5 + Evolution System]

```
Decision Made → Action Taken → Outcome Observed → Decision Recorded
                                                       │
                                                       ▼
                                              Performance Evaluation
                                                       │
                                                       ▼
                                              Model Improvement
```

### 13.2 Decision Audit Record

```python
@dataclass
class DecisionRecord:
    decision_id: str
    timestamp: datetime
    world_state_snapshot: Dict    # S(t), B(t), R(t)
    agent_votes: Dict
    scenarios_considered: List
    chosen_action: str
    confidence: float
    reasoning_trace: List[str]
    actual_outcome: Optional[Dict] # backfilled
    lesson: Optional[str]          # backfilled
```

### 13.3 Learning Metrics

| Metric | Purpose |
|--------|---------|
| Decision accuracy | Was the action direction correct in hindsight? |
| Confidence calibration | Did high-confidence decisions outperform? |
| Regime-specific performance | Which regimes generate best decisions? |
| Override frequency | How often does human override AI? |

---

## 14. Engineering Requirement

### 14.1 Implementation Constraints

| Constraint | Value |
|------------|-------|
| Decision latency | < 100ms (not including simulation) |
| Max concurrent evaluations | 10 |
| Decision history retention | All decisions, indefinitely |
| Compute | CPU-friendly (utility calc is lightweight) |

### 14.2 Code Structure

```
decision_intelligence/
├── decision_engine.py          # Core decision pipeline
├── action_selector.py          # Action space + selection
├── utility_calculator.py       # U(A) computation
├── confidence_manager.py       # Confidence scoring + gates
├── fusion_integrator.py        # Multi-engine input fusion
├── strategy_router.py          # Decision → Strategy translation
├── governance_gate.py          # Human authorization logic
├── decision_audit.py           # Decision record + audit trail
├── learning_feedback.py        # Outcome tracking + improvement
└── __init__.py
```

---

## 15. Freeze Criteria

1. **Architecture Review Passed** — Correctly positioned between World Model and Strategy
2. **Decision ≠ Strategy distinction clear** — Direction vs Method
3. **Multi-engine fusion preserved** — No single model decision
4. **Confidence gates defined** — 4 levels with clear behavior
5. **Risk override authority maintained** — Risk can veto any decision
6. **Human governance integrated** — Authorization thresholds defined
7. **A-share specialization** — Emotion cycle + limit-up decisions
8. **Audit trail specified** — Every decision traceable
9. **Engineering ready** — Pipeline, data structures, API, code structure

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-3 | `AQFT_AGI_Decision_Architecture_Design_V3.0.0` Ch.1-2 |
| 4 | Decision Theory + Constitution Ch.2 |
| 5 | `AQFT_AGI_Decision_Architecture_Design_V3.0.0` Ch.2 |
| 6 | `AQFT_AI_Brain_Design_V2.8.6.md` Ch.6 |
| 7-8 | `AQFT_AGI_Decision_Architecture_Design_V3.0.0` Ch.4 |
| 9 | Inferred from Belief State + State Vector confidence models |
| 10 | `AQFT_Risk_Design_V2.8.6.md` + Constitution Ch.7 |
| 11 | `AQFT_Strategy_Design_V2.8.6.md` |
| 12 | Constitution Ch.10 + Human-AI Collaboration V3.0.0 |
| 13 | Evolution System V2.8.6 |
| 14-15 | V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Fusion weight values (0.25/0.25/0.20/0.20/0.10) — confirm? | §6 |
| 2 | Authorization thresholds (which decisions need human?) | §12 |
| 3 | Risk override: should Risk or Decision have final say? | §10 |
| 4 | Agent Council voting mechanism (majority? weighted? consensus?) | §7 |
| 5 | Directory location: `03_AI_Brain/Decision_Intelligence/` — confirm? | — |

---

*AQF-T Decision Intelligence Architecture V2.9.1 — ENGINEERING DRAFT*  
*Source: AQFT_AGI_Decision_Architecture_Design_V3.0.0 + AI Brain Design V2.8.6*  
*No original design added. All content traceable to existing AQF-T architecture.*
