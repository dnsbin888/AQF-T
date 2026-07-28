# AQF-T V4.0 Canonical Data & Interface Contract

Version: V1.0.0 | Status: ARCHITECT APPROVED 99/100 — Architecture Era CLOSED
Phase: V4.0 Engineering Foundation — Final Architecture Freeze
Date: 2026-07-28

---

## 一、目标

**建立 AQF-T 全系统唯一数据语言。这是设计阶段最后一个架构级冻结点。完成之后进入 Software Engineering。**

Principle: **Canonical Before Implementation** — Contract → Review → Freeze → Coding. 禁止先写代码后统一。

## 二、七大 Canonical Objects

| ID | Object | Flow | Description |
|----|--------|------|-------------|
| O-001 | MarketObservation | Market → WM | 统一市场输入 |
| O-002 | BeliefState | WM → Decision | World Model 输出 |
| O-003 | DecisionContext | Decision → Execution | 唯一决策对象 |
| O-004 | TradeIntent | Execution → Broker | 执行意图 |
| O-005 | TradeEpisode | Execution → Memory | 完整交易记录 |
| O-006 | ReflectionRecord | Episode → Knowledge | 反思与学习 |
| O-007 | KnowledgeUnit | Memory → Future | 知识资产 |

## 三、决策对象示例 (O-003 DecisionContext)

```json
{
  "context_id": "DEC-20260728-00001",
  "direction": "ENTER",
  "confidence": { "raw": 0.82, "calibrated": 0.74, "historical_reliability": 0.71 },
  "risk": { "level": "Medium", "score": 35 },
  "position": { "target_pct": 0.30, "max_pct": 0.50 },
  "reason": ["Regime=Expansion", "Emotion=Warming", "Leader=Confirmed"],
  "evidence_chain": [{ "source": "LimitUp", "conf": 0.81, "level": "C" }],
  "conflict_score": 0.12,
  "calibration": { "samples": 386, "ece": 0.06 }
}
```

## 四、四大接口类型

| Type | Method | Side-effect | Example |
|------|--------|:----------:|---------|
| Query | Read state | None | Get MarketObservation |
| Infer | Observation→Belief | None | World Model inference |
| Decide | Belief→Decision | None | Decision Engine |
| Learn | Episode→Knowledge | Update Memory | Reflection |

所有模块只能属于四类之一。禁止模块自定义 ad-hoc 接口。

## 五、统一规范

**ID**: OBS-/BEL-/DEC-/INT-/EPI-/REF-/KNW- 前缀 + timestamp/counter

**Evidence Contract** (MC-001): 每个对象携带 Evidence Level, Source, Chain

**Confidence Contract**: Raw → Calibration → Adjusted → Historical Reliability. 统一。禁止模块自算。

**Runtime Contract**: Observation→Belief→Decision→Intent→Execution→Episode→Reflection→Knowledge. 禁止跳层。

**Plugin Contract**: 所有 BUY 模块统一 Adapter 接入。

## 六、Schema 文件

```
03_Engineering/Canonical/
├── observation.schema | belief.schema | decision.schema | intent.schema
├── episode.schema | reflection.schema | knowledge.schema
```

## 七、验收

任何开发者无需阅读全部架构，仅阅读 Contract 即可开发。新增模块无需修改已有模块。

---

*AQF-T V4.0-003 Canonical Contract V1.0 — Last Architecture Freeze Before Coding*
