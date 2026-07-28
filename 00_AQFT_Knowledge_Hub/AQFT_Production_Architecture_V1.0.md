# AQF-T V2.8.6 Production Architecture V1.0


# AQF-T 生产运行架构


**Version:** V1.0 | **Status:** Discussion Draft | **Date:** 2026-07-28
**定位:** V2.8.6 的精简生产实现版本。V2.8.6 = 设计母库, Production = 可执行系统。


---

## 零、总原则

```
1. V2.8.6 不动。它是设计资产库，所有知识保留。
2. Production 是 V2.8.6 的精简运行子集。
3. 研究级资产 (World Model/Counterfactual/Multi-Agent) → 冻结在 99_Research_Lab, 不参与生产。
4. 7 个生产模块。AI 是插件。交易主链不可绕过。
```

---

## 一、两层架构

```
                 AQF-T

        ┌──────────────────┐
        │  Research Layer   │  冻结, 不运行
        │                   │
        │  World Model      │
        │  Counterfactual   │
        │  Multi-Agent      │
        │  Advanced AI      │
        └──────────────────┘
                 │
                 │  知识沉淀
                 ▼
        ┌──────────────────┐
        │ Production Layer  │  7 模块, 可编码运行
        │                   │
        │  01 Constitution  │  交易制度
        │  02 Data          │  数据入口
        │  03 Strategy      │  策略生成
        │  04 Risk          │  风控审批 ← 最高否决权
        │  05 Execution     │  订单执行
        │  06 Learning      │  评分/建议/经验 (纯建议, 不参与交易链)
        │  07 Review        │  复盘/统计/评价
        └──────────────────┘
                 │
                 ▼
               QMT
                 │
              A股市场
```

---

## 二、七模块定义

### 01 Constitution — 交易制度

```
来源: V2.8.6 02_Constitution

保留:
  ✅ 14 边界宪法 (C004-C016): 每个模块的权限边界
  ✅ CC 最高约束: Risk > Strategy > Execution 优先级
  ✅ MC-016 Reality Over Architecture
  ✅ 交易纪律: 单票≤10%, 日亏≤3%, 总回撤≤15%

不保留:
  ❌ Meta 宪法 (研究级治理, 生产不需要)
  ❌ AI 协作模型 (单兵作战, 不需要)
```

### 02 Data — 数据入口

```
来源: V2.8.6 07_Data + 10_Engineering

功能:
  sources/     akshare (日线+涨停+龙虎榜) + QMT Level-2 (盘口)
  storage/     SQLite 10张表 (复用 V2.8.6 DB Schema)
  features/    100个A股因子 (复用 V2.8.6 10_Engineering)

不保留: 数据流架构文档 (概要级, 生产不需要)
```

### 03 Strategy — 策略生成

```
来源: V2.8.6 04_Strategy + 03_AI_Brain Sentiment Engine

功能:
  rules/
    dragon.py        龙头战法 (6判定+3买入+5卖出)
    trend.py         趋势策略
    sentiment.py     情绪周期择时 (四阶段+情绪值公式)
    volume_price.py  量价策略 (N字反包+弱转强)
    defensive.py     防御策略 (降仓/空仓)

  signals.py         TradingSignal 统一输出

策略选择: 根据情绪周期+Regime自动切换 (适配矩阵)
```

### 04 Risk — 风控审批 (最高否决权)

```
来源: V2.8.6 05_Risk

功能:
  formulas.py       风险评分 (44个公式)
  limits.py         限额管理
  pre_trade.py      7项下单前检查
  kill_switch.py    紧急熔断

输出: APPROVE / ADJUST / REJECT

任何交易信号必须经过 Risk 审批。
Risk 不可被绕过, 不可被关闭。
```

### 05 Execution — 订单执行

```
来源: V2.8.6 06_Execution + 99_Archive V3代码

功能:
  qmt_adapter.py    MiniQMT/xtquant 实盘
  paper_broker.py   模拟交易
  order_manager.py  订单状态机
  a_share_rules.py  T+1/涨跌停/费率/手数

只执行经 Risk APPROVE/ADJUST 的订单。
```

### 06 Learning — 评分/建议/经验 (纯建议)

```
来源: V2.8.6 03_AI_Brain Prediction Engine + DeepSeek API

定位: AI 是插件, 不是一级架构。只提供评分/概率/建议/经验。

plugins/
  predictor.py        LightGBM/CatBoost 趋势预测
  sentiment_ai.py     DeepSeek API 情绪分析
  dragon_ai.py        龙头识别ML辅助
  llm_advisor.py      LLM选股建议 (DeepSeek/Kimi)

禁止: 直接生成订单 / 绕过 Risk / 修改风控参数
```

### 07 Review — 复盘/统计/评价

```
来源: V2.8.6 22_Evolution (精简版) + 09_Test

功能:
  performance.py     策略绩效 (胜率/盈亏比/夏普/最大回撤)
  attribution.py     归因分析 (哪笔赚的? 哪笔亏的? 为什么?)
  experience.py      交易经验库 (成功案例/失败案例)
  schedule.py        复盘节奏 (日/周/月)

复盘闭环:
  交易 → 结果 → Review → Experience → Learning → 下次更好
```

---

## 三、交易主链 (硬编码, 不可绕过)

```
每笔交易:

  Data → Strategy → Risk → Execution → QMT → 市场
            ↑         ↑
            │ 评分     │ 参考
            └── Learning (只读)


Risk 决策:
  APPROVE → Execution 执行
  ADJUST  → 降低仓位/数量后执行
  REJECT  → 放弃 (记录原因, 反馈给 Review)


复盘闭环:
  成交 → Review(统计+归因) → Experience(经验存储) → Learning(模型优化)
```

---

## 四、V2.8.6 → Production 映射

| Production 模块 | V2.8.6 来源 | 保留 | 删除 |
|------|-----------|------|------|
| 01 Constitution | 02_Constitution | 14边界宪法+CC约束 | Meta宪法 |
| 02 Data | 07_Data + 10_Engineering | A股Schema+100因子+10表DDL | 数据流架构文档 |
| 03 Strategy | 04_Strategy + 03_AI_Brain | Dragon+Sentiment+适配矩阵 | P3 Runtime |
| 04 Risk | 05_Risk | 44公式+Kill Switch+仓位计算 | P3 Runtime |
| 05 Execution | 06_Execution + 99_Archive代码 | QMT适配+订单状态机+A股规则 | P3 Runtime |
| 06 Learning | 03_AI_Brain Prediction + DeepSeek | 预测插件+LLM插件 | World Model/Fusion |
| 07 Review | 22_Evolution(精简) + 09_Test | 绩效+归因+经验+复盘节奏 | 六环进化 |

### 冻结到 99_Research_Lab 的 V2.8.6 资产

```
99_Research_Lab/
├── 24_World_Model_System/        # 五层认知架构
├── Counterfactual Engine         # 反事实推理
├── 23_Agent_Intelligence_System/ # Multi-Agent
├── 25_Decision_Intelligence/     # AGI决策
├── 26_Cross_Market/              # 跨市场
├── 22_Evolution_System/          # 六环(精简版进Review)
├── P3 Runtime (14-21)            # 运行层(合并到各模块)
└── 03_AI_Brain 子模块            # World_Model/Reasoning/Knowledge (预测+情绪进Learning)
```

---

## 五、编码优先级

```
Phase 1: 数据 (3天)
  Data/sources/akshare → SQLite 10张表
  验证: 能看到今日涨停列表

Phase 2: 策略 (3天)
  Strategy/rules/dragon.py + sentiment.py
  验证: 输出情绪周期 + 龙头候选

Phase 3: 风控+执行 (2天)
  Risk/pre_trade.py + Execution/paper_broker.py
  验证: 模拟交易跑通

Phase 4: 复盘 (2天)
  Review/performance.py + experience.py
  验证: 日终自动生成复盘报告

Phase 5: Learning (3天)
  Learning/plugins/predictor.py + llm_advisor.py
  验证: AI提供评分/建议, 不参与交易链

Phase 6: QMT实盘 (1周)
  Execution/qmt_adapter.py, ≤10万, 单一策略
```

---

## 六、与行业对齐

| | 行业实战 (2026) | AQF-T Production |
|------|---------|------|
| 数据 | akshare + QMT Level-2 | ✅ 对齐 |
| 策略 | Dragon+Trend+Sentiment | ✅ 对齐 |
| 风控 | 三级风控+日内熔断 | ✅ 对齐 (Kill Switch) |
| 执行 | QMT/MiniQMT | ✅ 对齐 |
| AI | LightGBM + DeepSeek API | ✅ 插件化 |
| 复盘 | 手工Excel → 自动化 | ✅ Review模块 |
| 部署 | 本地Windows | ✅ 对齐 |

---

## 七、设计声明

本文件为 AQF-T V2.8.6 Production Architecture V1.0。

V2.8.6 不动。Production 是它的精简运行子集。

7 个生产模块。AI 是插件, 不参与交易主链。Strategy→Risk→Execution 硬链不可绕过。

研究级资产冻结在 99_Research_Lab, 不影响生产。

**From Design Library to Production System.**

Version: V1.0 | Status: Discussion Draft
END OF AQF-T PRODUCTION ARCHITECTURE
