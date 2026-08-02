# DEC-034: Decision Learning Architecture

Version: V1.1.0
Status: ✅ FROZEN — GPT revisions applied
Date: 2026-08-03
Type: Architecture Decision Record (ADR-004)
Based on: DEC-033 Decision Engine (FROZEN) / DEC-032 Evidence Intelligence (FROZEN)
Scope: M4 — Decision Learning
Review: GPT Architecture Review — APPROVED with minor refinements → ALL APPLIED

---

## Principle 0: Learning Independence

> **AQF-T never learns model parameters. AQF-T only learns Evidence Trustworthiness.**
>
> ✅ 学习: Trend Evidence 在高潮期的权重、Momentum Evidence 的健康阈值
> ❌ 不学习: LGBM 超参数、XGBoost max_depth、任何 Producer 内部实现

## Principle 1: Human Governance

> **Every Learning Proposal SHALL be reviewable, auditable, and revertible before activation.**
>
> Learning → Proposal → Architecture Review → Approval → Activation
> 不自动修改任何 Evidence Weight。只出建议，人审批。

## Architecture Invariant

```
Learning Never Updates Models.
Learning Only Updates Evidence Knowledge.

任何直接修改 Producer 实现的学习机制 → 直接拒绝。
```

---

## 零、定位

M4 不只是 Replay。M4 是 **Decision 如何从历史中学习**。

```
Evidence → Decision → Execution → Outcome → Evaluation → Learning → Evidence Weight Update
                                                                          ↑
                                                              学习的不是模型
                                                              学习的是 Evidence 的可信度
```

## Part A: Replay Runtime

### A.1 定义

Replay 不是测试工具。Replay 是 Learning 的基础设施。

```
历史 Evidence（EFL 存储，Immutable）
        │
        ▼
   Replay Runtime
        │  用历史 Evidence Snapshot 重放 Decision Lifecycle
        │  相同 Evidence → 相同 Decision（确定性）
        ▼
   Compare: 历史 Decision vs 实际 Outcome
```

### A.2 铁律

> **Replay Runtime SHALL NEVER recompute historical Evidence.**
> Replay 只能 Replay Evidence Snapshot，不能重新生成 Evidence。
> 否则 Replay 永远无法保证 100% 确定性。

### A.3 要求

- 确定性: 相同 Evidence Snapshot → 100% 相同 Decision
- 可追溯: 每次 Replay 记录 runtime_version
- 可并行: 60 天 Replay 可并行执行

## Part B: Outcome Evaluation

### B.1 定义

不评估模型。评估 Decision 质量。

```
Decision(t) → Execution(t) → Outcome(t+N)
                                    │
                                    ▼
                           Outcome Evaluation
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Direction OK?    Timing OK?      Magnitude OK?
                                    │
                               Alpha vs Benchmark?
```

### B.2 评估维度

| 维度 | 问题 | 影响 |
|------|------|------|
| Direction Accuracy | 方向对吗？ | → Evidence 可信度 |
| Timing Quality | 时机好吗？ | → Entry Timing Evidence |
| Magnitude Appropriateness | 仓位合适吗？ | → Policy Gate 参数 |
| Regime Appropriateness | Regime判断对吗？ | → Regime Evidence 权重 |
| Alpha vs Benchmark | 跑赢基准了吗？ | → Decision 有效性 |

### B.3 Outcome Object

```python
@dataclass
class DecisionOutcome:
    decision_id: str
    direction_correct: bool
    forward_return: float        # t+N 日收益
    benchmark_return: float      # 同期基准收益（沪深300）
    alpha_return: float          # forward_return - benchmark_return
    max_adverse: float           # 持有期间最大回撤
    holding_days: int            # 实际持有天数
    exit_reason: str             # 退出原因
    grade: str                   # A / B / C / D / F
    lesson: str                  # 人类可读教训
```

## Part C: Pattern Memory

### C.1 定义

不是日志。不是 Evidence。是经验。

```
历史 Decision + Outcome
        │
        ▼
   Pattern Extraction
        │  什么条件下 → 什么 Decision → 什么结果？
        ▼
   Pattern Memory（Versioned, Append-only）
        │
        ├── Pattern-001 v1: "高潮期 + Trend>0.8 + Board>0.9 → BUY 胜率 78%"
        ├── Pattern-001 v2: "高潮期 + Trend>0.8 + Board>0.9 → BUY 胜率 74%" (更新)
        └── Pattern-002 v1: "退潮期 + 任何 BUY → 胜率 12%"
```

### C.2 铁律

> **Pattern SHALL be Versioned. Never overwrite. Always append.**
> Pattern v1 → v2 → v3，永远保留历史。Pattern 本身也是 Evidence。

### C.3 Pattern Object

```python
@dataclass
class DecisionPattern:
    pattern_id: str
    version: int               # v1, v2, v3...
    conditions: dict           # {regime: "高潮期", trend_min: 0.8}
    action: str                # BUY / SELL / HOLD
    sample_size: int
    win_rate: float
    avg_return: float
    confidence: float
```

## Part D: Knowledge Update

### D.1 Evidence Weight Learning

```
Pattern Memory
        │
        ▼
   Evidence Trustworthiness Update
        │
        ├── Trend Evidence 在高潮期可信度 0.82 → weight 0.30
        ├── Trend Evidence 在退潮期可信度 0.15 → weight 0.00
        └── Momentum Evidence 近30天衰减 → drift=MEDIUM → weight 0.20
        │
        ▼
   Learning Proposal（不直接生效）
        │
        ▼
   Architecture Review → 人审批 → Activation
```

### D.2 Learning Policy

> **Learning SHALL NOT auto-modify. Learning → Proposal → Review → Approval → Activation.**

```
Learning Discovery
        │
        ▼
   Learning Proposal (auto-generated, human-reviewed)
        │
        ▼
   Architecture Review Gate
        │
        ▼
   Approval → Activation
   或 Reject → Record & Skip
```

### D.3 Learning Contract

```python
@dataclass
class LearningUpdate:
    update_id: str              # LRN-20260803-000001
    target: str                 # "trend_evidence"
    update_type: str            # confidence | weight | calibration | health
    before: float               # 0.30
    after: float                # 0.26
    reason: str                 # "近30天命中率从74%降至68%"
    evidence_ids: list[str]     # 支撑此更新的 Evidence 列表
    proposal_status: str        # PROPOSED / APPROVED / REJECTED / ACTIVATED
    runtime_version: str        # "decision.runtime.v1.2"
    reviewed_by: str            # "Human" | "AR-Gate"
```

### D.4 学习的是 Evidence，不是模型

```
✅ 学习: Trend Evidence 的 Regime-自适应权重
✅ 学习: Momentum Evidence 的健康阈值
✅ 学习: Board Evidence 的置信度校准

❌ 不学习: LGBM 的超参数
❌ 不学习: XGBoost 的 max_depth
❌ 不学习: 任何模型内部参数
❌ 不学习: 不自动修改 Evidence Weight（只出 Proposal）
```

## Part E: Self Evolution（M5 扩展位）

```
Knowledge Update
        │
        ▼
   Producer Health → 自动检测（不自动调整）
        │
        ▼
   Fusion Weight → 自动检测 → Learning Proposal
        │
        ▼
   New Producer Discovery → 人工审批
        │
        ▼
   Architecture Evolution → Architecture Review Gate
```

> **Self Evolution IS Architecture Governed.**
> 任何 Self Evolution 必须经过 Architecture Review，不是 Runtime 自主决定。

M4 不做 Self Evolution。只预留接口。

## 与现有系统的关系

| 现有模块 | DEC-034 后 |
|----------|-----------|
| P0-3 `evidence_eval.py` | → Outcome Evaluation（已有基础） |
| P0-4 `evidence_health.py` | → Evidence Weight Learning 输入 |
| `ml_daily_report.py` 的信号跟踪 | → Replay Runtime 数据源 |
| P0-5 `exit_attribution.py` | → Outcome.exit_reason 数据源 |

---

*DEC-034 Decision Learning Architecture V1.1 — FROZEN*
*GPT 修订: Learning Contract + Learning Policy + Immutable Replay + Benchmark + Versioned Pattern*
