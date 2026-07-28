# AQF-T Slim — 精简实战架构 V1.0


# AQF-T 精简实战版架构设计

**Version:** V1.0 | **Status:** Draft Proposal | **Date:** 2026-07-28
**定位:** 基于V2.8.6冻结基线, 面向游资/个人量化A股实战的精简可编码版本


---

## 零、设计原则

```
1. 只有5个一级模块 (Data/Strategy/Risk/Execution/Learning)
2. 所有AI算法是插件, 挂在Learning下
3. AI永远不直接下单。交易主链: Strategy → Risk → Execution (硬链, 不可绕过)
4. 借鉴行业实战, 不做基础研究。能用QMT就用QMT, 能用LightGBM就用LightGBM
5. V2.8.6冻结基线不动。本文件是独立精简版, 用于指导编码
```

---

## 一、架构全景

```
AQF-T Slim

┌─────────────────────────────────────────────────────────┐
│                    Data (数据)                           │
│  sources: akshare / QMT Level-2 / tushare               │
│  storage: SQLite (单机) → PostgreSQL (团队)              │
│  features: 100个A股因子 (复用V2.8.6 10_Engineering)      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Strategy (策略) — 交易主链              │
│  rules/                                                  │
│    dragon.py      龙头战法 (复用V2.8.6 04_Strategy)      │
│    trend.py       趋势策略                                │
│    sentiment.py   情绪周期择时                             │
│  signals.py       统一信号 → TradingSignal (14字段)       │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Risk (风控) — 交易主链, 最高否决权     │
│  pre_trade.py     7项下单前检查                           │
│  limits.py        限额 (单票≤10%, 日亏≤3%, 总回撤≤15%)   │
│  kill_switch.py   紧急熔断                                │
│  formulas.py      风险评分公式 (复用V2.8.6 05_Risk 44公式)│
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 Execution (执行) — 交易主链               │
│  qmt_adapter.py   QMT/MiniQMT 实盘                       │
│  paper_broker.py  模拟交易                                │
│  order_manager.py 订单状态机 (复用V2.8.6 06_Execution)    │
│  a_share_rules.py T+1/涨跌停/费率 (复用V2.8.6)           │
└─────────────────────────────────────────────────────────┘

                           ║
                     QMT/券商柜台
                           ║
                        A股市场


┌─────────────────────────────────────────────────────────┐
│                 Learning (AI) — 纯建议, 不参与交易链      │
│                                                         │
│  plugins/      (所有AI算法是插件)                        │
│    predictor.py        LightGBM 趋势预测 (复用03_AI_Brain)│
│    sentiment_ai.py     DeepSeek API 情绪分析              │
│    dragon_ai.py        龙头识别辅助                       │
│    llm_advisor.py      LLM 选股建议 (DeepSeek/Kimi)      │
│                                                         │
│  backtest/      回测引擎 (事件驱动, A股规则)              │
│  experience/    经验记忆 (成功/失败案例库)                 │
│                                                         │
│  输出: 评分/概率/建议 → Strategy 和 Risk 参考             │
│  禁止: 直接生成订单                                      │
└─────────────────────────────────────────────────────────┘
```

---

## 二、决策链 (硬编码, 不可绕过)

```
每笔交易必须经过:

  Data → Strategy → Risk → Execution → QMT
            ↑         ↑
            │ 评分/建议 │
            └── Learning (纯建议, 只读)

Risk 拥有最高否决权:
  APPROVE → Execution 执行
  ADJUST  → 降低仓位后执行
  REJECT  → 放弃交易

Learning 的AI输出:
  ✅ 可以: 提供评分、概率、建议、经验
  ❌ 禁止: 直接生成订单、绕过Risk、修改风控参数
```

---

## 三、模块详细设计

### 3.1 Data — 复用 V2.8.6: 07_Data + 10_Engineering

```
sources/
  akshare_source.py    # 免费日线+涨停+龙虎榜
  qmt_source.py        # QMT Level-2实时行情
  tushare_source.py    # 财务数据

storage/
  sqlite_store.py      # 10张表DDL (10_Engineering)
  cache.py             # 三级缓存 (15_Data_Runtime)

features/
  technical.py         # 30个技术因子
  alpha.py             # 30个Alpha因子
  sentiment.py         # 20个情绪因子 (含涨停/龙虎榜/北向)
  capital.py           # 20个资金因子
  → 全部100个因子公式复用 V2.8.6 10_Engineering
```

### 3.2 Strategy — 复用 V2.8.6: 04_Strategy + 03_AI_Brain Sentiment

```
rules/
  dragon.py
    龙头判定: 连板≥3 + 题材涨停≥5 + 封单/流通>5% + 游资席位
    买入: 首板打板 / 二板接力 / 弱转强
    卖出: 炸板>10分钟 / 竞价低开>3% / 题材退潮 / 连板中断 / 异动

  trend.py
    买入: MA5上穿MA20 + 放量>1.5倍
    卖出: MA5下穿MA20 / 止损-5%

  sentiment.py
    情绪值 = 涨停×2 - 跌停×3 + 连板×5 + 北向×10
    冰点(<20): 试错首板, 仓位1-2成
    回暖(20-50): 接力二板, 仓位3-5成
    高潮(50-80): 龙头锁仓, 仓位5-7成
    退潮(>80): 空仓/轻仓

signals.py
  输出: TradingSignal (14字段, 复用V2.8.6 04_Strategy Schema)
```

### 3.3 Risk — 复用 V2.8.6: 05_Risk

```
formulas.py
  Risk Score = Market×0.25 + Position×0.25 + Strategy×0.20 + Sentiment×0.15 + Liquidity×0.15
  (44个公式, 复用V2.8.6 05_Risk)

limits.py
  单票≤10% | 总仓位≤70% | 日亏损≤3% | 总回撤≤15%
  退潮期强制≤20%仓位
  冰点期禁止Dragon Strategy

pre_trade.py (7项检查)
  Risk状态 | T+1 | 涨跌停 | 资金 | 仓位 | 手数(100股) | 交易时段

kill_switch.py
  6触发条件 → 撤单+停策略+清仓+断Broker+通知
```

### 3.4 Execution — 复用 V2.8.6: 06_Execution + 99_Archive V3代码

```
qmt_adapter.py   # MiniQMT/xtquant 封装 (复用99_Archive V3代码)
paper_broker.py  # 模拟撮合 (滑点+手续费+涨跌停)
order_manager.py # 订单状态机

a_share_rules.py
  T+1引擎 | 涨跌停引擎(5档) | 费率引擎 | 结算引擎
  → 全部复用 V2.8.6 06_Execution + 99_Archive代码
```

### 3.5 Learning — 插件化, 纯建议

```
plugins/
  predictor.py        LightGBM/CatBoost 趋势预测
  sentiment_ai.py     DeepSeek API 情绪分析
  dragon_ai.py        龙头识别ML辅助
  llm_advisor.py      LLM选股建议 (DeepSeek/Kimi/阶跃星辰)

backtest/
  事件驱动引擎 | A股规则(T+1/涨跌停/费率/滑点) | 绩效报告

experience/
  成功案例库 | 失败案例库 | 经验检索
```

---

## 四、与 V2.8.6 的映射

| Slim模块 | 复用V2.8.6资产 |
|---------|---------------|
| Data | 07_Data (6类A股数据源+AuctionData/LongHuRecord) + 10_Engineering (10表DDL) |
| Strategy | 04_Strategy (Dragon+6策略+适配矩阵) + 03_AI_Brain (Sentiment Engine) |
| Risk | 05_Risk (44公式+Kill Switch+仓位计算) |
| Execution | 06_Execution (订单状态机+QMT适配+A股规则) + 99_Archive代码 |
| Learning | 03_AI_Brain (Prediction Engine) + 10_Engineering (100因子) + DeepSeek API (新增) |

**不纳入Slim的V2.8.6资产:**
- 24_World_Model (五层认知) → 行业实战不需要
- Counterfactual Engine → 游资不关心"如果当时"
- Multi-Agent投票 → 游资一个人决策
- 22_Evolution六环 → 精简为Learning/experience
- P3 Runtime (14-21) → 合并到5个Slim模块内部

---

## 五、编码优先级

```
Phase 1 (本周): 跑通数据
  Data/sources/akshare → SQLite → 能看到涨停列表

Phase 2 (下周): 算情绪+找龙头
  Strategy/sentiment.py → 情绪值 → 四阶段
  Strategy/dragon.py → 龙头判定 → 候选标的

Phase 3: 加风控+模拟跑
  Risk/pre_trade.py + limits.py → 下单前检查
  Execution/paper_broker.py → Paper Trading 1个月

Phase 4: QMT实盘 (小资金验证)
  Execution/qmt_adapter.py → ≤10万, 单一策略
```

---

## 六、设计声明

本文件为 AQF-T Slim V1.0 精简实战版架构。基于 V2.8.6 冻结基线, 面向游资/个人量化A股实战。5个一级模块, AI纯建议不下单。V2.8.6原有资产不动。

**Slim is not a replacement. It is the executable subset of V2.8.6.**

Version: V1.0 | Status: Draft Proposal
END OF AQF-T SLIM ARCHITECTURE
