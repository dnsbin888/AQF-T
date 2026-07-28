# AQF-T Benchmark Framework V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — V3.1

---

## 1. Purpose

No module may claim effectiveness by comparing only to itself. Every original module must benchmark against at least one external baseline.

## 2. Benchmark Matrix

| AQF-T Module | vs Baseline | Metrics |
|-------------|------------|---------|
| LimitUp Intelligence | Traditional Breakout Strategy | Win Rate, Sharpe, MaxDD |
| Opponent Model | Simple Capital Flow Model | Decision Accuracy |
| Quant Footprint | Hawkes Process Model | Detection Precision |
| Pattern Extractor | Standard RAG Retrieval | Retrieval Accuracy |

## 3. Benchmark Result

```json
{
  "module": "LimitUp_Intelligence",
  "aqft_score": { "win_rate": 0.62, "sharpe": 1.45 },
  "baseline_score": { "win_rate": 0.48, "sharpe": 0.82 },
  "improvement_pct": 29.2,
  "verdict": "AQFT_SUPERIOR"
}
```

## 4. Verdicts

AQFT_SUPERIOR → KEEP | EQUIVALENT → SIMPLIFY (use simpler) | BASELINE_SUPERIOR → REPLACE
