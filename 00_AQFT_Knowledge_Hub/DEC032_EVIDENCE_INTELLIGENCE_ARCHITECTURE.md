# DEC-032: Evidence Intelligence Architecture

Version: V1.0.0
Status: ✅ FROZEN — Architecture Contracts Only
Date: 2026-08-03
Type: Architecture Decision Record (ADR-002)
Approval: GPT + 老板 (2026-08-03)
Based on: DEC-029 Evidence First / DEC-031 EFL v1.0

## Frozen Scope

> **This document freezes architectural contracts only.**
> **It does not freeze algorithms, models, features, parameters, or implementation details.**
>
> Trend Producer 可以从 LightGBM 换成 Transformer——只要它仍然只回答"趋势是否成立"。
> Fusion Weight 可以变化——只要它仍然只综合已有 Evidence，不产生新事实。

---

## 零、架构哲学

> **One Producer, One Responsibility.**
> **One Evidence, One Meaning.**
> **Fusion does not create new facts.**

这三句话是 DEC-032 不可妥协的基石。

---

## 一、架构位置

```
Level 0: Execution Platform (潜龙)
    ↑
Level 1: Evidence Foundation (DEC-029/031) ✅ FROZEN
    ↑
Level 2: Evidence Intelligence (DEC-032) 🟡 CANDIDATE
    ↑
Level 3: Decision Intelligence (未来)
    ↑
Level 4: Learning System (未来)
```

DEC-032 定义的是 Level 2——所有 Evidence 如何组织、分工、专业化、融合。

---

## 二、核心原则

### P1: One Producer, One Responsibility

一个 Producer 只回答一个问题。不做一个"什么都会"的万能模型。

→ 详见 [DEC-032B](DEC032B_PRODUCER_RESPONSIBILITY.md)

### P2: One Evidence, One Meaning

一个 Evidence 永远只有一种语义。

- Trend Evidence 永远只表达"趋势是否成立"
- 不能今天表示趋势，明天表示趋势+风险，后天表示趋势+量能
- Ontology 一旦定义，语义不可漂移

→ 详见 [DEC-032A](DEC032A_EVIDENCE_ONTOLOGY.md)

### P3: Ownership Hierarchy

```
Evidence Domain（不变）
    │
    └── Producer（稳定身份，可替换）
            │
            └── Implementation（算法/模型/版本，可替换）
```

- 换 Implementation → Producer 身份不变
- 换 Producer → Domain 不变
- 这才是真正的 Architecture Stability

→ 详见 [DEC-032C](DEC032C_EVIDENCE_SPECIALIZATION.md)

### P4: Fusion Does Not Create New Facts

- Fusion 综合已有 Evidence，不推断、不猜测、不预测
- "综合趋势+动量+盘口 → BUY" 是 Fusion
- "我猜明天还会涨 → BUY" 是 Prediction，不是 Fusion
- Fusion 不是预测引擎

→ 详见 [DEC-032D](DEC032D_FUSION_POLICY.md)

### P5: Naming Discipline

禁止使用模型名称呼 Producer。

```
❌ "LGBM Producer"
✅ "Trend Producer (implementation: LightGBM)"

❌ "XGB Signal"
✅ "Momentum Evidence (source: XGBoost)"
```

---

## 三、子文档索引

| 文档 | 内容 |
|------|------|
| [DEC-032A](DEC032A_EVIDENCE_ONTOLOGY.md) | Evidence Universe — 12 个 Domain 定义 |
| [DEC-032B](DEC032B_PRODUCER_RESPONSIBILITY.md) | 8 个 Producer — 各自只回答一个问题 |
| [DEC-032C](DEC032C_EVIDENCE_SPECIALIZATION.md) | Feature Ownership + 四步过渡策略 |
| [DEC-032D](DEC032D_FUSION_POLICY.md) | Regime 权重 + Confidence Gate + Risk Override |

---

## 四、Architecture Review Gate

冻结前必须通过三项验证：

### AR-1: Ontology Mapping

用现有 6 个 Producer 验证：

| Producer | Domain | 是否无歧义？ |
|----------|--------|:--:|
| TrendML (LGBM) | Trend Evidence | 待验证 |
| MomentumML (XGBoost) | Momentum Evidence | 待验证 |
| TDX Formula | Formula Evidence | 待验证 |
| Path A | Board Evidence | 待验证 |
| RegimeEngine | Regime Evidence | 待验证 |
| ExitPipeline | Exit Evidence | 待验证 |

### AR-2: Responsibility Conflict Check

检查：
- 是否存在两个 Producer 回答同一个问题？
- 是否存在一个 Producer 回答多个问题？

### AR-3: Fusion Consistency

用 60 天真实模拟回放验证：
- Fusion 能否仅依赖 Evidence 做出一致解释？
- 是否存在需要引入额外隐式规则才能决策的情况？

---

## 五、冻结条件

DEC-032 正式从 CANDIDATE → FROZEN 的条件：

1. AR-1/2/3 全部通过
2. 至少一次完整的模拟交易回放验证
3. 老板最终批准

---

*DEC-032 Evidence Intelligence Architecture V1.0 — CANDIDATE*
*待 AR Gate 验证后升级为 FROZEN*
