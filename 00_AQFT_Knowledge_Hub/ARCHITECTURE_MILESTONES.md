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

M4: Learning System
    └── Weight Learning + Adaptive Fusion + Experience Memory
    ⏳ Not Started
```

## Architecture Debt Log

| ID | 债务 | 影响 | 计划清偿 |
|----|------|------|----------|
| AD-001 | Trend Producer 仍使用 LightGBM | Producer 身份与实现绑定 | M3: 实现可替换 |
| AD-002 | Momentum Feature Ownership 未拆分 | 特征与 Trend 重叠 | M2 Step 3: 分步重训 |
| AD-003 | Fusion 使用静态权重 | 无法自适应 | M3: 接入 Evaluation 动态权重 |
| AD-004 | 潜龙 ML 训练与 AQF-T Evidence 未分离 | 训练数据不共享 | M3: Contract 定义 |

---

*AQF-T Architecture Milestones V1.0*
