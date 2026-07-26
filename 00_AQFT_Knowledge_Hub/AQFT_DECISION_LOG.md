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

## 决策原则

1. 风险优先 — 任何可能引入风险的决策，保守方案优先
2. 可追溯 — 每个决策必须记录"为什么"
3. 可回滚 — 重大决策保留回退路径
4. 人机共读 — 同时面向人类和 AI Agent

---

*此日志由 AQF-T 知识治理层维护。每个架构决策即时记录。*
