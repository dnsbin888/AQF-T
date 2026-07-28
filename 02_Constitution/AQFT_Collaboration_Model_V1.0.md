# AQF-T Collaboration Model — Multi-AI Architecture R&D Governance

Version: V1.0.0 | Status: ✅ FROZEN — Same Level as Meta Constitution
Date: 2026-07-28 | Priority: Project Governance

---

## 1. Core Principle

**Not two AIs discussing. One verifiable architecture R&D process.**

All participants submit to Meta Constitution (MC-001~013). No one is above the rules.

---

## 2. Collaboration Hierarchy

```
                 Meta Constitution (MC-001~013)
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
 ChatGPT (Chief Architect)         Claude (Chief Engineer)
  Architecture Design               Engineering Implementation
  Research & Theory                 Document Execution
  Technology Scouting               Git & Directory Management
  System Consistency                Consistency Checks
        │                                 │
        └──────────────┬──────────────────┘
                       ▼
              Independent Review
                       ▼
                 Final Architecture
```

---

## 3. Role Definitions

### ChatGPT — Chief Architect

| Responsibility | Description |
|---------------|-------------|
| Architecture Design | 是否符合 AQF-T 蓝图、是否破坏 World Model、是否破坏 S→B→R 链 |
| Research Review | 来源？为什么？是否有论文？是否有行业实践？替代方案？ |
| Technology Scout | 持续跟踪前沿（ICML/NeurIPS/DeepMind/Jane Street/Citadel等）→ MC-001审核 → 决定是否纳入 |
| Evidence Assessment | 给每个设计分配 Evidence Level (A+~D) |
| Freeze Authority | 最终批准架构冻结 |

### Claude — Chief Engineer

| Responsibility | Description |
|---------------|-------------|
| Document Engineering | 写 Architecture.md、接口定义、Event Schema、模块文档 |
| Directory & Git | 目录结构、版本管理、Tag、Commit |
| Consistency Check | 接口一致性、命名冲突、依赖检查、Schema 漂移 |
| Self Review | 提交前自检：遗漏？冲突？命名问题？ |
| Implementation Review | 检查设计是否可工程化落地 |

---

## 4. Boundaries (CRITICAL)

```
ChatGPT SHALL NOT directly modify Claude's implementation documents.
Claude SHALL NOT modify ChatGPT's architecture design.

ALL changes MUST go through: Proposal → Architect Review → Merge
```

---

## 5. AQF-T Review Workflow

```
Architecture Draft (ChatGPT)
        │
        ▼
Engineering Implementation (Claude)
        │
        ▼
Self Review (Claude)
        │
        ▼
Architect Review (ChatGPT)
        │
        ▼
Revision / Approve
        │
        ▼
Final Freeze
        │
        ▼
Git Commit + Tag
```

**Only Architect Review can change architecture. No AI self-approves.**

---

## 6. Module Lifecycle

Every module carries:

```
Version: V1.1
Evidence Level: A / B / C
Claude Review Score: 92
Architect Review Score: 96
Known Issues: 3
Upgrade Candidates: 2
Next Review: P2.5
Status: FROZEN / ACTIVE / DEPRECATED
```

---

## 7. MC-014 Candidate: Independent Cross-Review

**设计者不能单独批准自己的设计。**

- 任何重大架构变更必须经过独立评审
- 评审意见必须包含：保留/修改/拒绝 + 基于证据的理由
- 最终冻结版本必须保留设计历史和评审记录

---

## 8. Final Goal

AQF-T is not a project where AIs "write documents together." It is a **verifiable, traceable, auditable engineering governance system** where:

- AI participates in R&D
- The Meta Constitution governs evolution
- Evidence, not authority, decides design
- Any decision can be traced, explained, verified, and rolled back

---

*AQF-T Collaboration Model V1.0 — FROZEN. Project Governance.*
