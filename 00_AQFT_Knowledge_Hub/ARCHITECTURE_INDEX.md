# AQF-T Architecture Index

Version: V2.0.0
Date: 2026-08-03
Status: Architecture Baseline Established — M0→M4 COMPLETE
Purpose: 任何人 5 分钟内理解整个 Decision OS 的演进路线

## Architecture Principle #1

> **Contracts are stable. Implementations are replaceable.**
>
> Evidence Contract / Ontology / Decision Contract / Learning Contract — frozen.
> Producer / Model / Feature / Weight / Parameter / Fusion Strategy — all replaceable.
>
> 此原则来自 Meta Constitution MC-020 (Contract Before Code) + MC-022 (Truth Over Ownership)。
> 应出现在所有 ADR 首页。

---

## Architecture Layers

```
M6  Architecture Governance (FUTURE)

M5  Adaptive Decision Gov   (FUTURE)
    └── Learning Proposal → Governance → Activation

M4  Decision Learning       ✅ FROZEN
    └── Replay / Outcome Eval / Pattern Memory / Knowledge Update

M3  Decision Engine         ✅ FROZEN
    └── 8-stage Lifecycle: Normalize→Validate→Filter→Fusion→Policy Gate→Risk Override→Decision→Trace

M2  Evidence Intelligence   ✅ FROZEN
    └── Ontology / Responsibility / Specialization / Fusion Policy

M1  Evidence Foundation     ✅ FROZEN
    └── Registry / Builder / Identity / Evaluation / Health / Attribution

M0  Capability Platform     ✅ STABLE
    └── 潜龙: QMT / ML / TDX / Web / Data / Execution
```

## Core Principle

> **Contracts Freeze, Implementations Evolve.**
>
> M1→M3 冻结的是契约（Evidence怎么说话、Ontology怎么组织、Decision怎么生成），
> 不是算法、模型、参数。LGBM换成Transformer — 只要它仍然只回答"趋势是否成立"。

## Milestone Index

| Milestone | 名称 | 状态 | DEC | 关键资产 |
|:--:|------|:--:|------|----------|
| M0 | Capability Platform | STABLE | — | 潜龙 363模块 |
| M1 | Evidence Foundation | FROZEN | DEC-029, DEC-031 | EFL v1.0, 6模块, 6 Gate |
| M2 | Evidence Intelligence | FROZEN | DEC-032A/B/C/D | Ontology 12 Domain, 8 Producer, AR-1/2/3 |
| M3 | Decision Engine | FROZEN | DEC-033 | 8-stage Lifecycle, Decision Object, Fusion纯函数 |
| M4 | Decision Learning | DESIGN | DEC-034 | Replay / Outcome Eval / Pattern Memory / Knowledge |
| M5 | Adaptive Decision | FUTURE | — | Autonomous Evolution / Self-Governance |

## Key Documents

| 文档 | 内容 |
|------|------|
| [DEC-029](DEC029_EVIDENCE_FIRST_ARCHITECTURE.md) | Evidence First 架构哲学 |
| [DEC-031](DEC031_PHASE1_FOUNDATION_FREEZE.md) | Phase 1 Foundation 冻结 |
| [DEC-032](DEC032_EVIDENCE_INTELLIGENCE_ARCHITECTURE.md) | Evidence Intelligence Master |
| [DEC-032A](DEC032A_EVIDENCE_ONTOLOGY.md) | Evidence Ontology — 12 Domain |
| [DEC-032B](DEC032B_PRODUCER_RESPONSIBILITY.md) | Producer Responsibility — 每个Producer只回答一个问题 |
| [DEC-032C](DEC032C_EVIDENCE_SPECIALIZATION.md) | Evidence Specialization — Feature Ownership |
| [DEC-032D](DEC032D_FUSION_POLICY.md) | Fusion Policy |
| [DEC-033](DEC033_DECISION_ENGINE_ARCHITECTURE.md) | Decision Engine Architecture |
| [ARCHITECTURE_MILESTONES.md](ARCHITECTURE_MILESTONES.md) | Milestone 路线 + Architecture Debt |
| [ARCHITECTURE_INDEX.md](ARCHITECTURE_INDEX.md) | 本文件 — 5分钟导航 |

## Git Tags

| Tag | Milestone |
|-----|-----------|
| `Phase1-Foundation-v1.0` | M1 |
| `EFL-v1.0` | M1 Evidence Foundation Layer |
| `M2-Evidence-Intelligence-v1.0` | M2 |
| `M3-Decision-Engine-v1.0` | M3 |
| `M4-Decision-Learning-v1.0` | M4 |

## Architecture Baseline Declaration

```
M0→M4 COMPLETE. Architecture Baseline Established.

Contracts Frozen:
  Evidence Contract (M1)
  Ontology Contract (M2)
  Decision Contract (M3)
  Learning Contract (M4)

Implementations Replaceable:
  Producer / Model / Feature / Weight / Parameter / Fusion Strategy / Replay Engine / Learning Algorithm
```

## Architecture Stability Index (ASI)

| 维度 | 当前状态 |
|------|:--:|
| Contract Stability | 100% — 4 Contracts Frozen |
| Replay Stability | 100% — AR-3.1 passed |
| Compatibility | 100% — AR-1/AR-2 no conflicts |
| Determinism | 100% — Decision Equivalence verified |
| Governance Compliance | 100% — Meta Constitution aligned |

**ASI: 100%** — Architecture Baseline established.

## Constitution Cross-Reference

| DEC | Aligned MC |
|-----|-----------|
| DEC-029 Evidence First | MC-001 Design Evidence First |
| DEC-032 Evidence Intelligence | MC-023 Minimal Cognitive Core, MC-019 Canonical Interface |
| DEC-033 Decision Engine | C-004 Strategy≠Decision, C-007 Execution≠Decision |
| DEC-034 Decision Learning | MC-022 Truth Over Ownership, MC-016 Reality Over Architecture |
| Architecture Principle #1 | MC-020 Contract Before Code + MC-022 |

---

*AQF-T Architecture Index V2.0 — Architecture Baseline Established 2026-08-03*
