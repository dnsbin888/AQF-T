# AQF-T V3.1-001 Architecture Audit & Capability Optimization

Version: V1.0.0 | Status: ✅ FROZEN — V3.1 Task Card
Date: 2026-07-28 | Phase: V3.1 Validation & Scientific Engineering

---

## 一、核心原则

**Validate Before Expand。不是增加系统能力，而是回答：当前每一个模块是否值得存在？**

**Evidence Before Expansion**: 禁止"发现新技术→马上增加模块"。必须经过完整评估→老板审批→引入。

## 二、TAF-001 技术引入五阶段

| Stage | Name | Key Question |
|:-----:|------|-------------|
| 1 | Technology Identification | 这个技术是什么？ |
| 2 | Evidence Evaluation | 证据等级？(A+~D per MC-001) |
| 3 | AQF-T Compatibility | 是否增强AQF-T？是否破坏S→B→R→Ω？ |
| 4 | Build vs Buy Analysis | Buy First → Hybrid → Build Only When Unique |
| 5 | Final ROI Decision | Capability Gain / Complexity Cost |

五种结果: KEEP / REPLACE / MERGE / SIMPLIFY / REMOVE

## 三、V3.0 全模块审计矩阵

| 模块 | 价值 | 复杂度 | 建议 |
|------|:----:|:-----:|:----:|
| World Model | ★★★★★ | ★★★ | KEEP |
| Belief Engine | ★★★★★ | ★★ | KEEP |
| Experience Memory | ★★★★★ | ★★★ | KEEP |
| Reflection Engine | ★★★★★ | ★★ | KEEP |
| LimitUp Intelligence | ★★★★ | ★★ | KEEP |
| Opponent Model | ★★★★ | ★★★ | KEEP |
| Quant Footprint | ★★★★ | ★★★ | 验证 |
| Hypothesis Arbitration | ★★★★ | ★★ | KEEP |
| Pattern Extractor | ★★★★ | ★★ | Benchmark vs RAG |

## 四、重点审查：原创 vs 成熟方案

**Pattern→Knowledge**: Benchmark vs Vector Retrieval / RAG / Knowledge Graph / Embedding Search。原创更好→保留。成熟方案更好→替代。

**成熟技术引入方向**: 时间序列(TFT/TimesNet)辅助Forecast | 知识管理(Graph/Vector DB)增强Memory | 回测(VectorBT/Backtrader)不重复造 | ML Pipeline(MLflow/DVC)工程化

## 五、Evidence Library 结构

```
01_Research/
├── Papers | Industry | Books | OpenSource | Benchmark
├── Empirical | Original | Validation | Retirement
```

每个模块绑定 Evidence ID (R-XXX)。

## 六、Complexity Budget

任何新增模块必须回答：Capability Gain vs Complexity Cost。CPU/Memory/Code/Maintenance/Cognitive Budget全部计入。

## 七、V3.1 六大任务

V3.1-001 Architecture Audit → V3.1-002 Technology Radar → V3.1-003 Benchmark Framework → V3.1-004 Memory Optimization → V3.1-005 Model Calibration → V3.1-006 Engineering Readiness

## 八、模块删除审批链

Audit Report → Technical Review → Cost Benefit Analysis → Architect Recommendation → **Boss Final Approval** → Retirement Record

REMOVE 是最后结果，不是第一选择。

## 九、V3.1 最终目标

不是让AQF-T更大。而是让AQF-T更像一个真正的小型私募系统。**少而精、可信、可验证、可维护、可进化。**

---

*AQF-T V3.1-001 Architecture Audit Task Card V1.0 — FROZEN*
