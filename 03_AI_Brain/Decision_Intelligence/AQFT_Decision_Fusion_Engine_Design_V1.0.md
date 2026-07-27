# AQF-T Decision Fusion Engine Design

Version: V1.0.0
Status: FROZEN — V2.9.1 Decision Intelligence Freeze
Phase: V2.9 Intelligence Era — Decision Intelligence
Module: Decision_Intelligence
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Decision_Fusion_Engine_Design_V1.0.md |
| Module | Decision Intelligence — Fusion Engine |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_Decision_Intelligence_Architecture_V2.9.1 |
| Upstream | World Model ✅ + AI Brain V2.8.6 + Risk Intelligence |
| Downstream | Decision Engine (Action Selection) |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | AI Brain Design V2.8.6 Ch.6 + Decision Architecture V3.0.0 + World Model V2.9.0 |

---

## 1. Purpose

### 1.1 What Fusion Engine Does

Fusion Engine 是 Decision Intelligence 的 **证据整合器（Evidence Integrator）**。

它不负责交易。它负责：**将多个独立认知来源的信号，融合为统一、可解释、带置信度的决策证据。**

| Component | Responsibility |
|-----------|---------------|
| World Model | 提供市场认知 |
| AI Brain Engines | 提供预测/情绪/风险信号 |
| Fusion Engine | 融合以上 → 统一 Evidence |
| Decision Engine | 基于 Evidence 选择 Action |

### 1.2 Why Fusion Exists Separately

[Source: Constitution V2.8.6 — Prohibition of Single-Model Decision]

```
Without Fusion:
  Prediction says BUY → Execute BUY   ❌ Single model

With Fusion:
  Prediction: BUY (confidence 0.70)
  Sentiment:  Warming (confidence 0.75)
  Risk:       Low (confidence 0.85)
  World:      Expansion regime
        ↓
  Fusion: BUY evidence, aggregated confidence 0.77
        ↓
  Decision: Increase, confidence 0.77   ✅ Multi-source
```

### 1.3 What Fusion Engine Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 交易信号生成器 | 证据整合引擎 |
| 简单加权平均 | 多源对齐 + 冲突检测 + 置信度聚合 |
| 固定权重 | 动态权重框架（Regime-adaptive） |
| 替代 Decision Engine | Decision Engine 的上游输入 |

---

## 2. Scope

### 2.1 In Scope

- Multi-source evidence alignment
- Evidence fusion pipeline
- Confidence aggregation from multiple signals
- Conflict detection and resolution
- Regime-adaptive fusion weights
- Explainable fusion trace output

### 2.2 Out of Scope

- ❌ Action selection (Decision Engine)
- ❌ Trade execution (Execution Runtime)
- ❌ Strategy implementation (Strategy Runtime)
- ❌ Fixed/hardcoded model weights
- ❌ Single-model buy/sell signals

---

## 3. Architecture Position

### 3.1 In Decision Intelligence

```
                    Evidence Sources
   ┌────────────────────┼────────────────────┐
   │                    │                    │
World Model      AI Brain Engines     Risk Intelligence
   │               │       │               │
   │          Prediction  Sentiment        │
   │                    │                    │
   └────────────────────┼────────────────────┘
                        ▼
              ┌─────────────────┐
              │  FUSION ENGINE  │  ← 本模块
              │  (Evidence)     │
              └────────┬────────┘
                        │
                        ▼ Unified Evidence
              ┌─────────────────┐
              │ DECISION ENGINE │
              │ (Action Brain)  │
              └─────────────────┘
```

### 3.2 Position in Pipeline

```
Evidence Sources → [Fusion Engine] → Unified Evidence → Decision Engine → Action
```

Fusion Engine is the **gateway** between raw multi-source signals and the decision layer.

---

## 4. Fusion Philosophy

### 4.1 Core Principles

**Principle 1: Evidence, Not Voting**

模型不是民主成员。融合不是简单多票制。

```
❌ Wrong:  3 models say BUY, 2 say SELL → BUY (majority vote)
✅ Right:  Each model provides EVIDENCE with CONFIDENCE → aggregate evidence strength
```

**Principle 2: Confidence Weighted, Not Equal Weighted**

高置信度的信号贡献更大权重。低置信度的信号自动降权。

**Principle 3: Conflict ≠ Stalemate**

当信号矛盾时，不是"不做决策"。而是降低融合置信度，交由 Decision Engine 在低置信度约束下选择保守行动。

**Principle 4: Regime-Aware**

同一个信号在不同 Regime 下权重不同。Expansion 中 Prediction 更重要，Panic 中 Risk 更重要。

---

## 5. Evidence Source Model

### 5.1 Six Evidence Sources

[Source: AI Brain Design V2.8.6 + World Model V2.9.0]

| Source | Provides | Signal Type | Update Freq |
|--------|----------|-------------|:-----------:|
| World Model | State S(t) + Belief B(t) + Regime R(t) | Context | 5 min |
| Prediction Engine | Trend direction + probability | Directional | 5 min |
| Sentiment Engine | Emotion phase + theme strength | Behavioral | 1 min |
| Microstructure (L2) | Order imbalance + queue pressure | Tactical | Tick |
| Risk Intelligence | Risk score + warnings | Constraint | 5 min |
| Experience Memory | Similar past situations | Historical | On query |

### 5.2 Evidence Object

```json
{
  "evidence_id": "EV_20260727_093500",
  "source": "Prediction Engine",
  "signal": {
    "type": "directional",
    "direction": "UP",
    "strength": 0.72
  },
  "confidence": 0.80,
  "timestamp": "2026-07-27T09:35:00",
  "metadata": {
    "model_version": "LightGBM-v3.2",
    "data_freshness": "current",
    "regime_context": "Expansion"
  }
}
```

---

## 6. Multi-Model Alignment

### 6.1 Alignment Problem

不同引擎的输出格式不同，需要对齐为统一 Evidence 格式。

```
Prediction:  { direction: "UP", probability: 0.72 }     → Directional Evidence
Sentiment:   { phase: "Warming", score: 65 }            → Behavioral Evidence
Risk:        { score: 28, level: "Low" }                → Constraint Evidence
World Model: { regime: "Expansion", confidence: 0.82 }  → Context Evidence
```

### 6.2 Alignment Pipeline

```
[1] Receive raw signals from each source
         │
[2] Normalize to unified Evidence format
         │
[3] Tag with Regime context
         │
[4] Check signal consistency (multi-source agreement?)
         │
[5] Resolve conflicts if any
         │
[6] Output aligned Evidence Set
```

### 6.3 Unified Evidence Schema

```json
{
  "evidence_set": [
    {
      "source": "Prediction",
      "evidence_type": "Directional",
      "value": { "direction": 1, "strength": 0.72 },
      "confidence": 0.80,
      "regime_relevance": 0.85
    },
    {
      "source": "Sentiment",
      "evidence_type": "Behavioral",
      "value": { "phase": "Warming", "score": 0.65 },
      "confidence": 0.75,
      "regime_relevance": 0.70
    }
  ],
  "alignment_score": 0.82,
  "conflicts": []
}
```

---

## 7. Fusion Pipeline

### 7.1 Five-Stage Fusion

```
Stage 1: COLLECT
  Gather evidence from all available sources
         │
Stage 2: ALIGN
  Normalize to unified Evidence format
  Tag with Regime context
         │
Stage 3: WEIGHT
  Apply Regime-adaptive weights to each source
  Apply confidence-based discount to low-confidence signals
         │
Stage 4: FUSE
  Aggregate weighted evidence into unified signal
  Detect and flag conflicts
         │
Stage 5: OUTPUT
  Unified Evidence + Aggregated Confidence + Fusion Trace
```

### 7.2 Fusion Formula

```
Fused_Evidence = Σ (Evidence_i × Weight_i × Confidence_i × Regime_Relevance_i)

Where:
  Evidence_i:      Normalized signal from source i
  Weight_i:        Regime-adaptive base weight
  Confidence_i:    Source's self-reported confidence
  Regime_Relevance: How relevant is this source type to current regime?
```

---

## 8. Confidence Aggregation

### 8.1 Aggregated Confidence Formula

```
Fusion_Confidence = f(
  Σ(Source_Confidence_i × Weight_i) / Σ(Weight_i),    # Weighted avg confidence
  Alignment_Score,                                      # Multi-source agreement
  Data_Freshness,                                       # Age penalty
  Conflict_Penalty                                      # Disagreement penalty
)
```

### 8.2 Confidence Output

| Aggregated Confidence | Meaning |
|:---------------------:|---------|
| > 0.80 | Strong evidence — Decision Engine can act freely |
| 0.60–0.80 | Moderate evidence — Decision Engine should be conservative |
| 0.40–0.60 | Weak evidence — Decision Engine limited to Observe/Hold |
| < 0.40 | Insufficient evidence — No action recommended |

---

## 9. Conflict Resolution

### 9.1 Conflict Detection

```
Detect conflict when:
  |Evidence_direction_i - Evidence_direction_j| > threshold

Example conflict:
  Prediction: direction=+1 (UP), confidence=0.70
  Sentiment:  phase=Recession (implied DOWN), confidence=0.65
  → Directional conflict detected
```

### 9.2 Resolution Hierarchy

[Source: Constitution V2.8.6 — Risk Priority]

```
IF Risk_Evidence.level IN [High, Extreme]:
  → Risk evidence dominates. Conservative bias applied.
  → Fused direction capped at Hold.

ELSE IF Conflict_Strength > 0.5:
  → Confidence penalty applied.
  → Default to conservative posture (Observe/Hold).

ELSE:
  → Weighted fusion with conflict discount.
```

### 9.3 Conflict Resolution Table

| Conflict Type | Resolution | Confidence Impact |
|--------------|------------|:-----------------:|
| Prediction vs Sentiment | Weighted fusion, lower confidence | −20% |
| Any vs Risk (High) | Risk overrides | Confidence capped at 0.50 |
| Any vs Risk (Extreme) | Risk blocks | Evidence output: Observe only |
| Multiple conflicts | Conservative default | Confidence capped at 0.40 |

---

## 10. Regime-Adaptive Fusion

### 10.1 Weight Table by Regime

[Source: AI Brain Design V2.8.6 Ch.6.3 — adapted]

| Regime | Prediction | Sentiment | World Model | Risk | Microstructure | Experience |
|--------|:----------:|:---------:|:-----------:|:----:|:-------------:|:----------:|
| Expansion | 0.30 | 0.25 | 0.15 | 0.15 | 0.05 | 0.10 |
| Mania | 0.20 | 0.30 | 0.15 | 0.20 | 0.05 | 0.10 |
| Distribution | 0.15 | 0.20 | 0.15 | 0.35 | 0.05 | 0.10 |
| Panic | 0.10 | 0.10 | 0.10 | 0.55 | 0.05 | 0.10 |
| Neutral | 0.25 | 0.25 | 0.20 | 0.15 | 0.05 | 0.10 |
| Recovery | 0.25 | 0.25 | 0.20 | 0.15 | 0.05 | 0.10 |

**[NEEDS ARCHITECT REVIEW]** — These are reference weights. Architecture is weight-framework, not weight-values. Evolution System should govern final calibration.

### 10.2 Dynamic Weight Governance

```
Weights are NOT hardcoded constants.
They are governed by:
  1. Evolution System: adjusts based on historical accuracy per regime
  2. Parameter Governance: tracks weight changes, versions, rollback
  3. Market Feedback: poor performance → automatic weight reduction
```

---

## 11. Decision Interface

### 11.1 Fusion → Decision Output

```python
class FusionOutput:
    timestamp: datetime

    # Fused evidence
    direction: str           # "Increase" | "Hold" | "Reduce"
    strength: float          # 0-1 fused evidence strength
    confidence: float        # aggregated confidence

    # Component breakdown
    evidence_sources: List[Evidence]  # individual source contributions
    alignment_score: float           # multi-source agreement

    # Conflict info
    conflicts: List[Conflict]
    conflict_resolution: str

    # Trace
    reasoning_summary: str          # human-readable
    fusion_trace: List[str]         # step-by-step
```

### 11.2 API

```python
POST /decision/fusion/evaluate
  Request: { sources: [Evidence, ...], regime: RegimeState }
  Response: FusionOutput

GET /decision/fusion/weights
  Response: { current_weights: {...}, regime: "Expansion", last_updated: "..." }
```

---

## 12. Risk Interface

### 12.1 Risk Evidence Priority

Risk evidence 在融合中拥有 **结构性优先权（Structural Priority）**，不是简单高权重。

```
Normal operation:
  All evidence sources contribute → weighted fusion

Risk elevated (score 60-80):
  Risk evidence weight × 2.0
  Other evidence weights × 0.7

Risk extreme (score 80+):
  Risk evidence DOMINATES
  Fused direction capped at "Hold"
  Confidence capped at 0.50
```

### 12.2 Risk Block Signal

```json
{
  "risk_block": true,
  "reason": "Risk Score 85 (Extreme). All Increase/aggressive signals blocked.",
  "max_allowed_posture": "Hold",
  "overridden_sources": ["Prediction:Increase", "Sentiment:Warming"]
}
```

---

## 13. Evolution Feedback

### 13.1 Learning Loop

[Source: Evolution System V2.8.6]

```
Fusion Output → Decision → Action → Outcome
                                       │
                                       ▼
                              Was the fused evidence correct?
                                       │
                              ┌────────┴────────┐
                              ▼                 ▼
                        Source Accuracy    Weight Adjustment
                        per Regime         per Regime
```

### 13.2 Feedback Metrics

| Metric | Feeds Into |
|--------|-----------|
| Per-source accuracy by regime | Weight adjustment |
| Confidence calibration error | Confidence model tuning |
| Conflict resolution accuracy | Conflict threshold tuning |
| Fusion vs actual outcome correlation | Overall fusion quality |

---

## 14. Engineering Requirement

### 14.1 Constraints

| Constraint | Value |
|------------|-------|
| Fusion latency | < 50ms |
| Max evidence sources | 10 |
| Weight update frequency | Daily (batch) |
| Compute | CPU-friendly (weighted sum) |

### 14.2 Code Structure

```
decision_intelligence/fusion_engine/
├── evidence_collector.py       # Gather from sources
├── evidence_aligner.py         # Normalize to unified format
├── weight_manager.py           # Regime-adaptive weights
├── fusion_calculator.py        # Core fusion computation
├── confidence_aggregator.py    # Aggregated confidence
├── conflict_resolver.py        # Detect + resolve conflicts
├── regime_adapter.py           # Regime → weight mapping
├── fusion_tracer.py            # Explainable trace output
└── __init__.py
```

---

## 15. Freeze Criteria

1. **Architecture Review Passed** — Correct position between evidence sources and Decision Engine
2. **Six evidence sources defined** — World Model + Prediction + Sentiment + Microstructure + Risk + Experience
3. **Fusion pipeline complete** — Collect → Align → Weight → Fuse → Output
4. **Conflict resolution specified** — Risk priority, confidence penalty, conservative default
5. **Regime-adaptive framework** — Weight table by regime, not fixed constants
6. **Confidence aggregation** — Per-source confidence → aggregated with penalties
7. **Not a trading strategy** — Fusion produces evidence, not orders
8. **Evolution feedback loop** — Accuracy → weight adjustment

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-3 | Decision Intelligence Architecture V2.9.1 |
| 4 | Constitution V2.8.6 — Multi-model fusion principles |
| 5 | World Model V2.9.0 + AI Brain Design V2.8.6 |
| 6-7 | AI Brain Fusion Engine Ch.6 |
| 8-9 | Inferred from Belief State + Decision Architecture |
| 10 | AI Brain Design Ch.6.3 + Evolution System |
| 11-12 | Decision Architecture V2.9.1 + Risk Design V2.8.6 |
| 13 | Evolution System V2.8.6 |
| 14-15 | V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Regime weight values — confirm reference values or mark as placeholder? | §10 |
| 2 | Conflict detection threshold value | §9 |
| 3 | Microstructure evidence weight (currently 0.05) — appropriate for non-HFT? | §10 |
| 4 | Weight update governance — Evolution System or Parameter Governance? | §10 |

---

*AQF-T Decision Fusion Engine Design V1.0 — ENGINEERING DRAFT*  
*Source: AI Brain Design V2.8.6 + Decision Architecture V3.0.0 + World Model V2.9.0*  
*No original design added. All content traceable to existing AQF-T architecture.*
