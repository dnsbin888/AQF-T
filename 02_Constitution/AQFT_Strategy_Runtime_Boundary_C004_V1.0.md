# AQF-T C-004: Strategy Runtime Boundary

Version: V1.0.0
Status: ✅ FROZEN — Constitution-Level
Date: 2026-07-28
Source: P0-003 Strategy Runtime Design V1.0
Applies to: All V3.0+ Strategy Runtime implementations

---

## Core Definition

**Strategy Runtime = Decision Executor Planner. Not Decision Maker. Not Second Brain.**

---

## MUST

| Rule | Description |
|------|-------------|
| ✅ Consume DecisionIntent | 唯一行动意图来源 |
| ✅ Generate StrategyPlan | 输出执行方案 |
| ✅ Respect RiskConstraint | 接受 Risk Runtime 约束 |
| ✅ Produce StrategyResult | 输出执行反馈 |
| ✅ Report Outcome to Memory | 形成经验闭环 |

---

## MUST NOT

| Rule | Description |
|------|-------------|
| ❌ Generate Market Direction | 属于 Decision Intelligence |
| ❌ Modify DecisionIntent | 违反 C-001 |
| ❌ Override Risk | 属于 Risk Runtime |
| ❌ Access QMT directly | 违反 C-003 |
| ❌ Modify Immutable Core | 违反 C-002 |
| ❌ Bypass Decision Intelligence | 违反 Intelligence Chain |
| ❌ Self-evolve trading logic | 属于 Evolution System |

---

## Permissions (Limited)

| Action | Allowed? | Constraint |
|--------|:--------:|------------|
| Save strategy parameters | ✅ | Configuration only, not market intelligence |
| Learn execution efficiency | ✅ | Slippage/speed/deviation only, not trading logic |
| Multi-strategy competition | ✅ | For execution suitability, not profit prediction |
| Suggest execution size | ✅ | Must pass Portfolio Manager + Risk Runtime |

---

*AQF-T C-004 Strategy Runtime Boundary — Constitution-Level. FROZEN.*
