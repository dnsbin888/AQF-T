# AQF-T Counterfactual Reasoning Engine Design

Version: V1.0.0
Status: FROZEN — V2.9.3 Reasoning Engine Freeze
Phase: V2.9 Intelligence Era — Reasoning Engine
Module: Reasoning_Engine
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Counterfactual_Reasoning_Engine_Design_V1.0.md |
| Module | Reasoning Engine — Counterfactual Reasoning |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_Reasoning_Engine_Architecture_V2.9.3 |
| Upstream | World Model V2.9.0 ✅ + Causal Reasoning V1.0 + Memory V2.9.2 ✅ |
| Downstream | Decision Intelligence V2.9.1 |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Counterfactual Intelligence V3.0.0 + Scenario Simulation V3.0.0 |

---

## 1. Purpose

### 1.1 What Counterfactual Reasoning Does

Counterfactual Reasoning Engine 回答：**"如果关键条件不同，市场会怎样？"**

[Source: `AQFT_Counterfactual_Intelligence_Engine_Design_V3.0.0` — Ch.1]

| Causal Reasoning | Counterfactual Reasoning |
|-----------------|-------------------------|
| "为什么发生?" | "如果不发生会怎样?" |
| Explains the past/present | Explores alternative realities |
| Causal chain from evidence | "What if" from changed assumptions |

### 1.2 Core Value

```
Without Counterfactual:
  AI sees: Leader stock strong → AI theme confirmed → Increase
  Risk: Blind to alternative scenarios

With Counterfactual:
  AI sees: Leader stock strong → AI theme confirmed → Increase
  BUT ALSO: What if leader炸板? → Capital rotates to 新能源 → Reduce AI exposure
  → Decision is risk-aware, not single-path
```

---

## 2. Scope

### 2.1 In Scope

- Counterfactual assumption generation
- Alternative scenario construction
- Impact evaluation of changed conditions
- Probability estimation of alternative paths
- A-share specific counterfactual scenarios

### 2.2 Out of Scope

- ❌ Predicting exact stock prices in alternative worlds
- ❌ Generating trading strategies from counterfactuals
- ❌ Infinite scenario generation (limited to top 5 most impactful)

---

## 3. Architecture Position

### 3.1 In Reasoning Engine

```
Causal Reasoning ("Why?")
        │
        ▼
Counterfactual Reasoning ("What if?")  ← 本模块
        │
        ▼
Scenario Reasoning ("Where to?")
        │
        ▼
Explainable Reasoning ("Why this conclusion?")
```

---

## 4. Counterfactual Philosophy

### 4.1 Core Principles

**Principle 1: One Change at a Time**

每次只改变一个关键变量。改变多个变量会导致组合爆炸和不可解释的结果。

**Principle 2: Plausible, Not Fictional**

反事实假设必须是可能发生的。不生成"如果火星人来炒股"式的荒诞场景。

**Principle 3: Impact-Focused**

只评估有决策影响的反事实。不影响当前决策的反事实不生成。

**Principle 4: Evidence-Anchored**

反事实的推演路径基于历史相似模式和市场机制，不是随机猜测。

---

## 5. Counterfactual Object Model

```json
{
  "counterfactual_id": "CF_20260727_093500",
  "timestamp": "2026-07-27T09:35:00",

  "base_reality": {
    "description": "Expansion regime, AI theme dominant, leader at 7-board",
    "current_action_contemplated": "Increase AI exposure"
  },

  "changed_assumption": {
    "variable": "leader_stock_status",
    "from": "strong_7_board",
    "to": "炸板_volume_spike",
    "rationale": "Leader stock fatigue risk at high board count"
  },

  "alternative_scenario": {
    "description": "Leader炸板 → 板块内部分化 → 资金寻找新方向",
    "causal_chain": "Leader Fail → Confidence Shock → Sector Rotation → Capital Migration",
    "expected_timeline": "1-3 days"
  },

  "impact": {
    "on_ai_theme": "Weakened. 跟风股跌5-10%",
    "on_sentiment": "短暂冲击。若新龙头出现则快速恢复",
    "on_decision": "Increase AI exposure 应延迟，等待确认",
    "severity": "Medium"
  },

  "probability": 0.25,
  "confidence": 0.70,
  "early_warnings": ["leader_volume_anomaly", "炸板率_rising"]
}
```

---

## 6. Assumption Generation

### 6.1 Key Variables for Counterfactual Change

| Variable | Relevance | A-Share Example |
|----------|-----------|-----------------|
| Leader stock status | 核心情绪锚 | 龙头炸板 / 连板成功 |
| Policy signal | 方向性驱动 | 政策出台 / 政策落空 |
| Capital flow | 资金方向 | 北向流入 / 北向流出 |
| Emotion phase | 情绪阶段 | 高潮 / 退潮 |
| Liquidity condition | 市场容量 | 放量 / 缩量 |
| External shock | 外部冲击 | 美股暴跌 / 汇率突变 |

### 6.2 Assumption Selection

```
For each key variable:
  [1] Is it relevant to current decision? → filter
  [2] Is a change plausible? (probability > 5%) → filter
  [3] Would the change significantly impact the decision? → filter
  [4] Select top 3-5 most impactful assumptions → generate counterfactuals
```

---

## 7. Alternative Scenario Engine

### 7.1 Scenario Construction

```
Base Reality (W)
       │
       ▼
Change Assumption: Variable X changes from A → A'
       │
       ▼
Clone World State: all else equal
       │
       ▼
Apply Changed Variable to cloned world
       │
       ▼
Simulate Alternative Trajectory:
  - Use World Model dynamics
  - Reference Memory for similar historical patterns
  - Apply known causal mechanisms
       │
       ▼
Output: Alternative Scenario W' + Comparison vs W
```

---

## 8. Impact Evaluation

### 8.1 Impact Dimensions

```json
{
  "impact": {
    "market_direction": {
      "base": "bullish",
      "alternative": "neutral_to_bearish",
      "magnitude": "moderate"
    },
    "sector_impact": {
      "primary_sector": "AI — weakened",
      "secondary_sector": "新能源 — potential beneficiary",
      "rotation_signal": true
    },
    "sentiment_impact": {
      "from": "Warming",
      "to": "Cooling (temporary)",
      "recovery_time": "1-3 days if new leader emerges"
    },
    "decision_impact": {
      "current_plan": "Increase AI exposure",
      "recommendation": "Delay Increase. Observe 1-2 days for leader confirmation.",
      "urgency": "Medium"
    }
  }
}
```

---

## 9. Probability Assessment

### 9.1 Counterfactual Probability

```
P(Counterfactual) = f(
  Base_Rate,              # How often does this variable change?
  Current_Conditions,     # Are conditions ripe for change?
  Historical_Frequency,   # Memory: similar setups → what happened?
  Warning_Signals         # Any early indicators firing?
)
```

### 9.2 Probability Calibration

| Probability | Label | Decision Weight |
|:----------:|-------|----------------|
| > 30% | Likely alternative | Serious consideration |
| 15-30% | Plausible alternative | Hedge consideration |
| 5-15% | Possible tail scenario | Awareness |
| < 5% | Remote | Noted, not acted on |

---

## 10. World Model Interface

| Input from World Model | Used For |
|-----------------------|----------|
| State S(t) | Base reality description |
| Belief B(t) | Which variables are uncertain? |
| Regime R(t) | Which counterfactuals are regime-relevant? |
| Simulation Engine | Alternative trajectory computation |

---

## 11. Simulation Interface

Counterfactual Engine leverages World Model Simulation (05_Simulation) for trajectory computation:

```
Counterfactual → Simulation Request → Alternative Trajectory → Impact Evaluation
```

---

## 12. Memory Interface

```
Query: "Has this counterfactual scenario played out before?"
  → Memory returns similar historical patterns
  → Used to calibrate probability and impact estimates

Store: Counterfactual results (predicted vs actual if the counterfactual condition materialized)
  → Used to improve future counterfactual accuracy
```

---

## 13. Decision Interface

### 13.1 Counterfactual → Decision

```json
{
  "counterfactual_report": {
    "base_plan": "Increase AI exposure",
    "top_counterfactual": {
      "scenario": "Leader炸板 → AI theme weakens",
      "probability": 0.25,
      "impact": "AI跟风股 -5% to -10%",
      "recommendation": "Delay Increase by 1-2 days"
    },
    "overall_assessment": "Base plan sound but monitor leader stock closely",
    "hedge_suggestion": "Prepare 新能源 allocation as rotation hedge"
  }
}
```

---

## 14. Engineering Requirement

| Constraint | Value |
|------------|-------|
| Counterfactual generation | < 500ms for 5 scenarios |
| Max counterfactuals per query | 5 |
| Key variables monitored | 6 |
| Compute | CPU-friendly |

### Code Structure

```
reasoning_engine/counterfactual/
├── assumption_generator.py     # What variables to change?
├── world_cloner.py             # Clone current state
├── alternative_simulator.py    # Trajectory under changed condition
├── impact_evaluator.py         # Compare W' vs W
├── probability_estimator.py    # How likely is this?
├── early_warning_monitor.py    # Track signals for key variables
└── __init__.py
```

---

## 15. Testing Requirement

- Known counterfactual condition → reasonable alternative trajectory
- Base case: no change → alternative = base
- Plausibility filter: implausible assumptions rejected
- Historical validation: counterfactual accuracy tested on known regime changes

---

## 16. Freeze Criteria

1. **Architecture Review Passed** — Correct position after Causal, before Scenario
2. **Counterfactual object model** — Base reality + changed assumption + alternative + impact
3. **6 key variables** — Leader, Policy, Capital, Emotion, Liquidity, External
4. **Probability calibrated** — 4-level with historical reference
5. **A-share scenarios** — Leader failure, theme switch, policy change, emotion shift, liquidity change
6. **No trading strategy generation** — Recommends caution, not orders

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-4 | Counterfactual Intelligence V3.0.0 Ch.1 |
| 5-7 | Counterfactual Intelligence V3.0.0 Ch.3-4 |
| 8-9 | Inferred from impact/probability analysis |
| 10-13 | Reasoning Architecture V2.9.3 interfaces |
| 14-16 | V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Key variables: 6 sufficient for A-share? | §6 |
| 2 | Max 5 counterfactuals per query — appropriate? | §14 |
| 3 | Probability thresholds (30%/15%/5%) — confirm? | §9 |

---

*AQF-T Counterfactual Reasoning Engine Design V1.0 — ENGINEERING DRAFT*  
*Source: Counterfactual Intelligence V3.0.0 + Scenario Simulation V3.0.0*  
*No original design added.*
