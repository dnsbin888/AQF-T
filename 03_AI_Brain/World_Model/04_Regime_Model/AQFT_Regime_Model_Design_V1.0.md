# AQF-T Regime Model Design

Version: V1.0.0
Status: FROZEN — V2.9.0 World Model Architecture Freeze
Phase: V2.9 Intelligence Era — World Model
Module: 04_Regime_Model
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Regime_Model_Design_V1.0.md |
| Module | World Model — Regime Model |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_World_Model_Intelligence_Spec_V2.9.0 |
| Upstream | Market State Space ✅ + Belief State Engine ✅ |
| Downstream | Scenario Simulation ⏳ + Decision Intelligence |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Market World Model V3.0.0 + Environment Model V3.0.0 + Strategy Design V2.8.6 |

---

## 1. Purpose

### 1.1 What Regime Model Does

Regime Model 回答：

**"当前市场属于哪个阶段？系统应该采用什么行为模式？"**

[Source: `AQFT_Market_World_Model_Design_V3.0.0` — Chapter 4 + `AQFT_Environment_Model_Design_V3.0.0`]

### 1.2 Regime Model ≠ Stock Predictor

| ❌ NOT | ✅ IS |
|--------|------|
| 预测个股涨跌 | 识别市场整体阶段 |
| 输出买卖信号 | 输出环境约束 |
| 单一数值指标 | 多维 Regime 分类 + 置信度 |
| 静态分类 | 动态转移追踪 |

### 1.3 Why Regime Matters for A-Share

A 股市场高度 Regime-dependent：

- 同一策略在 Expansion 和 Panic 中表现完全相反
- 游资生态高度依赖情绪周期阶段
- 趋势策略在震荡市（Neutral）中失效
- 防御策略在牛市中踏空

[Source: `AQFT_Strategy_Design_V2.8.6.md` — Strategy-Regime Adaptation Matrix]

---

## 2. Scope

### 2.1 In Scope

- Market regime classification (7 types)
- Regime transition detection
- A-share emotion cycle mapping
- Regime-confidence scoring
- Regime → Strategy constraint translation
- Regime → Risk level mapping

### 2.2 Out of Scope

- ❌ Individual stock selection
- ❌ Entry/exit timing
- ❌ Position sizing
- ❌ Institutional macro forecasting
- ❌ Global multi-asset regime modeling

---

## 3. Architecture Position

### 3.1 In World Model

```
Market State S(t) ──── [L1: 02_State_Model ✅]
        ↓
Belief State B(t) ──── [L2: 03_Belief_Model ✅]
        ↓
Regime Classification ─ [L2: 本模块]
        ↓
Scenario Simulation ─── [L3: 05_Simulation ⏳]
        ↓
Decision Intelligence
```

### 3.2 Information Chain

```
Observation → State Vector → Belief → Regime ID → Behavioral Constraint
                                                      ├→ Strategy Runtime
                                                      └→ Risk Runtime
```

---

## 4. Regime Intelligence Philosophy

### 4.1 Core Principle

市场不是随机游走。它在不同 Regime 之间切换，每个 Regime 有不同的统计特征、参与者和行为模式。

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 3]

### 4.2 Regime Awareness

```
Without Regime Model:
  Strategy sees: Price up +2% → Buy
  (but it's a bear market rally → trap)

With Regime Model:
  Strategy sees: Price up +2% in Distribution Regime → Caution
  (regime context changes the interpretation)
```

---

## 5. Regime State Definition

### 5.1 Seven Regime Types

[Source: `AQFT_Market_World_Model_Design_V3.0.0` — Chapter 4 — adapted from 10 World types to 7 AQF-T regimes]

| ID | Regime | A-Share Name | Key Features |
|----|--------|-------------|--------------|
| R0 | Neutral | 震荡市 | Sideways, low volume, no clear direction, sector rotation |
| R1 | Accumulation | 吸筹 | Quiet accumulation, institutional buying, low volatility |
| R2 | Expansion | 扩张/主升 | Trend UP, rising volume, broad participation, bullish |
| R3 | Mania | 狂热/高潮 | FOMO, limit-up frenzy, extreme sentiment, high leverage |
| R4 | Distribution | 派发 | Institutional selling, divergence, decreasing momentum |
| R5 | Panic | 恐慌 | Crash, liquidity dry-up, limit-down cascade, forced selling |
| R6 | Recovery | 恢复 | Stabilization, bottom formation, cautious return of capital |

### 5.2 Regime State Object

```json
{
  "regime_id": "BS_20260727_093500",
  "timestamp": "2026-07-27T09:35:00",
  "current_regime": {
    "regime_type": "Expansion",
    "regime_id": 2,
    "confidence": 0.82,
    "duration": "15 trading days",
    "phase_within_regime": "Mid"
  },
  "transition_risk": {
    "next_most_likely": "Mania",
    "probability": 0.35,
    "warning_signals": ["sentiment_heating", "volume_accelerating"]
  },
  "regime_features": {
    "trend_strength": 0.72,
    "breadth": 0.68,
    "participation": "Broad",
    "volatility_regime": "Normal"
  },
  "version": "V1.0"
}
```

---

## 6. Regime Classification Framework

### 6.1 Classification Input

[Source: `AQFT_Market_World_Model_Design_V3.0.0` — Chapter 4.3]

```
Input Vector = [
  S₁ Price Structure,     ← from Market State Space
  S₂ Volume/Liquidity,
  S₃ Capital Flow,
  S₄ Emotion State,
  S₅ Theme Rotation,
  S₆ Microstructure,
  S₇ Risk State,
  B_trend,                ← from Belief State Engine
  B_emotion,
  B_risk,
  B_regime_prior          ← prior regime belief
]
```

### 6.2 Classification Pipeline

```
Feature Vector → Regime Encoder → Regime Classifier → Regime ID + Confidence
```

**[NEEDS ARCHITECT REVIEW]** — Classifier method (rule-based / ML / hybrid) deferred to Implementation. Architecture is classifier-agnostic.

### 6.3 Multi-Timeframe Classification

| Timeframe | Purpose | Update |
|-----------|---------|--------|
| Short (intraday) | Tactical regime shifts | Every 5-15 min |
| Medium (daily) | Trend regime | Daily |
| Long (weekly) | Structural regime | Weekly |

```
Final Regime = 0.5 × Medium + 0.3 × Long + 0.2 × Short
```

---

## 7. A-Share Emotion Cycle Mapping

### 7.1 Emotion-Regime Correspondence

这是 AQF-T 区别于通用 Regime Model 的 A 股特色。

[Source: `AQFT_AI_Brain_Design_V2.8.6.md` — Chapter 4 Sentiment Engine + Market World Model Ch.4]

| Emotion Phase | Typical Regime | Strategy Posture |
|---------------|---------------|------------------|
| 冰点 (Ice) | Panic → Recovery 过渡 | 控仓试错，首板低吸 |
| 回暖 (Warming) | Recovery → Accumulation | 寻找主线，接力二板 |
| 高潮 (Climax) | Expansion → Mania | 龙头锁仓，挖掘补涨 |
| 退潮 (Recession) | Mania → Distribution | 减仓空仓，管住手 |

### 7.2 Emotion Score → Regime Mapping

```
Emotion Score < 20  → R5 Panic / R6 Recovery
Emotion Score 20-50 → R1 Accumulation / R6 Recovery
Emotion Score 50-80 → R2 Expansion
Emotion Score > 80  → R3 Mania / R4 Distribution (退潮预警)
```

### 7.3 A-Share Specific Regime Signals

| Signal | Regime Indication |
|--------|-------------------|
| 涨停>80家 + 连板>7 | R3 Mania |
| 炸板率>50% + 天地板出现 | R4 Distribution 开始 |
| 跌停>30家 + 连板高度≤2 | R5 Panic |
| 反包板出现 + 炸板率<30% | R6 Recovery → R1 过渡 |

---

## 8. Transition Model

### 8.1 Regime Transition Graph

[Source: `AQFT_Market_World_Model_Design_V3.0.0` — Chapter 5 Dynamics Model]

```
          ┌──────────────────────────────────┐
          │                                  │
          ▼                                  │
R0 Neutral ←──→ R1 Accumulation → R2 Expansion → R3 Mania
  ↑   │                                              │
  │   │                                              ▼
  │   │                                    R4 Distribution
  │   │                                              │
  │   │                                              ▼
  │   └──────────────────────────── R5 Panic ←───────┘
  │                                              │
  └────────────────── R6 Recovery ←──────────────┘
```

### 8.2 Transition Probability Matrix

**[NEEDS ARCHITECT REVIEW]** — Specific transition probabilities require historical A-share calibration.

Template:

| From \ To | Neutral | Accum. | Expans. | Mania | Distr. | Panic | Recov. |
|-----------|:-------:|:------:|:-------:|:-----:|:------:|:-----:|:------:|
| Neutral | 0.60 | 0.20 | 0.10 | 0.00 | 0.05 | 0.03 | 0.02 |
| Accumulation | 0.10 | 0.40 | 0.40 | 0.05 | 0.03 | 0.01 | 0.01 |
| Expansion | 0.05 | 0.05 | 0.45 | 0.30 | 0.10 | 0.03 | 0.02 |

(Values are placeholder — need empirical calibration)

### 8.3 Transition Detection Signals

| Signal | Indicates |
|--------|-----------|
| Trend weakening + Volume declining | Expansion → Distribution |
| High volatility spike | Any → Panic |
| Sentiment extreme + Capital outflow | Mania → Distribution |
| Falling limit-down count + stabilizing volume | Panic → Recovery |

---

## 9. Confidence Model

### 9.1 Regime Confidence

```
Confidence = f(
  Classification_Probability,    # classifier output
  Signal_Consistency,            # multi-signal agreement
  Historical_Accuracy,           # past regime call accuracy
  Transition_Ambiguity           # penalty for border-line cases
)
```

### 9.2 Confidence Levels

| Level | Range | Action |
|-------|-------|--------|
| High | >0.80 | Regime constraint fully active |
| Medium | 0.60-0.80 | Regime constraint active, wider tolerance |
| Low | <0.60 | Reduce regime-dependent constraints, fall back to Risk-first |

---

## 10. AI Brain Integration

### 10.1 Input from AI Brain

| Engine | Regime Input |
|--------|-------------|
| Sentiment Engine | Emotion phase + score → drives emotion-regime mapping |
| Prediction Engine | Trend probability → drives trend regime classification |
| Risk Intelligence | Risk score → drives risk-regime override |

### 10.2 Regime-Driven AI Behavior

| Regime | Prediction Weight | Sentiment Weight | Risk Weight |
|--------|:----------------:|:----------------:|:-----------:|
| Expansion | 0.35 | 0.25 | 0.20 |
| Mania | 0.20 | 0.35 | 0.30 |
| Panic | 0.15 | 0.20 | 0.50 |
| Neutral | 0.25 | 0.25 | 0.30 |

[Source: `AQFT_AI_Brain_Design_V2.8.6.md` — Chapter 6 Fusion Engine dynamic weights]

---

## 11. Strategy Runtime Interface

### 11.1 Regime → Strategy Constraint

```
Regime Model Output → Strategy Runtime → Strategy Selection
```

| Regime | Allowed Strategy Types | Restricted |
|--------|----------------------|------------|
| Neutral | 趋势、价值、量价 | 禁止追高 |
| Expansion | 趋势、龙头 | — |
| Mania | 龙头、补涨 | 禁止低吸 |
| Distribution | 防御 | 禁止追高、禁止龙头接力 |
| Panic | 仅防御 | 禁止新开仓 |
| Recovery | 试错首板 | 禁止重仓 |

### 11.2 API

```python
def get_regime_constraint(regime_id: int) -> StrategyConstraint:
    """Return strategy behavior constraints for current regime."""
```

---

## 12. Risk Runtime Interface

### 12.1 Regime → Risk Level Override

```
Regime Model → Risk Runtime → Position Limit
```

| Regime | Default Risk Level | Position Limit | Special Rule |
|--------|:-----------------:|:-------------:|--------------|
| Neutral | Medium | 50% | — |
| Expansion | Low-Medium | 70% | — |
| Mania | High | 50% | 退潮预警激活 |
| Distribution | High | 30% | 禁止加仓 |
| Panic | Extreme | 10% | 仅平仓 |
| Recovery | Medium-High | 30% | 试错仓位 |

### 12.2 Regime Risk Override

当 Regime 判定与 Risk Intelligence 冲突时：

```
IF Regime = Panic AND Risk_Score = Low
   → Regime override: apply Panic constraint regardless
   (Regime has constitutional priority in structural risk scenarios)

IF Regime = Expansion AND Risk_Score = High
   → Risk override: apply High Risk constraint regardless
   (Risk Fortress has highest constitutional priority)
```

[Source: Constitution V2.8.6 — Risk Control Highest Authority]

---

## 13. Engineering Requirement

### 13.1 Implementation Constraints

| Constraint | Value |
|------------|-------|
| Classification latency | < 50ms |
| Regime change detection | Within 1 bar (5min) |
| Historical regime store | Last 5 years daily |
| Memory | < 200MB for regime model + cache |

### 13.2 Code Structure

```
world_model/regime_model/
├── regime_classifier.py       # Regime classification logic
├── transition_detector.py     # Regime change detection
├── emotion_regime_mapper.py   # A-share emotion → regime mapping
├── regime_constraint.py       # Strategy + Risk constraint output
├── regime_store.py            # Persistence
└── __init__.py
```

---

## 14. Testing Requirement

### 14.1 Unit Tests

- Each regime correctly classified from feature vector
- Transition detection accuracy on known regime changes
- Emotion-regime mapping correctness
- Confidence degradation on borderline inputs

### 14.2 Historical Period Coverage

| Period | Expected Regime Path |
|--------|---------------------|
| 2015 H1 | Accumulation → Expansion → Mania |
| 2015 H2 | Distribution → Panic |
| 2018 | Neutral → Distribution → Panic |
| 2020 Q1 | Panic (COVID) → Recovery |
| 2020 H2 | Recovery → Expansion |
| 2024 | [NEEDS ARCHITECT REVIEW] — period-specific calibration |

### 14.3 Integration Test

- Full chain: State → Belief → Regime → Strategy Constraint
- Regime-aware strategy backtest vs regime-unaware baseline

---

## 15. Freeze Criteria

1. **Architecture Review Passed** — Correctly positioned between Belief and Simulation
2. **7 regimes validated** — Each with clear features, signals, and constraints
3. **A-share emotion cycle mapped** — 冰点/回暖/高潮/退潮 correctly linked to regimes
4. **Strategy + Risk interfaces defined** — Constraints clearly specified
5. **No trading strategy design** — Regime model constrains, does not decide
6. **Engineering ready** — Classifier design, storage, testing plan specified

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-3 | `AQFT_World_Model_Architecture_V3.0.0` Ch.5 + `AQFT_Environment_Model_Design_V3.0.0` |
| 4 | `AQFT_World_Model_Architecture_V3.0.0` Ch.3 |
| 5-6 | `AQFT_Market_World_Model_Design_V3.0.0` Ch.4 |
| 7 | `AQFT_AI_Brain_Design_V2.8.6.md` Ch.4 + Market World Model Ch.4 |
| 8 | `AQFT_Market_World_Model_Design_V3.0.0` Ch.5 |
| 9 | Inferred from Belief State + State Vector confidence models |
| 10 | `AQFT_AI_Brain_Design_V2.8.6.md` Ch.6 |
| 11-12 | `AQFT_Strategy_Design_V2.8.6.md` + `AQFT_Risk_Design_V2.8.6.md` |
| 13-15 | Inferred from Blueprint principles + V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Classifier method (rule-based / ML / hybrid) | §6 |
| 2 | Transition probability calibration (need A-share empirical data) | §8 |
| 3 | 2024 period Regime path annotation | §14 |
| 4 | Multi-timeframe fusion weights (0.5/0.3/0.2) — confirm? | §6 |

---

*AQF-T Regime Model Design V1.0 — ENGINEERING DRAFT*  
*Source: 3 Blueprint documents + AI Brain / Strategy / Risk V2.8.6*  
*No original design added. All content traceable to existing AQF-T architecture.*
