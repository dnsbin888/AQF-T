# AQF-T MC-018 & MC-019: Engineering Principles

Version: V1.0.0 | Status: ✅ FROZEN — Meta Constitution
Date: 2026-07-28 | Source: V4.0-002 Architect Review

---

## MC-018: Stable Foundation First（稳定基础优先）

**成熟基础设施优先采用。AQF-T 不重复建设已经成熟的底层能力。原创开发仅用于形成长期竞争优势。**

Sub-principle: Complexity Budget — Capability_Gain / Complexity_Cost > 1.

---

## MC-019: Canonical Interface First（统一规范接口优先）

**任何模块通信必须使用统一 Canonical Object。禁止模块之间自行定义数据格式。**

All interfaces through Canonical Schema. MarketObservation, BeliefState, DecisionContext, TradeEpisode, ReflectionRecord, KnowledgeUnit — one definition per object.

---

## AQF-T Build Boundary (Frozen)

| Decision | Scope |
|:--------:|-------|
| **BUY** | Database, Vector DB, Agent Framework, ML Framework, Calibration, Infrastructure |
| **BUILD** | World Model, Decision Context, Failure Memory, A-Share Combat Knowledge, Constitution |

AQF-T never builds infrastructure. AQF-T builds cognition.

---

*AQF-T MC-018 & MC-019 — FROZEN.*
