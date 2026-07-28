# AQF-T V4.0 Engineering Refinement Plan V1.0


# AQF-T V4.0 工程精进计划


Version: V1.0
Status: APPROVED — CC Audit Response
Date: 2026-07-28
Governing: MC-016 / MC-021 / MC-022 / MC-023

---

## 零、治理原则

```
MC-016: Reality Over Architecture    — 架构服务于验证，非反之
MC-021: Knowledge Governance         — 知识资产可追溯
MC-022: Truth Over Ownership         — 正确性 > 归属
MC-023: Cognitive Density > Module Count — 认知密度 > 模块数量

Architecture Era: CLOSED
Engineering Era Objective: 将冻结架构转化为可执行现实
```

---

## 一、Canonical Module ID 体系

引入规范模块标识，目录名仅用于导航，Canonical ID 用于身份标识。

| Canonical ID | 模块 | 认知层 | 职责 |
|:---:|------|------|------|
| GOV-001 | 00_Knowledge_Hub | 治理层 | 知识入口+决策日志+成熟度矩阵 |
| GOV-002 | 00_Project | 治理层 | 项目管理+版本控制+路线图 |
| ARC-001 | 01_Architecture | 架构层 | 系统架构+数据流+模块+部署 |
| CNST-001 | 02_Constitution | 宪法层 | Meta宪法+边界宪法+工程原则 |
| COG-001 | 03_AI_Brain | 认知架构层 | 认知流程+智能编排+推理架构 |
| EXEC-001 | 04_Execution_Intelligence | 能力实现层 | 策略运行时+组合+仓位+订单+QMT |
| STRAT-001 | 04_Strategy | 能力实现层 | 策略体系+Dragon+适配矩阵 |
| OBS-001 | 05_Observation_Intelligence | 能力实现层 | 执行事件+绩效+漂移检测+反馈 |
| RISK-001 | 05_Risk | 能力实现层 | 风险审批+Kill Switch+仓位控制 |
| EXEC-002 | 06_Execution | 能力实现层 | 订单管理+Broker接口+A股规则 |
| EXP-001 | 06_Experience_Intelligence | 能力实现层 | 交易片段+模式提取+知识路由 |
| DATA-001 | 07_Data | 能力实现层 | 数据采集+存储+特征+服务 |
| REFL-001 | 07_Reflection_Intelligence | 能力实现层 | 自反思+决策回顾+教训提取 |
| CMBT-001 | 08_Combat_Intelligence | 能力实现层 | 涨停智能+对手建模+量化足迹+假设仲裁 |
| PARAM-001 | 08_Parameter | 能力实现层 | 参数治理+版本+生命周期 |
| TEST-001 | 09_Test | 能力实现层 | 单元+集成+回测+压力 |
| VAL-001 | 09_Validation_Framework | 能力实现层 | 实验注册+回放+基准+统计+校准 |
| ENGR-001 | 10_Engineering | 工程层 | 编码规范+DB Schema+API+因子 |
| IMPL-001 | 11_AI_Implementation | 实现层 | AI工程实现 |
| IMPL-002 | 12_Data_Engineering | 实现层 | 数据工程实现 |
| IMPL-003 | 13_Code_Framework | 实现层 | 代码框架 |
| RT-001 | 14_Runtime | 运行层 | 系统启动+服务管理 |
| RT-002 | 15_Data_Runtime | 运行层 | 数据管道运行 |
| RT-003 | 16_AI_Runtime | 运行层 | AI推理运行 |
| RT-004 | 17_Strategy_Runtime | 运行层 | 策略运行 |
| RT-005 | 18_Risk_Runtime | 运行层 | 风控运行 |
| RT-006 | 19_Execution_Runtime | 运行层 | 执行运行 |
| RT-007 | 20_Simulation_System | 运行层 | 模拟交易+回测 |
| RT-008 | 21_Production_Runtime | 运行层 | 生产部署 |
| EVL-001 | 22_Evolution_System | 进化层 | 监控→优化→学习→决策→知识→治理 |
| AGT-001 | 23_Agent_Intelligence_System | 自主智能层 | 多Agent协作+自反思+数据合成 |
| WM-001 | 24_World_Model_System | 自主智能层 | World Model五层认知 |
| DEC-001 | 25_Decision_Intelligence_System | 自主智能层 | 决策智能 |
| CM-001 | 26_Cross_Market_Intelligence_System | 自主智能层 | 跨市场智能 |
| HAI-001 | 27_Human_AI_Collaboration_System | 自主智能层 | 人机协同治理 |
| RSRCH-001 | 01_Research | 研究层 | 行业研究+技术准入 |

---

## 二、模块生命周期管理

每个模块根目录必须包含 `STATUS.md`：

```
# MODULE STATUS

Canonical ID: WM-001
Module: 24_World_Model_System
Lifecycle Stage: DESIGN  | CONTRACT | IMPLEMENT | VALIDATE | PRODUCTION
Current Stage: DESIGN
Frozen Documents: 7
Last Updated: 2026-07-26
Next Milestone: Contract Definition (V4.0-EP-003)
```

### 生命周期五阶段

| 阶段 | 含义 | 准入标准 |
|------|------|---------|
| DESIGN | 架构设计完成 | 设计文档冻结 |
| CONTRACT | 接口契约定义 | I/O Schema + API + 状态机 |
| IMPLEMENT | 代码实现 | 可运行 + 单元测试 |
| VALIDATE | 验证通过 | 回测+模拟+压力 |
| PRODUCTION | 生产就绪 | 实盘验证 |

---

## 三、文档清理方案

### 立即归档 (→ 99_Archive/Release_History/)

```
00_Project/ 中的 V2.9 版控文件 (25份):
  V2.9.0~V2.9.5 Freeze_Review/Approval/Audit → 归档
  保留: V3.1 战略文档 (当前活跃版本)

02_Constitution/ 中已退役的边界宪法 → 标注 [DEPRECATED]
```

### 创建单一真相源

```
新建: AQFT_Current_State.md (根目录)

内容:
  - 当前版本基线: V3.0.0
  - 活跃模块清单 (Canonical ID + 生命周期阶段)
  - 当前工程焦点
  - 最近决策 (链接到DECISION_LOG)
```

---

## 四、工程优先级

### EP-001: 文档清理 (P0)

```
动作: 25份V2.9版本文档归档
效果: 00_Project 49→24文档
风险: 零 (不删除)
```

### EP-002: Canonical ID 部署 (P0)

```
动作: 为每个模块创建 STATUS.md + Canonical ID
效果: 统一模块身份标识
风险: 零 (仅新增文件)
```

### EP-003: DEC-001 决策智能深化 (P0)

```
模块: 25_Decision_Intelligence_System (3.1KB→20KB)
内容: 决策算法伪代码 + 状态机 + I/O Schema + 验证方法
目标生命周期: DESIGN → CONTRACT
```

### EP-004: 运行层补齐 (P1)

```
模块: RT-004(17) / RT-005(18) / RT-006(19)
目标: 3.5-4.5KB → 12KB+
内容: 运行时接口 + 状态机 + 伪代码
```

### EP-005: 创建 AQFT_Current_State.md (P1)

```
位置: 根目录
内容: 版本基线+模块清单+工程焦点+最近决策
目标: 单一真相源
```

### EP-006: 跨市场深化 (P2)

```
模块: CM-001(26) 3.3KB→10KB
内容: A股传导链量化模型
```

---

## 五、认知架构 vs 能力实现 分离

```
认知架构层 (COG-001: 03_AI_Brain):
  职责: 认知流程编排 / 智能推理架构 / 子系统集成
  不拥有: World Model实现 / Decision实现 / Memory实现

能力实现层:
  WM-001:  24_World_Model_System — World Model能力
  DEC-001: 25_Decision_Intelligence — 决策能力
  EVL-001: 22_Evolution_System — 进化能力

原则: 一个概念, 一个Owner。认知架构不重复定义实现能力。
```

---

## 六、冻结声明

本文件定义 AQF-T V4.0 工程精进计划。

Architecture Era CLOSED。Engineering Era 目标: 将冻结架构转化为可执行现实。

优化原则: 减少重复, 增加可执行性, 保护认知架构。

Version: V1.0
Status: APPROVED
END OF AQF-T V4.0 ENGINEERING REFINEMENT PLAN
