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

## DEC-20260726-011

- **date**: 2026-07-26
- **decision**: 建立 Simulation Memory 作为 World Model Layer 5 — 五层架构完整闭环
- **context**: World Model 已具备 State/Environment/Scenario/Counterfactual 四层，需要长期经验积累与持续进化能力
- **options**:
  - A: 使用传统数据库记录交易历史
  - B: 建立四层经验记忆体系（World/Scenario/Counterfactual/Decision） + 自进化闭环
- **chosen**: B
- **reason**: 传统数据库只能存数据，不能形成经验。AQF-T 需要记住"在什么世界中，什么选择导致什么结果"，并在未来类似世界中被检索和使用。这使 World Model 从模拟器升级为具有经验人格的认知系统
- **impact**: 建立四层记忆（World/Scenario/Counterfactual/Decision）；1024-dim Experience Embedding；Memory Importance Model I=f(R,C,U)；Experience Learning Loop 自进化闭环；三层治理（Short/Long/Wisdom）；World Model 五层架构全部完成
- **milestone**: P5-WM-05 World Model Complete — AQF-T 获得 Observe→Understand→Imagine→Reason→Remember→Improve 完整认知循环

---

## DEC-20260726-012

- **date**: 2026-07-26
- **decision**: 建立 AGI Decision Architecture V3.0.0 — 从世界认知到自主行动
- **context**: World Model 已解决"市场是什么/未来怎样/不同选择会怎样/过去经验是什么"，需要解决最后一个问题："现在应该做什么？"
- **options**:
  - A: 使用传统 Signal → Buy/Sell 决策模型
  - B: 建立预期效用决策优化引擎 + 多Agent投票 + 可解释推理链
- **chosen**: B
- **reason**: 传统模型只回答"有没有信号"，AQF-T 需要回答"在当前世界理解下，什么行动具有最高长期效用"。六级行动空间替代简单的 Buy/Sell；预期效用函数 U(A) 替代单纯收益最大化；Decision Council 替代单一模型判断
- **impact**: 建立 Decision Reasoning Pipeline (Think→Act→Learn)；六级行动空间 (Observe/Hold/Increase/Reduce/Hedge/Exit)；预期效用优化 U(A)=Return-Risk+Knowledge-Uncertainty；Multi-Agent Decision Council；100% 可解释 Reasoning Trace；Self-Improving Decision Loop

---

## DEC-20260726-013

- **date**: 2026-07-26
- **decision**: 建立 Cross-Market Intelligence 作为 AQF-T 全球金融认知层
- **context**: World Model 解决了单市场内部运行规律，但金融市场相互关联。需要理解"一个市场变化如何影响另一个"
- **options**:
  - A: 保持单市场 World Model，通过数据接口获取外部信息
  - B: 建立独立的全球跨市场智能层
- **chosen**: B
- **reason**: 美联储加息→美元→人民币→北向资金→A股，这种传导链无法在单市场模型中捕捉。Cross-Market Graph Engine + Transmission Engine 形成全球冲击传播模型，使 AQF-T 具备"站在全球视角理解 A 股"的能力
- **impact**: 建立 Global Market Graph (节点+加权边)；Transmission Engine M(t+1)=f(M,C,E)；Capital Flow Intelligence 全球资金监测；Dynamic Correlation (环境自适应)；Contagion Detector 风险传染预警

---

## DEC-20260726-014

- **date**: 2026-07-26
- **decision**: 建立 Human-AI Collaborative Governance — P5 最终治理层
- **context**: P5 前四层已完成 Agent/World Model/Decision/Cross-Market，需要最终的人类-AI治理机制。AI 自主能力越强，越需要治理边界
- **options**:
  - A: 简单的人工审批界面
  - B: 建立完整的人机协同治理体系
- **chosen**: B
- **reason**: AQF-T 的目标不是替代人类，而是建立 Aligned Intelligence。六级自主权限 (L0-L5)、Intent Engine (理解意图非命令)、Explanation Engine (100% 可解释推理链)、Trust Engine (AI 不自大)、Alignment Engine (目标一致)、Override System (人类最终控制权) — 这些构成完整的治理闭环
- **impact**: 建立九大治理模块；六级自主权限 (Human Only → Full Autonomous)；Human-AI Collaboration Loop；AI Safety Layer 四重边界；Governance Dashboard 人机协作指标
- **milestone**: 🏆 P5 Autonomous Intelligence COMPLETE — AQF-T V3.0.0 五层自主智能全部冻结

---

## DEC-20260726-015

- **date**: 2026-07-26
- **decision**: 正式启动 V3.1.0 P6 — Autonomous Intelligence Runtime Engineering
- **context**: V3.0.0 完成 35 模块 50+ 文档的架构设计。系统需要从 Design Intelligence 进入 Running Intelligence
- **options**:
  - A: 继续扩展 P5 增加理论模块
  - B: 进入 P6 Runtime 工程化，让 World Model + Decision + Agent 首次运行
- **chosen**: B
- **reason**: 设计已经足够完整。继续增加理论模块会延迟验证。P6 的核心价值是让系统"活起来"——接入真实数据、运行 World Model、产生真实决策、接受人类协作、建立能力基准
- **impact**: P6 五层运行时 (Data/Sim/Decision/Human/Evaluation) + Runtime Orchestrator + Intelligence Monitor；V3.1.0 宪法级架构；版本路线 V2.8.6→V3.0.0→V3.1.0→V4.0.0

---

## DEC-20260730-016

- **date**: 2026-07-30
- **decision**: GPT Final Engineering Review — V1.0 Integration Phase PASS WITH NOTES, 进入 Runtime Hardening
- **context**: Claude 完成 M2-M7 主管线串联（pipeline.py / paper_runner.py / 9 tests PASSED）。GPT 评审确认 Pipeline 闭环形成，但 Live Trading 仍需 Runtime Hardening
- **options**:
  - A: 直接进入 Live Trading
  - B: 先 Runtime Hardening（QMT数据/ClockProvider/Report持久化）再考虑Live
  - C: 先训练ML模型优化收益
- **chosen**: B — Runtime Hardening 优先，ML训练最后
- **reason**: AQF-T 当前最大价值不是预测能力，而是可靠交易基础设施。模型训练属于优化收益，但基础设施还有真实风险缺口（datetime硬编码、无真实数据源、Report无持久化）
- **impact**:
  - P0执行顺序: QMT Adapter → ClockProvider → Report Persistence → 真实数据Replay → Pattern Evidence扩展 → ML Research
  - 5个设计调整: Regime Confidence / Path A评分归一化 / Portfolio Exposure Limits / Event Severity Score / ClockProvider
  - 不新增Pattern、不训练模型
  - 22天回放结果: 50候选→45信号→1成交，统计意义不足，需至少90交易日

---



## DEC-20260730-017

- **date**: 2026-07-30
- **decision**: GPT Final Architecture Review — V1.0 Integration PASS WITH NOTES, 进入 V1.1 Runtime Hardening
- **context**: Claude 完成 V1.0 Integration Phase (ClockProvider / Portfolio Exposure / Regime Confidence / QMT Adapter / Report Persistence)。GPT 最终架构评审确认系统已从"模块集合"进入"可运行交易系统"
- **options**:
  - A: 直接进入 Live Trading
  - B: V1.1 Runtime Hardening — MarketDataProvider统一接口 + 真实数据验证
  - C: 模型训练
- **chosen**: B — V1.1 Runtime Hardening
- **reason**: 当前最大的风险不是alpha，而是"系统看到的数据=真实市场数据吗？"如果不是，CPCV/DSR/PBO全部失去意义。QMT Adapter + 真实数据接入是唯一P0
- **impact**:
  - P0: MarketDataProvider统一接口(get_tick/get_orderbook/get_snapshot) → 替换_estimate_price()硬编码
  - P0: Regime Multiplier (高潮1.0/回暖0.8/冰点0.3/退潮0)
  - P1: Pipeline拆分为pipeline/orchestrator.py + phases/
  - P1: Path A评分版本追踪(score_version: pathA_v1)
  - P2: 真实数据30-60交易日Replay
  - 不新增Pattern/AI模型/策略
  - zhatban_rate内部使用，展示层保留"炸板率" — 建立兼容层
  - 最终仓位 = base_position × regime_multiplier × risk_multiplier

---

## 决策原则

1. 风险优先 — 任何可能引入风险的决策，保守方案优先
2. 可追溯 — 每个决策必须记录"为什么"
3. 可回滚 — 重大决策保留回退路径
4. 人机共读 — 同时面向人类和 AI Agent

---

*此日志由 AQF-T 知识治理层维护。每个架构决策即时记录。*
