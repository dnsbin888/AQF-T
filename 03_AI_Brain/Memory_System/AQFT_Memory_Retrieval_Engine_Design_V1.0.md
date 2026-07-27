# AQF-T Memory Retrieval Engine Design

Version: V1.0.0
Status: FROZEN — V2.9.2 Memory System Freeze
Phase: V2.9 Intelligence Era — Memory System
Module: Memory_System
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Memory_Retrieval_Engine_Design_V1.0.md |
| Module | Memory System — Retrieval Engine |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_Memory_System_Architecture_V2.9.2 |
| Upstream | Memory layers (Working/Episodic/Pattern/Knowledge) |
| Downstream | Decision Intelligence (context enhancement) |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Simulation Memory V3.0.0 + Knowledge Evolution V2.8.6 |

---

## 1. Purpose

### 1.1 What Retrieval Engine Does

Retrieval Engine 是 Memory System 的 **经验召回器（Experience Recall Engine）**。

它不是搜索引擎。它回答：**"在当前市场状态下，过去最相似的经验是什么？那些经验告诉我们什么？"**

| Search Engine | Retrieval Engine |
|--------------|-----------------|
| "Find documents containing X" | "Find situations similar to now" |
| Keyword match | Context similarity |
| Rank by relevance | Rank by similarity + outcome quality + recency |
| Return documents | Return decision-relevant experience |

### 1.2 What Retrieval Engine Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 搜索引擎 | 经验召回系统 |
| 数据库查询 | 上下文相似度检索 |
| 自动化决策 | 决策支持（提供经验依据） |
| 训练系统 | 检索系统（只读） |

---

## 2. Scope

### 2.1 In Scope

- Context-to-memory similarity matching
- Multi-criteria retrieval ranking
- Cross-layer retrieval (Episodic + Pattern + Knowledge)
- Retrieval confidence scoring
- Decision context enhancement
- Retrieval quality feedback

### 2.2 Out of Scope

- ❌ Web-scale search infrastructure
- ❌ Large vector database clusters
- ❌ Automated model training from retrieval
- ❌ Replacing Decision Intelligence
- ❌ Real-time streaming search

---

## 3. Architecture Position

### 3.1 In Memory System

```
Decision Intelligence
        │
        ├── Query: "Current market similar to?"
        │
        ▼
┌───────────────────────────┐
│    RETRIEVAL ENGINE       │  ← 本模块
│                           │
│  [1] Context Encode       │
│  [2] Multi-index Match    │
│  [3] Similarity Score     │
│  [4] Rank & Filter        │
│  [5] Confidence Calibrate │
│  [6] Return Experience    │
└───────────┬───────────────┘
        │
        ▼
Memory Layers (Episodic / Pattern / Knowledge)
        │
        ▼
Decision Intelligence (enhanced context)
```

---

## 4. Retrieval Philosophy

### 4.1 Core Principles

**Principle 1: Context, Not Keywords**

检索基于市场上下文相似度，不是关键词匹配。"Expansion+Warming+LowRisk" 作为一个完整的市场状态来匹配。

**Principle 2: Quality Over Quantity**

返回 5-20 条高质量匹配，不是 500 条弱相关结果。低质量经验比没有经验更危险。

**Principle 3: Recency Matters**

最近的经验权重更高。3 年前的市场结构可能与现在不同。

**Principle 4: Outcome-Informed Ranking**

成功经验（Grade A/B）排名高于失败经验（Grade D/F），除非当前查询的是"什么情况下会失败？"

---

## 5. Query Context Model

### 5.1 Query Composition

```json
{
  "query_id": "QRY_20260727_093500",
  "timestamp": "2026-07-27T09:35:00",

  "market_context": {
    "regime": "Expansion",
    "emotion_phase": "Warming",
    "emotion_score": 65,
    "risk_level": "Low",
    "risk_score": 28
  },

  "decision_context": {
    "contemplated_action": "Increase",
    "current_exposure": 0.35
  },

  "retrieval_preferences": {
    "layers": ["episodic", "pattern", "knowledge"],
    "max_results": 20,
    "min_similarity": 0.60,
    "min_outcome_grade": "C",
    "recency_weight": 0.30
  }
}
```

### 5.2 Context Vector Encoding

```
Query → Encode → Vector
         │
         ├── Regime: one-hot → embedding lookup
         ├── Emotion: score normalized → [0,1]
         ├── Risk: score normalized → [0,1]
         └── Action: embedding lookup
                  │
                  ▼
         Context Vector [384-dim]
```

---

## 6. Memory Matching Model

### 6.1 Multi-Criteria Similarity

| Criterion | Weight | Method |
|-----------|:------:|--------|
| Regime Similarity | 0.30 | Exact match + transition proximity |
| Emotion Similarity | 0.25 | Score distance within same phase |
| Risk Similarity | 0.20 | Score distance + level match |
| Action Similarity | 0.15 | Same action type |
| Market Structure | 0.10 | Multi-dim state vector distance |

### 6.2 Similarity Score

```
Similarity(Q, M) = Σ (Criterion_i_Weight × Similarity_i(Q, M))

Where Similarity_i:
  Regime:     1.0 if exact match, 0.7 if adjacent regime, 0.3 otherwise
  Emotion:    1.0 - |score_Q - score_M| / 100
  Risk:       1.0 - |score_Q - score_M| / 100
  Action:     1.0 if same, 0.5 if adjacent action level
  Structure:  Cosine_similarity(state_vector_Q, state_vector_M)
```

### 6.3 Layer-Specific Matching

| Layer | Match Method |
|-------|-------------|
| Episodic | Vector similarity + criteria match |
| Pattern | Condition logic match (regime=X AND emotion=Y AND risk<Z) |
| Knowledge | Rule relevance (tag match + applicability check) |

---

## 7. Similarity Evaluation

### 7.1 Similarity Thresholds

| Similarity | Label | Action |
|:----------:|-------|--------|
| > 0.85 | Very Similar | High confidence — strong reference |
| 0.70–0.85 | Similar | Good reference — apply with caution |
| 0.60–0.70 | Somewhat Similar | Weak reference — informational only |
| < 0.60 | Dissimilar | Not returned (filtered) |

### 7.2 Similarity Breakdown

```json
{
  "episode_id": "EP_20250615_003",
  "total_similarity": 0.82,
  "breakdown": {
    "regime_similarity": 1.00,
    "emotion_similarity": 0.85,
    "risk_similarity": 0.90,
    "action_similarity": 1.00,
    "structure_similarity": 0.72
  },
  "outcome_grade": "A",
  "age_days": 42,
  "relevance": "High"
}
```

---

## 8. Ranking Mechanism

### 8.1 Composite Rank Score

```
Rank_Score = 
  0.35 × Similarity_Score       # How similar is this experience?
+ 0.25 × Outcome_Quality         # Was the outcome good? (A=1.0, B=0.8, C=0.5, D=0.2, F=0.0)
+ 0.25 × Recency_Factor          # How recent? (exponential decay, half-life=180 days)
+ 0.15 × Retrieval_Frequency     # Has this been useful before? (normalized usage count)
```

### 8.2 Recency Decay

```
Recency_Factor = e^(-λ × age_days)

Where λ = ln(2) / 180  (half-life = 180 days)

Example:
  age=0:    1.00
  age=90:   0.71
  age=180:  0.50
  age=365:  0.25
```

### 8.3 Ranking Output

```
Rank  | Episode    | Similarity | Grade | Age  | Rank_Score
──────┼────────────┼────────────┼───────┼──────┼────────────
  1   | EP_0627_01 |    0.85    |   A   | 15d  |   0.91
  2   | EP_0612_03 |    0.82    |   A   | 42d  |   0.87
  3   | EP_0520_07 |    0.78    |   B   | 68d  |   0.79
  4   | EP_0615_02 |    0.80    |   C   | 38d  |   0.72
  5   | EP_0410_05 |    0.75    |   A   | 108d |   0.68
```

---

## 9. Retrieval Confidence

### 9.1 Confidence Factors

```
Retrieval_Confidence = f(
  Top-K_Similarity_Avg,       # Average similarity of top results
  Result_Consistency,          # Do top results agree on outcome?
  Sample_Sufficiency,          # Enough results? (>5 = good, <3 = low)
  Recency_Quality              # Are top results recent enough?
)
```

### 9.2 Confidence Levels

| Confidence | Meaning | Decision Impact |
|:----------:|---------|----------------|
| > 0.80 | Strong reference | Can significantly weight experience |
| 0.60–0.80 | Moderate reference | Use as supplementary input |
| 0.40–0.60 | Weak reference | Informational only, do not rely on |
| < 0.40 | Insufficient | No useful experience found |

---

## 10. Decision Interface

### 10.1 Experience-Enhanced Decision Context

```python
POST /memory/retrieve
  Request: QueryContext
  Response:
  {
    "retrieval_id": "RET_20260727_093500",
    "query_context": { ... },

    "results": {
      "episodes": [ /* top 10 similar episodes */ ],
      "patterns": [ /* matching patterns */ ],
      "knowledge": [ /* applicable rules */ ]
    },

    "summary": {
      "total_found": 47,
      "top_similarity_avg": 0.82,
      "historical_success_rate": 0.72,
      "most_common_outcome": "Increase → Grade A/B (68%)",
      "key_risk_pattern": "None matching current conditions"
    },

    "recommendation_context": {
      "supports_contemplated_action": true,
      "confidence_boost": +0.05,
      "key_reference": "EP_0627_01: Similar Expansion+Warming, Increase→A, +8.2%",
      "caution": null
    },

    "retrieval_confidence": 0.78
  }
```

### 10.2 Integration Flow

```
Decision Intelligence contemplates "Increase"
        │
        ▼
Retrieval Engine: "Has this worked before?"
        │
        ▼
Returns: "72% success rate in similar conditions. Strongest match: +8.2%"
        │
        ▼
Decision Intelligence: Confidence adjusted +0.05. Action: Increase.
```

---

## 11. Evolution Interface

### 11.1 Retrieval Quality Feedback

```
After outcome, evaluate retrieval quality:

  Did the retrieved experiences accurately predict the outcome?
  Were the top-ranked results actually the most relevant?
  Should any patterns be updated based on new data?
```

### 11.2 Feedback Metrics

| Metric | Feeds Into |
|--------|-----------|
| Retrieval precision@K | Similarity model tuning |
| Rank correlation with outcome | Ranking weight adjustment |
| Pattern hit rate | Pattern extraction threshold |
| Retrieval confidence calibration | Confidence model |

---

## 12. Failure Handling

### 12.1 What If No Good Match Exists?

```
IF top_similarity < 0.60 OR result_count < 3:
  → Return "No sufficient experience"
  → Decision proceeds without memory enhancement
  → This event recorded as "novel situation"
  → Flagged for future pattern learning
```

### 12.2 What If Retrieved Experience Was Wrong?

```
IF retrieval suggested success but outcome was poor:
  → Flag the retrieved episode for re-evaluation
  → Reduce ranking weight of similar episodes temporarily
  → Feed contradiction signal to Evolution System
```

---

## 13. Engineering Requirement

### 13.1 Constraints

| Constraint | Value |
|------------|-------|
| Retrieval latency | < 100ms |
| Max results returned | 20 |
| Min similarity threshold | 0.60 |
| Index update frequency | Daily (batch) |
| Vector dimension | 384 (lightweight) |
| Index backend | FAISS (local) or Chroma (embedded) |

### 13.2 Code Structure

```
memory_system/retrieval/
├── query_encoder.py            # Context → query vector
├── similarity_scorer.py        # Multi-criteria similarity
├── episodic_searcher.py        # Episodic memory search
├── pattern_matcher.py          # Pattern condition matching
├── knowledge_lookup.py         # Knowledge rule retrieval
├── ranker.py                   # Composite ranking
├── confidence_calibrator.py    # Retrieval confidence
├── decision_enhancer.py        # Decision context enrichment
└── __init__.py
```

---

## 14. Testing Requirement

### 14.1 Unit Tests

- Same regime → similarity > 0.85
- Different regime → similarity < 0.50
- A-grade outcome → rank boost vs D-grade
- Recent (7d) → higher rank than old (365d), all else equal

### 14.2 Integration Tests

- Full loop: Decision query → Retrieve → Enhance → Decision output
- No results scenario: novel situation handling
- Retrieval quality feedback → rank weight adjustment

---

## 15. Freeze Criteria

1. **Architecture Review Passed** — Correct position between Memory layers and Decision Intelligence
2. **5-criteria similarity model defined** — Regime + Emotion + Risk + Action + Structure
3. **Composite ranking specified** — Similarity + Outcome + Recency + Frequency
4. **Retrieval confidence gated** — 4 levels with clear decision impact
5. **Decision interface clear** — Enhances context, does not make decisions
6. **Failure handling** — Novel situations, wrong retrievals
7. **Personal workstation scale** — Local index, 384-dim vectors, <100ms

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-3 | Memory System Architecture V2.9.2 |
| 4 | Retrieval design principles |
| 5-6 | Simulation Memory V3.0.0 Ch.4-5 |
| 7-8 | Inferred from similarity/ranking best practices |
| 9 | Confidence models from Belief State + Decision |
| 10-11 | Decision Intelligence V2.9.1 + Evolution System V2.8.6 |
| 12-15 | V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Recency half-life: 180 days appropriate for A-share? | §8 |
| 2 | Min similarity threshold: 0.60 — confirm? | §7 |
| 3 | Vector dimension: 384 (local) vs 768 (Blueprint) — confirm? | §13 |

---

*AQF-T Memory Retrieval Engine Design V1.0 — ENGINEERING DRAFT*  
*Source: Simulation Memory V3.0.0 + Memory System Architecture V2.9.2*  
*No original design added. All content traceable to existing AQF-T architecture.*
