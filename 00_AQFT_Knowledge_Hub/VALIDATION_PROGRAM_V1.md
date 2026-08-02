# AQF-T Validation Program V1.0

Version: V1.0.0
Status: ACTIVE — Validation Phase
Date: 2026-08-03
Based on: Architecture Baseline v1.0 (M0→M4)
Goal: 证明 Architecture Baseline 可以支撑真实系统运行，而不仅仅是设计正确。

---

## 模式切换

```
Before: Architecture Mode（设计架构）
Now:    Validation Mode（验证架构）

不写新 DEC。不设计新模块。
用真实系统运行，验证已冻结的架构是否成立。
```

## 四阶段验证

### AV-1: Contract Validation

**目标**: 证明所有 Contract 能支撑真实运行，无冲突、无遗漏。

| 检查项 | 方法 |
|--------|------|
| Evidence Contract 字段完整性 | 用真实 TrendML/MomentumML 信号生成 Evidence，检查是否所有必需字段可填充 |
| Decision Contract 生命周期 | 模拟 PENDING→APPROVED→EXECUTED→TRACED 完整链路 |
| Trace Contract 可追溯性 | 回放一个 Decision，检查能否从 Trace 反推所有输入 Evidence |
| Contract 间无循环依赖 | 检查 Evidence→Decision→Trace→Learning 是否单向无环 |

**产出**: Contract Validation Report

### AV-2: Runtime Validation

**目标**: 证明 Decision Engine 在真实数据上稳定、可解释、可追溯。

| 检查项 | 方法 |
|--------|------|
| 60天 Replay 稳定性 | 用潜龙历史数据生成 Evidence → 重放 Decision Lifecycle → 验证 100% 确定性 |
| 决策可解释性 | 每个 Decision 输出完整的 top_evidence + reasoning + gates |
| 零交易影响 | 只输出 Trace，不输出任何实际订单。潜龙完全不受影响 |
| Dashboard 展示 | 将 Decision Trace 展示在潜龙 Flask 页面 |

**产出**: Runtime Validation Report + 60天 Replay 数据

### AV-3: Governance Validation

**目标**: 证明新增 Producer 只需要 Registry + Ontology，不修改 Fusion/Decision/Learning。

| 检查项 | 方法 |
|--------|------|
| 新增 Producer 成本 | 注册一个新的 Formula Producer（模拟），检查需要改动哪些模块 |
| Fusion 不感知 Producer | 新 Producer 注册后，Fusion 代码是否零改动即可消费 |
| Decision 不感知 Producer | Decision Engine 代码是否零改动 |
| 解耦验证 | 如果改动>2个模块 → Architecture 还有耦合 |

**产出**: Governance Validation Report

### AV-4: Evolution Validation

**目标**: 证明 P1（Contracts stable, Implementations replaceable）真正成立。

| 检查项 | 方法 |
|--------|------|
| 替换 Producer 实现 | 将 TrendML 内部从 LightGBM 模拟替换为不同算法 |
| Contract 不变 | Evidence Schema / Decision Schema / Trace Schema 是否零改动 |
| Replay 一致性 | 新旧 Producer 各自 Replay，对比 Decision 是否可复现 |
| 零破坏 | 替换过程是否影响任何其他 Producer 或 Decision |

**产出**: Evolution Validation Report

---

## Architecture Stability Index (ASI)

每次 Validation 完成后更新：

| 维度 | 基线 | AV-1 | AV-2 | AV-3 | AV-4 |
|------|:--:|:--:|:--:|:--:|:--:|
| Contract Compatibility | 100% | ⏳ | ⏳ | ⏳ | ⏳ |
| Replay Determinism | 100% | ⏳ | ⏳ | ⏳ | ⏳ |
| Producer Independence | — | ⏳ | ⏳ | ⏳ | ⏳ |
| Governance Completeness | — | ⏳ | ⏳ | ⏳ | ⏳ |
| Evolution Cost | — | ⏳ | ⏳ | ⏳ | ⏳ |
| Constitution Alignment | 100% | ⏳ | ⏳ | ⏳ | ⏳ |
| **ASI** | **100%** | ⏳ | ⏳ | ⏳ | ⏳ |

---

## 规则

- **不写新 DEC**: Validation 阶段不新增架构设计
- **不修改 Contract**: 发现问题 → 记录 → 等 M5 统一修订
- **不控制交易**: 所有验证只输出 Trace，不影响潜龙
- **Feature Toggle**: 所有验证模块可关闭

---

*AQF-T Validation Program V1.0 — 2026-08-03*
*Mode: Validation. Next: AV-1 Contract Validation.*
