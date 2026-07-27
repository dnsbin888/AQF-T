# AQF-T Memory System Architecture

Version: V2.9.2
Status: FROZEN — V2.9.2 Memory System Freeze
Phase: V2.9 Intelligence Era — Memory System
Module: Memory_System
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Memory_System_Architecture_V2.9.2.md |
| Module | Memory System — Cognitive Experience Layer |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V2.9.2 |
| Parent | AQF-T V2.9.1 Decision Intelligence (FROZEN) |
| Upstream | World Model V2.9.0 ✅ + Decision Intelligence V2.9.1 ✅ |
| Downstream | Evolution System V2.8.6 |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Simulation Memory V3.0.0 + Knowledge Evolution V2.8.6 + Self Learning V2.8.6 |

---

## 1. Purpose

### 1.1 What Memory System Does

Memory System 是 AQF-T 的 **长期经验认知层（Cognitive Experience Layer）**。

它不是数据库。它回答：

| Question | Memory Layer |
|----------|-------------|
| 现在正在发生什么？ | Working Memory |
| 过去发生过什么？ | Episodic Memory |
| 反复出现什么模式？ | Pattern Memory |
| 我们学到了什么？ | Knowledge Memory |

### 1.2 Why Memory Matters

```
Without Memory:  Each market event is new. No learning accumulates.
With Memory:     Past experience informs present decisions. System improves.
```

[Source: Constitution V2.8.6 — Principle 8: Historical Respect]

### 1.3 Memory System ≠ Database

| Database | Memory System |
|----------|--------------|
| Stores raw data | Stores experience |
| SQL queries | Semantic retrieval |
| Row-level access | Context-based recall |
| Dumb storage | Intelligent recall |
| "What was the price?" | "Has this pattern appeared before?" |

---

## 2. Scope

### 2.1 In Scope

- 4-layer memory architecture (Working / Episodic / Pattern / Knowledge)
- Memory record capture from Decision Intelligence
- Pattern extraction from historical records
- Context-based memory retrieval
- Memory consolidation (short-term → long-term)
- Decision Intelligence query interface
- Evolution System learning interface

### 2.2 Out of Scope

- ❌ Raw market data storage (Data Runtime)
- ❌ Trade execution logs (Execution Runtime)
- ❌ Automatic model parameter modification (Evolution System)
- ❌ Large-scale enterprise knowledge graph
- ❌ Cloud-based vector database clusters

### 2.3 Target Scale

| Constraint | Limit |
|------------|-------|
| Active Working Memory | Current session only |
| Episodic records | Last 3 years (~5,000 decisions) |
| Pattern library | ~200 patterns |
| Knowledge rules | ~500 rules |
| Storage | Local SQLite/PostgreSQL + FAISS/Chroma (local) |

---

## 3. Architecture Position

### 3.1 In AQF-T System

```
World Model ──→ Decision Intelligence ──→ Strategy → Risk → Execution
       │               │
       │               ▼
       │        ┌──────────────┐
       └───────→│MEMORY SYSTEM │←─────── Experience Capture
                │              │
                │ Working      │ 现在
                │ Episodic     │ 过去
                │ Pattern      │ 模式
                │ Knowledge    │ 知识
                └──────┬───────┘
                       │
                       ▼
                Evolution System
```

### 3.2 Relationship to Other Systems

| System | Memory Provides | Memory Receives |
|--------|----------------|-----------------|
| World Model | Historical regime patterns | Current state context |
| Decision Intelligence | Similar past situations, pattern alerts | Decision records |
| Evolution System | Structured experience data | Knowledge updates |

---

## 4. Memory Philosophy

### 4.1 Core Principles

**Principle 1: Memory Is Selective**

不是记录一切。只记录对决策有价值的信息。噪声数据不进入记忆。

**Principle 2: Memory Consolidates Over Time**

短期记忆（Working）→ 评估 → 有价值 → 进入长期记忆（Episodic/Pattern/Knowledge）

**Principle 3: Memory Is Retrievable by Context**

不是靠 ID 查询。靠"当前市场环境类似什么？"检索。

**Principle 4: Memory Drives Improvement**

记忆的目的不是存档。是让未来决策比过去更好。

### 4.2 Memory Consolidation Cycle

```
Decision(t) → Working Memory (active)
       │
       ▼ (outcome observed)
Episodic Memory (stored with evaluation)
       │
       ▼ (pattern detected across multiple episodes)
Pattern Memory (generalized rule)
       │
       ▼ (validated across regimes and time)
Knowledge Memory (trusted principle)
```

---

## 5. Memory Layer Architecture

### 5.1 Four-Layer Structure

```
┌─────────────────────────────────────────────┐
│              KNOWLEDGE MEMORY               │  "我们学到的真理"
│   Validated principles, market rules,       │
│   trusted patterns across regimes            │
│   Size: ~500 rules                           │
│   TTL: Permanent (until refuted)             │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────┴───────────────────────┐
│              PATTERN MEMORY                  │  "反复出现的模式"
│   Recurring market patterns,                 │
│   regime transitions, behavior templates     │
│   Size: ~200 patterns                        │
│   TTL: Months to years                       │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────┴───────────────────────┐
│              EPISODIC MEMORY                 │  "发生过的事件"
│   Specific market events with full context,  │
│   decisions made, outcomes, evaluation       │
│   Size: ~5,000 episodes (3 years)            │
│   TTL: 3 years, then archived               │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────┴───────────────────────┐
│              WORKING MEMORY                  │  "当前正在发生"
│   Active session context: current state,     │
│   active decisions, pending outcomes         │
│   Size: ~50 active items                     │
│   TTL: Current trading session               │
└─────────────────────────────────────────────┘
```

### 5.2 Layer Comparison

| Layer | Question | Content | Update | Retrieval |
|-------|----------|---------|--------|-----------|
| Working | What now? | Active context | Real-time | Direct access |
| Episodic | What happened? | Event records | Daily | Similarity search |
| Pattern | What repeats? | Generalized patterns | Weekly | Pattern matching |
| Knowledge | What's true? | Validated rules | Monthly | Rule lookup |

---

## 6. Working Memory Design

### 6.1 Purpose

Working Memory 是当前交易会话的活跃上下文。类似人类的"短期记忆"——容量有限，高度活跃，随会话结束清空。

### 6.2 Content

```json
{
  "session_id": "SES_20260727",
  "active_since": "2026-07-27T09:30:00",

  "current_state": {
    "regime": "Expansion",
    "emotion": "Warming",
    "risk_level": "Low",
    "active_positions": 3,
    "exposure": 0.45
  },

  "pending_decisions": [
    { "id": "DEC_001", "status": "awaiting_outcome", "since": "+2d" }
  ],

  "active_alerts": [
    { "type": "sentiment_heating", "severity": "info" }
  ],

  "recent_retrievals": [
    { "query": "Expansion+Warming patterns", "results": 12, "timestamp": "..." }
  ]
}
```

### 6.3 Capacity

- Max 50 active items
- Auto-eviction: oldest/lowest relevance first
- Session reset at market close

---

## 7. Episodic Memory Design

### 7.1 Purpose

Episodic Memory 存储完整的市场事件——包含上下文、决策、结果和评估。

### 7.2 Memory Record

```json
{
  "episode_id": "EP_20260727_001",
  "timestamp": "2026-07-27T09:35:00",

  "context": {
    "regime": "Expansion",
    "emotion_phase": "Warming",
    "emotion_score": 65,
    "risk_level": "Low",
    "scenario": "Expansion continues (P=45%)"
  },

  "decision": {
    "action": "Increase",
    "confidence": 0.78,
    "reasoning_summary": "Expansion+Warming+Low Risk → aggressive supported"
  },

  "outcome": {
    "observed_at": "2026-08-06",
    "direction_correct": true,
    "return_5d": "+4.2%",
    "return_20d": "+7.8%",
    "evaluation_grade": "A"
  },

  "patterns_triggered": ["expansion_warming_increase"],
  "learning_value": 0.85,
  "tags": ["Expansion", "Warming", "Increase", "A-grade"]
}
```

### 7.3 Retrieval

```python
# Find similar episodes
GET /memory/episodic/search
  ?regime=Expansion
  &emotion=Warming
  &grade=A
  &limit=20
  → Returns top 20 similar successful episodes
```

---

## 8. Pattern Memory Design

### 8.1 Purpose

Pattern Memory 从多个 Episodic 记录中提取反复出现的模式。

### 8.2 Pattern Types

| Pattern Type | Example | Detection |
|-------------|---------|-----------|
| Regime-Action | "Expansion+Warming → Increase succeeds 72%" | Frequency + outcome |
| Regime Transition | "Mania → Distribution preceded by sentiment peak" | Sequence mining |
| Failure Pattern | "Increase during Distribution → D/F 65%" | Outcome clustering |
| Timing Pattern | "Enter within 3d of Warming onset → 78% success" | Temporal analysis |
| Risk Pattern | "Risk<40 + Expansion → 85% decision quality" | Threshold discovery |

### 8.3 Pattern Object

```json
{
  "pattern_id": "PAT_001",
  "name": "Expansion-Warming-Increase",
  "type": "Regime-Action",
  "condition": {
    "regime": "Expansion",
    "emotion_phase": "Warming",
    "risk_max": 40
  },
  "action": "Increase",
  "statistics": {
    "sample_size": 127,
    "success_rate": 0.72,
    "avg_return_5d": "+5.2%",
    "avg_return_20d": "+9.1%",
    "confidence": 0.78
  },
  "last_updated": "2026-07-27",
  "status": "active"
}
```

---

## 9. Knowledge Memory Design

### 9.1 Purpose

Knowledge Memory 是经过长期验证、跨多个 Regime 和市场周期确认的原则。这是 AQF-T "深信不疑"的知识。

### 9.2 Knowledge Types

| Type | Example |
|------|---------|
| Market Rule | "Expansion 期趋势策略优于反转策略" |
| Risk Principle | "Risk Score > 60 时禁止新开仓" |
| Regime Knowledge | "Mania→Distribution 转换通常由炸板率飙升先行" |
| Decision Principle | "高置信度(>0.8)决策的准确率显著高于低置信度" |
| A-Share Specific | "连板高度≥11 + 异动 → 退潮概率 65%" |

### 9.3 Knowledge Object

```json
{
  "knowledge_id": "KN_001",
  "principle": "Expansion regime favors trend-following over mean-reversion",
  "evidence": {
    "derived_from": "PAT_001, PAT_007, PAT_015",
    "episodes_supporting": 347,
    "episodes_contradicting": 53,
    "confidence": 0.87,
    "validated_regimes": ["Expansion", "Recovery"]
  },
  "status": "validated",
  "last_reviewed": "2026-07-27",
  "reviewed_by": "Evolution System"
}
```

### 9.4 Knowledge Lifecycle

```
Pattern detected → Pattern validated (n>100) → Promoted to Knowledge
Knowledge refuted → Confidence drops → Demoted to Pattern → Re-evaluated
```

---

## 10. Memory Retrieval Engine

### 10.1 Retrieval Modes

| Mode | Query | Returns |
|------|-------|---------|
| Similarity | "Current market looks like?" | Top-K similar episodes |
| Pattern | "Known patterns matching current conditions?" | Matching patterns |
| Knowledge | "What do we know about this regime?" | Relevant knowledge rules |
| Hybrid | "What does past experience say?" | Combined results ranked by relevance |

### 10.2 Retrieval Pipeline

```
[1] Encode current context → context vector
        │
[2] Multi-index search:
    ├→ Episodic index (similarity)
    ├→ Pattern index (condition match)
    └→ Knowledge index (rule lookup)
        │
[3] Rank results by relevance + recency + outcome_quality
        │
[4] Return top-K with confidence scores
```

### 10.3 API

```python
GET /memory/retrieve
  ?context={current_state}
  &layers=episodic,pattern,knowledge
  &limit=20
  Response:
  {
    "episodes": [...],     # similar past situations
    "patterns": [...],     # matching patterns
    "knowledge": [...],    # relevant rules
    "summary": "72% of similar Expansion+Warming episodes resulted in successful Increase decisions"
  }
```

---

## 11. Memory Update Mechanism

### 11.1 Update Triggers

| Trigger | Action |
|---------|--------|
| Decision made | → Working Memory (new active item) |
| Outcome observed | → Episodic Memory (record with evaluation) |
| N similar episodes accumulated (N≥30) | → Pattern extraction check |
| Pattern validated (n≥100, confidence≥0.70) | → Knowledge promotion check |
| Knowledge contradicted (3+ counter-examples) | → Knowledge review trigger |

### 11.2 Consolidation Schedule

| Process | Frequency | Trigger |
|---------|:---------:|---------|
| Working → Episodic | Per outcome | Outcome observed |
| Episodic → Pattern | Weekly | N≥30 similar episodes |
| Pattern → Knowledge | Monthly | Pattern confidence ≥ 0.70, n ≥ 100 |
| Knowledge review | Quarterly | Scheduled or triggered by contradiction |

---

## 12. Decision Interface

### 12.1 Memory → Decision Intelligence

```
Before each decision, Decision Intelligence queries Memory:

  "Has the market been in this state before?"
  "What patterns match these conditions?"
  "What do we know about this situation?"

Memory returns:
  - Similar episodes with outcomes
  - Matching patterns with statistics
  - Applicable knowledge rules
  - Suggested confidence adjustment
```

### 12.2 Decision Context Enhancement

```python
POST /memory/enhance-decision
  Request: { decision_context }
  Response:
  {
    "similar_situations": 15,
    "historical_success_rate": 0.72,
    "matching_patterns": ["Expansion-Warming-Increase"],
    "applicable_knowledge": ["Expansion favors trend-following"],
    "confidence_adjustment": +0.05,
    "risk_warning": null
  }
```

---

## 13. Evolution Interface

### 13.1 Memory → Evolution System

```
Memory feeds Evolution System with structured experience:

  - Episodic records → Training data for pattern recognition
  - Pattern statistics → Parameter tuning feedback
  - Knowledge rules → Validation targets
  - Contradiction reports → Areas needing model improvement
```

### 13.2 Feed API

```python
GET /memory/evolution-feed
  ?since=2026-07-01
  &layers=episodic,pattern
  Response: Structured batch of evaluated experiences
```

---

## 14. Engineering Requirement

### 14.1 Constraints

| Constraint | Value |
|------------|-------|
| Working Memory capacity | 50 items |
| Episodic retention | 3 years (~5,000 records) |
| Pattern library | ~200 patterns |
| Knowledge base | ~500 rules |
| Retrieval latency | < 100ms |
| Storage | Local SQLite/PostgreSQL + FAISS/Chroma |
| Embedding dimension | 384 (lightweight, local) |

### 14.2 Code Structure

```
memory_system/
├── working_memory.py           # Active session context
├── episodic_store.py           # Episode capture + retrieval
├── pattern_extractor.py        # Pattern mining from episodes
├── knowledge_base.py           # Rule storage + validation
├── retrieval_engine.py         # Multi-index similarity search
├── consolidation_worker.py     # Background: episodic→pattern→knowledge
├── decision_enhancer.py        # Decision context enrichment
├── evolution_feeder.py         # Evolution System data feed
└── __init__.py
```

### 14.3 Storage Schema

```sql
CREATE TABLE episodic_memory (
    episode_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    regime TEXT,
    emotion_phase TEXT,
    action TEXT,
    confidence REAL,
    grade TEXT,
    context_json TEXT,
    outcome_json TEXT,
    embedding BLOB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE patterns (
    pattern_id TEXT PRIMARY KEY,
    name TEXT,
    condition_json TEXT,
    statistics_json TEXT,
    confidence REAL,
    status TEXT
);

CREATE TABLE knowledge (
    knowledge_id TEXT PRIMARY KEY,
    principle TEXT,
    evidence_json TEXT,
    confidence REAL,
    status TEXT
);
```

---

## 15. Freeze Criteria

1. **Architecture Review Passed** — Memory correctly positioned between Decision and Evolution
2. **Four layers defined** — Working / Episodic / Pattern / Knowledge with clear distinctions
3. **Retrieval engine specified** — Multi-index similarity + pattern + knowledge search
4. **Consolidation pipeline** — Working→Episodic→Pattern→Knowledge lifecycle
5. **Decision interface clear** — Memory enhances, does not replace, Decision Intelligence
6. **Evolution interface clear** — Memory feeds, does not drive, Evolution System
7. **Personal workstation scale** — Local DB, <200 patterns, <500 rules
8. **Not a database** — Semantic retrieval, not SQL queries

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-4 | Constitution V2.8.6 + Decision Intelligence V2.9.1 |
| 5 | Simulation Memory V3.0.0 Ch.3-4 |
| 6-7 | Simulation Memory V3.0.0 Ch.5 + Decision Memory V2.9.1 |
| 8-9 | Knowledge Evolution V2.8.6 + Self Learning V2.8.6 |
| 10-11 | Inferred from Memory retrieval patterns |
| 12-13 | Decision Intelligence V2.9.1 + Evolution System V2.8.6 |
| 14-15 | V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Embedding dimension: 384 (lightweight) or 768 (Blueprint)? | §14 |
| 2 | Pattern extraction: rule-based clustering or ML-based? | §8 |
| 3 | Consolidation thresholds (N≥30, N≥100) — appropriate for A-share sample sizes? | §11 |
| 4 | Memory retrieval: FAISS (local vector) or Chroma (embedded DB)? | §14 |

---

*AQF-T Memory System Architecture V2.9.2 — ENGINEERING DRAFT*  
*Source: Simulation Memory V3.0.0 + Knowledge Evolution V2.8.6 + Self Learning V2.8.6 + Decision Memory V2.9.1*  
*No original design added. All content traceable to existing AQF-T architecture.*
