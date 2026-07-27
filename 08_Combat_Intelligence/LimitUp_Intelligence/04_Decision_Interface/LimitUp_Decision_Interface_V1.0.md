# AQF-T Limit-Up Decision Interface V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## 1. Decision Input Upgrade

Decision(S,B,R,Clock) → Decision(S,B,R,Clock,**LimitUpState**)

## 2. Decision Impact Matrix

| Board Type | Time | Conf Δ | Risk Δ | Position | Action |
|-----------|------|:------:|:------:|:--------:|--------|
| 换手板 | OpenDrive | +0.10 | 0% | Full | ENTER candidate |
| 换手板 | ClosePricing | −0.10 | +15% | Half | Prepare only |
| 回封板 | MorningTrend | +0.05 | +5% | Half | Conditional |
| 回封板 | ClosePricing | −0.15 | +20% | Minimal | Wait |
| 烂板 | Any | −0.20 | +25% | None | Avoid |
| 天地板 | Any | −0.50 | EXTREME | Exit | Emergency |

## 3. F006 — New Failure Pattern

高潮接力失败: Mania+高位板(≥7)+封单衰减→次日退潮。约束: 高位板仓位减半。conf −0.20, risk +15.

## 4. Examples

**09:45 换手板**: Leader+OpenDrive+Seal 0.85 → conf+0.10, Full ENTER candidate.

**14:50 换手板**: Leader+ClosePricing+Seal 0.80 → conf−0.10, Prepare, F005 active.

**烂板 2次炸**: Seal<0.60, BreakPressure>0.70 → conf−0.20, Avoid, Risk HIGH.
