# AQF-T C-013: Market Microstructure Interpretation Boundary

Version: V1.0.0 | Status: ✅ FROZEN — Constitution-Level
Date: 2026-07-28 | Source: P2-003 Quant Footprint Intelligence V1.1

---

## Core Definition

**Microstructure modules may interpret market behavior, shall never generate trading decisions. Decision always belongs to Decision Engine.**

---

## MAY

| Rule | Description |
|------|-------------|
| ✅ Detect algorithmic patterns | Momentum Ignition, Mean Reversion, Passive Liquidity, etc. |
| ✅ Output Footprint Hypothesis | With confidence, evidence chain, temporal persistence |
| ✅ Adjust decision context | Confidence, risk, execution style |
| ✅ Detect contradictions | Footprint vs Opponent conflict → confidence reduction |

---

## SHALL NOT

| Rule | Description |
|------|-------------|
| ❌ Generate trading signals | 属于 Decision Intelligence |
| ❌ Claim specific institution/account | AQF-T is not 交易所后台 |
| ❌ Claim illegal activity | Hypothesis only. "Consistent with" language, never definitive |
| ❌ Modify Immutable Core | 违反 C-002 |

---

## Core Pattern

```
Observed Microstructure → Evidence Fusion → Footprint Hypothesis → Confidence → Decision Context
NOT: Footprint → BUY/SELL
```

---

*AQF-T C-013 Market Microstructure Interpretation Boundary — Constitution-Level. FROZEN.*
