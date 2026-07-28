# AQF-T MC-021: Metrics Drive Evolution（指标驱动进化）

Version: V1.0.0 | Status: ✅ FROZEN — Meta Constitution
Date: 2026-07-28 | Source: Architect Final Assessment

---

## Core Definition

**任何模块的优化、保留、替换或删除，都必须基于可量化指标，而不是主观感觉。**

---

## Four Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | Every core module owns a Health Score | World Model→Accuracy, Decision→Calibration, Execution→Fill Rate, Memory→Recall |
| 2 | Optimize by metrics, not opinions | 指标驱动，非观点驱动 |
| 3 | Regression is mandatory before release | 发布前必须通过回归验证 |
| 4 | Production metrics override design assumptions | 生产数据高于设计假设 |

---

## Module Health Examples

| Module | Health Metrics |
|--------|---------------|
| World Model | Accuracy, Calibration, Latency, Coverage, Failure Rate |
| Decision | Decision Quality, Confidence Calibration, Explainability |
| Execution | Fill Rate, Slippage, Cancel Rate, Recovery Time |
| Memory | Recall, Transfer, Compression, Knowledge Gain, Duplicate Rate |

---

## Reality → Metrics → Validation → Knowledge → Evolution

Not: Idea → Discussion → New Design

---

## Pair with MC-016

MC-016: Reality Over Architecture（现实高于架构）
MC-021: Metrics Drive Evolution（指标驱动进化）

Architecture Score retired. Health Score begins.

---

*AQF-T MC-021 Metrics Drive Evolution — Meta Constitution. FROZEN.*
