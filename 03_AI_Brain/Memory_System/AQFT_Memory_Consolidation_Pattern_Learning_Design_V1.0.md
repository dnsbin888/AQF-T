# AQF-T Memory Consolidation & Pattern Learning Design

Version: V1.0.0
Status: FROZEN — V2.9.2 Memory System Freeze
Phase: V2.9 Intelligence Era — Memory System
Module: Memory_System
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Memory_Consolidation_Pattern_Learning_Design_V1.0.md |
| Module | Memory System — Consolidation & Pattern Learning |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_Memory_System_Architecture_V2.9.2 |
| Upstream | Episodic Memory + Retrieval Engine |
| Downstream | Pattern Memory → Knowledge Memory → Evolution System |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Simulation Memory V3.0.0 + Knowledge Evolution V2.8.6 + Self Learning V2.8.6 |

---

## 1. Purpose

### 1.1 What Consolidation Does

Consolidation Engine 是 Memory System 的 **经验提炼器（Experience Distiller）**。

它回答：**"从大量交易经历中，哪些重复出现的模式值得被永久记住？"**

| Episodic Memory | Consolidation | Pattern Memory |
|----------------|--------------|----------------|
| 具体事件 | → 提炼 → | 通用模式 |
| "2026-07-27 Expansion, Increase, +8%" | | "Expansion+Warming → Increase 成功率 72%" |
| Single case | | Generalized rule |

### 1.2 What Consolidation Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 自动策略生成器 | 模式识别引擎 |
| 模型训练系统 | 经验提炼系统 |
| 替代 Evolution System | Evolution 的数据预处理 |
| 自动修改交易规则 | 发现可复用经验模式 |

---

## 2. Scope

### 2.1 In Scope

- Episode clustering and pattern detection
- Pattern validation (statistical significance check)
- Pattern confidence scoring
- A-share specific pattern types
- Pattern → Knowledge promotion pipeline
- Consolidation scheduling (when to run)

### 2.2 Out of Scope

- ❌ Automatic strategy modification
- ❌ Automatic model parameter changes
- ❌ Replacing Evolution System (this provides input TO Evolution)
- ❌ Large-scale ML training infrastructure

---

## 3. Architecture Position

### 3.1 In Memory System

```
Episodic Memory (raw experiences)
        │
        ▼
┌───────────────────────────────┐
│    CONSOLIDATION ENGINE       │  ← 本模块
│                               │
│  [1] Episode Collection       │
│  [2] Pattern Detection        │
│  [3] Pattern Validation       │
│  [4] Confidence Scoring       │
│  [5] Pattern → Knowledge      │
│  [6] Output to Memory Layers  │
└───────────────┬───────────────┘
        │
        ▼
Pattern Memory → Knowledge Memory
        │
        ▼
Evolution System
```

### 3.2 Consolidation Triggers

| Trigger | Action |
|---------|--------|
| N≥30 similar episodes accumulated | Run pattern detection |
| Weekly scheduled run | Check for new patterns |
| Existing pattern confidence drops | Re-evaluate pattern |
| New regime detected | Cross-check existing patterns |
| Manual (human review) | Ad-hoc consolidation |

---

## 4. Consolidation Philosophy

### 4.1 Core Principles

**Principle 1: Quality Over Quantity**

不是每个重复事件都是模式。需要统计显著性验证。N<30 不形成模式。

**Principle 2: Context Is Everything**

同一价格形态在不同 Regime 下是不同模式。Expansion 中的突破 ≠ Distribution 中的突破。

**Principle 3: Patterns Have Expiry**

市场结构会变。3 年前的模式今天可能无效。模式需要周期性重新验证。

**Principle 4: A-Share Characteristics Matter**

涨停生态、情绪周期、游资行为——这些 A 股特有的结构性特征必须体现在模式识别中。

---

## 5. Experience Processing Pipeline

### 5.1 Full Pipeline

```
Stage 1: COLLECT
  Gather episodes from Episodic Memory
  Filter: Grade A-C, age < 3 years
         │
Stage 2: GROUP
  Cluster by: Regime + Emotion Phase + Action + Outcome
  Min cluster size: N ≥ 30
         │
Stage 3: DETECT
  Statistical test: Is this cluster significantly different from baseline?
  Effect size: Success rate vs. random action selection
         │
Stage 4: VALIDATE
  Cross-validation: split episodes into train/validate sets
  Temporal validation: does pattern hold in recent data?
         │
Stage 5: SCORE
  Assign pattern confidence based on sample size, consistency, recency
         │
Stage 6: STORE
  Write valid pattern to Pattern Memory
  Or: update existing pattern if refinement detected
         │
Stage 7: PROMOTE (optional)
  IF pattern confidence > 0.80 AND N > 100 AND cross-regime validated
  → Promote to Knowledge Memory
```

---

## 6. Pattern Extraction

### 6.1 Pattern Detection Methods

| Method | Use Case |
|--------|----------|
| Frequency analysis | "How often does action X succeed in regime Y?" |
| Sequence mining | "What typically happens after event Z?" |
| Contrast analysis | "What differs between successful and failed cases?" |
| Temporal clustering | "What time patterns emerge around regime transitions?" |

### 6.2 Pattern Object

```json
{
  "pattern_id": "PAT_EXPANSION_WARMING_INCREASE",
  "name": "Expansion-Warming-Increase Success Pattern",
  "type": "Regime-Action",

  "condition": {
    "regime": ["Expansion"],
    "emotion_phase": ["Warming"],
    "risk_level": ["Low", "Medium"],
    "risk_score_max": 50
  },

  "action": "Increase",

  "statistics": {
    "total_episodes": 127,
    "success_count": 91,
    "success_rate": 0.72,
    "avg_return_5d": 0.052,
    "avg_return_20d": 0.091,
    "max_drawdown_5d": -0.035,
    "sharpe_like": 1.45
  },

  "validation": {
    "train_success_rate": 0.73,
    "test_success_rate": 0.69,
    "temporal_decay": 0.05,
    "cross_regime_valid": true
  },

  "confidence": 0.78,
  "sample_sufficiency": true,
  "last_updated": "2026-07-27",
  "next_review": "2026-10-27",
  "status": "active"
}
```

---

## 7. Pattern Validation

### 7.1 Validation Checklist

| Check | Criteria | Pass? |
|-------|----------|:-----:|
| Sample size | N ≥ 30 | ✅ |
| Statistical significance | p < 0.05 vs random | ✅ |
| Temporal stability | Test set success rate ≥ 0.85 × Train | [NEEDS REVIEW] |
| Recency check | ≥ 5 episodes in last 90 days | ✅ |
| No contradiction | No Knowledge rule directly contradicts | ✅ |

### 7.2 Validation Failures

| Failure | Action |
|---------|--------|
| N < 30 | Keep in "candidate" status, wait for more data |
| p ≥ 0.05 | Not a real pattern — discard or keep as "weak signal" |
| Temporal decay > 0.15 | Pattern may be obsolete. Flag for human review |
| Contradiction found | Both flagged. Evolution System resolves conflict |

---

## 8. Pattern Confidence Model

### 8.1 Confidence Formula

```
Pattern_Confidence = 
  0.30 × Sample_Size_Factor     # min(1.0, N/100)
+ 0.25 × Success_Consistency     # 1.0 - std_dev(success_rate)
+ 0.25 × Temporal_Stability      # test/train ratio
+ 0.20 × Recency_Factor          # % of episodes in last 180 days
```

### 8.2 Confidence Levels

| Confidence | Status | Usage |
|:----------:|--------|-------|
| > 0.80 | Trusted | Used by Decision Intelligence as strong reference |
| 0.65–0.80 | Active | Used with caveat |
| 0.50–0.65 | Candidate | Monitored, not yet trusted for decisions |
| < 0.50 | Weak | Informational only |

---

## 9. Pattern Storage

### 9.1 Pattern Lifecycle

```
Detected → Candidate → Validated → Active → Trusted
                                       │
                                       ▼
                                   Outdated → Archived
                                       │
                                       ▼
                                   Contradicted → Reviewed → Updated/Retired
```

### 9.2 A-Share Specific Pattern Types

| Type | Example | Detection |
|------|---------|-----------|
| 情绪周期模式 | "冰点→回暖，首板晋级率 > 60% 后 3 日" | Emotion score trajectory |
| 龙头演化模式 | "龙头高度 7→11 期间，跟风扩散特征" | Board height + breadth |
| 主线切换模式 | "旧主线退潮→新主线确认的时间窗口" | Theme rotation detection |
| 涨停梯队模式 | "连板梯队完整(2/3/4/5+) → 情绪持续性" | Board ladder structure |
| 风险预警模式 | "炸板率>40% + 天地板 → 退潮概率 70%" | Risk signal combination |

---

## 10. Knowledge Interface

### 10.1 Pattern → Knowledge Promotion

```
Pattern confidence > 0.80
AND N > 100
AND cross-regime validated (applicable across multiple cycles)
AND no contradiction in last 90 days
        │
        ▼
Promoted to Knowledge Memory
```

### 10.2 Knowledge Demotion

```
Knowledge contradicted by 3+ new episodes
OR temporal decay > 0.20
        │
        ▼
Demoted back to Pattern for re-evaluation
```

---

## 11. Decision Interface

### 11.1 Patterns Supporting Decisions

```
Decision Intelligence queries:
  "What patterns match current conditions?"

Consolidation provides:
  - Active patterns matching current regime + emotion
  - Success rates per pattern
  - Confidence levels
  - Recent validation status
```

### 11.2 Pattern Alert

When a known high-risk pattern is detected:

```json
{
  "alert": "PATTERN MATCH: Distribution-Emotion-Divergence",
  "pattern_confidence": 0.82,
  "historical_outcome": "65% probability of regime shift to Panic within 5 days",
  "recommended": "Review aggressive positions"
}
```

---

## 12. Evolution Interface

### 12.1 Consolidation → Evolution

```
Consolidation extracts patterns.
Evolution System decides:
  - Should strategy weights change based on this pattern?
  - Should risk thresholds adjust?
  - Should model training incorporate this pattern?
```

### 12.2 Pattern Data Feed

```python
GET /memory/patterns/feed
  ?status=active,trusted
  &updated_since=2026-07-01
  
  → Evolution System receives structured pattern data
  → Evolution decides HOW to use it
```

**Boundary: Consolidation discovers patterns. Evolution acts on them. No direct auto-modification.**

---

## 13. Failure Handling

### 13.1 Pattern Deterioration

```
IF pattern success rate drops > 10% in recent 50 episodes:
  → Flag: "Pattern may be deteriorating"
  → Reduce confidence
  → Schedule re-validation
```

### 13.2 False Pattern Prevention

```
IF pattern detected but:
  - N < 30: labeled "candidate" (not active)
  - p > 0.05: labeled "weak signal"
  - Only in 1 regime: labeled "regime-specific" (not generalized)
```

---

## 14. Engineering Requirement

### 14.1 Constraints

| Constraint | Value |
|------------|-------|
| Consolidation runtime | < 5 minutes (batch, weekly) |
| Min episodes per pattern | 30 |
| Max active patterns | 200 |
| Storage per pattern | < 2KB |
| Compute | CPU-friendly (statistical tests, not deep learning) |

### 14.2 Code Structure

```
memory_system/consolidation/
├── episode_collector.py        # Gather + filter episodes
├── cluster_engine.py           # Group similar episodes
├── pattern_detector.py         # Statistical pattern detection
├── pattern_validator.py        # Cross-validation + significance
├── confidence_scorer.py        # Pattern confidence model
├── a_share_patterns.py         # A-share specific pattern types
├── knowledge_promoter.py       # Pattern → Knowledge promotion
├── consolidation_scheduler.py  # Trigger management
└── __init__.py
```

---

## 15. Freeze Criteria

1. **Architecture Review Passed** — Correct position between Episodic and Pattern/Knowledge memory
2. **7-stage pipeline complete** — Collect→Group→Detect→Validate→Score→Store→Promote
3. **Pattern model defined** — Condition + Statistics + Validation + Confidence
4. **Statistical validation** — N≥30, p<0.05, temporal stability, recency
5. **A-share pattern types** — 5 specific types: emotion cycle, leader, theme, ladder, risk
6. **Knowledge promotion/demotion** — Clear criteria for pattern→knowledge lifecycle
7. **No auto-modification** — Consolidation discovers; Evolution acts
8. **Personal workstation scale** — Statistical methods, not deep learning clusters

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-4 | Memory System Architecture V2.9.2 + Simulation Memory V3.0.0 |
| 5-6 | Simulation Memory V3.0.0 Ch.5-6 + Self Learning V2.8.6 |
| 7-8 | Inferred from statistical validation best practices |
| 9 | A-share emotion cycle + Market State Space V1.0 |
| 10-11 | Memory Architecture V2.9.2 + Decision Intelligence V2.9.1 |
| 12 | Evolution System V2.8.6 — Knowledge Evolution |
| 13-15 | V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Min cluster size N=30 — appropriate for A-share? Rare patterns may need lower threshold | §5 |
| 2 | Temporal stability threshold (test ≥ 0.85 × train) — confirm? | §7 |
| 3 | Pattern expiry: auto-archive after 365 days no new supporting episodes? | §9 |

---

*AQF-T Memory Consolidation & Pattern Learning Design V1.0 — ENGINEERING DRAFT*  
*Source: Simulation Memory V3.0.0 + Knowledge Evolution V2.8.6 + Self Learning V2.8.6*  
*No original design added. All content traceable to existing AQF-T architecture.*
