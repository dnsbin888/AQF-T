# DEC-033: Decision Engine Architecture

Version: V1.1.0
Status: FROZEN — 5项修订完成
Date: 2026-08-03
Type: Architecture Decision Record (ADR-003)
Based on: DEC-032 Evidence Intelligence (FROZEN) / DEC-029 Evidence First
Scope: M3 — Decision Engine
Review: GPT Architecture Review — APPROVED WITH MINOR REVISIONS → ALL APPLIED

---

## 零、定位

Decision Engine 不是 Fusion Engine。Fusion 是其中的一个阶段。

Decision Engine 是 **Evidence 变成 Decision 的完整运行时**。

## Principle 0: Zero-Disruption Evolution

> **Existing logic MUST NOT be rewritten. Only recomposed.**
>
> `decision_core.py` / `arbitration.py` / `risk_guard.py` — 不重写，只重组到新的 Lifecycle 阶段。

## Principle 1: Producer Independence

> **Fusion MUST NOT reference Producer. Fusion MAY reference Domain only.**
>
> ✅ `"trend_evidence"`, `"momentum_evidence"`, `"regime_evidence"`
> ❌ `"trend_ml"`, `"momentum_ml"`, `"LGBM"`, `"XGBoost"`

## Architecture Invariant

```
Decision Engine MUST remain Producer-independent.
No algorithm name / model name / feature name / implementation detail
may appear inside Fusion Runtime.

任何违反此不变量的代码 → 直接拒绝。
```

---

## 一、Decision Lifecycle

```
Evidence Input（来自 EFL）
        │
   [1] Normalize
        │  统一 Evidence → Decision 内部格式
        ▼
   [2] Validate
        │  Schema / Signature / Timestamp / Version / UUID / Registry / Producer
        ▼
   [3] Filter
        │  lifecycle=ARCHIVED? drift=HIGH? enabled=false? expired?
        ▼
   [4] Fusion（纯函数）
        │  加权融合 → Direction + Strength + Confidence
        │  Fusion 只认识 Ontology Domain
        │  Fusion 不知道 Regime / Risk / Position
        ▼
   [5] Policy Gate
        │  Regime Gate: 退潮期？→ 所有 BUY 禁止
        │  Confidence Gate: Fusion.confidence < threshold → 降级
        ▼
   [6] Risk Override
        │  Risk Evidence.level = EXTREME → REJECT all
        │  Risk Evidence.level = HIGH → cap at HOLD
        ▼
   [7] Decision Output
        │  Decision Object → Execution Request
        ▼
   [8] Trace
           Decision Event Stream → Decision Record
```

**关键变化**: Fusion 是纯函数 — 只回答"Evidence综合后市场方向是什么？"。Regime/Confidence/Position 由 Policy Gate 处理。

---

## 二、Decision Object

```python
@dataclass
class Decision:
    # ── 身份 ──
    decision_id: str            # DEC-20260803-000001

    # ── 生命周期 ──
    status: str                 # PENDING / APPROVED / EXECUTED / REJECTED / CANCELLED / EXPIRED

    # ── 类型 ──
    decision_type: str          # BUY / SELL / HOLD / WAIT / EXIT

    # ── 结果 ──
    action: str                 # BUY / SELL / HOLD
    position_pct: float         # 建议仓位百分比
    confidence: float           # 0-1

    # ── 来源（不包含 reasoning，reasoning 属于 Trace） ──
    top_evidence: list[str]     # ["Regime", "Trend", "Board"]
    evidence_contributions: dict  # {domain: contribution_weight}

    # ── 风险 ──
    risk_level: str             # LOW / MEDIUM / HIGH / EXTREME
    risk_override: bool         # Risk 是否否决了某条 Evidence

    # ── 约束 ──
    regime_phase: str           # 高潮期 / 回暖期 / 冰点期 / 退潮期
    max_position_cap: float     # Regime 允许的最大仓位

    # ── 元数据 ──
    timestamp: str              # ISO8601
    runtime_version: str        # "decision.runtime.v1.2"
    decision_version: str       # "decision.v1"
    evidence_sources: list[str] # 参与融合的 evidence_id 列表
```

**关键变化**: 
- `reasoning` 移除 → 属于 Trace
- `status` 新增 → 异步执行生命周期
- `runtime_version` 新增 → Replay 一致性

---

## 三、Fusion Interface（纯函数）

```python
class EvidenceFusionEngine:
    """
    Fusion 纯函数 — 只认识 Ontology Domain，不管 Producer 实现。
    不访问 Regime / Risk / Position。

    Principle 1: Fusion MUST NOT reference Producer.
    """

    def fuse(self, evidence_set: list[Evidence]) -> FusionResult:
        """
        evidence_set: 已验证+已过滤的 Evidence

        Fusion 内部:
          1. 按 Domain 分组
          2. 应用权重（权重由 Policy 层提供，Fusion 不自己决定权重）
          3. 加权聚合 → direction + strength
          4. 输出 FusionResult（纯数据，不含策略判断）
        """
        ...

@dataclass
class FusionResult:
    direction: str              # LONG / SHORT / NEUTRAL
    strength: float             # 0-1
    confidence: float           # 0-1
    top_domains: list[str]      # 贡献最大的 Domain
    contributions: dict         # {domain: contribution_weight}
```

---

## 四、Decision Trace

每个 Decision 生成完整 Event Stream 和可追溯记录。

### 4.1 Decision Event Stream（当前 + M4 扩展位）

```
DecisionCreated
    ↓
DecisionValidated
    ↓
DecisionApproved
    ↓
DecisionExecuted
    ↓
DecisionCompleted
```

### 4.2 Trace Record

```json
{
  "decision_id": "DEC-20260803-000001",
  "timestamp": "2026-08-03T09:35:00",
  "runtime_version": "decision.runtime.v1.2",

  "input": {
    "regime": {"phase": "高潮期", "confidence": 0.94},
    "risk": {"level": "LOW", "confidence": 0.90},
    "trend": {"direction": "LONG", "strength": 0.82, "confidence": 0.81},
    "momentum": {"direction": "LONG", "strength": 0.77, "confidence": 0.73}
  },

  "fusion": {
    "direction": "LONG",
    "strength": 0.85,
    "confidence": 0.87,
    "top_domains": ["trend_evidence", "momentum_evidence"]
  },

  "decision": {
    "action": "BUY",
    "position_pct": 0.12,
    "confidence": 0.87
  },

  "gates": {
    "validate": "PASS — 3 evidence valid",
    "filter": "PASS — 0 filtered out",
    "regime_gate": "PASS — 高潮期允许 BUY",
    "confidence_gate": "PASS — 0.87 > 0.60",
    "risk_override": "No — Risk LOW"
  },

  "reasoning": "高潮期 + 趋势确认 + 动量配合 → 进攻",

  "evidence_sources": [
    "AQFT-20260803-000001",
    "AQFT-20260803-000003",
    "AQFT-20260803-000005"
  ],

  "trace_version": "decision.trace.v1"
}
```

**关键变化**: `reasoning` 在 Trace 中，不在 Decision 中。`runtime_version` 保证 Replay 一致性。

---

## 五、与现有系统的关系

| 现有模块 | DEC-033 后 |
|----------|-----------|
| `decision_core.py` | 保留 → 迁移到 Filter + Policy Gate 阶段 |
| `arbitration.py` | 保留 → 迁移到 Fusion 阶段 |
| `risk_guard.py` | 保留 → 迁移到 Risk Override 阶段 |
| `knowledge_hub.py` | 保留 → 接入 Trace 输出 |
| `evidence_registry.py` | 保留 → Validate 阶段引用 |
| `evidence_eval.py` | 保留 → Filter 阶段引用 drift/health 数据 |

**不替换，只重组。**

---

## 六、与 Ontology 的对齐

DEC-033 的 Fusion 接口不引用任何 Producer ID。只引用 DEC-032A 的 Domain：

```
✅ Fusion 引用: "trend_evidence", "momentum_evidence", "regime_evidence"
❌ Fusion 不引用: "trend_ml", "momentum_ml", "LGBM", "XGBoost"
```

---

*DEC-033 Decision Engine Architecture V1.1 — FROZEN*
*5项GPT修订全部应用。M3 Decision Engine 正式架构基线。*
