# AQF-T Limit-Up OrderFlow Model V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## 1. Purpose

What happens ON the limit-up board matters more than the fact of the limit-up itself. Is capital accumulating or distributing?

## 2. Board Volume Analysis

| Pattern | Signal | Meaning |
|---------|:------:|---------|
| 缩量封板 (volume declining on board) | Bullish | Sellers exhausted, holders confident |
| 放量封板 (volume rising, seal holds) | Neutral | Capital exchanging, watch direction |
| 放量炸板 (volume spike + seal breaks) | Bearish | Distribution. Someone is dumping. |

## 3. Seal Trajectory

```
Seal Strength over time:
  封单递增 → Strong confidence (接力资金持续进场)
  封单稳定 → Normal (封板健康)
  封单衰减 → Warning (板上资金撤单 or 抛压增加)
  封单骤降 → Critical (可能炸板)
```

## 4. BreakPressure Score

BreakPressure = 炸板次数×0.40 + 炸板深度×0.30 + 回封耗时×0.30. Score > 0.70 → High risk.
