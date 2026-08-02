# AQF-T Architecture Milestones

Version: V1.0.0
Date: 2026-08-03

---

## Milestone 路线

```
M0: Trading System
    └── 潜龙独立运行。QMT/ML/Flask/DingTalk
    ✅ Complete (2026-07)

M1: Evidence Foundation
    └── Registry + Builder + Identity + Evaluation + Health + Attribution
    ✅ FROZEN (2026-08-02) — EFL v1.0

M2: Evidence Intelligence
    └── Ontology + Responsibility + Specialization + Fusion
    ✅ FROZEN (2026-08-03) — Architecture Contracts Only. AR-1/2/3 ALL PASSED.

M3: Decision Engine
    └── DEC-033: Decision Engine Architecture (先设计)
    └── DEC-034: Decision Replay & Learning Architecture
    └── Evidence Fusion Engine (EFE) 实现
    ⏳ Not Started — Do NOT implement before DEC-033 reviewed.

M4: Decision Learning
    └── Replay + Outcome Eval + Pattern Memory + Knowledge Update
    ✅ FROZEN (2026-08-03) — Learning Independence + Human Governance.

M5: Adaptive Decision Governance
    └── Learning Proposal → Governance → Activation
    └── Human-in-the-loop for automated changes
    ⏳ Not Started

M6: Architecture Governance
    └── Multi-App Platform Governance
    ⏳ Not Started
```

## Architecture Debt Log

| ID | 债务 | 影响 | 计划清偿 |
|----|------|------|----------|
| AD-001 | Trend Producer 仍使用 LightGBM | Producer 身份与实现绑定 | M3: 实现可替换 |
| AD-002 | Momentum Feature Ownership 未拆分 | 特征与 Trend 重叠 | M2 Step 3: 分步重训 |
| AD-003 | Fusion 使用静态权重 | 无法自适应 | M3: 接入 Evaluation 动态权重 |
| AD-004 | 潜龙 ML 训练与 AQF-T Evidence 未分离 | 训练数据不共享 | M3: Contract 定义 |
| AD-005 | 历史交易缺失 model_version | 无法回溯 Evidence | 从现在开始记录 |
| AD-006 | 历史交易缺失 regime | 无法评估 Decision 质量 | 从现在开始记录 |
| AD-007 | 历史交易缺失 confidence | DEC-034 缺少校准数据 | 从现在开始记录 |
| AD-008 | Producer 版本未与交易关联 | 历史回放不可复现 | M3: Decision Trace |
| AD-009 | ML Signal Track 仅 10 天 | Learning 样本不足 | 30 天后自然解决 |

---

*AQF-T Architecture Milestones V1.0*
