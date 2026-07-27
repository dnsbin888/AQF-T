# AQF-T Reasoning Engine Architecture

Version: V2.9.3
Status: FROZEN — V2.9.3 Reasoning Engine Freeze
Phase: V2.9 Intelligence Era — Reasoning Engine
Module: Reasoning_Engine
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Reasoning_Engine_Architecture_V2.9.3.md |
| Module | Reasoning Engine — Cognitive Inference Layer |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V2.9.3 |
| Parent | AQF-T V2.9.2 Memory System (FROZEN) |
| Upstream | World Model V2.9.0 ✅ + Memory System V2.9.2 ✅ |
| Downstream | Decision Intelligence V2.9.1 ✅ |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Counterfactual Intelligence V3.0.0 + Scenario Simulation V3.0.0 + Decision Architecture V3.0.0 |

---

## 1. Purpose

### 1.1 What Reasoning Engine Does

Reasoning Engine 是 AQF-T 的 **认知推理层（Cognitive Inference Layer）**。

它不是预测模型。不是交易策略。它回答 AI 交易中最难的问题：

| Question | Reasoning Type |
|----------|---------------|
| 为什么市场会这样？ | Causal Reasoning |
| 如果条件不同会怎样？ | Counterfactual Reasoning |
| 未来可能如何演化？ | Scenario Reasoning |
| 这个判断的依据是什么？ | Explainable Reasoning |

### 1.2 Why Reasoning Matters

```
Without Reasoning:
  AI: "BUY, confidence 0.72"
  Human: "Why?"
  AI: "..." (black box)

With Reasoning:
  AI: "Expansion regime + capital inflow strengthening + leader stock confirming.
       Causal chain: liquidity↑ → sector rotation → AI theme dominance.
       Counterfactual: if leader fails, capital likely rotates to 新能源.
       BUY, confidence 0.72. Evidence: 3 engines agree, historical success 72%."
```

### 1.3 What Reasoning Engine Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 预测模型 | 因果分析引擎 |
| 交易策略 | 推理与解释系统 |
| 自动交易 | 决策支持（提供推理依据） |
| 黑箱 AI | 可解释推理链 |
| 大语言模型 | 结构化推理框架 |

---

## 2. Scope

### 2.1 In Scope

- Causal chain reasoning from market observations
- Counterfactual analysis ("what if X didn't happen?")
- Scenario-based inference from current state
- Explainable reasoning trace generation
- Reasoning object model with evidence chain
- Interfaces to World Model, Memory, Decision

### 2.2 Out of Scope

- ❌ Training large language models
- ❌ Real-time NLP dialogue
- ❌ External AI service dependency
- ❌ Direct trading signal generation
- ❌ Replacing Decision Intelligence
- ❌ Replacing Strategy Runtime

### 2.3 Target Scale

| Constraint | Limit |
|------------|-------|
| Reasoning latency | < 500ms per query |
| Concurrent reasoning chains | 5 |
| Causal graph nodes | < 1,000 |
| Compute | CPU-friendly (structured inference, not neural) |
| External dependency | None (fully local) |

---

## 3. Architecture Position

### 3.1 In AQF-T System

```
World Model ──→ Memory System ──→ REASONING ENGINE ──→ Decision Intelligence
   (认知)         (经验)              (推理)                (行动)
     │               │                    │                     │
     └───────────────┴────────────────────┴─────────────────────┘
                                   │
                             Evolution System
```

### 3.2 Reasoning as Middle Layer

```
Without Reasoning:
  World Model → Decision Intelligence → Action
  (black box between understanding and action)

With Reasoning:
  World Model → Reasoning Engine → Decision Intelligence → Action
  (causal understanding bridges the gap)
```

---

## 4. Reasoning Philosophy

### 4.1 Core Principles

**Principle 1: Reasoning Is Structured, Not Generative**

不使用大语言模型自由生成文本。使用结构化推理框架：因果图 + 证据链 + 假设检验。

**Principle 2: Every Conclusion Has Evidence**

每个推理结论必须有可追溯的证据。没有"AI 觉得"——只有"因为 X、Y、Z，所以……"

**Principle 3: Multiple Hypotheses, Not One Answer**

不输出单一结论。输出多个假设及其置信度。让 Decision Intelligence 在充分信息下选择。

**Principle 4: Counterfactual Is Core Intelligence**

"如果……会怎样？"是 AQF-T 区别于所有传统量化系统的核心认知能力。

---

## 5. Reasoning Layer Architecture

### 5.1 Four Reasoning Engines

```
┌──────────────────────────────────────────────────────┐
│                 REASONING ENGINE                      │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                  │
│  │   CAUSAL     │  │COUNTERFACTUAL│                  │
│  │   REASONING  │  │  REASONING   │                  │
│  │              │  │              │                  │
│  │ "Why did     │  │ "What if X   │                  │
│  │  this happen?"│  │  didn't?"    │                  │
│  └──────┬───────┘  └──────┬───────┘                  │
│         │                 │                           │
│  ┌──────┴───────┐  ┌──────┴───────┐                  │
│  │   SCENARIO   │  │ EXPLAINABLE  │                  │
│  │   REASONING  │  │  REASONING   │                  │
│  │              │  │              │                  │
│  │ "Where could │  │ "Why this    │                  │
│  │  this go?"   │  │  conclusion?"│                  │
│  └──────────────┘  └──────────────┘                  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 5.2 Engine Summary

| Engine | Question | Input | Output |
|--------|----------|-------|--------|
| Causal | Why? | State + Events + Patterns | Causal chain + confidence |
| Counterfactual | What if? | State + Alternative condition | Counterfactual world + comparison |
| Scenario | Where to? | State + Belief + Regime + Memory | Multiple future paths |
| Explainable | Why this conclusion? | Full reasoning trace | Human-readable explanation |

---

## 6. Causal Reasoning Engine

### 6.1 Purpose

Causal Reasoning 回答：**"为什么市场发生变化？"**

[Source: `AQFT_Counterfactual_Intelligence_Engine_Design_V3.0.0` — Ch.3]

### 6.2 Causal Chain Model

```
Observation: "指数上涨+2%"
       │
       ▼
Causal Analysis:
  [1] 流动性: 北向资金净流入+50亿 → 增量资金入场
  [2] 情绪: 涨停家数+30% → 风险偏好提升
  [3] 结构: AI板块领涨 → 主线确认
  [4] 外部: 美股科技上涨 → 情绪传导
       │
       ▼
Causal Chain:
  外部传导 → 增量资金 → 主线确认 → 情绪扩散 → 指数上涨
       │
       ▼
Confidence: 0.78 (evidence from 4 sources, consistent)
```

### 6.3 Causal Graph

```
Market Causal Graph (simplified):

  Macro/Policy ──→ Liquidity ──→ Sector Rotation ──→ Theme Dominance
                                      │
  External Market ──→ Sentiment ──────┤
                                      │
  Capital Flow ──→ Leader Stock ──────┤
                                      │
                                      ▼
                                 Index Movement
```

Each edge has:
- Direction (→ causal direction)
- Strength (correlation coefficient)
- Lag (time delay in bars)
- Confidence (how reliable is this causal link?)

---

## 7. Counterfactual Reasoning Engine

### 7.1 Purpose

Counterfactual Reasoning 回答：**"如果条件不同，结果会怎样？"**

[Source: `AQFT_Counterfactual_Intelligence_Engine_Design_V3.0.0` — Ch.1-3]

### 7.2 Mathematical Model

```
P(W' | do(A'), W, E)

Where:
  W  = Actual world state
  A  = Actual action/event
  A' = Alternative action/event
  W' = Counterfactual world
  E  = Environment conditions
```

### 7.3 Counterfactual Types

| Type | Example Question |
|------|-----------------|
| Event Counterfactual | "如果今早没有政策利好，市场会怎样?" |
| Action Counterfactual | "如果昨天没有加仓，现在会怎样?" |
| Condition Counterfactual | "如果龙头炸板，资金会往哪去?" |
| Regime Counterfactual | "如果当前不是 Expansion 而是 Distribution?" |

### 7.4 Counterfactual Chain

```
[1] Identify actual world W + actual event A
[2] Define counterfactual condition A'
[3] Clone world state W (all else equal)
[4] Apply A' to cloned world
[5] Simulate alternative trajectory
[6] Compare: W' vs W
[7] Output: CounterfactualScenario + comparison
```

---

## 8. Scenario Reasoning Engine

### 8.1 Purpose

Scenario Reasoning 回答：**"未来可能朝哪些方向演化？"**

[Source: `AQFT_Scenario_Simulation_Engine_Design_V3.0.0` + World Model V2.9.0 Simulation]

### 8.2 Scenario Generation

```
Current State + Belief + Regime + Memory Patterns
        │
        ▼
Scenario Generation:
  S1: Bull continuation (P=45%) — liquidity sustains, leader holds
  S2: Consolidation    (P=30%) — profit-taking, sector rotation
  S3: Policy shock     (P=15%) — unexpected regulation
  S4: External crisis  (P=10%) — global risk-off
        │
        ▼
Per-Scenario Analysis:
  - Expected return range
  - Risk factors
  - Key trigger conditions
  - Early warning signals
```

### 8.3 Scenario-Reasoning Interface

```json
{
  "scenario_id": "SCEN_20260727_001",
  "scenarios": [
    {
      "name": "Bull continuation",
      "probability": 0.45,
      "causal_basis": "Liquidity inflow sustained + leader stock confirming",
      "counterfactual": "If leader fails, this scenario probability drops to 15%",
      "expected_path": "Expansion → Mania in 5-10 days",
      "key_triggers": ["Leader stock holds", "Volume > 5d avg"]
    }
  ]
}
```

---

## 9. Explainable Reasoning Engine

### 9.1 Purpose

Explainable Reasoning 回答：**"为什么给出这个结论？依据是什么？"**

### 9.2 Explanation Structure

```
Level 1: WHAT — "Recommend Increase posture"
Level 2: WHY — "Expansion regime + Warming sentiment + Low risk"
Level 3: BECAUSE — "Causal: liquidity inflow → sector rotation → AI theme"
Level 4: EVIDENCE — "3/4 engines agree. Memory: 72% historical success."
Level 5: CONFIDENCE — "Confidence 0.78. Key risk: sentiment overheating."
Level 6: ALTERNATIVES — "Hold would also be reasonable if risk tolerance lower."
```

### 9.3 Human-Readable Reasoning Report

```json
{
  "reasoning_report": {
    "conclusion": "Increase posture from 35% to 50%",
    "why_chain": [
      "Expansion regime confirmed (confidence 0.82)",
      "Warming sentiment phase — momentum building",
      "Low risk environment — budget available",
      "Capital inflow strengthening — institutional support"
    ],
    "evidence_summary": {
      "engines_agreeing": 3,
      "engines_total": 4,
      "historical_similar_success": "72% (127 episodes)",
      "strongest_match": "2026-06-15: similar setup → +8.2% over 10d"
    },
    "key_risks": [
      "Sentiment approaching overheat (score 65/100, threshold 80)",
      "Leader stock at 7-board — monitor for fatigue"
    ],
    "alternative_view": "If risk tolerance lower, Hold would be defensible",
    "confidence": 0.78
  }
}
```

---

## 10. Reasoning Object Model

### 10.1 Core Reasoning Record

```json
{
  "reasoning_id": "REAS_20260727_093500",
  "timestamp": "2026-07-27T09:35:00",
  "question": "Should AQF-T increase exposure?",

  "input_context": {
    "world_state": { "regime": "Expansion", "emotion": "Warming" },
    "memory_context": { "similar_episodes": 127, "success_rate": 0.72 },
    "decision_context": { "contemplated_action": "Increase" }
  },

  "causal_analysis": {
    "causal_chain": ["Liquidity↑", "Sector Rotation", "Theme Dominance", "Index↑"],
    "confidence": 0.78
  },

  "counterfactual": {
    "condition": "Leader stock炸板",
    "alternative_outcome": "Capital rotates to 新能源, AI theme weakens",
    "impact_on_decision": "Increase confidence would drop 20%"
  },

  "scenarios": [
    { "name": "Bull continuation", "probability": 0.45 },
    { "name": "Consolidation", "probability": 0.30 }
  ],

  "conclusion": {
    "supports_action": "Increase",
    "confidence": 0.78,
    "reasoning_trace": [...]
  }
}
```

---

## 11. Reasoning Pipeline

### 11.1 Full Pipeline

```
Stage 1: QUESTION
  Decision Intelligence queries: "Should we Increase?"
        │
Stage 2: CONTEXT GATHER
  Collect: World State + Memory Patterns + Market Events
        │
Stage 3: CAUSAL ANALYSIS
  Build causal chain: What drove current state?
        │
Stage 4: COUNTERFACTUAL CHECK
  Test: What if key assumptions are wrong?
        │
Stage 5: SCENARIO GENERATION
  Project: Where could this go from here?
        │
Stage 6: EXPLANATION FORMATION
  Compile: Structured reasoning trace
        │
Stage 7: REASONING REPORT
  Output: Conclusion + Evidence + Confidence + Alternatives
        │
        ▼
Decision Intelligence
```

### 11.2 Pipeline Triggers

| Trigger | Reasoning Depth |
|---------|:--------------:|
| Routine decision check | Light (Causal + Explainable) |
| Significant action (Enter/Exit/Increase > 50%) | Full (all 4 engines) |
| Regime change detected | Full |
| Pattern contradiction detected | Full + human review flag |
| New market pattern (novel situation) | Extended (exploratory reasoning) |

---

## 12. Decision Interface

### 12.1 Reasoning → Decision

```python
POST /reasoning/analyze
  Request: {
    question: "Should AQF-T Increase?",
    context: { world_state, memory, decision_context }
  }
  Response: ReasoningReport {
    conclusion, causal_chain, counterfactuals,
    scenarios, evidence, confidence, alternatives
  }
```

### 12.2 Authority Boundary

```
Reasoning Engine: PROVIDES analysis and recommendations
Decision Intelligence: MAKES the decision

Reasoning enhances Decision quality. It does not replace it.
```

---

## 13. Memory Interface

### 13.1 Reasoning → Memory

Reasoning Engine queries Memory for:

- Similar past situations (for causal pattern reference)
- Historical counterfactual outcomes ("did this alternative play out before?")
- Validated knowledge rules ("what do we know about this setup?")

### 13.2 Memory ← Reasoning

Reasoning outputs stored for future reference:

- Successful reasoning chains → reinforce causal links
- Counterfactuals validated by actual outcomes → strengthen causal graph
- Failed reasoning → flagged for review

---

## 14. Engineering Requirement

### 14.1 Constraints

| Constraint | Value |
|------------|-------|
| Reasoning latency | < 500ms |
| Max concurrent chains | 5 |
| Causal graph nodes | < 1,000 |
| Counterfactual simulations | < 10 alternatives per query |
| Compute | CPU-friendly (graph traversal + statistical inference) |
| External dependency | None |

### 14.2 Code Structure

```
reasoning_engine/
├── causal_reasoner.py          # Causal chain construction
├── counterfactual_engine.py    # "What if" analysis
├── scenario_reasoner.py        # Future path projection
├── explanation_generator.py    # Human-readable explanation
├── reasoning_pipeline.py       # Orchestrator
├── causal_graph.py             # Market causal graph
├── evidence_collector.py       # Evidence gathering
├── reasoning_store.py          # Persistence
└── __init__.py
```

---

## 15. Testing Requirement

### 15.1 Unit Tests

- Causal chain: known input → correct causal direction
- Counterfactual: modified condition → different outcome
- Scenario: multiple paths generated, probabilities sum to ~1.0
- Explanation: all 6 levels present in output

### 15.2 Integration Tests

- Full chain: World Model + Memory → Reasoning → Decision
- Counterfactual validation: compare counterfactual prediction vs actual (when condition occurred)
- Causal accuracy: retrospective check on causal chains

---

## 16. Freeze Criteria

1. **Architecture Review Passed** — Correct position between World/Memory and Decision
2. **Four reasoning engines defined** — Causal + Counterfactual + Scenario + Explainable
3. **Reasoning pipeline complete** — Question → Context → Causal → Counterfactual → Scenario → Report
4. **Reasoning object model** — Full record with evidence chain
5. **Structured, not generative** — No LLM dependency, CPU-friendly
6. **Decision interface clear** — Reasoning supports, does not replace, Decision
7. **Memory interface clear** — Queries past; stores reasoning for future
8. **A-share specificity** — Emotion cycle, leader lifecycle, capital migration reasoning

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-4 | Reasoning philosophy + AQF-T Constitution |
| 5 | Synthesis from all Blueprint reasoning capabilities |
| 6 | Counterfactual Intelligence V3.0.0 Ch.3 (causal reasoner) |
| 7 | Counterfactual Intelligence V3.0.0 Ch.1-3 |
| 8 | Scenario Simulation V3.0.0 + World Model V2.9.0 Simulation |
| 9 | Explainability principles from Constitution + AI Brain |
| 10-11 | Decision Architecture V3.0.0 + pipeline synthesis |
| 12-13 | Decision Intelligence V2.9.1 + Memory System V2.9.2 |
| 14-16 | V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Causal graph initialization: manual seed or learned from data? | §6 |
| 2 | Counterfactual simulation method: dynamics model or historical replay? | §7 |
| 3 | Explanation depth: 6 levels appropriate for A-share trader audience? | §9 |
| 4 | Reasoning depth triggers: thresholds for Light vs Full reasoning? | §11 |

---

*AQF-T Reasoning Engine Architecture V2.9.3 — ENGINEERING DRAFT*  
*Source: Counterfactual Intelligence V3.0.0 + Scenario Simulation V3.0.0 + Decision Architecture V3.0.0*  
*No original design added. All content traceable to existing AQF-T architecture.*
