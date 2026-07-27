# AQF-T Memory Cold Start Strategy

Version: V1.0.0 | Status: ARCHITECT REVIEW PASSED — Phase 1 Cold Start Complete
Phase: V3.0 Phase 1 | Module: Memory System — Cold Start
Created: 2026-07-28

---

## Document Control

| Item | Value |
|------|-------|
| Document Name | AQFT_Memory_Cold_Start_Strategy_V1.0.md |
| Module | Memory System — Cold Start Controller |
| Parent | AQFT_Memory_System_Architecture_V2.9.2 |
| Upstream | Decision Intelligence, World Model |
| Constitutions | C-001, C-002, C-009(candidate) |
| Status | ENGINEERING DRAFT |

---

## 1. Purpose

当 AQF-T 没有个人经验时（Memory=Empty, Pattern=Empty, Knowledge=Empty），定义安全决策行为。

```
问题: Day 1 AQF-T → 零经验 → 如何交易？
答案: Cold Start Mode → 保守智能 → 经验积累 → 逐步激活
```

---

## 2. Cold Start State Machine

```
INIT ──→ COLD_START ──→ LEARNING ──→ MATURE
 0 ep      0-30 ep      30-100 ep     ≥100 ep
```

| State | Episodes | Pattern | Decision Weight | Risk | Confidence |
|-------|:-------:|:------:|-----------------|:----:|:----------:|
| INIT | 0 | 0 | WM(60%)+Reasoning(40%) | ×0.50 | ×0.75 |
| COLD_START | 0-30 | 0 | WM(55%)+Reasoning(35%)+Exp(10%) | ×0.60 | ×0.80 |
| LEARNING | 30-100 | 1-5 | WM(45%)+Reasoning(30%)+Exp(25%) | ×0.75 | ×0.90 |
| MATURE | ≥100 | ≥5 | WM(35%)+Reasoning(30%)+Exp(35%) | ×1.00 | ×1.00 |

---

## 3. ColdStartState Object

```json
{
  "mode": "COLD_START",
  "episode_count": 12,
  "pattern_count": 0,
  "knowledge_count": 0,
  "experience_weight": 0.10,
  "risk_multiplier": 0.60,
  "confidence_adjustment": 0.80,
  "activated_capabilities": ["World_Model", "Reasoning"],
  "next_activation": { "episodic_at": 100, "pattern_at": 30, "knowledge_at": 100 }
}
```

---

## 4. Memory Retrieval Rules

**Case 1 — Memory Empty**: Return `{ mode: "NO_EXPERIENCE", confidence_adjustment: -20%, knowledge_support: 0 }`. Decision uses Fusion only.

**Case 2 — Weak Experience** (<30 episodes): Return episode references but marked "LOW_CONFIDENCE". Pattern retrieval disabled.

**Case 3 — Mature**: Return relevant Patterns + historical outcomes + confidence.

---

## 5. Activation Thresholds

| Memory Layer | Threshold | Auto-Activate? |
|-------------|:---------:|:--------------:|
| Episodic Memory | Episode ≥ 100 | ✅ |
| Pattern Memory | N ≥ 30, p < 0.05 | ✅ |
| Knowledge Memory | N ≥ 100, Confidence ≥ 0.80, Cross-Regime validated | ⚠️ Human review |

---

## 6. Safety Guards

During Cold Start, **prohibit**:
- Auto-scaling position after consecutive wins (may be random)
- Forming patterns from < 30 samples
- Modifying core rules (C-009)

**ColdStartRiskPenalty**: Position = Normal × risk_multiplier. Confidence = Raw × confidence_adjustment.

---

## 7. Constitution

| Rule | Status |
|------|:------:|
| C-001: Intelligence Ownership | ✅ Cold Start adjusts confidence, not direction |
| C-002: Immutable Core | ✅ Reads state, never writes |
| C-009: Learning ≠ Modification | ✅ Experience activates gradually, never auto-deploys |

---

## Items Requiring Architect Review

| # | Item |
|---|------|
| 1 | Risk multiplier: 0.50/0.60/0.75/1.00 — appropriate? |
| 2 | Activation thresholds: 30/100 — correct for A-share? |
| 3 | C-009 formalization? |

---

*AQF-T Memory Cold Start Strategy V1.0 — ENGINEERING DRAFT*
