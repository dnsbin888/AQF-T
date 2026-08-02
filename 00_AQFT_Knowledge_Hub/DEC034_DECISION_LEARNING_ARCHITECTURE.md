# DEC-034: Decision Learning Architecture

Version: V1.0.0
Status: DESIGN — 待评审
Date: 2026-08-03
Type: Architecture Decision Record (ADR-004)
Based on: DEC-033 Decision Engine (FROZEN) / DEC-032 Evidence Intelligence (FROZEN)
Scope: M4 — Decision Learning

---

## 零、定位

M4 不只是 Replay。M4 是 **Decision 如何从历史中学习**。

```
Evidence → Decision → Execution → Outcome → Evaluation → Learning → Evidence Weight Update
                                                                          ↑
                                                              学习的不是模型
                                                              学习的是 Evidence 的可信度
```

核心闭环:

> 不是更新 LGBM，是更新"Trend Evidence 最近30天可信度下降 → Health下降 → Fusion权重下降"。

## Part A: Replay Runtime

### A.1 定义

Replay 不是测试工具。Replay 是 Learning 的基础设施。

```
历史 Evidence（EFL 存储）
        │
        ▼
   Replay Runtime
        │  用历史 Evidence 重放 Decision Lifecycle
        │  相同 Evidence → 相同 Decision（确定性）
        ▼
   Compare: 历史 Decision vs 实际 Outcome
```

### A.2 要求

- 确定性: 相同 Evidence → 100% 相同 Decision
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
              (涨了吗?)        (准时吗?)        (仓位够吗?)
```

### B.2 评估维度

| 维度 | 问题 | 影响 |
|------|------|------|
| Direction Accuracy | 方向对吗？ | → Evidence 可信度 |
| Timing Quality | 时机好吗？ | → Entry Timing Evidence |
| Magnitude Appropriateness | 仓位合适吗？ | → Policy Gate 参数 |
| Regime Appropriateness | Regime判断对吗？ | → Regime Evidence 权重 |

### B.3 Outcome Object

```python
@dataclass
class DecisionOutcome:
    decision_id: str
    direction_correct: bool
    forward_return: float        # t+N 日收益
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
   Pattern Memory
        │
        ├── "高潮期 + Trend>0.8 + Board>0.9 → BUY 胜率 78%"
        ├── "退潮期 + 任何 BUY → 胜率 12%"
        └── "Trend>0.7 + Momentum<0.5 → 持仓<3天胜率最高"
```

### C.2 Pattern Object

```python
@dataclass
class DecisionPattern:
    pattern_id: str
    conditions: dict        # {regime: "高潮期", trend_min: 0.8, board_min: 0.9}
    action: str             # BUY / SELL / HOLD
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
   Fusion Weight Table（回写到 DEC-032D 的权重模型）
```

### D.2 学习的是 Evidence，不是模型

```
✅ 学习: Trend Evidence 的 Regime-自适应权重
✅ 学习: Momentum Evidence 的健康阈值
✅ 学习: Board Evidence 的置信度校准

❌ 不学习: LGBM 的超参数
❌ 不学习: XGBoost 的 max_depth
❌ 不学习: 任何模型内部参数
```

## Part E: Self Evolution（M5 扩展位）

```
Knowledge Update
        │
        ▼
   Producer Health → 自动调整
        │
        ▼
   Fusion Weight → 自动调整
        │
        ▼
   New Producer Discovery → 人工审批
        │
        ▼
   Architecture Evolution → Architecture Review Gate
```

M4 不做 Self Evolution。只预留接口。

## 与现有系统的关系

| 现有模块 | DEC-034 后 |
|----------|-----------|
| P0-3 `evidence_eval.py` | → Outcome Evaluation（已有基础） |
| P0-4 `evidence_health.py` | → Evidence Weight Learning 输入 |
| `ml_daily_report.py` 的信号跟踪 | → Replay Runtime 数据源 |
| P0-5 `exit_attribution.py` | → Outcome.exit_reason 数据源 |

---

*DEC-034 Decision Learning Architecture V1.0 — 待评审*
