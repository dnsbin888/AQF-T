# AQF-T V4.0 Production Readiness Audit

Version: V1.0.0 | Status: ENGINEERING AUDIT — Awaiting Architect Review
Date: 2026-07-28 | Phase: V4.0 Operate & Evolve

---

## 一、审计目标

将 AQF-T 从 Architecture Intelligence 转换为 Operational Trading Intelligence。

回答：如果明天开始运行，AQF-T 是否具备形成交易闭环的能力？

**MC-016: Architecture Score ≠ Market Score.**

---

## 二、MVP 模块审计矩阵

| Module | Trading Value | Reality Dep | Impl Cost | Maint Cost | Replace? | Decision |
|--------|:-----------:|:----------:|:--------:|:---------:|:--------:|:--------:|
| World Model (S→B→R) | ★★★★★ 30% | ★★★★ | ★★★ | ★★ | ❌ | **KEEP** Tier 1 |
| Market Clock | ★★★★ 15% | ★ | ★ | ★ | ❌ | **KEEP** Tier 1 |
| Decision Intelligence | ★★★★★ 20% | ★★★ | ★★★ | ★★ | ❌ | **KEEP** Tier 1 |
| Fusion Engine | ★★★★★ | ★★ | ★★ | ★ | ❌ | **KEEP** |
| Action Selection | ★★★★★ | ★★ | ★★ | ★ | ❌ | **KEEP** |
| Strategy Runtime | ★★★★ | ★★★ | ★★★ | ★★ | ❌ | **KEEP** |
| Portfolio Manager | ★★★★ | ★★★ | ★★ | ★★ | ❌ | **KEEP** |
| Position Engine | ★★★★ | ★★★★ | ★★ | ★★ | ❌ | **KEEP** |
| Order Planner | ★★★★ | ★★★★ | ★★ | ★ | ❌ | **KEEP** |
| QMT Adapter | ★★★★★ | ★★★★★ | ★ | ★ | ❌ | **KEEP** |
| Reflection Engine | ★★★★★ | ★★★ | ★★ | ★ | ❌ | **KEEP** Tier 1 |
| Experience Memory | ★★★★★ | ★★★★ | ★★★ | ★★ | ❌ | **KEEP** Tier 1 |
| LimitUp Intelligence | ★★★★★ A-share | ★★ | ★★ | ★ | ❌ | **KEEP** Tier 1 |
| Opponent Model | ★★★★ | ★★★ | ★★★ | ★★ | ⚠️ | **KEEP** (validate) |
| Hypothesis Arbitration | ★★★★ | ★★ | ★ | ★ | ❌ | **KEEP** |
| Cold Start Strategy | ★★★★ | ★ | ★ | ★ | ❌ | **KEEP** |
| Failure Pattern Library | ★★★★★ | ★★★ | ★ | ★ | ❌ | **KEEP** Tier 1 |
| Calibration Engine | ★★★★ | ★★★★★ | ★★ | ★ | ⚠️ Buy First | **BUY** (Platt/Bayesian) |
| Knowledge Lifecycle | ★★★ | ★★★ | ★★ | ★★ | ❌ | **DELAY** V4.0 Beta |
| Validation Framework | ★★★ | ★★★★★ | ★★★ | ★★ | ❌ | **DELAY** V4.0 Beta |
| Memory Benchmark | ★★ | ★★★★★ | ★★★ | ★★ | ❌ | **DELAY** V4.0 Beta |
| Quant Footprint | ★★★ | ★★★★ | ★★★ | ★★ | ⚠️ | **DELAY** V4.0 Beta |
| Technology Benchmark | ★ | ★★★★★ | ★★ | ★★ | ❌ | **DELAY** V4.0 Beta |
| Agent Debate | ★ | ★ | ★★★★ | ★★★ | ✅ Buy First | **BUY** (LangGraph) |
| Replay Engine | ★★★ | ★★★★★ | ★★★ | ★★ | ❌ | **DELAY** V4.0 Beta |

---

## 三、MVP Decision Summary

| Decision | Count | Modules |
|:--------:|:-----:|---------|
| **KEEP (V4.0 Alpha)** | **17** | World Model, Decision, Execution chain, Reflection, Experience, LimitUp, Cold Start, Failure Library, Arbitration |
| **BUY** | **2** | Calibration Engine (Platt/Bayesian), Agent Framework (LangGraph) |
| **DELAY (V4.0 Beta)** | **7** | Validation, Calibration integration, Memory Benchmark, Quant Footprint, Replay, Technology Radar, Knowledge Lifecycle |

**MVP: 17 core modules + 2 bought. Not 36 modules.**

---

## 四、MVP 五层架构

**Layer 1 — Market Perception**: Market Data (QMT xtdata) → Observation State

**Layer 2 — World Model Core**: S(t)→B(t)→R(t) + Market Clock + LimitUp Intelligence

**Layer 3 — Decision Core**: Fusion → Action → Strategy → Portfolio → Position → Arbitration → DecisionContext

**Layer 4 — Execution**: Order Planner → QMT Adapter → xttrader (ZERO intelligence)

**Layer 5 — Learning Loop**: Trade Episode → Reflection → Failure Library → Experience Memory → Next Decision

---

## 五、DELAY 暂缓模块

Cross-Market Intelligence, Multi-Agent Debate, Complex Auto-Training, Validation Framework (until Beta), Knowledge Lifecycle (until Beta), Replay Engine (until Beta). 第一版价值未验证，不进入 Alpha。

## 六、第一版真实运行目标（非赚钱）

Trading Reality Loop: Market Data → World Model → Decision → Paper Trade → Outcome → Validation → Memory → Next Decision。先建立闭环。先不追求收益。

---

*AQF-T V4.0 Production Readiness Audit V1.0 — COMPLETE*
