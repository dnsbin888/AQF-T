# AQF-T Meta Constitution — Knowledge Governance Framework

Version: V1.1.0 | Status: ✅ FROZEN — Highest-Level Constitution
Date: 2026-07-28 | Priority: Above all C-001~C-012

---

## 定位

本文件不仅是架构约束，更是 **AQF-T Knowledge Governance Framework（知识治理框架）** — 项目中所有 AI、人类架构师和未来自动化工具共同遵守的知识治理规范。它是 AQF-T 最长期、最稳定、最难复制的基础设施。

---

## MC-001: Design Evidence First（设计证据优先）

### 最高原则

AQF-T 的任何设计、模块、模型、算法、接口、规则，都必须有明确的知识来源（Evidence）。

**禁止：因为 AI 认为应该这样设计。**

**必须回答：为什么这样设计？依据是什么？**

---

## MC-002: Evidence Level（证据等级）

Evidence Level 描述的是**证据成熟度**，不是**设计价值**。

| Level | Name | Criteria | Examples |
|:-----:|------|----------|----------|
| **A+** | Industry Proven | 已成为行业事实。论文+工程+长期实践验证。 | Bayesian Updating, Counterfactual Reasoning, Risk Budget, Kelly, Portfolio Theory |
| **A** | Academic Proven | 大量论文支持，多个团队验证。 | Transformer, RL, MCTS, Bayesian Network, HMM, GNN |
| **B** | Industry Best Practice | 无严格论文，但行业大量采用。 | Event-driven architecture, DDD, Risk Pipeline |
| **C** | Empirical | 经验模型。有市场验证但非理论。 | 游资经验, 龙头战法, 涨停板经验, 盘口规律 |
| **D** | AQF-T Original | 原创。尚未形成行业共识。**允许创新，要求持续验证。** 不代表价值最低——可能未来升级为 A+。 | Belief Engine, Pattern→Knowledge, S(t)→B(t)→R(t), Decision Quality Matrix |

---

## MC-003: Five Questions for Every Design（设计五问）

任何新增设计必须回答。建议所有 Design Doc 固定模板：

```
Problem → Design → Evidence → Validation → Boundary
```

1. **为什么？** — 解决什么问题？
2. **来源？** — 来自哪里？
3. **为什么相信？** — 论文？行业？经验？原创？
4. **如何验证？** — Backtest / Paper / Real Trading / Simulation
5. **什么条件下失效？** — 例如涨停板模型：港股/美股失效

---

## MC-004: Knowledge Source Priority（知识来源优先级）

| Priority | Source | Usage |
|:--------:|--------|-------|
| P0 | 数学、公理、统计学、控制论 | 默认可信 |
| P1 | 顶级同行评审论文（NeurIPS、ICML、ICLR、Nature、Science等） | 优先采用 |
| P2 | 世界领先机构工程实践（DeepMind、OpenAI、Jane Street、Bridgewater等） | 经架构适配后采用 |
| P3 | A股长期统计规律与可验证市场经验 | 仅限A股模块，持续验证 |
| P4 | AQF-T原创设计 | 必须注明原创、验证计划和适用边界 |
| **P5** | **AQF-T自身长期验证（真实交易结果）** | **对AQF-T自身决策最有约束力的证据** |
| ❌ | **禁止：无来源、无法解释、仅凭AI猜测** | **不允许进入正式架构** |

**P5 说明：** 当真实交易验证与文献、行业经验冲突时，以可重复验证的真实交易结果为准。例如：论文说突破成功率72%，AQF-T真实1000次=58% → 相信58%。因为自己的市场、自己的交易、自己的数据。

---

## MC-005: No Hallucinated Design（禁止幻觉设计）

任何模型、算法、公式、接口，必须能够说明来源。否则不能进入正式设计。**任何 AI（Claude/ChatGPT/Gemini/DeepSeek）都必须说明依据。否则 Reject。**

---

## MC-006: Architect's Responsibility（架构师职责）

Architect 不再只是"设计系统"，而是"维护 AQF-T 的知识体系"。每个模块需经过三层审核：

1. **技术正确性** — 算法、模型、工程设计是否合理
2. **证据充分性** — 是否有明确来源、适用范围和验证依据
3. **AQF-T 一致性** — 是否符合 Constitution，是否与现有认知链一致

---

## MC-007: Evidence Library（证据库）

```
01_Research/
├── Papers/        # 学术论文
├── Industry/      # 行业报告/白皮书
├── Books/         # 书籍
├── Standards/     # 工程标准 (FIX, ONNX, Arrow, DDD, OpenTelemetry等)
├── Datasets/      # 数据集引用
├── Benchmarks/    # 基准测试
├── Empirical/     # 经验总结
├── Original/      # AQF-T原创
└── Validation/    # 验证结果（真实交易统计）
```

每个模块引用 Research ID (R-XXX)。

---

## MC-008: Evidence Is Versioned（证据可演化）

证据不是永久正确的。2024年正确的论文，2029年可能已经过时。

| Status | Meaning |
|--------|--------|
| Active | 当前有效 |
| Deprecated | 已被更优证据替代 |
| Superseded | 被新版本覆盖 |
| Rejected | 经AQF-T自身验证后被否定 |

Evidence Library 应允许升级、降级、替换。

---

## MC-009: Multi-source Confirmation（多源确认）

重要设计至少需要两个来源。例如 Opponent Model 应有：论文(Jane Street) + A股经验。A+ 级证据应有 Academic + Industry 共同支持。

---

## MC-010: Validation Overrides Authority（验证高于权威）

**当真实交易验证与文献、行业经验冲突时，以可重复验证的真实交易结果为准。**

这是 AQF-T 真正自主智能的基础——不盲从论文，不盲从权威，以自身数据为最终裁判。

---

## Constitution Hierarchy

```
AQF-T Meta Constitution (MC-001 ~ MC-010)  ← 最高知识治理框架
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

*AQF-T Meta Constitution V1.1 — Knowledge Governance Framework. FROZEN.*
