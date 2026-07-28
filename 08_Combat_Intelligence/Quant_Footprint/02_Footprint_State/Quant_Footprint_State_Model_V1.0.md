# AQF-T Quant Footprint State Model V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## Design Evidence

| Item | Value |
|------|-------|
| Core Concept | QuantFootprintState — algorithmic trading activity level |
| Evidence Level | A (academic: HFT detection literature) + B (industry: microstructure signals) |
| Applicable Scope | A股连续竞价 |
| Failure Boundary | 低流动性(<日均1000万成交额) |

---

## 1. QuantFootprintState

```json
{
  "symbol": "SH.603xxx",
  "timestamp": "2026-07-28T10:00:00",
  "activity_level": "HIGH",
  "footprint_score": 78,
  "confidence": 0.83,
  "dominant_pattern": "Momentum_Ignition",
  "evidence_chain": [
    { "feature": "cancel_ratio", "value": 0.62, "weight": 0.25, "conf": 0.85, "source": "L2_orderflow" },
    { "feature": "order_size_pattern", "value": "small_burst", "weight": 0.20, "conf": 0.78, "source": "L2_tick" },
    { "feature": "bid_ask_symmetry", "value": 0.75, "weight": 0.20, "conf": 0.82, "source": "L2_depth" },
    { "feature": "holding_duration_ms", "value": 450, "weight": 0.20, "conf": 0.88, "source": "trade_flow" },
    { "feature": "vwap_deviation_pct", "value": 0.35, "weight": 0.15, "conf": 0.80, "source": "price_data" }
  ],
  "alternative_hypothesis": "Institution_High_Frequency_Adjustment",
  "alternative_confidence": 0.35
}
```

## 2. Activity Levels

| Level | Score | Meaning |
|-------|:----:|---------|
| NONE | 0-15 | No algorithmic patterns detected |
| LOW | 15-35 | Minor algo activity, negligible impact |
| MEDIUM | 35-55 | Noticeable algo presence, monitor |
| HIGH | 55-80 | Significant algo dominance, adjust |
| DOMINANT | 80-100 | Market primarily algo-driven, caution |

## 3. Evidence Chain (MC-001 Compliant)

Every footprint classification backed by observable signals: cancel_ratio, order_size_pattern, bid_ask_symmetry, holding_duration_ms, vwap_deviation_pct. Each with weight, confidence, and data source. 100% explainable.
