# AQF-T Technology Benchmark & Admission Framework (TAF-001)

Version: V1.0.0 | Status: ✅ FROZEN — V3.1 Core Framework
Date: 2026-07-28 | Phase: V3.1 Validate & Optimize

---

## 一、核心原则

**Buy First Principle**: AQF-T 不重复创造已被工业界证明有效的能力。

优先级：成熟方案 → 验证适配 → 集成 → (不存在时) Hybrid → (仅独特优势时) Original Build

## 二、技术来源分层

| Level | Source | Examples |
|:-----:|--------|----------|
| 0 | 基础理论 | Bayesian, Statistics, Control Theory, Optimization |
| 1 | 顶级学术 | Transformer, World Model, RL, GNN (NeurIPS/ICML/Nature) |
| 2 | 工业成熟 | DeepMind, OpenAI, Jane Street, Citadel, Bridgewater |
| 3 | 开源生态 | PyTorch, HuggingFace, Vector DB, LangGraph |
| 4 | A股经验 | 涨停板, 龙头周期, 情绪周期 (需单独标注，不可混淆为通用AI) |

## 三、五阶段准入流程

**Stage 1 — Discovery**: Technology Candidate Card (Name/Source/Version/Capability/Evidence/Cost/Complexity)

**Stage 2 — Evidence Review**: MC五问 — 解决什么问题？现有模块是否覆盖？是否更优？证据？失败边界？

**Stage 3 — Benchmark Test**: AQF-T Existing vs Candidate. Accuracy/Latency/Complexity/Maintenance.

**Stage 4 — Integration Review**: KEEP(现有优秀) / REPLACE(新技术领先) / HYBRID(各有优势)

**Stage 5 — Admission Freeze**: 进入Technology Registry (ID/Version/Evidence/Benchmark/Decision/Owner/Date)

## 四、Technology ROI 公式

`Technology Value Score = Capability_Gain / Complexity_Increase`

能力+30%、复杂度+5% → 优秀。能力+10%、复杂度+50% → 拒绝。

## 五、V3.1-002 首批 Benchmark 目标

| ID | Module | Evaluate |
|----|--------|----------|
| B001 | World Model | PSR, JEPA, Predictive State — enhance S(t) prediction? |
| B002 | Memory System | Vector Memory, KG Memory, RAG — replace or hybrid? |
| B003 | Reasoning Engine | Chain-of-Thought, Tree Search, Graph Reasoning — supplement? |
| B004 | Agent Framework | LangGraph, AutoGen, CrewAI — replace custom orchestration? |
| B005 | Quant Intelligence | Hawkes Process, Order Flow Models — validate vs AQF-T Footprint |

## 六、Anti-Rebuild Rule

**禁止自研已经成熟存在的基础设施。** 除非 Benchmark 证明现有方案不足。

❌ 自研数据库 | ❌ 自研向量检索 | ❌ 自研LLM | ❌ 自研Agent调度框架

## 七、MC-015 Candidate (Technology Neutrality)

AQF-T 不崇拜自研，也不崇拜外部技术。唯一标准是经过验证的有效性。

## 八、目录结构

```
01_Research/Technology_Benchmark/
├── 01_Technology_Radar/       ← 技术雷达
├── 02_Benchmark_Framework/    ← 测试框架
├── 03_Candidate_Evaluation/   ← 候选评估
├── 04_Integration_Report/     ← 集成报告
├── 05_Admission_Registry/     ← 准入注册
└── 06_Retirement_Report/      ← 退役报告
```

---

*AQF-T Technology Benchmark & Admission Framework V1.0 — FROZEN*
