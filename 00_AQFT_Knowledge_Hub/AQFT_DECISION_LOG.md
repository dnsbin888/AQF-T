# AQF-T Decision Log


# AQF-T 架构决策日志

> 记录每一个关键设计决策的原因、背景和影响。未来 AI/人回溯时可理解"为什么当时这样做"。

---

## DEC-20260726-001

- **date**: 2026-07-26
- **decision**: 建立 00_AQFT_Knowledge_Hub 知识治理层
- **context**: 系统已有 30 个模块、40+ 文档，但缺少统一导航入口。每次访问需要手动查找路径
- **options**:
  - A: 保持现状，手动管理
  - B: 建立集中式知识索引
  - C: 引入外部 Wiki/Documentation 系统
- **chosen**: B
- **reason**: 保持与代码同仓库的单一事实源，不引入外部依赖，AI 和人类均可直接访问
- **impact**: 所有模块进入统一导航体系；后续新增模块必须在此注册

---

## DEC-20260726-002

- **date**: 2026-07-26
- **decision**: Git 资产冻结 v2.8.6-design-complete
- **context**: P0-P5 设计阶段产生 41 个文件、17000+ 行文档，全部处于 `git status ??` 未追踪状态
- **options**:
  - A: 继续不提交，等代码完成后一起提交
  - B: 立即全部提交并打 tag
- **chosen**: B
- **reason**: 设计资产是系统的核心 IP，磁盘故障或误操作将导致不可恢复的损失。版本保护优先级高于代码完成度
- **impact**: 建立 Architecture Freeze Point；未来任何变更可追溯至此基线

---

## DEC-20260726-003

- **date**: 2026-07-26
- **decision**: 消除 10_Engineering 与 13_Code_Framework 重复文档
- **context**: 发现两份内容相同、版本号相同的 AQFT_Code_Framework_Design_V2.8.6.md
- **options**:
  - A: 两份都保留
  - B: 保留 13_Code_Framework，删除 10_Engineering 中的副本
- **chosen**: B
- **reason**: 10_Engineering 应聚焦工程规范（Standard/Process/Rules），13_Code_Framework 负责代码架构。职责分离后更清晰
- **impact**: 消除维护歧义；10_Engineering 仅保留 Software_Engineering_Standard

---

## DEC-20260726-004

- **date**: 2026-07-26
- **decision**: 创建 AQFT_ROOT.md 作为系统单一入口
- **context**: 用户提出"如何实现设计方案共享，直接访问，而不进行二次访问"的核心需求
- **options**:
  - A: 依赖 Knowledge Hub 中的 INDEX.md
  - B: 在项目根目录创建 AQFT_ROOT.md
- **chosen**: B
- **reason**: 根目录入口使任何访问者（人/AI/新成员）打开项目即看到全貌，无需导航到子目录
- **impact**: 实现 Single Entry Architecture；AQFT_ROOT.md 成为系统第一入口

---

## DEC-20260726-005

- **date**: 2026-07-26
- **decision**: 建立 AQFT_DECISION_LOG.md 架构决策日志
- **context**: P4 Self Governance 要求系统具备"可解释、可审计、可追溯"能力。设计阶段的人类决策本身就是系统知识资产
- **options**:
  - A: 依赖 Git commit message 记录决策
  - B: 建立结构化决策日志
- **chosen**: B
- **reason**: Git message 太简短且分散。结构化日志可被 AI 直接解析，未来 AQF-T 自进化系统可读取此日志理解"初始设计意图"
- **impact**: 形成 Decision Memory；每个关键决策有 ID/背景/选项/结论/影响 五要素

---

## DEC-20260726-006

- **date**: 2026-07-26
- **decision**: 建立 World Model V3.0.0 五层认知架构
- **context**: 24_World_Model_System 已有目录骨架和概要设计文档，但缺少宪法级架构
- **options**:
  - A: 直接进入代码实现
  - B: 先建立 World Model 宪法级架构文档
- **chosen**: B
- **reason**: World Model 是 AQF-T 从量化系统跃迁为自主智能系统的核心。必须架构先行，定义五层模型（State → Dynamics → Scenario → Counterfactual → Memory）后再工程化
- **impact**: 确立 AQF-T V3.0.0 认知架构基线；定义 Market State Vector 10 维状态空间；建立 Counterfactual Engine 作为核心差异化能力

---

## DEC-20260726-007

- **date**: 2026-07-26
- **decision**: 建立 Market World Model 作为 V3.0.0 第一实现核心
- **context**: World Model Architecture V3.0.0 定义了五层认知架构，需要从 Layer 1+2 开始工程化设计
- **options**:
  - A: 从 Scenario Simulation 开始（Layer 3）
  - B: 从 Market World Model 开始（Layer 1+2）
- **chosen**: B
- **reason**: 全部上层（Scenario/Counterfactual/Memory）依赖市场状态的内部表示。先建立 Market World Model（State Encoder + Regime Detector + Dynamics + Causal Graph），上层才有基础
- **impact**: 定义 MarketWorldState 对象（7维 × 10+子维度）；建立 10 种 Market Regime Universe；引入 Causal Market Graph 作为反事实推理的因果基础

---

## DEC-20260726-008

- **date**: 2026-07-26
- **decision**: 建立 Environment Model 作为 World Model 的环境认知层
- **context**: Market World Model 解决了 State，但相同 State 可能属于完全不同的 Environment。需要建立高层环境语义理解
- **options**:
  - A: 跳过 Environment，直接进入 Scenario
  - B: 先建立 Environment Model
- **chosen**: B
- **reason**: State ≠ Environment。例如"指数上涨+放量"在牛市中与在熊市反弹中含义完全不同。必须先建立环境认知层，Scenario Engine 才能生成有意义的情景
- **impact**: 建立五层环境模型（Regime/Macro/Capital/Policy/Memory）；Environment Memory 实现"历史上有没有类似世界"检索；512-dim Environment Embedding 连接 Market World Model → Scenario Engine

---

## DEC-20260726-009

- **date**: 2026-07-26
- **decision**: 建立 Scenario Simulation Engine 作为 World Model Layer 3
- **context**: Market World Model 理解当下，Environment Model 理解环境，但系统需要"想象未来"的能力
- **options**:
  - A: 使用单一预测模型（传统量化路线）
  - B: 建立多分支未来世界树（AQF-T 路线）
- **chosen**: B
- **reason**: 单一预测在复杂金融市场中不可靠。多分支情景树 + 概率分布更适合不确定环境下的决策。三种生成方法（Historical Replay / Dynamics Simulation / Generative）互补覆盖
- **impact**: 建立 Future World Tree 结构；定义 Scenario Object（10 字段）；Probability Engine 概率校准；Extreme Scenario Generator 连接 Risk Runtime；Agent API scenario.simulate()

---

## DEC-20260726-010

- **date**: 2026-07-26
- **decision**: 建立 Counterfactual Intelligence Engine 作为 World Model Layer 4 — AQF-T 核心认知壁垒
- **context**: Scenario Engine 已具备未来生成能力，系统需要从"预测智能"跃迁到"推理智能"，实现 Self-Reflection
- **options**:
  - A: 使用传统 Backtest 作为决策评估
  - B: 建立反事实推理引擎，通过 do(A') 干预模拟替代世界
- **chosen**: B
- **reason**: Backtest 只能回答"这个策略过去表现如何"，无法回答"如果当时做了不同选择会怎样"。反事实推理让 AQF-T 具备自我反思能力，这是从量化系统跃迁为自主智能系统的关键
- **impact**: 建立五大核心能力（World Clone / Action Intervention / Causal Reasoning / Alternative Simulation / Outcome Comparison）；五种干预类型（Decision/Timing/Risk/Strategy/Market）；因果推理依赖 Market Causal Graph；Counterfactual → Update Policy → Future Improvement 形成 Self-Reflection Loop

---

## 决策原则

1. 风险优先 — 任何可能引入风险的决策，保守方案优先
2. 可追溯 — 每个决策必须记录"为什么"
3. 可回滚 — 重大决策保留回退路径
4. 人机共读 — 同时面向人类和 AI Agent

---

*此日志由 AQF-T 知识治理层维护。每个架构决策即时记录。*
