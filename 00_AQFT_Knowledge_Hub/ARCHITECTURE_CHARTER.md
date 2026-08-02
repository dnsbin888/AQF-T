# AQF-T Decision OS — Architecture Charter

Version: V1.0.0
Status: ✅ FROZEN
Date: 2026-08-03
Authority: GPT (Chief Architect) + 老板 (Project Owner) + CC (Engineering Audit)

---

## Vision

> **AQF-T is an evidence-driven decision operating system that separates capability, evidence, decision, learning, and governance through stable architectural contracts.**

```
M0 Capability  →  M1 Evidence  →  M2 Intelligence  →  M3 Decision  →  M4 Learning
                                                                              ↓
                                                                   M5 Adaptive Policy
                                                                              ↓
                                                                   M6 Architecture Governance
```

## Five Principles

### P1 — Contract Stability

> **Contracts are stable. Implementations are replaceable.**

Evidence Contract. Ontology Contract. Decision Contract. Learning Contract — frozen.
Producer. Model. Feature. Weight. Parameter. Fusion Strategy — all replaceable.
Contract Version IS the architecture version.

### P2 — Evidence Centrality

> **Evidence is the architectural center. Algorithms are evidence producers. Decisions are evidence interpretation.**

LGBM. XGBoost. Rules. LLM. Agent. — all are Producers. Not the Decision.
Decision Engine. Learning. Replay. Governance. — all operate on Evidence.
The system doesn't ask "which model is best?" — it asks "which Evidence is most trustworthy?"

### P3 — Producer Independence

> **Every Producer owns one responsibility and one ontology domain.**

One Producer answers one question. Never two.
Fusion never knows TrendML, MomentumML, LGBM, XGBoost.
Fusion only knows Trend Domain, Momentum Domain.
Producer can be replaced. Domain never changes.

### P4 — Deterministic Decision

> **The same evidence must always produce the same decision.**

Replay = 100%. Decision Equivalence = 100%.
Runtime Version. Decision Trace. Immutable Evidence.
This is the single most important Runtime Invariant of the Decision OS.

### P5 — Evolution Without Disruption

> **Architecture evolves through contracts, never through breaking production behavior.**

Zero-breaking Evolution.
Every evolution raises the abstraction level.
Never breaks production. Never rewrites. Only recomposes.

---

## Compliance Check

任何新模块/策略/能力接入前，必须回答：

| # | 问题 | 对应原则 |
|:--:|------|:--:|
| 1 | Contract 是否定义并冻结？ | P1 |
| 2 | 输出的是 Evidence 还是 Decision？ | P2 |
| 3 | 只回答一个问题吗？属于哪个 Domain？ | P3 |
| 4 | 相同 Evidence → 相同 Decision 100%？ | P4 |
| 5 | 是否零破坏现有生产行为？ | P5 |

**5 问全部通过 → 可以接入。任一不通过 → 拒绝。**

---

*AQF-T Architecture Charter V1.0 — FROZEN 2026-08-03*
*This Charter governs all future architecture decisions. Amendments require Architecture Review.*
