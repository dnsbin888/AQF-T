# AQF-T V2.8.6 成果深度总结

> 给新 AI 的完整上下文 — 读完即理解 AQF-T 的设计深度、重点方向与当前状态
> 2026-07-27

---

## 一、AQF-T 本质定位

AQF-T（Adaptive Quantitative Fusion Trading System）**不是交易策略集合，不是回测框架，不是 AI 炒股工具**。

它是一个 **面向 A 股游资/个人量化场景的 Financial Intelligence Operating System（金融智能操作系统）**。

核心哲学：**在复杂、不确定、高噪声市场中，通过数据+模型+策略+风险+执行+反馈，形成持续进化的智能决策闭环。**

---

## 二、V2.8.6 已完成：6 阶段 33 模块全部架构冻结

### P0 — Foundation
- **Knowledge Hub**: 知识治理层，系统地图、模块注册表、AI上下文、版本控制
- **Project Management**: 文档索引、路线图、开发计划

### P1 — Architecture (5 模块)
- **系统总体架构**: 七层架构（数据采集→数据处理→AI Brain→策略→风控→执行→进化）
- **数据流架构**: 端到端数据闭环设计
- **模块架构**: 33 模块依赖关系图
- **部署架构**: 本地单机 → 未来扩展
- **系统宪法**: 17 章，十大核心原则，最高约束文件

### P2 — Core Design (7 模块)
所有核心模块都有详细 Engineering Design：

- **AI Brain (V3.6.0)**: 四引擎架构 — Prediction + Sentiment + Risk Intelligence + Fusion。包含完整 API Schema、训练流程、模型治理、融合算法、动态权重
- **Strategy**: 五类策略（趋势/价值/量价/情绪/防御）+ 准入/评价/淘汰机制
- **Risk Fortress**: 四层风控（市场/资金/策略/系统）+ 最高否决权
- **Execution**: OMS 订单管理 + QMT 接口方向
- **Data**: 四类数据分层（市场/基本面/另类/系统运行）
- **Parameter**: 全局参数治理
- **Test**: 测试体系

### P3 — Engineering (4 模块)
- **Software Engineering Standard**: 工程规范
- **AI Implementation**: AI 工程化（模型部署、推理服务）
- **Data Engineering**: 数据工程实现
- **Code Framework**: Python 代码框架设计

### P4 — Runtime & Evolution (9 模块)
- **8 个独立运行时**: Data → AI → Strategy → Risk → Execution → Simulation → Production → Evolution
- **Evolution System (6 子模块)**: Monitoring Intelligence → Auto Optimization → Self Learning → Autonomous Decision Evolution → Knowledge Evolution → Self Governance

### P5 — Autonomous Intelligence Blueprint (5 模块)
- **Agent Intelligence System**: 多智能体交易系统
- **World Model System (7 文档)**: 世界模型架构 + 市场仿真 + 环境模型 + 场景仿真 + 反事实推理 + 仿真记忆
- **Decision Intelligence**: AGI 决策架构
- **Cross-Market Intelligence**: 跨市场智能
- **Human-AI Collaboration**: 人机协同治理

---

## 三、设计深度亮点（不是"概念好但不能编码"）

### 3.1 系统宪法 — 不是摆设

17 章宪法包含：
- **十大核心原则**: 安全第一、数据优先、模型融合、解释透明、动态适应、纪律执行、持续验证、历史尊重、人机协同、持续进化
- **三级冲突优先级**: 系统安全 > 风险控制 > 长期收益
- **模型投票机制**: 禁止单模型决策
- **信号置信度三级**: 高（正常执行）→ 中（降仓位）→ 低（禁止执行）
- **极端情况自动降级**: 降频→降仓位→暂停策略→安全模式
- **模型生命周期**: 进入→监控→退出，完整治理

### 3.2 AI Brain — 不是"调一个 LLM"

四个专业引擎 + 完整 Engineering Spec：

| 引擎 | 做什么 | 深度 |
|------|--------|------|
| Prediction Engine | 趋势+方向+概率 | LightGBM/XGBoost/Transformer，训练流程到推理 API |
| Sentiment Engine | 情绪+题材+参与者 | **游资核心**: 涨停梯队、炸板率、连板高度、情绪四阶段、量化公式 |
| Risk Intelligence | AI 视角风险预警 | 包含涨停股炸板风险、连板风险 |
| Fusion Engine | 四引擎融合 | 加权融合+动态权重按 Regime 调整（Bull/Bear/HighVol） |

具体到：
- 完整 Input/Output Schema
- REST API 端点定义
- 模型训练流程（Train/Val/Test 7:1.5:1.5）
- 上线标准（AUC>0.65, IC>0.05, Sharpe>1.0）
- 情绪值量化公式：`情绪值 = 涨停家数×2 - 跌停家数×3 + 连板高度×5 + 北向×10`

### 3.3 情绪周期模型 — A股游资特化

```
冰点期 → 回暖期 → 高潮期 → 退潮期 → 冰点期
(试错首板) (接力二板) (龙头锁仓) (空仓/轻仓)

情绪值量化:
  < 20:  冰点期  → 仓位 1-2 成
  20-50: 回暖期  → 加仓主线
  50-80: 高潮期  → 仓位 7 成
  > 80:  过热    → 警惕退潮
```

### 3.4 Evolution System — 不是"回测调参"

完整的自进化六环：
```
Monitor → Optimize → Learn → Decide → Know → Govern → Evolve
```

每个环都有独立设计文档。

### 3.5 Feature Engineering — 100 个 A 股因子

已有完整因子工程规范，100 个 A 股特征因子含公式定义。

### 3.6 Database Schema + API Spec

已有代码级工程规范：数据库表结构 + REST API 端点定义。

---

## 四、当前重点：V2.9 Intelligence Era

V2.8.6 Architecture Freeze 之后，路线已明确：

```
V2.8.6 (Architecture Era — 已冻结)
    ↓
V2.9.0 → World Model Intelligence      ← 🔴 当前正在做
V2.9.1 → Decision Intelligence
V2.9.2 → Memory System
V2.9.3 → Reasoning Engine
V2.9.4 → Autonomous Runtime
    ↓
V3.0   (Financial Intelligence OS)
```

**目标不是增加文档数量，而是把 P5 从 Blueprint 深化到可编码级别。**

---

## 五、工程治理 — 双 AI 协作

这是 AQF-T 的独特组织方式：

| 角色 | 职责 | 权限 |
|------|------|------|
| ChatGPT | Chief Architect | 设计权 — 唯一架构来源 |
| 你 | Project Owner | 批准权 |
| Claude Code | Engineering Executor | 执行权 — 保存/目录/Index/Git |
| Git | Source of Truth | 记录权 |

**CC 最高约束**: 禁止架构设计、模块修改、接口修改、优化设计。只执行。

**工作流**: ChatGPT FINAL Design → 你确认 → CC 落盘 → Git commit → ChatGPT Review → Freeze

---

## 六、设计质量标准 (V2.9+)

每个正式文档需满足 12 项完整性标准：
Document Control / Purpose / Scope / Architecture Position / Core Design / Module Definition / Data Model / Interface Definition / Dependency / Engineering Requirement / Testing Requirement / Freeze Criteria

**核心原则: Optimize for intelligence depth, not document quantity.**

---

## 七、当前工程数字

| 指标 | 值 |
|------|------|
| FINAL 文档 | 60 |
| 总 .md 文件 | 86 |
| 模块数 | 33 |
| Git Commits | 22 |
| Git Tags | 4 (含 v2.8.6-architecture-freeze) |
| 当前活跃 | V2.9.0 World Model |

---

## 八、下一步（ChatGPT 负责）

1. 输出 `AQFT_Market_State_Space_Design_V1.0.md` FINAL 完整设计
2. Architecture Review — 检查与 Constitution、AI Brain、Decision 的一致性
3. Freeze → 继续 V2.9.1

---

*给新 AI 的核心信息: AQF-T 不是 trading bot。它是一个正在从架构蓝图走向 Financial Intelligence OS 的大型工程。你的角色是 Chief Architect — 继续深化 V2.9 的 5 个 Intelligence Pillar，每个模块输出完整的 FINAL Design。CC 负责落盘。*
