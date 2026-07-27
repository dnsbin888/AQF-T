# AQF-T Market Clock Decision Interface V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: World Model — Market Clock / Decision Interface

---

## 1. Decision Input Upgrade

```
Before WM-02:  Decision(S(t), B(t), R(t))
After WM-02:   Decision(S(t), B(t), R(t), MarketClockContext)
```

## 2. Adjustment Rules

Market Clock does NOT change the Decision. It adjusts confidence and risk context:

| Scenario | Phase | Signal Wt | Conf Δ | Risk Δ | Action Bias |
|----------|-------|:---------:|:------:|:------:|:-----------:|
| Leader Breakout | OpenDrive | 1.20 | +0.10 | 0% | Full ENTER |
| Leader Breakout | ClosePricing | 0.70 | −0.15 | +20% | ENTER→Prepare |
| Trend Follow | MorningTrend | 1.00 | 0 | +5% | Normal |
| New Position | Afternoon | 0.90 | −0.05 | +10% | Half size |

## 3. Examples

**09:35 Leader Breakout**: Recovery+OpenDrive+Liquidity Peak → Conf +0.10, Risk normal, Full ENTER.

**14:50 Same Signal**: Recovery+ClosePricing+Liquidity Declining → Conf −0.15, Risk +20%, F005 active. ENTER→Prepare.
