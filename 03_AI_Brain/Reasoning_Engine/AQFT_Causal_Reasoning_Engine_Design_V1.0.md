# AQF-T Causal Reasoning Engine Design

Version: V1.0.0
Status: FROZEN — V2.9.3 Reasoning Engine Freeze
Phase: V2.9 Intelligence Era — Reasoning Engine
Module: Reasoning_Engine
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Causal_Reasoning_Engine_Design_V1.0.md |
| Module | Reasoning Engine — Causal Reasoning |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_Reasoning_Engine_Architecture_V2.9.3 |
| Upstream | World Model V2.9.0 ✅ + Memory System V2.9.2 ✅ |
| Downstream | Decision Intelligence V2.9.1 |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Counterfactual Intelligence V3.0.0 + World Model Architecture V3.0.0 |

---

## 1. Purpose

### 1.1 What Causal Reasoning Does

Causal Reasoning Engine 回答市场分析中最根本的问题：**"为什么？"**

| Surface Observation | Causal Question |
|--------------------|-----------------|
| 指数上涨 +2% | 为什么上涨？ |
| 成交量放大 | 增量资金还是存量博弈？ |
| 龙头炸板 | 个股原因还是板块退潮？ |
| 情绪转冷 | 正常回调还是趋势反转？ |

### 1.2 What Causal Reasoning Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 相关性分析 ("X和Y一起动") | 因果分析 ("X驱动Y") |
| 预测模型 | 解释模型 |
| 自动交易信号 | 决策参考依据 |
| 单一指标归因 | 多因素因果链 |

---

## 2. Scope

### 2.1 In Scope

- Causal chain construction from market events
- Cause → Mechanism → Effect → Feedback modeling
- A-share specific causal factors
- Causal confidence scoring
- Evidence-based causal validation

### 2.2 Out of Scope

- ❌ Generating buy/sell rules from causal chains
- ❌ Automated strategy modification
- ❌ Replacing market prediction models
- ❌ Large-scale causal discovery (big data mining)

---

## 3. Architecture Position

### 3.1 In Reasoning Engine

```
Reasoning Engine (REASON-001)
        │
        ├── Causal Reasoning    ← 本模块
        ├── Counterfactual      (REASON-003)
        ├── Scenario            (REASON-004)
        └── Explainable         (REASON-005)
```

### 3.2 Causal Chain Flow

```
Market Event Detected
        │
        ▼
┌───────────────────────────┐
│    CAUSAL REASONING        │
│                           │
│  [1] Event Identification │
│  [2] Cause Extraction     │
│  [3] Mechanism Analysis   │
│  [4] Impact Evaluation    │
│  [5] Feedback Check       │
│  [6] Confidence Scoring   │
│  [7] Causal Chain Output  │
└───────────┬───────────────┘
            │
            ▼
Decision Intelligence + Memory System
```

---

## 4. Causal Reasoning Philosophy

### 4.1 Core Principles

**Principle 1: Correlation ≠ Causation**

"成交量放大的同时指数上涨" ≠ "成交量放大导致指数上涨"。两者可能都是流动性改善的结果。

**Principle 2: Causal Chains, Not Single Causes**

市场变化极少由单一因素驱动。Causal Engine 构建因果链，不是找"唯一原因"。

**Principle 3: Mechanism Matters**

不只是"A导致B"。要说明 A 通过什么机制导致 B。

**Principle 4: Evidence-Anchored**

每个因果断言必须有可验证的证据来源。没有"AI 推测"——只有"基于 X、Y、Z 证据的因果推断"。

---

## 5. Causal Object Model

### 5.1 Causal Record

```json
{
  "causal_id": "CAUS_20260727_093500",
  "timestamp": "2026-07-27T09:35:00",

  "event": {
    "type": "index_surge",
    "description": "上证指数上涨 2.1%",
    "magnitude": 0.021,
    "timeframe": "intraday"
  },

  "causes": [
    {
      "cause_id": "C1",
      "factor": "policy",
      "description": "国务院发布AI产业支持政策",
      "mechanism": "政策信号 → 行业预期改善 → 资金集中流入",
      "evidence": ["新闻时间戳 09:05", "AI板块同步拉升"],
      "strength": 0.40,
      "confidence": 0.85
    },
    {
      "cause_id": "C2",
      "factor": "liquidity",
      "description": "北向资金净流入 +50亿",
      "mechanism": "外资流入 → 蓝筹权重股买盘 → 指数推升",
      "evidence": ["北向资金数据", "权重股成交放大"],
      "strength": 0.35,
      "confidence": 0.90
    },
    {
      "cause_id": "C3",
      "factor": "sentiment",
      "description": "连板高度突破 7板",
      "mechanism": "龙头高度 → 情绪扩散 → 跟风资金入场",
      "evidence": ["涨停梯队数据", "板块联动"],
      "strength": 0.25,
      "confidence": 0.72
    }
  ],

  "causal_chain": "Policy → AI Sector Surge → Sentiment Spread → Broad Buying → Index +2.1%",

  "total_confidence": 0.82,
  "alternative_hypothesis": "Technical rebound after 3-day decline (strength 0.15)",
  "validated_by": "pending_outcome"
}
```

---

## 6. Cause Extraction

### 6.1 A-Share Causal Factors

| Factor | Examples | Detection |
|--------|----------|-----------|
| 政策 (Policy) | 国务院文件、监管变化、行业政策 | News NLP + time correlation |
| 流动性 (Liquidity) | 北向资金、融资余额、央行操作 | Fund flow data |
| 情绪 (Sentiment) | 涨停家数、连板高度、炸板率 | Sentiment Engine |
| 资金 (Capital) | 主力净流入、板块资金迁移 | L2 data + fund flow |
| 板块 (Sector) | 龙头带动、板块轮动 | Sector rotation detection |
| 外部 (External) | 美股、港股、汇率、商品 | Cross-market data |
| 事件 (Event) | 财报、公告、突发事件 | News feed |
| 技术 (Technical) | 突破、背离、超买超卖 | Technical indicators |

### 6.2 Cause Extraction Pipeline

```
Event detected → Search candidate causes:
  [1] Time-window scan: what happened before the event? (t-60min to t-5min)
  [2] Correlation check: which factors moved in sync?
  [3] Mechanism match: does a known causal mechanism explain this?
  [4] Counter-check: could the event have happened WITHOUT this cause?
  [5] Rank causes by strength + evidence quality
```

---

## 7. Mechanism Analysis

### 7.1 Known Causal Mechanisms

| Mechanism | Pattern | A-Share Example |
|-----------|---------|-----------------|
| 政策传导 | Policy → Sector Expectation → Capital → Price | AI政策 → AI板块涨停潮 |
| 流动性驱动 | Capital Inflow → Weight Stocks → Index → Sentiment | 北向资金→权重股→情绪扩散 |
| 情绪扩散 | Leader Stock → Sentiment → Follower Stocks | 龙头7板→板块跟风 |
| 资金迁移 | Sector A Weakening → Capital Exit → Sector B Entry | 新能源退潮→AI接棒 |
| 风险传导 | Risk Event → Liquidity Drop → Forced Selling | 黑天鹅→流动性枯竭→踩踏 |

### 7.2 Mechanism Validation

```
Mechanism hypothesis: "Policy → AI Sector Surge"
  ✓ Time sequence: Policy (09:05) → AI stocks rise (09:10)
  ✓ Specificity: AI sector surged; non-AI sectors did not
  ✓ Exclusion: No other factor explains AI-specific surge
  → Mechanism confidence: 0.85
```

---

## 8. Impact Evaluation

### 8.1 Impact Assessment

```json
{
  "impact": {
    "scope": "sector_wide",
    "affected": ["AI板块", "半导体", "算力"],
    "magnitude": "strong",
    "persistence": "medium (1-3 days expected)",

    "direct_effects": [
      "AI板块涨停家数 +15",
      "龙头股封单强度 8%",
      "板块成交额 +120%"
    ],

    "indirect_effects": [
      "情绪扩散至科技板块",
      "游资活跃度提升",
      "短期风险偏好上升"
    ],

    "feedback_risk": [
      "若政策预期落空 → 情绪快速反转",
      "若龙头炸板 → 板块分化"
    ]
  }
}
```

---

## 9. Feedback Modeling

### 9.1 Feedback Loop Detection

```
Primary Cause → Primary Effect
                      │
                      ▼
              Secondary Effects
                      │
              ┌───────┴───────┐
              ▼               ▼
        Positive Feedback  Negative Feedback
        (reinforcing)      (dampening)

Example:
  Policy → AI Surge → Sentiment ↑ → More Buying → Further Surge (+)
  Policy → AI Surge → Valuation Concern → Profit Taking → Cool-off (−)
```

### 9.2 Feedback Monitoring

After causal chain output, monitor for:
- Reinforcing signals (feedback amplifying)
- Dampening signals (feedback weakening)
- Regime-shift signals (feedback changing the regime)

---

## 10. Confidence Assessment

### 10.1 Causal Confidence Formula

```
Causal_Confidence = 
  0.30 × Evidence_Quality      # Data freshness, source reliability
+ 0.25 × Mechanism_Strength    # Known mechanism? Plausible?
+ 0.20 × Temporal_Consistency  # Cause before effect? Lag appropriate?
+ 0.15 × Exclusion_Score       # Alternative causes ruled out?
+ 0.10 × Historical_Match      # Similar causal pattern seen before?
```

### 10.2 Confidence Levels

| Confidence | Label | Usage |
|:----------:|-------|-------|
| > 0.80 | Strong causal link | Used as primary reasoning input |
| 0.60–0.80 | Plausible link | Used with caveat |
| 0.40–0.60 | Weak link | Informational only |
| < 0.40 | Speculative | Not used for decisions |

---

## 11. World Model Interface

### 11.1 Input from World Model

| Data | Used For |
|------|----------|
| Market State S(t) | Event detection baseline |
| Regime R(t) | Context for mechanism selection |
| Belief B(t) | Cross-check causal interpretation |
| Scenario forecasts | Compare causal chain vs scenario projections |

### 11.2 Output to World Model

Causal chains feed back to improve:
- Regime transition understanding
- Belief update evidence
- Scenario generation accuracy

---

## 12. Memory Interface

### 12.1 Query

```python
GET /memory/retrieve
  ?context={current event}
  &query_type=causal_pattern
  → "Has this causal pattern appeared before? What was the outcome?"
```

### 12.2 Store

```python
POST /memory/store/causal_chain
  { causal_record }
  → Stored for future pattern matching and validation
```

---

## 13. Decision Interface

### 13.1 Causal → Decision

```json
{
  "causal_report": {
    "event": "Index +2.1%",
    "primary_cause": "Policy-driven AI sector surge",
    "causal_chain": "Policy → AI Surge → Sentiment → Broad Buying",
    "confidence": 0.82,
    "decision_implication": "Surge has causal foundation — not purely speculative",
    "risk_note": "Monitor policy follow-through; if absent, surge may reverse"
  }
}
```

---

## 14. Engineering Requirement

### 14.1 Constraints

| Constraint | Value |
|------------|-------|
| Causal analysis latency | < 200ms |
| Max causes per event | 8 |
| Causal factor library | 8 factor types |
| Mechanism library | ~20 known mechanisms |
| Compute | CPU-friendly |

### 14.2 Code Structure

```
reasoning_engine/causal/
├── event_detector.py           # Market event identification
├── cause_extractor.py          # Multi-factor cause search
├── mechanism_analyzer.py       # Mechanism matching
├── impact_evaluator.py         # Effect assessment
├── feedback_modeler.py         # Feedback loop detection
├── confidence_scorer.py        # Causal confidence
├── causal_store.py             # Persistence
└── __init__.py
```

---

## 15. Testing Requirement

### 15.1 Unit Tests

- Known causal pattern → correct mechanism identified
- Noisy event → multiple causes ranked, not single false cause
- Temporal check: cause timestamp < effect timestamp
- Confidence: strong evidence → high confidence; weak → low

### 15.2 Integration Tests

- Full chain: Event → Causal → Counterfactual → Decision
- Causal validation: retrospective check against known market events
- Memory feedback: causal chain stored and retrievable

---

## 16. Freeze Criteria

1. **Architecture Review Passed** — Correct position within Reasoning Engine
2. **Causal object model complete** — Event + Causes + Mechanism + Impact + Feedback
3. **8 A-share causal factors** — Policy, Liquidity, Sentiment, Capital, Sector, External, Event, Technical
4. **5 known mechanisms** — Policy transmission, liquidity drive, sentiment diffusion, capital migration, risk transmission
5. **Confidence model** — 4-level with clear usage gates
6. **No trading rules** — Causal chains explain, do not command
7. **CPU-friendly** — Structured inference, not neural generation

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-4 | Reasoning Engine Architecture V2.9.3 + Causal philosophy |
| 5-6 | Counterfactual Intelligence V3.0.0 Ch.3 |
| 7-9 | Inferred from A-share market mechanisms |
| 10-13 | Reasoning Architecture V2.9.3 interfaces |
| 14-16 | V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Causal factor library: 8 types comprehensive for A-share? | §6 |
| 2 | Mechanism library: seed with 5 or allow learned mechanisms? | §7 |
| 3 | Causal confidence formula weights — confirm? | §10 |

---

*AQF-T Causal Reasoning Engine Design V1.0 — ENGINEERING DRAFT*  
*Source: Counterfactual Intelligence V3.0.0 + World Model Architecture V3.0.0*  
*No original design added. All content traceable to existing AQF-T architecture.*
