# AQF-T Failure Pattern Library Design

Version: V1.0.0 | Status: ENGINEERING DRAFT — Awaiting Architect Review
Phase: V3.0 Phase 1 | Module: Memory System — Failure Patterns
Created: 2026-07-28

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Failure_Pattern_Library_Design_V1.0.md |
| Module | Memory System — Failure Pattern Library |
| Parent | AQFT_Memory_Consolidation_Pattern_Learning_Design_V1.0 (MEM-003) |
| Upstream | Reflection Intelligence (P1-003 Error Attribution) |
| Downstream | Decision Intelligence (confidence/risk adjustment) |
| Constitutions | C-001, C-002, C-009(candidate) |

---

## 1. Purpose

成功模式寻找机会。失败模式保护资本。两者目标不同，必须独立管理。

传统系统只记录交易盈亏。AQF-T 记录**为什么失败、失败模式是什么、如何防止再次失败**。

## 2. Architecture

```
Reflection (P1-003) → Error Attribution → Failure Candidate → Failure Pattern Library
                                                                      │
                                              ┌───────────────────────┘
                                              ▼
                                    Decision Adjustment
                                    (confidence ↓ / risk ↑ / action constrained)
```

## 3. FailurePattern Object

```json
{
  "failure_id": "FAIL_001",
  "pattern_type": "Fake_Breakout",
  "market_context": { "regime": "Neutral", "emotion": "Warming", "trigger": "Volume surge + price breakout" },
  "wrong_assumption": "Breakout confirms Expansion transition",
  "actual_outcome": { "next_day": "Price falls below breakout level", "regime": "Stays Neutral" },
  "loss_characteristic": { "avg_loss_pct": -4.2, "max_loss_pct": -8.5, "frequency": "12% of breakout signals" },
  "prevention_rule": "Require 2-day confirmation above breakout level before ENTER",
  "confidence": 0.85,
  "episodes_supporting": 23,
  "decision_impact": { "confidence_penalty": 0.15, "risk_bump": 10, "action_constraint": "ENTER→Prepare until confirmed" }
}
```

## 4. A-Share Priority Failure Library (V3.0)

**F001 — 假突破**: Expansion信号→次日回Neutral。约束: 需2日确认。损失: avg -4.2%。

**F002 — 龙头高潮接力失败**: Mania→次日退潮。约束: 高位板>7→仓位减半。损失: avg -7.8%。

**F003 — 情绪周期误判**: 疑似Recovery→继续Ice。约束: Recovery信号需3项共振(涨停↑+炸板↓+连板↑)。损失: avg -5.5%。

**F004 — 流动性陷阱**: 放量突破→次日缩量跌回。约束: 突破日换手>5%+次日量不缩。损失: avg -3.8%。

**F005 — 尾盘追高**: 14:45追→次日低开。约束: 14:30后禁止新开ENTER。损失: avg -2.5%。

## 5. Failure → Decision Impact

| Failure Match | Confidence | Risk | Action Constraint |
|:------------:|:----------:|:----:|:-----------------:|
| F001 Fake Breakout | −0.15 | +10 | ENTER→Prepare |
| F002 Leader Top Chase | −0.20 | +15 | Reduce max position 50% |
| F003 Emotion Misjudge | −0.25 | +15 | ENTER blocked until confirmed |
| F004 Liquidity Trap | −0.10 | +10 | Require volume confirmation |
| F005 Late-Day Chase | −0.15 | +5 | Block ENTER after 14:30 |

## 6. Failure Extraction Pipeline

```
Error Attribution (P1-003) → DecisionQuality=BAD + similar context × N≥5 → Failure Candidate
  → Manual review → FailurePattern (if validated) → Decision Adjustment Rules
```

**N≥5 for failure patterns** (vs N≥30 for success patterns). 失败案例稀缺但信息密度高。

## 7. Constitution

C-009: Failure Pattern constrains (confidence↓/risk↑/action blocked). Never auto-modifies core logic.

---

## Items Requiring Architect Review

| # | Item |
|---|------|
| 1 | N≥5 for failure patterns (vs N≥30 for success) — appropriate? |
| 2 | 5 initial failure types — sufficient for V3.0? |
| 3 | Failure→Decision impact values — confirm? |

---

*AQF-T Failure Pattern Library V1.0 — ENGINEERING DRAFT*
