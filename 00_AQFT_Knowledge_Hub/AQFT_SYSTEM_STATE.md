# AQF-T System State


# AQF-T 系统状态文件

> 人机共读。AI Agent 可直接解析。

---

## System Identity

- **name**: AQF-T
- **full_name**: Autonomous Quantitative Fusion Trading System
- **version**: V1.2 Production Runtime
- **git_branch**: design
- **last_updated**: 2026-07-31 (DEC-027 ExitPipeline Frozen)

---

## Architecture Status

- **phase**: V1.2 CLOSED — Real Market Evidence Pending
- **status**: code_frozen — 等待QMT环境
- **p0-p4**: frozen
- **p5**: frozen (V3.0.0 Architecture Design)
- **production**: runtime_hardened + evidence_validated

---

## Current Focus

- **module**: AQF-T_Production
- **version**: V1.2
- **task**: Phase 2.4 — QMT Real Market Validation (等待环境)
- **priority**: high (blocked by QMT)

---

## Phase Progress

| phase | name | progress | status |
|-------|------|----------|--------|
| P0 | Architecture | 5/5 | frozen |
| P1 | Core Design | 7/7 | frozen |
| P2 | Engineering | 6/6 | frozen |
| P3 | Running System | 8/8 | frozen |
| P4 | Continuous Evolution | 6/6 | frozen |
| P5 | Autonomous Intelligence | 5/5 | frozen |
| V1.0 | Pipeline Integration | 9/9 tests | complete |
| V1.1 | Runtime Hardening Phase 1 | 6/6 items | complete |
| V1.2 | Production Runtime | 7/7 modules | complete |
| P1 | Pattern补全 4→6 | 6/6 validated | complete |
| — | Evidence Package V1 | 6 funnels | complete |
| — | Dashboard V1.3 | 10 modules | complete |

---

## Module Summary

- **total_modules**: 30+ (core) + 7 (runtime) + 2 (patterns) + 1 (dashboard)
- **frozen**: all
- **patterns**: 卡位博弈 / 龙头8维 / 梯队完整性 / 情绪周期 / 板块轮动 / 相对强度
- **pipeline**: Regime→Perception→PathA/B→Decision→Risk→Execution→KnowledgeHub
- **runtime**: Supervisor / Recovery / PositionReconciler / KillSwitch / Idempotency / ConfigValidator / Logger
- **dashboard**: 系统状态 / 今日交易 / 持仓 / 成交明细 / 风控热力 / 7日Regime / Pattern排序 / 收益摘要
- **evidence**: 30D SIM + 60D Long + Package V1 + Stability/Contribution/Fingerprint

---

## Frozen Versions

- v2.8.6 (Constitution Freeze)
- v2.8.6-FINAL (Architecture Freeze)
- v2.8.6-design-complete (P0-P5 Design Asset Freeze)
- V1.2 (Production Runtime Freeze)

---

## Active Tasks

1. Phase 2.4 — QMT Real Market Validation (BLOCKED — 等待QMT环境)
2. Dashboard 实时价格接入 (待QMT)
3. Paper→Live migration

---

## Recent Decisions

- 2026-07-31: DEC-027 — Evidence Package V1 FROZEN
- 2026-07-30: DEC-026 — Phase 2.2 Long Evidence 60D PASS
- 2026-07-30: DEC-025 — V1.2 Runtime Layer verified, ARCHITECTURE_NOTE aligned
- 2026-07-30: DEC-024 — QMT Role Redefinition: Execution Adapter → Execution Agent
- 2026-07-30: DEC-023 — Phase 2.1-A CLOSED, Evidence Infrastructure Frozen
- 2026-07-30: DEC-016 — Runtime Hardening Phase 1 complete
- 2026-07-26: DEC-001 — Knowledge Hub 建立

---

## Key Files

- 宪法: 02_Constitution/AQF-T_System_Constitution/AQFT_System_Constitution_V2.8.6_FINAL.md
- 决策日志: 00_AQFT_Knowledge_Hub/AQFT_DECISION_LOG.md
- 根入口: AQFT_ROOT.md
- 系统全景: 00_AQFT_Knowledge_Hub/SYSTEM_MAP.md
- 架构笔记: AQF-T_Production/runtime/ARCHITECTURE_NOTE.md
- Dashboard: AQF-T_Production/dashboard.py
- Evidence: AQF-T_Production/evidence/PHASE2_EVIDENCE_PACKAGE_V1.json

---

*此文件由 AQF-T 知识治理层维护。模块变更时同步更新。*
