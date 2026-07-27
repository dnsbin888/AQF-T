# AQF-T Decision Memory & Feedback Interface Design

Version: V1.0.0
Status: FROZEN — V2.9.1 Decision Intelligence Freeze
Phase: V2.9 Intelligence Era — Decision Intelligence
Module: Decision_Intelligence
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Decision_Memory_Feedback_Interface_Design_V1.0.md |
| Module | Decision Intelligence — Memory & Feedback |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_Decision_Intelligence_Architecture_V2.9.1 |
| Upstream | Action Selection + Evolution System V2.8.6 + Simulation Memory V3.0.0 |
| Downstream | Evolution System — Self Learning + Knowledge Evolution |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Decision Architecture V3.0.0 + Evolution System V2.8.6 + Simulation Memory V3.0.0 |

---

## 1. Purpose

### 1.1 What Decision Memory Does

Decision Memory 是 Decision Intelligence 的 **学习记忆系统**。

它不是简单的日志文件。它回答：**"我们做了什么决定？为什么？结果如何？下次如何做得更好？"**

| Component | Question |
|-----------|----------|
| Decision Record | What did we decide? |
| Reason Trace | Why did we decide that? |
| Outcome Evaluation | Was it right? |
| Feedback Processing | How to improve? |

### 1.2 Why Memory Matters

```
Without Memory:  Each decision is isolated. Same mistakes repeated.
With Memory:     Past decisions inform future ones. System improves over time.
```

[Source: Constitution V2.8.6 — Principle 8: Historical Respect + Principle 10: Continuous Evolution]

### 1.3 What Decision Memory Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 简单交易日志 | 完整决策上下文记录 |
| 自动修改模型参数 | 反馈接口（参数修改由 Evolution System 执行） |
| 替代 Evolution System | Evolution System 的数据源 |
| 只记录结果 | 记录决策全链（原因→行动→结果→教训） |

---

## 2. Scope

### 2.1 In Scope

- Decision record with full context capture
- Reasoning trace storage
- Outcome evaluation against actual market
- Feedback processing pipeline
- Learning interface to Evolution System
- Human review interface for significant decisions
- Knowledge extraction from decision history

### 2.2 Out of Scope

- ❌ Automatic model parameter modification
- ❌ Automatic Risk rule changes
- ❌ Strategy algorithm modification
- ❌ Replacing Evolution System (Evolution System decides HOW to learn; Memory provides WHAT to learn from)

---

## 3. Architecture Position

### 3.1 In Decision Intelligence

```
Action Selection → Decision Output
        │
        ├──→ Strategy Runtime (action execution)
        │
        └──→ Decision Memory (record)
                    │
                    ▼
              Outcome Tracking
                    │
                    ▼
              Evaluation Engine
                    │
                    ▼
              Feedback Processor
                    │
                    ▼
              Evolution System (learning)
```

### 3.2 Feedback Loop

```
Decision(t) → Action(t) → Outcome(t+n) → Evaluation → Feedback → Improved Decision(t+m)
```

Memory is the **bridge** between past decisions and future improvement.

---

## 4. Decision Memory Philosophy

### 4.1 Core Principles

**Principle 1: Record Everything That Mattered**

不是记录所有数据。而是记录影响决策的关键因素：Market Context、Evidence、Alternatives、Confidence、Risk。

**Principle 2: Evaluate, Don't Just Store**

存储是手段，评估是目的。每个决策在结果出来后必须被评估。

**Principle 3: Learn From Both Success and Failure**

失败案例是系统最重要的资产。成功的决策也需要验证：是能力还是运气？

**Principle 4: Human-Reviewable**

重大决策的记录必须人类可理解、可审查。

---

## 5. Decision Record Model

### 5.1 Complete Decision Record

```json
{
  "record_id": "REC_20260727_093500001",
  "decision_id": "DEC_20260727_093500",

  "timestamp": "2026-07-27T09:35:00",

  "context": {
    "market_regime": "Expansion",
    "emotion_phase": "Warming",
    "emotion_score": 65,
    "regime_confidence": 0.82,
    "scenario": {
      "top_scenario": "Expansion continues",
      "probability": 0.45
    }
  },

  "evidence": {
    "prediction": { "direction": "UP", "strength": 0.72, "confidence": 0.80 },
    "sentiment": { "phase": "Warming", "score": 65, "confidence": 0.75 },
    "risk": { "score": 28, "level": "Low" },
    "fusion_confidence": 0.78,
    "alignment_score": 0.82
  },

  "decision": {
    "chosen_action": "Increase",
    "confidence": 0.78,
    "alternatives_considered": ["Hold (utility 0.55)", "Enter (utility 0.48)"],
    "reasoning_trace": [
      "Expansion regime supports aggressive posture",
      "Sentiment warming confirms momentum",
      "Risk low — budget available",
      "3/4 agents vote Increase"
    ],
    "constraints_applied": [
      "Regime: Increase allowed",
      "Risk: Low — no restriction",
      "Confidence: 0.78 — full execution"
    ]
  },

  "risk_state": {
    "pre_decision_risk": 28,
    "post_decision_risk": 35,
    "risk_limit_used": "50%"
  },

  "outcome": {
    "status": "pending",
    "actual_result": null,
    "evaluated_at": null,
    "was_correct": null,
    "lessons": []
  },

  "human_review": {
    "required": false,
    "reviewed_by": null,
    "override": null
  }
}
```

### 5.2 Record Lifecycle

```
[Created] → Decision made, record written
    │
[Pending] → Waiting for outcome (t+n days)
    │
[Evaluated] → Outcome observed, evaluation complete
    │
[Learned] → Lessons extracted, feedback sent to Evolution System
    │
[Archived] → Stored for historical reference
```

---

## 6. Reason Trace

### 6.1 Trace Structure

每个 Decision Record 携带完整的推理链：

```
Level 1: Context
  "Market was in Expansion regime, Warming sentiment phase"

Level 2: Evidence
  "Prediction: UP 72% | Sentiment: Warming 65 | Risk: Low 28"

Level 3: Alternatives
  "Increase (U=0.72) vs Hold (U=0.55) vs Enter (U=0.48)"

Level 4: Decision
  "Selected Increase — best utility with acceptable risk"

Level 5: Conditions
  "Valid unless: Sentiment shifts to Recession OR Risk exceeds 60"
```

### 6.2 Human-Readable Format

```json
{
  "reasoning_trace": [
    "当前处于 Expansion 扩张期，情绪回暖阶段 → 支持进攻性姿态",
    "预测引擎方向 UP (72%)，情绪引擎回暖 (65分)，风险低 (28分) → 证据一致",
    "对比方案：Hold (过于保守，错失机会)，Reduce (完全不符合当前阶段)",
    "选择 Increase：风险预算充足，置信度 0.78 支持执行",
    "关注条件：若情绪转为退潮或风险升至 60+ → 立即转为 Reduce"
  ]
}
```

---

## 7. Outcome Evaluation

### 7.1 Evaluation Timing

| Decision Type | Evaluation Window | Evaluation Criteria |
|--------------|:-----------------:|---------------------|
| Enter | t+5 to t+20 days | Direction correct? Timing appropriate? |
| Increase | t+5 to t+20 days | Was adding exposure beneficial? |
| Hold | t+1 to t+5 days | Was holding better than exiting? |
| Reduce | t+1 to t+10 days | Did risk materialize? Was reduction timely? |
| Exit | t+1 to t+20 days | Was exit premature or late? |

### 7.2 Evaluation Dimensions

```json
{
  "evaluation": {
    "direction_correct": true,
    "direction_confidence": 0.85,

    "timing_appropriate": true,
    "timing_score": 0.72,

    "magnitude_appropriate": false,
    "magnitude_detail": "Position could have been 20% larger given outcome",

    "risk_assessment_accurate": true,
    "risk_detail": "Risk remained Low through holding period",

    "alternative_would_have_been_better": "Hold",
    "alternative_detail": "Hold would have yielded +2% less but with 30% less risk",

    "overall_grade": "B+",
    "key_lesson": "Regime identification correct. Position sizing slightly conservative."
  }
}
```

### 7.3 Evaluation Grades

| Grade | Meaning | Action |
|:-----:|---------|--------|
| A | Decision optimal | Reinforce pattern |
| B | Good, minor improvements possible | Fine-tune |
| C | Acceptable but suboptimal | Review constraints |
| D | Poor decision | Analyze failure |
| F | Decision harmful | Urgent review, pattern suppression |

---

## 8. Feedback Processing

### 8.1 Feedback Pipeline

```
[1] Outcome observed (market data at t+n)
        │
[2] Compare: Decision vs Actual
        │
[3] Evaluate: Score each dimension
        │
[4] Classify: What type of error (if any)?
        │
[5] Extract: What lesson?
        │
[6] Route: Which system needs this feedback?
        │
[7] Deliver: Feedback → Evolution System / Human
```

### 8.2 Error Classification

| Error Type | Example | Routes To |
|-----------|---------|-----------|
| Regime misclassification | Thought Expansion, was Distribution | World Model Regime |
| Evidence overweight | Prediction dominated, ignored Risk warning | Fusion Engine weights |
| Confidence miscalibration | High confidence, wrong outcome | Confidence model |
| Risk underestimation | Risk scored Low, drawdown was High | Risk Intelligence |
| Timing error | Direction correct, entered too early | Strategy Runtime |

### 8.3 Feedback Routing

```
Feedback → Target System:

  Regime error → World Model Regime Engine
  Fusion error → Fusion Engine weight calibration
  Confidence error → Confidence model
  Risk error → Risk Intelligence
  Strategy error → Strategy Runtime
  Pattern discovery → Knowledge Evolution
```

---

## 9. Learning Interface

### 9.1 Evolution System Integration

[Source: Evolution System V2.8.6 — Self Learning Engine + Knowledge Evolution]

```
Decision Memory → Evaluated Records → Evolution System
                                         │
                              ┌──────────┼──────────┐
                              ▼          ▼          ▼
                        Self Learning  Knowledge   Auto
                        Engine        Evolution   Optimization
```

### 9.2 Learning Query Interface

```python
# Evolution System queries Decision Memory
GET /decision/memory/query
  ?regime=Expansion
  &min_grade=B
  &limit=50
  → Returns top 50 successful decisions in Expansion regime

GET /decision/memory/errors
  ?error_type=regime_misclassification
  &from=2026-01-01
  → Returns all regime misclassification errors for analysis

GET /decision/memory/patterns
  ?metric=confidence_calibration
  &regime=all
  → Returns confidence calibration patterns across regimes
```

---

## 10. Evolution System Interface

### 10.1 What Memory Provides to Evolution

| Evolution Component | Memory Input |
|--------------------|-------------|
| Self Learning Engine | Decision-outcome pairs for supervised learning |
| Knowledge Evolution | Successful decision patterns → knowledge graph |
| Auto Optimization | Parameter performance across decisions |
| Monitoring Intelligence | Decision quality trends, error rate tracking |

### 10.2 Feedback Contract

```python
# Memory → Evolution System
def export_feedback_batch(
    from_date: datetime,
    to_date: datetime,
    min_samples: int = 100
) -> FeedbackBatch:
    """
    Export evaluated decisions as training feedback.
    Returns structured {context, decision, outcome, grade}.
    """
```

---

## 11. Human Review Interface

### 11.1 Review Triggers

| Trigger | Action |
|---------|--------|
| Decision grade D or F | Mandatory human review |
| Full Exit decision | Recommended human review |
| 3 consecutive C-grade decisions | Alert human |
| New regime pattern detected | Notify for human verification |
| Confidence < 0.50 but action taken | Flag for review |

### 11.2 Review Dashboard Data

```python
GET /decision/memory/review-queue
  Response:
  {
    "pending_reviews": [
      {
        "record_id": "REC_...",
        "grade": "D",
        "decision": "Increase in Distribution regime",
        "reason": "Regime misclassification — action inappropriate",
        "suggested_correction": "Review regime detection threshold"
      }
    ],
    "statistics": {
      "total_decisions": 1523,
      "grade_distribution": { "A": 0.25, "B": 0.40, "C": 0.25, "D": 0.08, "F": 0.02 },
      "trend": "improving (last 100: A/B = 72%)"
    }
  }
```

---

## 12. Knowledge Update

### 12.1 Knowledge Extraction Pipeline

```
Evaluated Records (graded A/B)
        │
        ▼
Pattern Extraction: What do good decisions have in common?
        │
        ▼
Rule Derivation: If (context X) then (action Y tends to succeed)
        │
        ▼
Knowledge Storage: Write to Knowledge Evolution graph
        │
        ▼
Future Decision Enhancement: Retrieved when similar context arises
```

### 12.2 Knowledge Types

| Type | Example |
|------|---------|
| Regime-Action Rule | "In Expansion+Warming, Increase succeeds 72% of time" |
| Risk Boundary | "Enter when Risk<40 has 85% success rate" |
| Timing Pattern | "Enter within 3 days of Warming onset → 78% success" |
| Failure Pattern | "Increase during Distribution → D/F grade 65% of time" |

**[NEEDS ARCHITECT REVIEW]** — Knowledge extraction automation: rule-based pattern mining or ML-based? Deferred to V2.9.2 Memory System.

---

## 13. Engineering Requirement

### 13.1 Constraints

| Constraint | Value |
|------------|-------|
| Record write latency | < 10ms (async) |
| Evaluation batch processing | Daily (end-of-day) |
| Storage per record | < 5KB |
| Retention | All records, indefinitely |
| Query performance | < 100ms for last 1000 records |

### 13.2 Code Structure

```
decision_intelligence/memory/
├── decision_recorder.py        # Write decision records
├── reason_tracer.py            # Generate reasoning trace
├── outcome_evaluator.py        # Evaluate decision vs actual
├── feedback_processor.py       # Classify errors, route feedback
├── learning_interface.py       # Evolution System queries
├── human_review_queue.py       # Review triggers + dashboard
├── knowledge_extractor.py      # Pattern mining from history
├── memory_store.py             # Persistence layer
└── __init__.py
```

### 13.3 Storage Schema

```sql
CREATE TABLE decision_records (
    record_id UUID PRIMARY KEY,
    decision_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    regime VARCHAR(32),
    emotion_phase VARCHAR(32),
    chosen_action VARCHAR(32),
    confidence FLOAT,
    risk_score INTEGER,
    grade CHAR(2),
    outcome_status VARCHAR(16),
    context_json JSONB,
    evidence_json JSONB,
    reasoning_trace_json JSONB,
    evaluation_json JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    evaluated_at TIMESTAMP,
    archived_at TIMESTAMP
);

CREATE INDEX idx_regime_grade ON decision_records(regime, grade);
CREATE INDEX idx_timestamp ON decision_records(timestamp);
```

---

## 14. Testing Requirement

### 14.1 Unit Tests

- Record creation: all fields populated correctly
- Outcome evaluation: known outcome → correct grade
- Feedback routing: regime error → routes to Regime Engine
- Age-based evaluation window: Enter evaluated at t+5 to t+20

### 14.2 Integration Tests

- Full loop: Decision → Record → Outcome → Evaluation → Feedback
- Evolution System query: returns correct records
- Human review queue: D/F decisions flagged

---

## 15. Freeze Criteria

1. **Architecture Review Passed** — Memory correctly positioned as decision→evolution bridge
2. **Decision Record complete** — Context + Evidence + Decision + Outcome + Evaluation
3. **Reasoning trace mandatory** — Every decision explainable post-hoc
4. **Outcome evaluation defined** — Timing, dimensions, grading rubric
5. **Feedback routing specified** — Error type → target system mapping
6. **Evolution System interface defined** — Query + feedback contract
7. **Human review triggers** — D/F grades, new patterns, high-stakes decisions
8. **No automatic model modification** — Memory provides data, Evolution decides
9. **Knowledge extraction pipeline** — Pattern → Rule → Storage → Retrieval

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-3 | Decision Intelligence Architecture V2.9.1 |
| 4 | Constitution V2.8.6 — Principles 8, 9, 10 |
| 5-6 | Decision Architecture V3.0.0 Ch.5 (Decision Audit) |
| 7-8 | Inferred from Evolution System + World Model feedback loops |
| 9-10 | Evolution System V2.8.6 — Self Learning + Knowledge Evolution |
| 11 | Constitution Ch.10 — Human-AI Collaboration |
| 12 | Simulation Memory V3.0.0 + Knowledge Evolution |
| 13-15 | V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Knowledge extraction automation: rule-based or ML? | §12 |
| 2 | Evaluation windows (t+5 to t+20) — appropriate for A-share timeframes? | §7 |
| 3 | Auto-archival policy: when to move records from active to archive? | §5 |

---

*AQF-T Decision Memory & Feedback Interface Design V1.0 — ENGINEERING DRAFT*  
*Source: Decision Architecture V3.0.0 + Evolution System V2.8.6 + Simulation Memory V3.0.0*  
*No original design added. All content traceable to existing AQF-T architecture.*
