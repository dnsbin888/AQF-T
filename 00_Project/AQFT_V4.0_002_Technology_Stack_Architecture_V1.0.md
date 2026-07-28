# AQF-T V4.0 Technology Stack & Integration Architecture

Version: V1.0.0 | Status: ENGINEERING DRAFT — Awaiting Architect Review
Phase: V4.0 Engineering | Date: 2026-07-28

---

## 一、目标

将 17 Core MVP 映射到真实可运行软件系统。回答：AQF-T 这台机器用什么零件制造？

## 二、Technology Stack Decision (Buy/Build/Adapt)

| Layer | Technology | Decision | Evidence |
|-------|-----------|:--------:|:------:|
| Language | Python 3.10+ | **BUY** | A+ Industry Standard |
| Time-Series DB | TimescaleDB / InfluxDB | **BUY** | A |
| Structured DB | PostgreSQL | **BUY** | A+ |
| Vector Memory | FAISS / Chroma | **BUY** | A |
| Agent Runtime | LangGraph | **BUY** | B |
| ML Framework | PyTorch / Scikit-learn / XGBoost | **BUY** | A+ |
| Calibration | Platt + Bayesian + Isotonic | **BUY** | A |
| World Model Schema | AQF-T Original | **BUILD** | D — Core Cognitive Model |
| Decision Context | AQF-T Original | **BUILD** | D — Final Trading Judgment |
| Failure Memory | AQF-T Original | **BUILD** | D — Long-term Alpha |
| A-Share Combat Knowledge | AQF-T Original | **BUILD** | D/C — Cannot Buy |
| Constitution Governance | AQF-T Original | **BUILD** | D — System Soul |

## 三、Modular Monolith Architecture

```
aqft_core/
├── world_model/    (State + Belief + Regime + Clock + LimitUp)
├── decision/       (Fusion + Action + Strategy + Portfolio + Position + Arbitration)
├── execution/      (Order Planner + QMT Adapter)
├── memory/         (Experience + Reflection + Failure + Cold Start)
└── shared/         (database + model_service + api)
```

Not microservices. Personal maintenance optimal.

## 四、First Deployment

Single workstation: 8-16 Core CPU, 32-64GB RAM, GPU optional. PostgreSQL + TimescaleDB + FAISS/Chroma. **No Kubernetes. No cloud cluster.**

## 五、Build Order (V4.0 Alpha)

Phase 1: Data Layer → Phase 2: World Model → Phase 3: Decision Core → Phase 4: Execution → Phase 5: Learning Loop

## 六、MC-018 Candidate: Complexity Budget

Any technology introduction must prove Capability_Gain > Complexity_Cost. Otherwise REJECT.

## 七、Deliverables

```
00_Project/ AQFT_V4.0_002_Technology_Stack_Architecture_V1.0.md (this document)
03_Engineering/ Technology_Selection/ | 04_Integration/
```

---

*AQF-T V4.0-002 Technology Stack & Integration Architecture V1.0 — ENGINEERING DRAFT*
