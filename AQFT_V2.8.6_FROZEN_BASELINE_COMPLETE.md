# AQF-T V2.8.6 冻结基线 — 完整设计档案


# AQF-T V2.8.6 FROZEN BASELINE — Complete Design Archive


**版本:** V2.8.6-FINAL
**状态:** ARCHITECTURE FREEZE (FROZEN) — 不可修改
**范围:** P0-P4 全 22 模块
**规模:** 88 份设计文档 | 569KB
**日期:** 2026-07-26 (冻结日期)
**文件路径:** D:\AQF-T

---

## 零、系统定位

AQF-T (Adaptive Quantitative Fusion Trading System) 是一套面向A股游资及个人量化交易的AI驱动自主进化智能交易系统。

### 核心理念

```
数据驱动 + AI融合 + 多策略协同 + 风险约束 + 自动执行 + 持续学习
```

### 版本路线

```
Era 1: Architecture Era
  V2.8.6  Architecture Freeze (CURRENT STABLE BASELINE) ◄── 本文件

Era 2: Intelligence Era
  V2.9.x  World Model / Decision / Memory / Reasoning Upgrade

Era 3: Autonomous Era
  V3.0    Financial Intelligence Operating System
```

---

## 一、全模块清单 (22模块)

### P0 — 架构与宪法 (2模块 / 31文档 / 85KB)

#### 01_Architecture (5文档 / 15KB)
- `01_System_Architecture/AQFT_System_Architecture_V2.8.6_FINAL.md` (4.5KB) — 七层总体架构: 用户交互→决策管理→AI Brain→策略融合→风险控制→数据计算→数据采集
- `02_Data_Flow/AQFT_Data_Flow_Architecture_V2.8.6.md` — 数据闭环模型: 外部数据→采集→存储→处理→特征→AI→策略→风险→执行→反馈
- `03_Module_Architecture/AQFT_Module_Architecture_V2.8.6.md` — 七模块边界定义: AI/Strategy/Risk/Execution/Data/Parameter/Test
- `04_Deployment_Architecture/AQFT_Deployment_Architecture_V2.8.6.md` — 部署架构: Win/Linux, Python 3.11+, 四层存储, 开发/回测/模拟/实盘四模式

#### 02_Constitution (26文档 / 70KB)
- `AQFT_System_Constitution_V2.8.6_FINAL.md` (23KB) — **最高约束文件。17章。** 定义了系统安全>风险控制>长期收益的优先级。禁止单模型决策, 要求多模型融合。Risk拥有最高否决权。
- `AQFT_Meta_Constitution_V1.0.md` — 元宪法: 知识治理框架
- **MC工程原则系列:**
  - `MC-016` Reality Over Architecture (现实优先于架构)
  - `MC-018/MC-019` Engineering Principles (工程原则)
  - `MC-020` Contract Before Code (契约先于代码)
  - `MC-021` Metrics Drive Evolution (度量驱动进化)
  - `MC-022` Truth Over Ownership (真相优先于归属)
  - `MC-023` Minimal Cognitive Core (最小认知核心)
- **14 边界宪法 (C004-C016):**
  - `C004` Strategy Runtime Boundary
  - `C005` Portfolio Authority Boundary
  - `C006` Position Authority Boundary
  - `C007` Order Execution Boundary
  - `C008` QMT Adapter Boundary
  - `C010` Market Context Boundary
  - `C011` LimitUp Intelligence Boundary
  - `C012` Participant Interpretation Boundary
  - `C013` Microstructure Interpretation Boundary
  - `C014` Hypothesis Arbitration Boundary
  - `C015` Confidence Integrity Boundary
  - `C016` Knowledge Lifecycle Boundary
- `AQFT_CC_Execution_Constraint_V1.0.md` — CC最高约束
- `AQFT_Collaboration_Model_V1.0.md` — 双AI协作研发治理
- `AQFT_QMT_Integration_Principle_V1.0.md` — QMT集成宪法

### P1 — 核心设计 (7模块 / 66KB)

#### 03_AI_Brain (主设计1文档/15KB + 子模块23文档/311KB)
**主设计文档: `AQFT_AI_Brain_Design_V2.8.6.md` (15KB)**

四大引擎:
- **Prediction Engine:** 输入Schema(PredictionInput: 行情+技术指标+市场Context+涨停环境) → 输出Schema(PredictionOutput: 趋势方向+概率+Regime+风险标记)。推荐模型: LightGBM(首选)→XGBoost→Transformer
- **Sentiment Engine:** ⭐ 游资核心。A股情绪数据源(涨停+龙虎榜+北向+融资+新闻)。情绪值公式: 涨停×2-跌停×3+连板×5+北向×10。四阶段周期: 冰点期(<20)→回暖期(20-50)→高潮期(50-80)→退潮期(>80)。题材热度公式: 政策级别×0.3+涨停家数×0.25+龙头×0.20+联动×0.15+资金×0.10
- **Risk Intelligence:** AI辅助风险预测 (波动/回撤/流动性/极端事件)
- **Fusion Engine:** 四引擎加权融合, 权重随Market Regime动态调整。FusionOutput含reasoning_trace可解释决策链
- **Learning Engine:** 交易结果→错误分析→模型重训练→部署
- **模型治理:** 生命周期(Dev→Test→Val→Prod→Archived), 上线标准(AUC>0.65, IC>0.05, DD<20%, Sharpe>1.0)

**子模块 (23文档/311KB):**
- `Autonomous_Runtime/` — 自主运行时架构
- `Decision_Intelligence/` — 决策智能(4文档: 架构/融合/选择/反馈)
- `Memory_System/` — 记忆系统(5文档: 架构/检索/冷启动/失败模式/巩固学习)
- `Reasoning_Engine/` — 推理引擎(5文档: 架构/因果/反事实/可解释/情景)
- `Knowledge_System/` — 知识系统(含生命周期)
- `World_Model/` — 世界模型(7文档: 架构/状态/信念/Regime/模拟/接口/市场时钟)

#### 04_Strategy (1文档/12KB)
**`AQFT_Strategy_Design_V2.8.6.md` (12KB)** ⭐ 游资核心

六大策略:
- **Dragon Strategy (龙头战法):** 6项龙头判定(连板≥3+题材涨停≥5+封单/流通>5%+游资席位+集合竞价封单>5000万+首板次日高开≥5%)。三买入模式(首板打板/二板接力/弱转强)。五卖出条件(炸板/竞价转弱/题材退潮/连板中断/异动警告)
- **Trend Strategy:** MA金叉+放量, 持仓5-20天, 仓位20-30%
- **Volume-Price Strategy:** N字反包+缩量回调+分时承接
- **Sentiment Strategy:** 情绪周期择时, 冰点试错→回暖加仓→高潮重仓→退潮空仓
- **Defensive Strategy:** 日内亏损>2%或跌停>50家或退潮期→降仓/空仓

策略-Regime-情绪周期适配矩阵 (10×4): 每种市场环境+情绪周期组合对应最优策略和仓位上限

信号统一格式 `TradingSignal`: 14字段(signal_id/timestamp/source/target/confidence/risk_context/reasoning/metadata)

信号融合优先级: 情绪周期约束 > 信号一致性 > AI置信度 > 风险约束

#### 05_Risk (1文档/11KB)
**`AQFT_Risk_Design_V2.8.6.md` (11KB)** ⭐ 全系统公式最密集 (44处)

**风险评分公式:**
```
Risk Score = Market×0.25 + Position×0.25 + Strategy×0.20 + Sentiment×0.15 + Liquidity×0.15
```

五因子每项有具体子公式。风险四级: Low(0-30)→Medium(31-55)→High(56-75)→Extreme(76-100)。

**游资特化风控:**
- 炸板风控: 涨停打开>10分钟→市价卖出+暂停策略30分钟
- 连板高位: 连板≥7 Score+20, ≥11 Score+40+仓位强制30%
- 题材退潮: 龙头炸板→板块Score+30, 暂停新开仓
- 情绪周期限额覆盖: 退潮期强制20%仓位+禁止打板; 高潮期可满仓70%

**Kill Switch:** 6触发条件→撤单+停策略+清仓+断Broker+通知+Safe Mode

**仓位计算:** 凯利公式 f*=(p×b-q)/b, 最终仓位=凯利×情绪系数×风险系数×流动性系数

#### 06_Execution (1文档/9KB)
**`AQFT_Execution_Design_V2.8.6.md` (9KB)**

订单状态机: CREATED→PRE-CHECK→SUBMITTED→ACCEPTED→PARTIALLY_FILLED→FILLED→COMPLETED

A股特殊状态: LIMIT_UP_LOCKED/LIMIT_DOWN_LOCKED/TODAY_BOUGHT_LOCKED/SUSPENDED

下单前7项检查: Risk/T+1/涨跌停/资金/仓位/手数/交易时段

执行策略: Market/Limit/TWAP/VWAP/Smart。游资以Market为主(速度优先)

A股规则: T+1(当日买次日卖), 涨跌停(主板±10%/科创创业±20%/北交±30%/ST±5%), 真实费率(佣金0.025%+印花税0.1%+过户费0.001%), 手数(100股)

Broker适配: QMT/xtquant实盘 + akshare fallback + Paper Trading模拟

#### 07_Data (1文档/9KB)
**`AQFT_Data_Design_V2.8.6.md` (9KB)** ⭐ Schema最丰富 (8处)

六大类A股数据源: 行情(Tick/分钟/日K/盘口/竞价)/涨停(列表/连板/炸板/封板强度/梯队)/龙虎榜(席位/机构/北向)/资金(融资/大宗/增减持)/基本面(财务/板块/ST)/情绪(涨跌比/炸板率/新闻/社交)

四层架构: Raw(Parquet/JSON)→Standard(统一Schema)→Feature(技术/情绪/涨停特征)→Result(交易/信号)

核心Schema: DailyKLine(16字段)/LimitUpRecord(12字段)/LongHuRecord(9字段)/AuctionData(7字段)

API: 16个数据服务端点

#### 08_Parameter (1文档/8KB)
**`AQFT_Parameter_Design_V2.8.6.md` (8KB)** ⭐ 参数最丰富 (57处)

30+参数: AI(7)/Strategy(11含Dragon特化)/Risk(12)/Execution(5)

参数状态机: DRAFT→TESTING→APPROVED→ACTIVE→DEPRECATED→ARCHIVED

变更管理: 提出→评估→回测→模拟→审批→发布→监控。审批分级: Low(自动)/Medium(人工)/High(人工+宪法检查)

#### 09_Test (1文档/7KB)
**`AQFT_Test_Design_V2.8.6.md` (7KB)**

六层测试: L1单元(覆盖率AI≥80%/Risk≥90%/Execution≥90%)→L2集成(5条核心链路)→L3回测(3年数据+A股规则)→L4模拟(≥1月Paper Trading)→L5压力(7极端场景)→L6上线(12项检查)

游资特化场景: 高潮期打板/退潮期防御/炸板处理/N字反包

### P2 — 工程实现 (4模块 / 43KB)

#### 10_Engineering (5文档/24KB) ⭐⭐⭐⭐⭐
- `AQFT_Database_Schema_Design_V3.6.0.md` — 10张表DDL: stock_basic/stock_daily/stock_minute/limit_up_record⭐/longhu_record⭐/factor_value/orders/positions/signals/risk_log。SQLite→PostgreSQL双轨制+SQLAlchemy接入代码
- `AQFT_API_Specification_V3.6.0.md` — 35个API端点: Data(9)+AI(5)+Strategy(4)+Risk(4)+Execution(5)+Simulation(2)+System(2)
- `AQFT_Feature_Engineering_Specification_V3.6.0.md` — 100个A股因子: 技术30+Alpha30+情绪20⭐+资金20。每因子有公式+周期+来源
- `AQFT_Software_Engineering_Standard_V2.8.6.md` (7.6KB) — 编码规范: PEP8+TypeHint+Docstring+Git分支模型
- `AQFT_Document_Completeness_Standard_V1.0.md` — 文档完整性标准

#### 11_AI_Implementation (1文档/6KB)
AI工程实现层目录骨架和接口规范 (概要级)

#### 12_Data_Engineering (1文档/6KB)
数据工程实现层: 采集/管道/仓库/特征存储/质量/服务 (概要级)

#### 13_Code_Framework (1文档/7KB)
代码框架: src/ai_brain/strategy/risk/execution/data/parameter/test/config 目录结构 + 模块Base Interface (概要级)

### P3 — 运行系统 (8模块 / 44KB)

#### 14_Runtime (1文档/9KB) ⭐ 状态机最丰富 (48处)
11步启动序列: 环境→配置→日志→数据库→参数→数据→AI→策略→风控→执行→调度→READY。8服务依赖管理。10项定时任务(含交易日特殊调度)。5级异常恢复(L1数据→L5系统)。

#### 15_Data_Runtime (1文档/6KB) ⭐ API最丰富 (19处)
6通道实时采集+三级缓存(内存→文件→数据库)+Feature Engine(768-dim,<50ms)。16个数据服务端点。

#### 16_AI_Runtime (1文档/5KB)
四引擎并发推理(<50ms延迟)。模型热切换(影子模式: 新模型24h对比→切换)。自动重训练触发。

#### 17_Strategy_Runtime (1文档/3.5KB) ⚠️ 薄弱
策略注册表+动态选择+事件驱动执行。借鉴Backtrader+FinRL-X权重中心化。缺少Schema和参数定义。

#### 18_Risk_Runtime (1文档/3.7KB) ⚠️ 薄弱
四层纵深防御(FIA 2024标准)+三级升级(0监控/1平仓/2熔断)+状态持久化。缺少Schema和参数定义。

#### 19_Execution_Runtime (1文档/4.5KB) ⚠️ 薄弱
订单管理+Broke多适配器(QMT/Paper/Backtest)+指数退避重连。缺少Schema和参数定义。

#### 20_Simulation_System (1文档/5.5KB)
统一引擎架构(回测=模拟=同一撮合核心)。四级撮合(理想/滑点/盘口/订单簿)。A股特殊规则(涨停封死/跌停封死/T+1)。虚拟组合管理+审计轨迹(8字段)。

#### 21_Production_Runtime (1文档/6.8KB)
生产部署体系(Docker/K8s)+Trading Gateway+高可用(主备切换)+全系统监控(系统/服务/交易三层)+告警系统(INFO→CRITICAL)+灾备恢复+运维控制台。

### P4 — 持续进化 (6文档 / 34KB)

#### 22_Evolution_System (6文档/34KB) ⭐⭐⭐⭐
- Monitoring Intelligence: 系统/交易/AI三层健康监控+异常检测(统计+模式+ML)+市场状态识别(牛/熊/震荡/危机)
- Auto Optimization: 五大优化器(参数/策略/模型/组合/风险)+Experiment Manager+安全发布(优化→模拟→审批→部署)
- Self Learning Engine: 经验采集+反馈处理+Reward Engine(R=收益-风险+稳定+质量)+RL(State→Action→Reward)+三级记忆(短/长/关键)
- Autonomous Decision Evolution: 策略自选+自适应策略+动态风险适应+环境理解+自主规划+决策记忆
- Knowledge Evolution: 市场/策略/风险/系统四大知识库+知识图谱+推理引擎(规则/模式/相似/经验)
- Self Governance: 策略/风险/模型/版本/决策/审计六治理+合规引擎+Kill Switch

---

## 二、架构全景图

```
                     AQF-T V2.8.6

        ┌──────────────────────────────────┐
        │        02_Constitution           │  最高宪法
        │     Meta + MC + 14边界宪法       │
        └──────────────────────────────────┘
                        │
        ┌──────────────────────────────────┐
        │        01_Architecture           │  系统架构
        │     七层架构 + 数据流 + 模块     │
        └──────────────────────────────────┘
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
┌───────┐  ┌───────┐  ┌───────┐  ┌───────────┐
│03_AI  │  │04_Str │  │05_Risk│  │06_Exec    │  P1 核心设计
│Brain  │→│ategy  │→│       │→│ution      │
│预测    │  │Dragon │  │APPROVE│  │QMT下单     │
│情绪    │  │龙头   │  │ADJUST │  │T+1/涨跌停  │
│融合    │  │适配   │  │REJECT │  │A股规则     │
└───────┘  └───────┘  └───────┘  └───────────┘
    │
┌───────┐  ┌───────┐  ┌───────┐
│07_Data│  │08_Para│  │09_Test│              P1 基础
│A股数据│  │mater  │  │六层测试│
│6类源  │  │30+参数│  │游资场景│
└───────┘  └───────┘  └───────┘
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
┌───────┐  ┌───────┐  ┌───────┐  ┌───────────┐
│10_Eng │  │11_AI  │  │12_Data│  │13_Code    │  P2 工程
│DB+API │  │Impl   │  │Eng    │  │Framework  │
│+100因子│ │       │  │       │  │           │
└───────┘  └───────┘  └───────┘  └───────────┘
                        │
    ┌───────────────────┼───────────────────┐
    │       │       │       │       │       │
┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐
│14 │ │15 │ │16 │ │17 │ │18 │ │19 │ │20 │ │21 │  P3 运行
│RT │ │Data│ │AI │ │Str│ │Risk│ │Exec│ │Sim│ │Prod│
└───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘
                        │
                ┌───────────┐
                │22_Evol    │                       P4 进化
                │监控→优化  │
                │→学习→决策 │
                │→知识→治理 │
                └───────────┘
```

---

## 三、设计深度五维指标

| 模块 | Schema | API | Formula | Param | State | 评级 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| 02_Constitution | 0 | 0 | 0 | 0 | 1 | ⭐⭐⭐⭐⭐ |
| 03_AI_Brain | 4 | 16 | 4 | 1 | 17 | ⭐⭐⭐⭐ |
| 04_Strategy | 0 | 8 | 7 | 5 | 17 | ⭐⭐⭐⭐ |
| **05_Risk** | 0 | 7 | **44** | 1 | **38** | ⭐⭐⭐⭐⭐ |
| 06_Execution | 1 | 9 | 9 | 0 | 36 | ⭐⭐⭐⭐ |
| 07_Data | 3 | 15 | 5 | 2 | 3 | ⭐⭐⭐⭐ |
| 08_Parameter | 0 | 9 | 0 | 12 | 14 | ⭐⭐⭐ |
| 09_Test | 1 | 0 | 8 | 1 | 37 | ⭐⭐⭐ |
| 10_Engineering | 10表 | 35端点 | 100因子 | 0 | 0 | ⭐⭐⭐⭐⭐ |
| 14_Runtime | 0 | 11 | 3 | 1 | 48 | ⭐⭐⭐ |
| 15_Data_Runtime | 1 | **19** | 7 | 2 | 14 | ⭐⭐⭐ |
| 17_Strategy_Runtime | **0** | 7 | 1 | **0** | 11 | ⭐⭐ |
| 18_Risk_Runtime | **0** | 8 | 2 | 1 | 9 | ⭐⭐ |
| 19_Execution_Runtime | **0** | 8 | 2 | 1 | 24 | ⭐⭐ |
| 22_Evolution | 0 | 0 | 2 | 0 | 12 | ⭐⭐⭐⭐ |

---

## 四、核心优势 (6项)

1. **宪法治理体系** — Meta宪法+MC工程原则+14边界宪法(C004-C016)，每次交易必须经过Risk审批
2. **风险公式完整** — 05_Risk 44个量化公式，五因子评分+游资特化(炸板/连板/题材退潮/情绪覆盖)
3. **Dragon龙头战法** — 04_Strategy 6项龙头判定+三买入+五卖出+10×4适配矩阵
4. **工程三件套** — 10_Engineering DB DDL+API 35端点+100因子公式，可直接编码
5. **A股数据Schema** — 07_Data LimitUpRecord/LongHuRecord/AuctionData 游资三核心
6. **进化六环完整** — 22_Evolution 监控→优化→学习→决策→知识→治理

---

## 五、核心劣势 (5项)

1. **P1→P3断层** 🔴 — Strategy(12KB)→Runtime(3.5KB), Risk(11KB)→Runtime(3.7KB), Execution(9KB)→Runtime(4.5KB)。P1设计完整但P3运行层空壳
2. **03_AI_Brain膨胀** 🟡 — 311KB/24文档，内含5个子系统，与P5独立模块功能重叠
3. **05_Risk缺Schema** 🟡 — 44个公式但风险决策输出格式未结构化定义
4. **P2工程层不均** 🟡 — 10强(24KB), 11-13弱(6-7KB)
5. **01_Architecture偏浅** 🟢 — 4.5KB概要级, 无架构决策记录

---

## 六、综合评分

| 维度 | 评分 |
|------|:---:|
| 宪法治理 | ⭐⭐⭐⭐⭐ |
| P1核心设计 | ⭐⭐⭐⭐ |
| P2工程规范 | ⭐⭐⭐ |
| P3运行系统 | ⭐⭐ |
| P4进化系统 | ⭐⭐⭐⭐ |
| 设计一致性 | ⭐⭐⭐ |
| 可编码性 | ⭐⭐⭐ |

**总评: V2.8.6 宪法+核心设计+工程规范达到生产级深度。P3运行层17/18/19是唯一明显短板(3.5-4.5KB, 缺Schema/参数)。P1层设计可以直接指导P3层的运行实现。**

---

## 七、文件索引 (完整88文件)

```
P0 架构宪法 (31文件):
  01_Architecture/01_System_Architecture/AQFT_System_Architecture_V2.8.6_FINAL.md
  01_Architecture/02_Data_Flow/AQFT_Data_Flow_Architecture_V2.8.6.md
  01_Architecture/03_Module_Architecture/AQFT_Module_Architecture_V2.8.6.md
  01_Architecture/04_Deployment_Architecture/AQFT_Deployment_Architecture_V2.8.6.md
  02_Constitution/AQFT_System_Constitution_V2.8.6_FINAL.md (最高约束)
  02_Constitution/AQFT_Meta_Constitution_V1.0.md
  02_Constitution/AQFT_Meta_Constitution_Extension_AI_Collaboration_V1.0.md
  02_Constitution/AQFT_Collaboration_Model_V1.0.md
  02_Constitution/AQFT_CC_Execution_Constraint_V1.0.md
  02_Constitution/AQFT_QMT_Integration_Principle_V1.0.md
  02_Constitution/AQFT_Strategy_Runtime_Boundary_C004_V1.0.md
  02_Constitution/AQFT_Portfolio_Authority_Boundary_C005_V1.0.md
  02_Constitution/AQFT_Position_Authority_Boundary_C006_V1.0.md
  02_Constitution/AQFT_Order_Execution_Boundary_C007_V1.0.md
  02_Constitution/AQFT_QMT_Adapter_Boundary_C008_V1.0.md
  02_Constitution/AQFT_Market_Context_Boundary_C010_V1.0.md
  02_Constitution/AQFT_LimitUp_Intelligence_Boundary_C011_V1.0.md
  02_Constitution/AQFT_Participant_Interpretation_Boundary_C012_V1.0.md
  02_Constitution/AQFT_Microstructure_Interpretation_Boundary_C013_V1.0.md
  02_Constitution/AQFT_Hypothesis_Arbitration_Boundary_C014_V1.0.md
  02_Constitution/AQFT_Confidence_Integrity_Boundary_C015_V1.0.md
  02_Constitution/AQFT_Knowledge_Lifecycle_Boundary_C016_V1.0.md
  02_Constitution/AQFT_Reality_Over_Architecture_MC016_V1.0.md
  02_Constitution/AQFT_Engineering_Principles_MC018_MC019_V1.0.md
  02_Constitution/AQFT_Contract_Before_Code_MC020_V1.0.md
  02_Constitution/AQFT_Metrics_Drive_Evolution_MC021_V1.0.md
  02_Constitution/AQFT_Truth_Over_Ownership_MC022_V1.0.md
  02_Constitution/AQFT_Minimal_Cognitive_Core_MC023_V1.0.md
  02_Constitution/AQFT_Architecture_Retirement_Governance_V1.0.md

P1 核心设计 (31文件):
  03_AI_Brain/AQFT_AI_Brain_Design_V2.8.6.md (主设计)
  03_AI_Brain/Autonomous_Runtime/
  03_AI_Brain/Decision_Intelligence/ (4文档)
  03_AI_Brain/Memory_System/ (5文档)
  03_AI_Brain/Reasoning_Engine/ (5文档)
  03_AI_Brain/Knowledge_System/
  03_AI_Brain/World_Model/ (7文档)
  04_Strategy/AQFT_Strategy_Design_V2.8.6.md
  05_Risk/AQFT_Risk_Design_V2.8.6.md
  06_Execution/AQFT_Execution_Design_V2.8.6.md
  07_Data/AQFT_Data_Design_V2.8.6.md
  08_Parameter/AQFT_Parameter_Design_V2.8.6.md
  09_Test/AQFT_Test_Design_V2.8.6.md

P2 工程实现 (8文件):
  10_Engineering/AQFT_Database_Schema_Design_V3.6.0.md
  10_Engineering/AQFT_API_Specification_V3.6.0.md
  10_Engineering/AQFT_Feature_Engineering_Specification_V3.6.0.md
  10_Engineering/AQFT_Software_Engineering_Standard_V2.8.6.md
  10_Engineering/AQFT_Document_Completeness_Standard_V1.0.md
  11_AI_Implementation/AQFT_AI_Engineering_Implementation_V2.8.6.md
  12_Data_Engineering/AQFT_Data_Engineering_Implementation_V2.8.6.md
  13_Code_Framework/AQFT_Code_Framework_Design_V2.8.6.md

P3 运行系统 (8文件):
  14_Runtime/AQFT_Runtime_Foundation_Design_V2.8.6.md
  15_Data_Runtime/AQFT_Data_Runtime_Design_V2.8.6.md
  16_AI_Runtime/AQFT_AI_Runtime_Design_V2.8.6.md
  17_Strategy_Runtime/AQFT_Strategy_Runtime_Design_V2.8.6.md
  18_Risk_Runtime/AQFT_Risk_Runtime_Design_V2.8.6.md
  19_Execution_Runtime/AQFT_Execution_Runtime_Design_V2.8.6.md
  20_Simulation_System/AQFT_Simulation_System_Design_V2.8.6.md
  21_Production_Runtime/AQFT_Production_Runtime_Design_V2.8.6.md

P4 进化系统 (6文件):
  22_Evolution_System/AQFT_Monitoring_Intelligence_Design_V2.8.6.md
  22_Evolution_System/AQFT_Auto_Optimization_Design_V2.8.6.md
  22_Evolution_System/AQFT_Self_Learning_Engine_Design_V2.8.6.md
  22_Evolution_System/AQFT_Autonomous_Decision_Evolution_Design_V2.8.6.md
  22_Evolution_System/AQFT_Knowledge_Evolution_Design_V2.8.6.md
  22_Evolution_System/AQFT_Self_Governance_Design_V2.8.6.md

根目录:
  README.md / VERSION.md / CHANGELOG.md / AQFT_ROOT.md
```

---

**AQF-T V2.8.6 — Architecture Freeze Complete. 22 modules. 88 documents. 569KB. FROZEN.**

*本文件可独立转发。收到者无需访问代码仓库即可理解AQF-T V2.8.6全貌。*
