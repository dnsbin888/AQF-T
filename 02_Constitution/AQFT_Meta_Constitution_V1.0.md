# AQF-T Meta Constitution — Design Evidence First

Version: V1.0.0 | Status: ✅ FROZEN — Highest-Level Constitution
Date: 2026-07-28 | Priority: Above all C-001~C-012

---

## MC-001: Design Evidence First（设计证据优先）

### 最高原则

AQF-T 的任何设计、模块、模型、算法、接口、规则，都必须有明确的知识来源（Evidence）。

**禁止：因为 AI 认为应该这样设计。**

**必须回答：为什么这样设计？依据是什么？**

---

## MC-002: Evidence Level（证据等级）

| Level | Name | Criteria | Examples |
|:-----:|------|----------|----------|
| **A+** | Industry Proven | 已成为行业事实。论文+工程+长期实践验证。 | Belief State, Bayesian Updating, Counterfactual Reasoning, World Model, Risk Budget, Kelly, Portfolio Theory |
| **A** | Academic Proven | 大量论文支持，多个团队验证。 | Transformer, RL, MCTS, Bayesian Network, Knowledge Graph, HMM, Particle Filter, GNN |
| **B** | Industry Best Practice | 无严格论文，但行业大量采用。 | Event-driven architecture, CQRS, DDD, Risk Pipeline |
| **C** | Empirical | 经验模型。有市场验证但非理论。 | 游资经验, 龙头战法, 涨停板经验, 盘口规律 |
| **D** | AQF-T Original | 原创。无公开成熟方案。**必须说明：为什么设计、解决什么问题、未来如何验证。** | Belief Engine, Pattern→Knowledge, S(t)→B(t)→R(t), Memory Constitution, Decision Quality Matrix |

---

## MC-003: Five Questions for Every Design

任何新增设计必须回答：

1. **为什么？** — 解决什么问题？
2. **来源？** — 来自哪里？
3. **为什么相信？** — 论文？行业？经验？原创？
4. **如何验证？** — Backtest / Paper / Real Trading / Simulation
5. **什么条件下失效？** — 例如涨停板模型：港股/美股失效

---

## MC-004: Knowledge Source Priority

| Priority | Source | Usage |
|:--------:|--------|-------|
| P0 | 数学、公理、统计学、控制论 | 默认可信 |
| P1 | 顶级同行评审论文（NeurIPS、ICML、ICLR、Nature、Science等） | 优先采用 |
| P2 | 世界领先机构工程实践（DeepMind、OpenAI、Jane Street、Bridgewater等） | 经架构适配后采用 |
| P3 | A股长期统计规律与可验证市场经验 | 仅限A股模块，持续验证 |
| P4 | AQF-T原创设计 | 必须注明原创、验证计划和适用边界 |
| ❌ | **禁止：无来源、无法解释、仅凭AI猜测** | **不允许进入正式架构** |

---

## MC-005: No Hallucinated Design

任何模型、算法、公式、接口，必须能够说明来源。否则不能进入正式设计。

---

## MC-006: Architect's Responsibility

Architect 不再只是"设计系统"，而是"维护 AQF-T 的知识体系"。每个模块需经过三层审核：

1. **技术正确性** — 算法、模型、工程设计是否合理
2. **证据充分性** — 是否有明确来源、适用范围和验证依据
3. **AQF-T 一致性** — 是否符合 Constitution，是否与现有认知链一致

---

## MC-007: Evidence Library

```
01_Research/
├── Papers/        # 学术论文
├── Industry/      # 行业报告
├── Books/         # 书籍
├── Empirical/     # 经验总结
├── Original/      # AQF-T原创
└── Validation/    # 验证结果
```

每个模块引用 Research ID (R-XXX)。

---

## Constitution Hierarchy

```
AQF-T Meta Constitution (MC-001 ~ MC-007)  ← 最高原则
│
├── C-001: Intelligence Ownership
├── C-002: Immutable Core
├── C-003: QMT Boundary
├── C-004: Strategy Runtime Boundary
├── C-005: Portfolio Authority Boundary
├── C-006: Position Authority Boundary
├── C-007: Order Execution Boundary
├── C-008: QMT Adapter Boundary
├── C-009: Decision Learning Boundary (candidate)
├── C-010: Market Context Boundary
├── C-011: Limit-Up Intelligence Boundary
├── C-012: Participant Interpretation Boundary (candidate)
```

---

*AQF-T Meta Constitution V1.0 — FROZEN. Highest-Level. Above all C-001~C-012.*
