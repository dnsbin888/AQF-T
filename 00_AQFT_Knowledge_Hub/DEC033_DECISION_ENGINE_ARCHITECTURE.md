# DEC-033: Decision Engine Architecture

Version: V1.0.0
Status: DESIGN — 待评审
Date: 2026-08-03
Type: Architecture Decision Record (ADR-003)
Based on: DEC-032 Evidence Intelligence (FROZEN) / DEC-029 Evidence First
Scope: M3 — Decision Engine

---

## 零、定位

Decision Engine 不是 Fusion Engine。Fusion 是其中的一个阶段。

Decision Engine 是 **Evidence 变成 Decision 的完整运行时**。

## 一、Decision Lifecycle

```
Evidence Input（来自 EFL）
        │
   [1] Normalize
        │  统一 Evidence → Decision 内部格式
        ▼
   [2] Filter
        │  过滤：lifecycle=ARCHIVED? drift=HIGH? enabled=false?
        ▼
   [3] Gate
        │  Regime Gate: 退潮期？→ 所有 BUY 禁止
        │  Confidence Gate: Evidence < min_confidence? → 降权
        ▼
   [4] Fusion
        │  加权融合 → Direction + Strength + Confidence
        │  Fusion 只认识 Ontology Domain，不认识具体 Producer
        ▼
   [5] Risk Override
        │  Risk Evidence.level = EXTREME → REJECT all
        │  Risk Evidence.level = HIGH → cap at HOLD
        ▼
   [6] Decision Output
        │  Decision Object → Execution Request
        ▼
   [7] Trace
           Decision Record → Reasoning Trace → Evidence Hub
```

## 二、Decision Object

Decision 是一级对象，不是 dict。

```python
@dataclass
class Decision:
    # ── 身份 ──
    decision_id: str            # DEC-20260803-000001

    # ── 类型 ──
    decision_type: str          # BUY / SELL / HOLD / WAIT / EXIT

    # ── 结果 ──
    action: str                 # BUY / SELL / HOLD
    position_pct: float         # 建议仓位百分比
    confidence: float           # 0-1

    # ── 推理 ──
    top_evidence: list[str]     # ["Regime", "Trend", "Board"]
    reasoning: str              # 人类可读: "高潮期 + 趋势确认 + 回封确认 → 买入"
    evidence_contributions: dict  # {evidence_source: contribution_weight}

    # ── 风险 ──
    risk_level: str             # LOW / MEDIUM / HIGH / EXTREME
    risk_override: bool         # Risk 是否否决了某条 Evidence

    # ── 约束 ──
    regime_phase: str           # 高潮期 / 回暖期 / 冰点期 / 退潮期
    max_position_cap: float     # Regime 允许的最大仓位

    # ── 元数据 ──
    timestamp: str              # ISO8601
    decision_version: str       # "decision.v1"
    evidence_sources: list[str] # 参与融合的 evidence_id 列表
```

## 三、Fusion Interface

Fusion 不直接认识 TrendML、MomentumML。只认识 Ontology Domain。

```python
class EvidenceFusionEngine:
    """
    Fusion 接口 — 只消费 Ontology Domain，不管 Producer 实现
    """

    def fuse(self, evidence_set: list[Evidence]) -> FusionResult:
        """
        evidence_set: 任意来源的 Evidence，已通过 Filter + Gate

        Fusion 内部:
          1. 按 Domain 分组 (Trend/Momentum/Board/Regime/Risk/...)
          2. 应用 Regime-自适应权重
          3. 加权聚合 → direction + strength
          4. 输出 FusionResult
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

## 四、Decision Trace

每个 Decision 自动生成可追溯记录。

```json
{
  "decision_id": "DEC-20260803-000001",
  "timestamp": "2026-08-03T09:35:00",

  "input": {
    "regime": {"phase": "高潮期", "confidence": 0.94},
    "risk": {"level": "LOW", "confidence": 0.90},
    "trend": {"direction": "LONG", "strength": 0.82, "confidence": 0.81},
    "momentum": {"direction": "LONG", "strength": 0.77, "confidence": 0.73}
  },

  "decision": {
    "action": "BUY",
    "position_pct": 0.12,
    "confidence": 0.87,
    "reason": "高潮期 + 趋势确认 + 动量配合 → 进攻"
  },

  "gates": {
    "regime_gate": "PASS — 高潮期允许 BUY",
    "confidence_gate": "PASS — 融合置信度 0.87 > 0.60",
    "risk_override": "No — Risk LOW"
  },

  "evidence_sources": [
    "AQFT-20260803-000001",
    "AQFT-20260803-000003",
    "AQFT-20260803-000005"
  ],

  "trace_version": "decision.trace.v1"
}
```

## 五、与现有系统的关系

| 现有模块 | DEC-033 后 |
|----------|-----------|
| `decision_core.py` | 保留 → 迁移到 Decision Engine 的 Filter+Gate 阶段 |
| `arbitration.py` | 保留 → 迁移到 Fusion 阶段 |
| `risk_guard.py` | 保留 → 迁移到 Risk Override 阶段 |
| `knowledge_hub.py` | 保留 → 接入 Trace 输出 |

**不替换，只重组**。现有代码逻辑不变，但调用链重新编排为 7 阶段 Lifecycle。

## 六、与 Ontology 的对齐

DEC-033 的 Fusion 接口不引用任何 Producer ID。只引用 DEC-032A 的 Domain：

```
✅ Fusion 引用: "trend_evidence", "momentum_evidence", "regime_evidence"
❌ Fusion 不引用: "trend_ml", "momentum_ml", "LGBM", "XGBoost"
```

这确保 Producer 可替换，Fusion 不受影响。

---

*DEC-033 Decision Engine Architecture V1.0 — 待评审*
