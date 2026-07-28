# AQF-T Quant Footprint Intelligence Architecture

Version: V1.0.0 | Status: ARCHITECT REVIEW PASSED — Phase 2 V1.1 | Module: 08_Combat_Intelligence
Created: 2026-07-28

---

## Design Evidence

| Item | Value |
|------|-------|
| Core Concept | Algorithmic Trading Footprint Detection |
| Evidence Level | A (Academic) / B (Industry) / C (Empirical per footprint) |
| Research ID | R-P2-003 |
| Applicable Scope | A股连续竞价市场 |
| Failure Boundary | 低流动性个股、集合竞价阶段、港股/美股 |
| Validation | 回测 + 仿真 + 实盘持续校验 |
| Original Extension | QuantFootprintHypothesis (AQF-T D-Level) |

---

## 1. Purpose

P2-001 answered: "What type of limit-up is this?" P2-002 answered: "Who is driving this?" P2-003 answers: **"Is this market being driven by algorithms?"**

Not identifying specific quant funds. Detecting algorithmic trading patterns in microstructure.

## 2. Architecture

```
Microstructure Data → Quant Footprint → Opponent Model → Decision Intelligence
```

Quant Footprint adds an evidence layer to Opponent Model.

## 3. Five Footprint Types

| Type | Behavior | Risk Impact |
|------|----------|:-----------:|
| F1 Passive Liquidity | 双边挂单, 点差维持 | Risk↓, Liquidity↑ |
| F2 Momentum Ignition | 连续追价, 放大波动 | 追高风险↑ |
| F3 Mean Reversion | 快速反向, 拉高即卖 | 突破持续性↓ |
| F4 Spoofing-like | 挂单-撤单模式 (Hypothesis only) | Trap↑, conf↓ |
| F5 HF Rotation | 大量小单, 快速换手 | Noise↑ |

## 4. Activity Levels

NONE → LOW → MEDIUM → HIGH → DOMINANT

## 5. C-013 Candidate

Quant Footprint may infer algorithmic patterns. Shall never claim specific institution, account, or illegal activity.

## 6. Deliverables

```
08_Combat_Intelligence/Quant_Footprint/
├── 01_Architecture/     ← This document
├── 02_Footprint_State/
├── 03_Inference_Engine/
├── 04_Decision_Interface/
└── 05_Test_Cases/
```

---

## V1.1 Architect Refinements (APPROVED — Score 94-96)

**R1 — Evidence Fusion**: Footprint confidence = multi-feature fusion, not single pattern. Passive Liquidity = OrderFlow + QueueStability + CancelRatio + SpreadStability → fused confidence. Aligned with Belief Engine.

**R2 — Temporal Consistency**: Footprint persistence tiers: Short(<5s, Observation) / Medium(5s-5min, Hypothesis) / Long(>5min, Belief Strength++). Duration matters more than detection.

**R3 — Contradiction Detection**: Footprint vs Opponent conflict → ConflictScore(0-1). High conflict → auto confidence reduction. Example: Momentum Ignition(HIGH) + Institution Accumulating → conflict, conf−0.05.

**C-013 — Market Microstructure Interpretation Boundary**: Microstructure modules may interpret behavior, shall never generate trading decisions. Decision always belongs to Decision Engine.

*Phase 2. APPROVED V1.1. 94-96/100.*
