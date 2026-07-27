# AQF-T Limit-Up Board Type Model V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## 1. LimitUpState Object

```json
{
  "symbol": "SH.603xxx",
  "board_type": "换手板",
  "first_limit_time": "09:45",
  "reopen_count": 0,
  "seal_strength": 0.85,
  "seal_decay_rate": -0.02,
  "board_turnover_pct": 8.5,
  "board_volume_profile": "Healthy_Exchange",
  "emotion_position": "Warming_Leader",
  "next_day_risk": 0.25,
  "confidence_adjustment": 0.10
}
```

## 2. Five Board Types

| Type | Seal | Turnover | Reopens | Time Quality | Decision |
|------|:----:|:--------:|:-------:|:------------:|----------|
| 一字板 | 0.99 | <1% | 0 | N/A | Wait for volume |
| 换手板 | 0.80+ | 5-15% | 0-1 | Best ★ | Leader Candidate |
| 烂板 | <0.60 | >20% | 2+ | Poor | Risk↑, avoid |
| 回封板 | 0.70+ | 10-20% | 1-2 | 早>午>尾 | Conditional |
| 天地板 | 0.00 | >25% | N/A | Worst | Risk Extreme |

## 3. SealQuality Formula

SealQuality = 封单持续性×0.40 + 封单变化稳定性×0.35 + 撤单低比例×0.25
