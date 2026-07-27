# AQF-T C-010: Market Context Boundary

Version: V1.0.0 | Status: ✅ FROZEN — Constitution-Level
Date: 2026-07-28 | Source: WM-02 Market Clock Design V1.0

---

## Core Definition

**Market Clock may influence decision context, but shall never own decision authority.**

---

## MAY

| Rule | Description |
|------|-------------|
| ✅ Provide temporal context | SessionPhase, liquidity_profile, volatility_profile |
| ✅ Adjust confidence weights | Based on phase-specific historical reliability |
| ✅ Adjust risk modifiers | Based on phase-specific risk characteristics |
| ✅ Feed historical phase statistics | Update from Experience feedback |

---

## SHALL NOT

| Rule | Description |
|------|-------------|
| ❌ Generate trading signals | 属于 Decision Intelligence |
| ❌ Modify strategy rules | 违反 C-004 |
| ❌ Override Risk Runtime | 违反 C-001 |
| ❌ Modify Immutable Core | 违反 C-002 |

---

*AQF-T C-010 Market Context Boundary — Constitution-Level. FROZEN.*
