# AQF-T Belief State Engine Design

Version: V1.0.0
Status: FROZEN — V2.9.0 World Model Architecture Freeze
Phase: V2.9 Intelligence Era — World Model
Module: 03_Belief_Model
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Belief_State_Engine_Design_V1.0.md |
| Module | World Model — Belief State Engine |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_World_Model_Intelligence_Spec_V2.9.0 |
| Upstream | AQFT_Market_State_Space_Design_V1.0 ✅ |
| Downstream | AQFT_Regime_Model_Design (⏳) |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Environment Model V3.0.0 + Market World Model V3.0.0 + World Model Architecture V3.0.0 |

---

## 1. Purpose

### 1.1 What Belief State Engine Is

Belief State Engine 是 World Model Layer 2 的核心组件。

它回答：**"在当前市场观测下，AI 认为真实情况是什么？"**

[Source: `AQFT_World_Model_Architecture_V3.0.0` — Chapter 5 + `AQFT_Environment_Model_Design_V3.0.0` — Chapter 1]

### 1.2 What Belief State Engine Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 预测引擎（那是 AI Brain Prediction Engine） | 认知推断引擎 |
| 直接输出交易信号 | 输出置信度加权的市场认知 |
| 单一数值判断 | 多维信念状态向量 |
| 黑箱输出 | 可追溯的证据链 |

### 1.3 Core Distinction

```
Prediction Engine:   "明天涨还是跌？"     → Future
Belief State Engine: "现在真实情况是什么？" → Present (hidden)
```

市场观测可能是噪声、误导或过时的。Belief State Engine 从噪声中提取信号。

[Source: `AQFT_Environment_Model_Design_V3.0.0` — Chapter 1.2: "State ≠ Environment"]

---

## 2. Architecture Position

### 2.1 In World Model

```
Market Data
     ↓
Market State Vector S(t) ─── [L1: 02_State_Model ✅]
     ↓
Belief State Engine ──────── [L2: 本模块]
     ↓
Regime Model ─────────────── [L2: 04_Regime_Model ⏳]
     ↓
Scenario Simulation ──────── [L3: 05_Simulation ⏳]
     ↓
Decision Intelligence
```

### 2.2 Information Flow

```
Observable              Hidden                 Belief
─────────              ──────                 ──────
Price Trend      →    真实趋势方向      →    Trend Belief + Confidence
Volume Spike     →    真实资金意图      →    Capital Belief + Confidence
Limit-Up Surge   →    真实情绪强度      →    Emotion Belief + Confidence
Low Volatility   →    暴风雨前的宁静?   →    Risk Belief + Confidence
```

[Source: `AQFT_Environment_Model_Design_V3.0.0` — Chapter 1.2 — "状态相似，世界不同"]

---

## 3. Core Design — Observation → Belief Pipeline

### 3.1 Belief Formation Process

```
Market Observation O(t)
        ↓
Evidence Extraction ──── 从观测中提取证据
        ↓
Prior Belief B(t-1) ─── 先验信念
        ↓
Belief Update ───────── 贝叶斯式信念更新
        ↓
Posterior Belief B(t) ─ 后验信念
        ↓
Confidence Calibration ─ 置信度校准
        ↓
Belief State Output ─── 最终信念状态
```

[Source: Inferred from `AQFT_World_Model_Architecture_V3.0.0` Chapter 5 — Layer 2 Dynamics Model]

### 3.2 Mathematical Abstraction

```
B(t) = Update( B(t-1), Evidence(O(t)) )

Where:
  B(t)    = Belief State at time t
  O(t)    = Observable Market State S(t) + additional signals
  Evidence = Function extracting signal from noise
  Update   = Belief revision mechanism
```

**[NEEDS ARCHITECT REVIEW]** — Specific update mechanism (Bayesian, Dempster-Shafer, or learned) deferred to Implementation Phase. Architecture remains model-agnostic.

---

## 4. Observation Layer

### 4.1 Input Sources

[Source: `AQFT_Market_State_Space_Design_V1.0.md` + `AQFT_Environment_Model_Design_V3.0.0`]

| Source | Provides |
|--------|----------|
| Market State Vector | S(t) — 9-dimension observable state |
| AI Brain Sentiment Engine | Emotion cycle phase, sentiment score |
| AI Brain Prediction Engine | Trend direction probability |
| Data Runtime | Raw L2 data, fund flow |
| Strategy Runtime Feedback | Strategy performance signals |

### 4.2 Observation Quality Assessment

每个观测不是同等可信。系统评估：

| Quality Factor | Meaning |
|----------------|---------|
| Data Freshness | 数据是否最新？ |
| Source Reliability | 数据源是否可靠？ |
| Signal Consistency | 多源信号是否一致？ |
| Historical Accuracy | 该信号历史准确率？ |

[Source: Composite from Constitution principles + State Confidence Engine in State Vector V1.0]

---

## 5. Belief State Representation

### 5.1 Belief Dimensions

[Source: `AQFT_Market_World_Model_Design_V3.0.0` — Chapter 3 + `AQFT_Environment_Model_Design_V3.0.0`]

```json
{
  "belief_state_id": "BS_20260727_093500001",
  "timestamp": "2026-07-27T09:35:00",
  "beliefs": {
    "trend_belief": {
      "direction": "UP",
      "strength": 0.72,
      "confidence": 0.80,
      "evidence_sources": ["price_structure", "capital_flow", "ma_alignment"]
    },
    "emotion_belief": {
      "phase": "Warming",
      "intensity": 0.65,
      "confidence": 0.75,
      "evidence_sources": ["limit_up_count", "board_height", "sentiment_score"]
    },
    "risk_belief": {
      "level": "Medium",
      "score": 35,
      "confidence": 0.82,
      "evidence_sources": ["volatility", "drawdown", "liquidity"]
    },
    "theme_belief": {
      "dominant_theme": "AI",
      "strength": 0.76,
      "persistence": "Strengthening",
      "confidence": 0.70
    },
    "regime_belief": {
      "current_regime": "Expansion",
      "transition_risk": 0.25,
      "confidence": 0.78
    }
  },
  "overall_confidence": 0.77,
  "belief_version": "V1.0"
}
```

### 5.2 Belief State vs Market State

| Market State S(t) | Belief State B(t) |
|-------------------|-------------------|
| 客观可观测 | 主观推断 |
| 数值精确 | 概率分布 |
| 无歧义 | 带置信度 |
| 即时 | 积累式更新 |
| "是什么" | "AI认为是什么" |

---

## 6. Confidence Estimation

### 6.1 Confidence Model

[Source: `AQFT_State_Vector_Definition_V1.0.md` — Chapter 9 + `AQFT_World_Model_Architecture_V3.0.0`]

```
Confidence = f(Evidence_Quality, Signal_Consistency, Historical_Match, Model_Stability)
```

### 6.2 Confidence Levels

| Level | Range | System Behavior |
|-------|-------|-----------------|
| High | >0.80 | 正常传递给 Decision Intelligence |
| Medium | 0.60-0.80 | 传递但标记不确定性 |
| Low | 0.40-0.60 | 降低下游权重 |
| Unreliable | <0.40 | 禁止驱动交易决策 |

### 6.3 Confidence Degradation

当证据冲突时，置信度自动降低：

```
IF Emotion Signal = Climax BUT Capital Flow = Outflow
   → Emotion Belief confidence *= 0.6  (conflicting signal penalty)
```

[Source: Constitution principles — model conflict resolution]

---

## 7. State Update Mechanism

### 7.1 Belief Revision Cycle

```
Timer / Event Trigger
        ↓
[1] Observe ── 获取新的 Market State + Signals
        ↓
[2] Evidence ─ 提取证据，评估质量
        ↓
[3] Compare ── 新证据 vs 当前信念
        ↓
[4] Update ─── 信念修正
        ↓
[5] Calibrate ─ 重新校准置信度
        ↓
[6] Output ─── 输出 B(t)
```

### 7.2 Update Frequency

| Market Condition | Update Rate | Rationale |
|-----------------|-------------|-----------|
| Normal | Every 5 min | 稳定更新 |
| High Volatility | Every 1 min | 快速响应 |
| Extreme Event | Every 30 sec | 紧急重新评估 |
| Overnight | Once (pre-market) | 隔夜信息消化 |

### 7.3 Belief Persistence

不是每次观测都完全推翻之前的信念。采用平滑更新：

```
B(t) = α × Evidence(O(t)) + (1-α) × B(t-1)

α (learning rate):
  Normal: 0.3 (gradual update)
  High Vol: 0.6 (faster adaptation)
  Regime Change Signal: 0.8 (rapid belief revision)
```

[Source: `AQFT_State_Vector_Definition_V1.0.md` — Chapter 11 — Dynamic Alpha mechanism, adapted for Belief]

---

## 8. Relationship with Upstream Modules

### 8.1 From Market State Space (02_State_Model ✅)

```
Market State S(t) → Belief State Engine → "What does this state really mean?"
```

Belief Engine 接收 S(t) 但不盲信。它评估：这个状态读数有多可靠？

### 8.2 From AI Brain

| Engine | Belief Input |
|--------|-------------|
| Prediction Engine | Trend direction → Trend Belief |
| Sentiment Engine | Emotion phase → Emotion Belief |
| Risk Intelligence | Risk score → Risk Belief |

---

## 9. Relationship with Downstream Modules

### 9.1 To Regime Model (04_Regime_Model)

```
Belief State B(t) → Regime Model → "Given these beliefs, which regime are we in?"
```

Regime Model 使用 Belief State（而非原始 Market State）做 Regime 分类，因为 Belief State 已经过滤了噪声。

### 9.2 To Decision Intelligence

```
Belief State B(t) → Decision Engine → "Given what I believe, what should I do?"
```

Decision Intelligence 使用置信度加权后的信念，而非原始数据。

### 9.3 To Evolution System

```
Belief(t) + Actual(t+n) → Belief Accuracy → Model Improvement
```

事后验证：AI 当时的信念是否正确？→ 反馈到置信度校准。

---

## 10. Data Model

### 10.1 Python Class

```python
@dataclass
class BeliefState:
    belief_id: str
    timestamp: datetime
    trend_belief: Dict       # direction, strength, confidence
    emotion_belief: Dict     # phase, intensity, confidence
    risk_belief: Dict        # level, score, confidence
    theme_belief: Dict       # dominant, strength, persistence
    regime_belief: Dict      # current, transition_risk, confidence
    overall_confidence: float
    evidence_summary: List   # trace of evidence used
    version: str = "V1.0"
```

### 10.2 Storage

| Data | Storage |
|------|---------|
| Current Belief | In-memory cache |
| Historical Beliefs | PostgreSQL / SQLite |
| Belief Change Log | Time-series DB |
| Evidence Trace | JSON field in DB |

---

## 11. Interface

### 11.1 Input

```python
def update_belief(
    market_state: MarketStateVector,   # from 02_State_Model
    ai_signals: Dict,                  # from AI Brain
    prior_belief: BeliefState          # B(t-1)
) -> BeliefState:                     # B(t)
```

### 11.2 Output

```python
def get_current_belief() -> BeliefState
def get_belief_history(from: datetime, to: datetime) -> List[BeliefState]
def get_confidence_breakdown() -> Dict
```

---

## 12. Engineering Requirement

### 12.1 Implementation Constraints

| Constraint | Value |
|------------|-------|
| Inference time | < 100ms per update |
| Memory | < 500MB for belief store |
| CPU-friendly | Yes (no GPU required for core logic) |
| Deterministic given same inputs | Yes (for audit) |

### 12.2 Code Structure

```
world_model/belief_engine/
├── observation_processor.py    # Evidence extraction
├── belief_updater.py           # Belief revision logic
├── confidence_calibrator.py    # Confidence scoring
├── belief_store.py             # Persistence
└── __init__.py
```

---

## 13. Testing Requirement

### 13.1 Unit Tests

- Belief update with consistent signals → confidence increases
- Belief update with conflicting signals → confidence decreases
- Confidence degradation on stale data

### 13.2 Scenario Tests

- Market regime transition (Expansion → Panic): belief shift latency
- Conflicting AI signals: confidence handling
- Missing data: graceful degradation

### 13.3 Historical Replay

- Test belief accuracy against known market events
- Compare B(t) at time t vs actual outcome at t+n

---

## 14. Freeze Criteria

1. **Architect Review Passed** — Belief concept correctly separated from Prediction
2. **Interface alignment** — I/O consistent with State Model + Regime Model
3. **Confidence model validated** — Levels + degradation logic reviewed
4. **Engineering readiness** — Class design, storage, update cycle specified
5. **No scope creep** — No prediction, no direct trading signals

---

## 15. Design Summary

Belief State Engine 是 AQF-T 的"认知过滤器"。

它不预测。它理解。

```
Market State S(t) ──客观观测
        ↓
Belief State Engine ──主观推断 + 置信度
        ↓
B(t) ──"这是 AI 认为当前市场真实的样子"
        ↓
Regime Model + Decision Intelligence
```

核心价值：**让 AI 对自己的认知有自知之明。**

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-2 | `AQFT_World_Model_Architecture_V3.0.0` Ch.5 + `AQFT_Environment_Model_Design_V3.0.0` Ch.1 |
| 3 | Inferred from World Model Architecture Layer 2 |
| 4 | `AQFT_Market_State_Space_Design_V1.0.md` + Environment Model |
| 5 | `AQFT_Market_World_Model_Design_V3.0.0` Ch.3 |
| 6 | `AQFT_State_Vector_Definition_V1.0.md` Ch.9 |
| 7 | Adapted from State Vector Update Mechanism Ch.11 |
| 8-9 | Composite from WM-001 Intelligence Spec |
| 10-14 | Inferred from Blueprint principles + V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Belief update algorithm (Bayesian / Dempster-Shafer / Learned) | §3 |
| 2 | Evidence extraction function specification | §4 |
| 3 | Confidence degradation formula weights | §6 |
| 4 | α parameter values for different conditions | §7 |

---

*AQF-T Belief State Engine Design V1.0 — ENGINEERING DRAFT*  
*Source: 3 Blueprint documents from 24_World_Model_System/*  
*No original design added. All content traceable to V3.0.0 Blueprint.*
