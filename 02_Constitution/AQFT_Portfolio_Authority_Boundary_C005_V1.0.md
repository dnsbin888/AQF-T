# AQF-T C-005: Portfolio Authority Boundary

Version: V1.0.0
Status: ✅ FROZEN — Constitution-Level
Date: 2026-07-28
Source: P0-004 Portfolio Manager Design V1.0

---

## Core Definition

**Portfolio Manager = Capital Allocation Intelligence. Not Alpha Generator. Not Market Predictor.**

---

## MUST

| Rule | Description |
|------|-------------|
| ✅ Consume DecisionIntent | From Decision Intelligence |
| ✅ Consume StrategyPlan | From Strategy Runtime |
| ✅ Generate CapitalAllocation | Output funding decision |
| ✅ Manage Portfolio Exposure | Total/Sector/Position limits |
| ✅ Respect RiskConstraint | From Risk Runtime |
| ✅ Output PortfolioDecision | APPROVE/REDUCE/REJECT/DEFER/WAIT |

---

## MUST NOT

| Rule | Description |
|------|-------------|
| ❌ Generate Market Direction | 属于 Decision Intelligence |
| ❌ Create Trading Signal | 属于 AI Brain |
| ❌ Modify DecisionIntent | 违反 C-001 |
| ❌ Override Risk Runtime | Risk has veto authority |
| ❌ Direct Submit Order | 违反 C-003 |
| ❌ Modify Immutable Core | 违反 C-002 |

---

## Permissions (Limited)

| Action | Allowed? | Constraint |
|--------|:--------:|------------|
| Reject DecisionIntent | ✅ | 资金/风险/相关性约束导致。记录原因→Memory |
| Reduce allocation proactively | ✅ | Based on exposure/correlation limits only |
| Manage sector concentration | ✅ | Cap enforcement, not theme judgment |
| Learn allocation efficiency | ✅ | Configuration efficiency only, not market direction |

---

*AQF-T C-005 Portfolio Authority Boundary — Constitution-Level. FROZEN.*
