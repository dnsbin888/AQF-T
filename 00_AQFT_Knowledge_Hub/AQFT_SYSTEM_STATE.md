# AQF-T System State


# AQF-T 系统状态文件

> 人机共读。AI Agent 可直接解析。

---

## System Identity

- **name**: AQF-T
- **full_name**: Autonomous Quantitative Fusion Trading System
- **version**: V2.8.6 → V3.0.0 Bridge
- **git_tag**: v2.8.6-design-complete
- **last_updated**: 2026-07-26

---

## Architecture Status

- **phase**: V1.1 Runtime Hardening Phase 1 — COMPLETE
- **status**: hardened
- **p0-p4**: frozen
- **p5**: frozen (V3.0.0 Architecture Design)
- **production**: runtime_hardened (ClockProvider / Portfolio Exposure / MarketDataProvider / Report)

---

## Current Focus

- **module**: AQF-T_Production
- **version**: V1.1
- **task**: Phase 2 — Real Market Evidence (30-60交易日Replay)
- **priority**: high

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

---

## Module Summary

- **total_modules**: 30
- **frozen**: 30
- **active**: 0 (待 Phase 2)
- **pipeline**: Regime→Perception→PathA/B→Decision→Risk→Execution→KnowledgeHub
- **hardening**: ClockProvider | Portfolio Exposure 40/25/20 | MarketDataProvider(QMT/Sim/Replay) | Regime Multiplier | Score Version | Event Evidence

---

## Frozen Versions

- v2.8.6 (Constitution Freeze)
- v2.8.6-FINAL (Architecture Freeze)
- v2.8.6-design-complete (P0-P5 Design Asset Freeze)

---

## Active Tasks

1. V1.0 Production Pipeline Integration (COMPLETE 2026-07-30)
2. Runtime hardening (trading hours, QMT connectivity)
3. Paper→Live migration path

---

## Recent Decisions

- 2026-07-30: V1.0 Integration Phase — Pipeline M2-M7 wired, 9/9 tests passing
- 2026-07-26: DEC-015 正式启动 V3.1.0 P6 Runtime Engineering
- 2026-07-26: DEC-004 创建 AQFT_ROOT.md 单一入口
- 2026-07-26: DEC-001 建立 Knowledge Hub

---

## Key Files

- 宪法: 02_Constitution/AQF-T_System_Constitution/AQFT_System_Constitution_V2.8.6_FINAL.md
- 根入口: AQFT_ROOT.md
- 系统全景: 00_AQFT_Knowledge_Hub/SYSTEM_MAP.md
- 模块注册: 00_AQFT_Knowledge_Hub/MODULE_REGISTRY.md
- 决策日志: 00_AQFT_Knowledge_Hub/AQFT_DECISION_LOG.md
- AI上下文: 00_AQFT_Knowledge_Hub/AI_CONTEXT.md

---

*此文件由 AQF-T 知识治理层维护。模块变更时同步更新。*
