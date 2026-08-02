# AQF-T AI Onboarding Guide

> 新 AI 对话启动时，阅读此文即可完整理解 AQF-T 项目。

Version: V1.0.0
Date: 2026-07-27
Purpose: New AI session onboarding

---

## 一、AQF-T 是什么

**AQF-T** (Adaptive Quantitative Fusion Trading System)

**中文名：** 自适应量化融合交易系统

**终极目标：** 从架构设计演进为 Financial Intelligence Operating System（金融智能操作系统）。

一句话：**用 AI 驱动的自主进化智能体，完成 A 股量化交易的全闭环。**

核心闭环：

```
Market Data → Feature → AI → Signal → Risk Decision → Order → Execution → Feedback → Learning → Evolve
```

---

## 二、我们已经走了多远

### Era 1: Architecture Era — V2.8.6 (FROZEN ✅)

完成了从零到完整架构蓝图。这是一个**架构深度**远超普通 trading bot 的系统：

| Phase | 内容 | 模块数 | 状态 |
|-------|------|--------|------|
| P0 | Foundation — 知识管理、项目管理 | 2 | ✅ Frozen |
| P1 | Architecture — 系统架构、数据流、模块架构、部署、宪法 | 5 | ✅ Frozen |
| P2 | Core — AI Brain、策略、风控、执行、数据、参数、测试 | 7 | ✅ Frozen |
| P3 | Engineering — 工程标准、AI实现、数据工程、代码框架 | 4 | ✅ Frozen |
| P4 | Runtime — 8个运行时系统 + 仿真 + 生产 + 进化 | 9 | ✅ Frozen |
| P5 | Intelligence Blueprint — Agent、World Model、Decision、Cross-Market、Human-AI | 5 | ✅ Blueprint |

**总计：33 模块，59 份 FINAL 文档，冻结于 `v2.8.6-architecture-freeze`。**

### Era 2: Intelligence Era — V2.9.x (CURRENT 🔄)

当前正在执行的阶段。目标：**将 P5 的 Blueprint 深化到可工程实现的 Engineering Specification。**

| 版本 | 焦点 | 优先级 |
|------|------|--------|
| V2.9.0 | World Model Intelligence | 🔴 P0 — 进行中 |
| V2.9.1 | Decision Intelligence | 🔴 P0 |
| V2.9.2 | Memory System | 🟡 P1 |
| V2.9.3 | Reasoning Engine | 🟡 P1 |
| V2.9.4 | Autonomous Runtime | 🟢 P2 |

### Era 3: Autonomous Era — V3.0 (TARGET)

所有 Intelligence Pillar 集成 → 自运行、自优化的 Financial Intelligence OS。

---

## 三、架构深度 —— 这不是一个简单的 Trading Bot

AQF-T 的设计深度体现在以下层面：

### 3.1 系统宪法 (Constitution)

整个系统受 `AQFT_System_Constitution_V2.8.6_FINAL.md` 约束。宪法高于一切模块设计。任何模块不得违反宪法原则。

### 3.2 AI Brain (03_AI_Brain)

不是"调一个 LLM"。

是多模型融合框架：
- LightGBM
- XGBoost
- Deep Learning
- Emotion Model (NLP sentiment)
- L2 Model (order book)

AI Brain 负责将多源信号融合为统一交易决策输入。

### 3.3 World Model (V2.9 重点)

不是"看看 K 线图"。

是完整的世界模型：
- **Market State Space** — 9维市场状态向量 S(t)：价格、成交量、流动性、情绪、资金、风险、微观结构、体制、外部
- **Belief State Engine** — 隐状态推断：观测层 → 推断层 → 置信度 → 状态更新
- **Regime Model** — A股7种市场体制：中性、吸筹、扩张、狂热、派发、恐慌、恢复 + 状态转移逻辑
- **Scenario Simulation** — 未来场景生成 + 概率评估 + 决策接口

### 3.4 Decision Intelligence

不是"if-else 策略"。

是 AGI 级决策架构：
- 多时间尺度决策框架
- 风险感知决策优化
- 策略选择智能
- 决策可解释性

### 3.5 Evolution System

不是"回测调参"。

是完整的自进化闭环：Monitor → Optimize → Learn → Decide → Know → Govern → Evolve

### 3.6 Runtime Architecture

定义了 8 个独立运行时系统：
Data Runtime → AI Runtime → Strategy Runtime → Risk Runtime → Execution Runtime → Simulation System → Production Runtime → Evolution System

---

## 四、双 AI 协作协议

这是 AQF-T 最独特的工程治理创新。

### 角色边界

```
ChatGPT (Chief Architect)  →  设计权 (What)
你 (Project Owner)         →  批准权 (Whether)
Claude Code (Engineering)  →  执行权 (How to repo)
Git                        →  记录权 (Truth)
```

### CC 最高约束

CC **禁止**：架构设计、模块修改、接口修改、优化设计、自行创建模块

CC **允许**：保存文件、创建目录、更新 Index/Status、Git 操作、创建代码框架

CC 不自己理解、解释、扩展设计。所有架构判断以 ChatGPT 为准。

### 工作流程

```
ChatGPT 输出【AQF-T FINAL DESIGN DOCUMENT】+【CC ACTION BLOCK】
        ↓
你确认
        ↓
CC 落盘执行 → 更新 Index → Git commit
        ↓
返回: Saved / Index Updated / Commit ID
        ↓
ChatGPT Architecture Review → Freeze 或 Revision
```

### 文档流转格式

ChatGPT 输出：
```
【AQF-T FINAL DESIGN DOCUMENT】
Document: AQFT_xxx.md
Target Path: 03_xxx/xxx/
[完整 Markdown 内容]
【END OF DOCUMENT】

【CC ACTION BLOCK】
Create file: xxx
Insert above FINAL DESIGN content
Update: Index, Status
Git: commit message: xxx
```

---

## 五、设计原则

### 核心原则

**Optimize for intelligence depth, not document quantity.**

### Six Review Gates (V2.9+)

每个模块设计必须通过 6 道审查：

1. Architecture Review — 与系统架构一致？
2. Dependency Review — 无循环/缺失依赖？
3. Interface Review — 接口契约匹配？
4. Engineering Spec Review — 具体到可编码？
5. Implementation Readiness — 前置条件满足？
6. Freeze Review — 可以冻结？版本已分配？

### 文档完整性标准 (12 项)

每个正式文档必须包含：
Document Control / Purpose / Scope / Architecture Position / Core Design / Module Definition / Data Model / Interface Definition / Dependency / Engineering Requirement / Testing Requirement / Freeze Criteria

**不允许出现"概念好但不能编码"的文档。**

---

## 六、目录与命名规范

### 模块目录标准化 (V2.9+)

```
03_AI_Brain/
└── World_Model/
    ├── 01_Architecture/       ← 主规格文档
    ├── 02_State_Model/        ← 市场状态空间
    ├── 03_Belief_Model/       ← 信念状态引擎
    ├── 04_Regime_Model/       ← 市场体制模型
    ├── 05_Simulation/         ← 场景仿真
    ├── 06_Interface/          ← 接口规范
    └── 99_Archive/            ← 历史版本
```

### 命名格式

```
AQFT_[模块名]_[文档类型]_V[版本号].md
```

示例：`AQFT_Market_State_Space_Design_V1.0.md`

### 版本规则

- Major (V3): 架构级变更
- Minor (V3.1): 模块级变更
- Patch (V3.1.1): 修正

**Freeze = Immutable。修改已冻结文档 → Review → Revision → 新版本号。绝不覆盖。**

---

## 七、Git 策略

```
v2.8.6-architecture-freeze  ← 所有 V2.9+ 开发起点
    │
    ├── v2.9.0-world-model
    ├── v2.9.1-decision
    ├── v2.9.2-memory
    ├── v2.9.3-reasoning
    ├── v2.9.4-runtime
    │
    ▼
v3.0.0
```

当前 HEAD：一系列 V2.9.0 工程基础提交。

---

## 八、当前状态 (2026-07-27)

| 项目 | 值 |
|------|------|
| Stable Baseline | V2.8.6 (FROZEN) |
| Active Phase | V2.9.0 World Model Intelligence Development |
| FINAL 文档 | 59 |
| AWAITING DESIGN | 6 (World Model 子模块，等待 ChatGPT 填充) |
| 总 .md 文件 | 86 |
| Git Commits | 21 |
| Git Tags | 4 |

### 当前焦点

**P5-02 World Model → V2.9.0 深化**

6 个文档框架已创建，等待 ChatGPT 输出 FINAL Design：
1. World Model Intelligence Spec V2.9.0
2. Market State Space Design V1.0
3. Belief State Engine Design V1.0
4. Regime Model Design V1.0
5. Scenario Simulation Design V1.0
6. World Model Interface Spec V1.0

### 下一步（等待 ChatGPT）

1. 输出 `AQFT_Market_State_Space_Design_V1.0.md` FINAL 版本
2. Architecture Review
3. Freeze
4. 继续 V2.9.1 Decision Intelligence

---

## 九、关键文件索引

| 文件 | 作用 |
|------|------|
| `AQFT_ROOT.md` | 系统根入口 |
| `00_Project/AQFT_Document_Index.md` | **唯一文档入口** |
| `00_Project/AQFT_Project_Status.md` | 当前工程状态快照 |
| `00_Project/AQFT_V2.9_Intelligence_Roadmap.md` | V2.9 路线图 |
| `00_Project/AQFT_Development_Spec_V1.0.md` | 双AI协作规范 |
| `00_Project/AQFT_Design_Principles_V2.8.6.md` | 设计原则 + 6 Gates |
| `00_Project/AQFT_Architecture_Map.md` | 架构全景图 |
| `02_Constitution/AQFT_System_Constitution_V2.8.6_FINAL.md` | 系统宪法 |
| `02_Constitution/AQFT_CC_Execution_Constraint_V1.0.md` | CC 最高约束 |
| `10_Engineering/AQFT_Document_Completeness_Standard_V1.0.md` | 文档完整性标准 |
| `VERSION.md` | 版本文件 |
| `AQFT_V3.0.0_RELEASE_MANIFEST.md` | V3.0 发布清单 |

---

## 十、给新 CC (Claude Code) 的快速理解

如果你是第一次接入 AQF-T 的 Claude Code：

### 你的角色（V2.0 升级）
**先读**: [CC_ROLE_V2.md](CC_ROLE_V2.md) — 完整角色定义

1. **你是执行者 + 审计官** — 收到 GPT 方案后，先审再等批复，批复后才写代码
2. **你是 GPT 的眼睛** — GPT 无法访问本地文件，你负责读代码/文档并精准反馈
3. **架构设计权归 ChatGPT** — 你不自行设计模块，但可以提出审计问题
4. **不要修改已冻结的文件** — 任何 Frozen 文档不可写
5. **老板拍板** — 审计意见供老板参考，最终决策权归老板

### 工作流
```
GPT 设计 → CC 二次审计 → 老板批复 → CC 写代码 → Git 提交
```

### 审计维度
蓝图对齐 | 安全可靠 | 进步验证 | 定位适配(游资/私募/个人量化/A股)

---

*AQF-T AI Onboarding Guide V1.1 — 更新于 2026-08-02*
