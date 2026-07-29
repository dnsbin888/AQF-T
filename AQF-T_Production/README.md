# AQF-T Production

**Version:** 1.0 | **Date:** 2026-07  
**定位:** A股游资/个人量化 生产级自动交易系统  
**前置:** 国金证券QMT + Level-2数据(已开通)  
**设计母库:** ../V2.8.6 (不动, 仅引用)

---

## 架构

```
Constitution     交易制度
Market Regime    总开关 (今天能不能做?)
Data             QMT L2 + akshare
Perception       8层感知
Path A           回封板 (规则)
Path B           半路/接力 (ML统计)
Decision Core    融合/优先级/仓位分配
Risk             合法?超仓?熔断?
Execution        国金QMT
Knowledge Hub    归因/经验/训练/注册
Learning(旁路)   预测/确认/记忆/LLM
```

## 决策主链 (不可绕过)

```
Market Regime → Perception → Path A/B → Decision Core → Risk → Execution → QMT
                                               ↑
                                        Learning (旁路, 只提供评分)
```

## 三条铁律

```
1. AI 永远不直接下单
2. Risk 拥有最高否决权, 不可绕过
3. 交易主链 Strategy→Risk→Execution 硬编码
```

---

## 模块速览

### Market Regime (总开关)
每天第一个运行。回答: 今天能不能做? 退潮→全停 / 冰点→仅B2 / 回暖→A+B / 高潮→A+B满仓

### Data
国金QMT L2(逐笔/十档/队列/大单) + akshare(涨停/龙虎榜)。SQLite 14张表。100因子。

### Perception (8层感知)
市场级: 情绪周期/涨停梯队/题材热度/赚钱效应
个股级: 炸板分类/回封确认/对手识别/足迹检测

### Path A — 回封板 (规则, 70-85%胜率)
板块地位→炸板分类(洗盘/诱多)→回封确认(缩量/快速/联动, ≥2进场)

### Path B — 半路/接力 (ML统计)
B1 Trend(LGBM三目标) / B2 Theme(规则) / B3 Intraday(XGBoost确认器)

### Decision Core
融合A/B信号, 冲突解决(Hypothesis Arbitration), 仓位分配(A优先于B)

### Risk (最高否决权)
44公式+7项检查+Kill Switch。APPROVE/ADJUST/REJECT

### Execution
国金miniQMT直连。Paper Broker模拟交易。T+1/涨跌停/真实费率

### Knowledge Hub
归因+经验+训练历史+模型注册+绩效评估+日/周/月报告

### Learning (旁路)
Offline: 训练/回测/数据集。Online: 预测/确认/记忆。LLM: DeepSeek/Qwen

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
| 2 | Market Regime + Perception | 情绪周期判断准确 > 80% |
| 3 | Path A (回封板) | 炸板分类+回封确认 模拟验证 |
| 4 | Path B (半路/接力) | LGBM回测 IC>0.05 |
| 5 | Decision + Risk + Execution | Paper Trading 跑通 |
| 6 | Knowledge Hub + Learning | 日终自动复盘报告 |
| 7 | 实盘: miniQMT | ≤10万, 人工监控 |

---

## V2.8.6 引用清单

```
Production 模块        V2.8.6 设计来源

01_Constitution    ←  02_Constitution (14边界宪法 C004-C016)
02_Data            ←  07_Data (6类A股数据源 + Schema)
                       10_Engineering (10表DDL + 100因子公式)
03_Strategy        ←  04_Strategy (Dragon + 5策略 + 适配矩阵)
                       03_AI_Brain §4 (情绪引擎 + 题材热度)
04_Risk            ←  05_Risk (44公式 + KillSwitch + 仓位计算)
05_Execution       ←  06_Execution (订单状态机 + A股规则 + QMT)
                       99_Archive代码 (qmt_adapter, a_share_rules)
06_Learning        ←  03_AI_Brain §3 (Prediction Engine)
                       10_Engineering (100因子)
07_Review          ←  22_Evolution (精简版)
                       09_Test (回测+压力场景)
```

## 设计原则

```
1. 不修改V2.8.6。本系统是独立生产版本。
2. 直接可用。国金QMT+L2已开通, 不依赖外部付费API。
3. 单机运行。Windows台式机, SQLite, 零Docker。
4. AI是插件。不是一级架构。不参与交易主链。
5. 游资优先。Dragon龙头战法 + L2订单流 + 情绪周期。
```
