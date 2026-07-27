# AQF-T Scenario Simulation Design

Version: V1.0.0
Status: FROZEN — V2.9.0 World Model Architecture Freeze
Phase: V2.9 Intelligence Era — World Model
Module: 05_Simulation
Created: 2026-07-27

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Scenario_Simulation_Design_V1.0.md |
| Module | World Model — Scenario Simulation (Layer 3-5) |
| System | AQF-T Adaptive Quantitative Fusion Trading System |
| Version | V1.0.0 |
| Parent | AQFT_World_Model_Intelligence_Spec_V2.9.0 |
| Upstream | Market State Space ✅ + Belief State ✅ + Regime Model ✅ |
| Downstream | Decision Intelligence + Strategy Runtime |
| Status | ENGINEERING DRAFT |
| Design Authority | AQF-T Chief Architect |
| Source Blueprint | Scenario Simulation Engine V3.0.0 + Counterfactual Intelligence V3.0.0 + Simulation Memory V3.0.0 |

---

## 1. Purpose

### 1.1 What Simulation Does

Scenario Simulation 回答：

**"如果未来发生变化，可能是什么样子？如果做了不同选择，结果会怎样？"**

[Source: `AQFT_Scenario_Simulation_Engine_Design_V3.0.0` — Chapter 1 + `AQFT_Counterfactual_Intelligence_Engine_Design_V3.0.0` — Chapter 1]

### 1.2 What Simulation Is NOT

| ❌ NOT | ✅ IS |
|--------|------|
| 预测唯一未来 | 生成多个可能的未来路径 |
| 自动交易 | What-if 分析 |
| 替代 Decision Engine | 为 Decision Engine 提供情景输入 |
| 保证准确 | 提供概率加权的多情景参考 |
| 超算级仿真 | 个人工作站级轻量模拟 |

### 1.3 Core Distinction

```
Prediction Engine:    "明天涨5%"                    → Single-point forecast
Scenario Simulation:  "情景A: 涨5%(45%) / 情景B: 震荡(35%) / 情景C: 跌(20%)" → Multi-path
Counterfactual:       "如果我昨天没卖，今天会怎样?"    → Alternative reality
```

---

## 2. Scope

### 2.1 In Scope

- Multi-scenario future path generation
- Scenario probability estimation
- Counterfactual reasoning ("what if")
- Extreme/risk scenario stress testing
- Simulation result storage for memory/learning
- Decision support (what-if analysis)

### 2.2 Out of Scope

- ❌ High-frequency tick-level simulation
- ❌ Institutional Monte Carlo with 100k+ paths
- ❌ Real-time full-market replay
- ❌ Distributed computing simulation
- ❌ Automated trading from simulation results

### 2.3 Target Scale

| Constraint | Limit |
|------------|-------|
| Max parallel scenarios | 10-20 per run |
| Monte Carlo paths | ≤ 1,000 |
| Simulation horizon | 1-20 trading days |
| Compute | Personal workstation CPU |

---

## 3. Architecture Position

### 3.1 In World Model

```
State S(t) + Belief B(t) + Regime R(t) ── [L1+L2: ✅]
              ↓
Scenario Simulation ──────────────────── [L3: 本模块]
              ↓
Counterfactual Reasoning ─────────────── [L4: 本模块]
              ↓
Simulation Memory ────────────────────── [L5: 本模块]
              ↓
Decision Intelligence
```

[Source: `AQFT_Scenario_Simulation_Engine_Design_V3.0.0` — Chapter 2]

### 3.2 Three Sub-modules in One

```
05_Simulation/
├── scenario_generator/     # L3: Multi-future scenario generation
├── counterfactual_engine/  # L4: "What if" reasoning
└── simulation_memory/      # L5: Scenario experience storage
```

---

## 4. Simulation Intelligence Philosophy

### 4.1 Single Future → Scenario Universe

[Source: `AQFT_Scenario_Simulation_Engine_Design_V3.0.0` — Chapter 1.2]

```
Traditional: Current Price → Model → Tomorrow +5%        (one path)
AQF-T:       Current World + Environment + Dynamics       (many paths)
                    ↓
             Future World Tree → Scenario Universe Ω
```

### 4.2 Scenario Universe

```
Ω = {W₁, W₂, W₃, ..., Wₙ}

Examples:
  W₁: Bull Expansion continues   (P=45%)
  W₂: Liquidity tightening       (P=25%)
  W₃: Policy shock hits          (P=15%)
  W₄: Extreme tail risk          (P=5%)
  W₅: Consolidation / sideways   (P=10%)
```

### 4.3 Counterfactual Reasoning Philosophy

```
Observed World (W)
       ↓
Create Alternative World (W')
       ↓
Simulate Different Action (A')
       ↓
Compare: Outcome(A) vs Outcome(A')
       ↓
Learn: Was my decision optimal?
```

[Source: `AQFT_Counterfactual_Intelligence_Engine_Design_V3.0.0` — Chapter 1]

---

## 5. Scenario Generation Framework

### 5.1 Three Generation Methods

[Source: `AQFT_Scenario_Simulation_Engine_Design_V3.0.0` — Chapter 3]

| Method | Description | Use Case |
|--------|-------------|----------|
| Historical Replay | Find similar historical regimes, replay patterns | Baseline scenarios |
| Dynamics Simulation | Use state transition model P(S_{t+1}\|S_t) | Core scenarios |
| Generative Scenario | [NEEDS ARCHITECT REVIEW] — ML-based generation | Tail risk exploration |

### 5.2 Scenario Generation Pipeline

```
Current Market World
       │
       ├→ [1] Extract Current State + Belief + Regime
       │
       ├→ [2] Select Generation Method(s)
       │
       ├→ [3] Generate Future World Branches
       │
       ├→ [4] Estimate Branch Probabilities
       │
       ├→ [5] Evaluate Impact (Return, Risk, Drawdown)
       │
       └→ [6] Package Scenario Objects → Output
```

### 5.3 Scenario Object

```json
{
  "scenario_id": "SC_20260727_001",
  "name": "Bull Expansion Continues",
  "probability": 0.45,
  "confidence": 0.78,
  "horizon_days": 10,
  "expected_return": "+8.5%",
  "risk_level": 35,
  "key_drivers": ["capital_inflow", "sentiment_momentum"],
  "future_path": [
    {"t+1": "regime:Expansion, emotion:72"},
    {"t+5": "regime:Expansion, emotion:78"},
    {"t+10": "regime:Mania, emotion:85"}
  ],
  "warning_signals": ["emotion_approaching_overheat"],
  "version": "V1.0"
}
```

---

## 6. Counterfactual Reasoning

### 6.1 Core Question

**"如果我当时做了不同的选择，结果会怎样？"**

[Source: `AQFT_Counterfactual_Intelligence_Engine_Design_V3.0.0`]

### 6.2 Mathematical Expression

```
P(W' | do(A'), W, E)

Where:
  W  = Actual world
  A  = Actual action taken
  A' = Alternative action
  W' = Counterfactual world
  E  = Environment conditions
```

### 6.3 Counterfactual Types

| Type | Example |
|------|---------|
| Portfolio | "如果当天我持仓了龙头而非跟风?" |
| Strategy | "如果这一天我用了趋势策略而非情绪策略?" |
| Risk | "如果我将仓位从50%降到30%?" |
| Timing | "如果我早一天/晚一天卖出?" |
| Parameter | "如果止损设为-5%而非-3%?" |

### 6.4 Counterfactual Loop

```
[1] Actual Trade Outcome recorded
        ↓
[2] Counterfactual question triggered
        ↓
[3] Alternative world W' constructed
        ↓
[4] Different action A' simulated in W'
        ↓
[5] Counterfactual outcome compared to actual
        ↓
[6] Learning: Was my decision near-optimal?
        ↓
[7] Experience stored in Simulation Memory
```

---

## 7. Market Path Simulation

### 7.1 Path Generation

Given S(t), B(t), R(t), generate N future paths:

```
Path_i = [S(t+1), S(t+2), ..., S(t+H)]

Where:
  H = horizon (1-20 days)
  S(t+k) sampled from P(S_{t+k} | S_{t+k-1}, R, B)
```

### 7.2 Path Types

| Type | Description | Generated By |
|------|-------------|-------------|
| Base Case | Regime continues, moderate volatility | Dynamics model |
| Bull Case | Trend strengthens, emotion rises | Dynamics + drift |
| Bear Case | Reversal, risk spikes | Dynamics - drift |
| Tail Case | Extreme event, regime shift | Historical replay |

### 7.3 Probability Assignment

```
P(Scenario_i) = f(
  regime_consistency,      # Does this path fit current regime?
  historical_frequency,    # How often did similar paths occur?
  current_momentum,        # Is there directional momentum?
  risk_indicators           # Are risk signals elevated?
)
```

**[NEEDS ARCHITECT REVIEW]** — Probability calibration method.

---

## 8. Risk Scenario Simulation

### 8.1 Extreme Scenario Generation

[Source: `AQFT_Scenario_Simulation_Engine_Design_V3.0.0` + A-share historical events]

| Scenario | Historical Reference | Key Feature |
|----------|---------------------|-------------|
| 流动性枯竭 | 2015 股灾 | Limit-down cascade, no buyers |
| 黑天鹅 | 2020 COVID | Gap down, panic selling |
| 政策冲击 | 2021 教育双减 | Sector collapse |
| 情绪崩溃 | 涨停→天地板 | Sentiment rapid reversal |
| 系统性风险 | 2018 去杠杆 | Broad market decline |

### 8.2 Risk Scenario Output

```json
{
  "risk_scenario": "Liquidity Dry-Up",
  "probability": 0.05,
  "severity": "Extreme",
  "estimated_drawdown": "-25%",
  "position_impact": "Most positions locked at limit-down",
  "recommended_action": "Pre-emptive position reduction"
}
```

**[NEEDS ARCHITECT REVIEW]** — Risk scenario triggering thresholds.

---

## 9. Bull / Bear / Extreme Scenario

### 9.1 Regime-Scenario Mapping

| Current Regime | Base Scenario | Bull Scenario | Bear Scenario | Extreme |
|---------------|---------------|---------------|---------------|---------|
| Expansion | Continue | Accelerate to Mania | Revert to Neutral | Policy shock |
| Mania | Peak then cool | Extend (rare) | Crash to Panic | Black swan |
| Panic | Stabilize | V-recovery | Deepen | Systemic |
| Neutral | Range-bound | Breakout up | Breakout down | External shock |
| Recovery | Gradual repair | Accelerate recovery | Double-dip | New crisis |

### 9.2 Simulation Output Format

```
SCENARIO REPORT — 2026-07-27
═══════════════════════════
Current: Expansion Regime, Emotion 72, Risk 25

Scenario 1 (45%): Expansion continues → +8% in 10d
Scenario 2 (25%): Consolidation → +2% in 10d
Scenario 3 (15%): Policy tightening → -5% in 10d
Scenario 4 (10%): External shock → -12% in 10d
Scenario 5 (5%): Black swan → -25% in 10d

Recommended: Position for Scenario 1, hedge against Scenario 4-5
```

---

## 10. Simulation Memory Relationship

### 10.1 Memory Integration

[Source: `AQFT_Simulation_Memory_Design_V3.0.0`]

```
Simulation Run → Result → Store in Memory → Future Retrieval
                                              ↓
                              "Similar situation in the past..."
```

### 10.2 What Gets Stored

| Item | Purpose |
|------|---------|
| Scenario generated | What was simulated? |
| Initial conditions | S(t), B(t), R(t) at simulation time |
| Predicted outcome | What did the simulation predict? |
| Actual outcome | What actually happened at t+H? |
| Accuracy score | Prediction-vs-actual delta |

### 10.3 Memory Retrieval

```
Query: "Current market looks like X. Has the model seen this before?"

Memory → Similar initial conditions found → Past scenario accuracy → Adjust current scenario confidence
```

**[NEEDS ARCHITECT REVIEW]** — Memory embedding dimensions and similarity threshold.

---

## 11. Decision Intelligence Interface

### 11.1 What Simulation Provides to Decision

```
Simulation Output → Decision Intelligence

Provides:
  [1] Multi-scenario probability distribution
  [2] Risk/reward range per scenario
  [3] Counterfactual insights from similar past situations
  [4] Extreme risk warnings
```

### 11.2 Decision Formula Integration

```
U(A) = Σ P(Scenario_i) × Utility(A, Scenario_i)

Where Utility(A, Scenario_i):
  = Expected_Return - Risk_Penalty + Knowledge_Gain - Uncertainty_Cost
```

[Source: `AQFT_AGI_Decision_Architecture_Design_V3.0.0`]

### 11.3 API

```python
def generate_scenarios(
    market_state: MarketStateVector,
    belief_state: BeliefState,
    regime: RegimeState,
    horizon_days: int = 10,
    num_scenarios: int = 5
) -> ScenarioReport

def run_counterfactual(
    actual_action: Action,
    alternative_action: Action,
    world_state: MarketWorldState
) -> CounterfactualResult

def get_simulation_history(
    from_date: datetime,
    to_date: datetime
) -> List[SimulationRecord]
```

---

## 12. Data Requirement

### 12.1 Simulation Input Data

| Data | Source | Frequency |
|------|--------|-----------|
| Market State S(t) | 02_State_Model | 5 min |
| Belief State B(t) | 03_Belief_Model | 5 min |
| Regime R(t) | 04_Regime_Model | Daily |
| Historical regime paths | Regime Store | — |
| Historical scenarios | Simulation Memory | — |

### 12.2 Minimum Data for Operation

- Last 3 years of daily market data
- Last 1 year of 5-min data
- 50+ historical regime transition records
- 100+ stored simulation-vs-actual accuracy records

---

## 13. Engineering Requirement

### 13.1 Implementation Constraints

| Constraint | Value |
|------------|-------|
| Scenario generation time | < 5 seconds for 10 scenarios |
| Counterfactual computation | < 10 seconds |
| Max scenarios per run | 20 |
| Monte Carlo paths | ≤ 1,000 |
| Storage per simulation | < 10KB |
| CPU-friendly | Yes (no GPU required) |

### 13.2 Code Structure

```
world_model/simulation/
├── scenario_generator.py      # Multi-path generation
├── dynamics_simulator.py      # State transition simulation
├── counterfactual_engine.py   # "What if" reasoning
├── probability_calibrator.py  # Scenario probability estimation
├── risk_scenario_gen.py       # Extreme scenario generation
├── simulation_memory.py       # Store + retrieve
├── scenario_reporter.py       # Formatted output
└── __init__.py
```

---

## 14. Testing Requirement

### 14.1 Unit Tests

- Scenario generation: N scenarios → all have valid paths
- Counterfactual: Different action → different outcome
- Probability sum: ΣP(scenario_i) ≈ 1.0
- Path consistency: S(t+k) derived from valid state transitions

### 14.2 Back-Testing

- Generate scenarios at historical time T
- Compare scenario predictions vs actual outcome at T+H
- Track: what % of actual outcomes fell within predicted scenario range?

### 14.3 Stress Testing

- Generate scenarios during known crisis periods (2015, 2020)
- Check: did the simulation include the actual outcome as a possible scenario?
- Extreme regime transitions: Mania→Panic correctly simulated?

---

## 15. Freeze Criteria

1. **Architecture Review Passed** — Correctly positioned at L3-L5 of World Model
2. **Scenario generation complete** — 3 methods defined, pipeline specified
3. **Counterfactual reasoning specified** — 5 types, loop defined
4. **Decision interface clear** — What simulation provides, how Decision uses it
5. **Engineering ready** — Code structure, constraints, data requirements specified
6. **No trading automation** — Simulation supports decisions, does not make them
7. **Personal workstation scale** — ≤1,000 Monte Carlo paths, ≤20 scenarios
8. **A-share risk scenarios** — 5 extreme scenario types defined

---

## Source References

| Section | Primary Source |
|---------|---------------|
| 1-5 | `AQFT_Scenario_Simulation_Engine_Design_V3.0.0` Ch.1-4 |
| 6 | `AQFT_Counterfactual_Intelligence_Engine_Design_V3.0.0` Ch.1-3 |
| 7-8 | `AQFT_Scenario_Simulation_Engine_Design_V3.0.0` Ch.4-5 |
| 9 | Derived from Regime Model V1.0 + Scenario Engine |
| 10 | `AQFT_Simulation_Memory_Design_V3.0.0` |
| 11 | `AQFT_AGI_Decision_Architecture_Design_V3.0.0` |
| 12-15 | Inferred from Blueprint principles + V2.9 Design Principles |

---

## Items Requiring Architect Review

| # | Item | Section |
|---|------|---------|
| 1 | Generative scenario method (ML-based generation) — confirm for V2.9? | §5 |
| 2 | Probability calibration method | §7 |
| 3 | Risk scenario triggering thresholds | §8 |
| 4 | Memory embedding dimensions + similarity threshold | §10 |

---

*AQF-T Scenario Simulation Design V1.0 — ENGINEERING DRAFT*  
*Source: 3 Blueprint documents from 24_World_Model_System/*  
*No original design added. All content traceable to V3.0.0 Blueprint.*
