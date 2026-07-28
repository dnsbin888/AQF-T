# AQF-T Quant Footprint Inference Engine V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## Design Evidence

| Item | Value |
|------|-------|
| Core Concept | Footprint pattern matching from microstructure signals |
| Evidence Level | A (HMM/pattern detection) + B (industry algo detection practices) |
| Applicable Scope | A股 L2 数据环境 |
| Failure Boundary | 无L2数据时降级为 NONE |

---

## 1. Five Footprint Patterns

| ID | Pattern | Key Signals | Evidence Level |
|----|---------|------------|:--------------:|
| F1 | Passive Liquidity | 双边挂单稳定, 点差小, 撤单率低 | A / B |
| F2 | Momentum Ignition | 连续追价, 大单拆小, 突破加速 | B |
| F3 | Mean Reversion | 快速反向, 拉高即卖, 下跌即买 | A |
| F4 | Spoofing-like | 挂单-快速撤单, 诱导流动性 (Hypothesis) | C |
| F5 | HF Rotation | 大量<1000股订单, 持仓<30s, 频繁交易 | B / C |

## 2. FootprintScore Formula

```
FootprintScore = Σ(feature_i × weight_i × confidence_i) / Σ(weight_i)

Where features include: cancel_ratio, order_frequency, size_consistency,
  holding_variance, bid_ask_imbalance, vwap_correlation, reversal_frequency
```

## 3. F4 Constraint (C-013)

Spoofing-like is a behavior hypothesis ONLY. AQF-T has no regulatory authority. Output always: "Observed pattern consistent with spoofing-like behavior (conf X.XX)" — never "This is spoofing."
