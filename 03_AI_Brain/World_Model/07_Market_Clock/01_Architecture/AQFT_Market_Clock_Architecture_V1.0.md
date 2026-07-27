# AQF-T Market Clock Design

Version: V1.0.0 | Status: ARCHITECT REVIEW PASSED — Phase 1 Complete
Phase: V3.0 Phase 1 — Final Module (6/6) | Module: World Model — Market Clock
Created: 2026-07-28

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Market_Clock_Design_V1.0.md |
| Module | World Model — Market Clock (Temporal Intelligence) |
| Parent | AQFT_World_Model_Intelligence_Spec_V2.9.0 + WM-02 State Model |
| Upstream | World Model S(t), Belief B(t) |
| Downstream | Decision Intelligence, MEM-003 Failure Library |
| Constitutions | C-001, C-002, C-009 |

---

## 1. Purpose

同一市场状态，不同时间阶段，含义完全不同。

```
09:35 龙头首板 = 强势确认 → 高价值信号
14:55 龙头首板 = 尾盘偷袭 → 次日大概率低开
```

Market Clock 将时间维度注入 World Model，让系统不仅知道 "现在是 Expansion"，更知道 "现在是 14:50 的 Expansion"。

---

## 2. Five A-Share Trading Phases

| Phase | Time | Market Meaning | Signal Weight | Risk |
|-------|------|---------------|:------------:|:----:|
| Auction | 09:15-09:25 | 集合竞价。预期形成。禁止交易。 | 0.00 | — |
| OpenDrive | 09:30-10:00 | 全天信息释放最快。方向确认价值最高。 | **1.20** | Normal |
| MorningTrend | 10:00-11:30 | 趋势确认/反转。追高风险增加。 | 1.00 | +5% |
| AfternoonConsolidation | 13:00-14:30 | 资金重新选择。分歧修复窗口。 | 0.90 | +10% |
| ClosePricing | 14:30-15:00 | 次日定价。尾盘反转风险最高。 | **0.70** | **+20%** |

---

## 3. SessionPhaseState Object

```json
{
  "date": "2026-07-28",
  "current_time": "14:52:00",
  "phase": "ClosePricing",
  "minutes_from_open": 322,
  "minutes_to_close": 8,
  "liquidity_profile": "Declining",
  "volatility_regime": "Elevated",
  "historical_behavior": { "tail_reversal_probability": 0.32, "breakout_reliability": 0.45 }
}
```

---

## 4. Decision Impact: Same Signal, Different Time

```
Signal: Leader Stock Breakout + Volume Surge

09:35 (OpenDrive):
  Signal_Weight: ×1.20
  Confidence: +0.10
  Rationale: "Early confirmation in high-liquidity window"

14:50 (ClosePricing):
  Signal_Weight: ×0.70
  Confidence: −0.15
  Risk: +20%
  Rationale: "Late breakout unreliable. High reversal probability. F005 activated."
```

---

## 5. MEM-003 Connection

F005 (Late-Day Chase) 从固定规则 "14:30后禁ENTER" 升级为认知调整：

```
Before WM-02: 14:30→Block ENTER (fixed rule)
After WM-02:  ClosePricing→Risk+20%, Weight×0.70, F005 check → Decision
```

---

## 6. MarketClockContext → Decision Pipeline

```
World Model S(t)+B(t)+R(t) + MarketClockContext → Decision Intelligence
                                                        │
                                          Confidence adjusted by phase weight
                                          Risk adjusted by phase modifier
                                          Failure patterns checked per phase
```

---

## 7. Constitution

| Rule | Status |
|------|:------:|
| C-002: Immutable Core | ✅ Provides context. Never writes S(t)/B(t)/R(t) |
| C-009: Learning Boundary | ✅ Phase weights from history, not hardcoded |

---

## Phase 1 Completion

WM-02 is the final Phase 1 module:

```
P1-001 Observation       ✅
P1-002 Experience        ✅
P1-003 Reflection        ✅
MEM-001 Cold Start       ✅
MEM-003 Failure Library  ✅
WM-02 Market Clock       ✅ → Awaiting Review

Phase 1: 6/6 submitted
```

---

## Items Requiring Architect Review

| # | Item |
|---|------|
| 1 | Phase signal weights (1.20/1.00/0.90/0.70) — confirm? |
| 2 | Risk modifiers (+0%/+5%/+10%/+20%) — appropriate? |
| 3 | F005 upgrade: rule→cognitive adjustment — approved? |

---

*AQF-T Market Clock Design V1.0 — ENGINEERING DRAFT*
