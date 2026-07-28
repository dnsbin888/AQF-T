# AQF-T Production

**Version:** 1.0 | **Date:** 2026-07  
**定位:** A股游资/个人量化 生产级自动交易系统  
**前置:** 国金证券QMT + Level-2数据(已开通)  
**设计母库:** ../V2.8.6 (不动, 仅引用)

---

## 架构

```
01_Constitution    交易制度 (不可违反)
02_Data            数据 (QMT L2 + akshare)
03_Strategy        策略 (规则 + L2订单流 + Dragon)
04_Risk            风控 (最高否决权)
05_Execution       执行 (国金miniQMT)
06_Learning        AI插件 (纯建议, 不参与交易链)
07_Review          复盘 (因子归因 + L2复盘 + 经验)
```

## 决策主链 (不可绕过)

```
Data → Strategy → Risk → Execution → 国金QMT → A股
         ↑         ↑
         └── Learning (评分/建议, 只读不写)

Risk: APPROVE → 执行 | ADJUST → 降仓执行 | REJECT → 放弃
```

## 三条铁律

```
1. AI 永远不直接下单
2. Risk 拥有最高否决权, 不可绕过
3. 交易主链 Strategy→Risk→Execution 硬编码
```

---

## 模块速览

### 01 Constitution
交易制度。引用V2.8.6: 14边界宪法(C004-C016)。限额: 单票≤10%, 日亏≤3%, 总回撤≤15%。

### 02 Data
- **L2**: 国金QMT — 逐笔成交/十档盘口/委托队列/大单统计
- **L1**: QMT基础 — 分钟/日K线  
- **Free**: akshare — 涨停列表/龙虎榜/财务
- **存储**: SQLite 14张表 (10基础+4 L2)
- **因子**: 100个 (技术30+Alpha30+情绪20+资金20)

### 03 Strategy
- **规则**: Dragon龙头战法 / Trend趋势 / Sentiment情绪周期 / VolumePrice量价 / Defensive防御
- **L2**: OrderFlow订单流 / LimitUpL2涨停增强 / OrderBook盘口失衡
- **信号**: TradingSignal统一14字段输出

### 04 Risk
- **公式**: 五因子评分(44公式, 引用V2.8.6 05_Risk)
- **限额**: 单票≤10% / 日亏≤3% / 总回撤≤15%
- **L2过滤**: 虚假信号识别 / 涨停风控(封单系数/撤单率/炸板)
- **Kill Switch**: 6触发→撤单+停策略+清仓

### 05 Execution
- **实盘**: 国金miniQMT (xtquant)
- **模拟**: 本地Paper Trading
- **规则**: T+1/涨跌停5档/真实费率/100股手数
- **模式**: QMT完整版(研发回测) + miniQMT(7×24挂机, 500MB)

### 06 Learning (AI插件)
- **本地**: LightGBM/CatBoost 趋势预测
- **云端**: Qwen(因子挖掘 IC2.95%) + DeepSeek(选股)
- **L2**: 模式识别(拆细/对倒/托单/压单)
- **禁止**: 直接下单 / 绕过Risk / 修改风控参数

### 07 Review
- **绩效**: 胜率/盈亏比/夏普/最大回撤
- **归因**: 因子贡献拆解 / 幸存者偏差修正
- **L2复盘**: 逐笔回放 / 主力行为回溯 / 封板质量
- **经验**: 成功/失败案例库
- **节奏**: 日/周/月

---

## 文件结构

```
AQF-T_Production/
├── README.md              本文件
├── constitution/           交易制度
├── data/                   数据采集+存储+因子
│   ├── sources/             QMT L2 / QMT L1 / akshare
│   ├── storage/             SQLite 14张表
│   └── features/            100个因子
├── strategy/               策略引擎
│   ├── rules/               规则策略
│   └── l2/                  L2专属策略
├── risk/                   风控引擎
├── execution/              执行引擎
│   └── guojin_qmt.py       国金miniQMT
├── learning/               AI插件
│   └── plugins/             模型插件
├── review/                 复盘系统
├── config/                 配置文件
├── tests/                  测试
└── logs/                   运行日志
```

---

## 编码顺序

| 阶段 | 内容 | 验证标准 |
|------|------|---------|
| 1 | Data: QMT L2→SQLite | xtdata.getl2transaction() 有数据 |
| 2 | Strategy: Dragon+情绪+L2订单流 | 输出情绪周期+龙头+L2信号 |
| 3 | Risk+Execution: 风控+miniQMT模拟 | Paper Trading 跑通 |
| 4 | Review: 归因+经验 | 日终自动复盘报告 |
| 5 | Learning: LightGBM+Qwen+DeepSeek | AI评分, 不参与交易链 |
| 6 | 实盘: miniQMT | ≤10万, 单一策略, 人工监控 |

---

## 设计原则

```
1. 不修改V2.8.6。本系统是独立生产版本。
2. 直接可用。国金QMT+L2已开通, 不依赖外部付费API。
3. 单机运行。Windows台式机, SQLite, 零Docker。
4. AI是插件。不是一级架构。不参与交易主链。
5. 游资优先。Dragon龙头战法 + L2订单流 + 情绪周期。
```
