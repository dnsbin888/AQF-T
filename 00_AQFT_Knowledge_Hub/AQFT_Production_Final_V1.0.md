# AQF-T Production Final V1.0


# AQF-T 生产架构终版

**Version:** V1.0 | **Date:** 2026-07-28 | **Status:** Discussion

**前提:** V2.8.6 设计母库(不动) + 国金QMT + L2数据(已开通) + miniQMT实盘


---

## 架构总图

```
┌─────────────────────────────────────────────────┐
│              V2.8.6 设计母库 (不动)               │
│  22模块 | 88文档 | 569KB | 全部知识保留           │
│  生产引用: 04_Strategy 05_Risk 06_Execution       │
│           07_Data 10_Engineering 02_Constitution  │
└─────────────────────────────────────────────────┘
                     │ 知识引用
                     ▼
┌─────────────────────────────────────────────────┐
│           AQF-T Production (7模块)               │
│                                                 │
│  01 Constitution   交易制度 (14边界宪法)          │
│  02 Data           QMT L2 + akshare + 10张表     │
│  03 Strategy       规则 + L2订单流 + Dragon       │
│  04 Risk           44公式 + Kill Switch + L2过滤  │
│  05 Execution      国金miniQMT直连                │
│  06 Learning       LightGBM+Qwen+DeepSeek 插件    │
│  07 Review         因子归因+L2复盘+经验库          │
└─────────────────────────────────────────────────┘
                     │
                     ▼
              国金miniQMT (实盘)
                     │
                  A股市场
```


---

## 模块定义

### 01 Constitution — 引用 V2.8.6: 02_Constitution

```
保留: 14边界宪法 (C004-C016) + CC最高约束 + MC-016
删减: Meta宪法 / AI协作模型 (单兵作战不需要)
作用: 交易纪律。单票≤10% / 日亏≤3% / 总回撤≤15% / Risk不可绕过
```

### 02 Data — 引用 V2.8.6: 07_Data + 10_Engineering

```
数据源 (三级, 均已可用):
  L2: 国金QMT
    xtdata.getl2transaction()  — 逐笔成交
    xtdata.getl2order()        — 逐笔委托
    xtdata.subscribe_quote()   — 十档盘口+委托队列
    xtdata.getl2transactioncount() — 大单统计

  L1: QMT基础
    xtdata.get_market_data()   — 分钟/日K线

  Free: akshare (兜底)
    涨停列表 / 龙虎榜(T+1) / 财务数据

存储: SQLite 10张表 (复用 V2.8.6 DB Schema)
  新增4张L2表: l2_transaction / l2_order / l2_orderbook_snapshot / l2_block_stats

因子: 100个 (复用 V2.8.6 10_Engineering)
  技术30 + Alpha30 + 情绪20 + 资金20
```

### 03 Strategy — 引用 V2.8.6: 04_Strategy + 03_AI_Brain Sentiment

```
规则策略 (主力):
  dragon.py        龙头战法 (6判定+3买入+5卖出)
  trend.py         趋势策略 (MA金叉+放量)
  sentiment.py     情绪周期 (四阶段+情绪值公式)
  volume_price.py  量价策略 (N字反包+弱转强)
  defensive.py     防御策略 (降仓/空仓)

L2策略 (国金QMT专属):
  orderflow.py     订单流策略
    大单拆细识别 / DDX/DDY/DDZ三维监控 / 资金共振
  limitup_l2.py    涨停L2增强
    封单系数 / 队列断层 / 撤单率 / 真封板vs假封板
  orderbook.py     盘口失衡策略
    失衡率>0.7做多 / <-0.6反转

信号融合:
  规则策略 + L2策略 → TradingSignal (14字段)
  优先级: 情绪周期约束 > L2信号 > 规则信号 > AI建议
```

### 04 Risk — 引用 V2.8.6: 05_Risk

```
核心 (复用44个公式):
  formulas.py      五因子评分 = Market×0.25+Position×0.25+Strategy×0.20+Sentiment×0.15+Liquidity×0.15
  limits.py        限额 (单票≤10%/日亏≤3%/总回撤≤15%)
  pre_trade.py     7项下单前检查
  kill_switch.py   6触发→撤单+停策略+清仓

L2增强:
  fake_signal.py   虚假信号过滤
    超大单流入BUT小单也流入 → 主力诱多 → Risk Score+20
    大单成交BUT无放量 → 对倒嫌疑 → 标记
  limitup_risk.py  涨停风控
    封单系数<3 → 禁止打板
    撤单率>30% → 建议撤单
    炸板>10分钟 → 强制卖出

输出: APPROVE / ADJUST / REJECT (不可绕过)
```

### 05 Execution — 国金miniQMT直连

```
guojin_qmt.py:
  from xtquant import XtQuantTrader
  trader = XtQuantTrader(path, session_id)
  trader.start()
  trader.connect()
  
  下单: trader.order_stock(account, code, type, price, volume)
  撤单: trader.cancel_order_stock(account, order_id)
  查询: query_stock_asset() / query_stock_positions() / query_stock_orders()

paper_broker.py:   本地模拟撮合 (Paper Trading验证用)
order_manager.py:  订单状态机 (复用 V2.8.6 06_Execution)
a_share_rules.py:  T+1/涨跌停/费率 (复用 V2.8.6)

模式:
  研发: QMT完整版 (策略编写+回测)
  实盘: miniQMT (500MB内存, 7×24静默挂机)
```

### 06 Learning — 三引擎插件

```
本地主力:
  predictor_lgb.py     LightGBM/CatBoost 趋势预测

云端辅助:
  factor_qwen.py       Qwen API 因子挖掘 (IC 2.95%)
  stock_deepseek.py    DeepSeek API 选股建议

L2模式:
  l2_pattern.py        L2模式识别 (拆细/对倒/托单/压单)

输出: 评分/概率/建议 → Strategy和Risk参考
禁止: 直接生成订单 / 绕过Risk / 修改风控参数
```

### 07 Review — 复盘闭环

```
performance.py       策略绩效 (胜率/盈亏比/夏普/最大回撤)
factor_attribution.py 因子归因 (哪笔赚的?哪个因子贡献的?)
l2_review.py          L2复盘 (逐笔回放/主力行为回溯/封板质量)
experience.py         交易经验库 (成功案例/失败案例)
schedule.py           复盘节奏 (日/周/月)
survivorship.py       幸存者偏差修正 (IC计算含买入失败)

复盘闭环: 交易→结果→Review→Experience→Learning→下次更好
```


---

## 决策主链 (不可绕过)

```
Data → Strategy → Risk → Execution → 国金QMT → A股市场
         ↑         ↑
         │ 评分/建议 │
         └── Learning (纯建议, 只读)

Risk 决策:
  APPROVE → Execution 执行
  ADJUST  → 降低仓位/数量后执行
  REJECT  → 放弃 (记录原因, 反馈Review)

复盘闭环:
  成交 → Review(归因) → Experience(经验) → Learning(优化)
```


---

## 编码优先级

```
Phase 1 (3天): Data
  QMT L2 → SQLite 14张表 (10+4 L2)
  验证: xtdata.getl2transaction() 有数据流

Phase 2 (3天): Strategy
  dragon.py + sentiment.py + orderflow.py
  验证: 输出情绪周期+Dragon候选+L2订单流信号

Phase 3 (2天): Risk + Execution
  pre_trade.py + guojin_qmt.py (paper模式)
  验证: 模拟交易跑通

Phase 4 (2天): Review
  factor_attribution.py + experience.py
  验证: 日终自动生成复盘报告

Phase 5 (3天): Learning
  predictor_lgb.py + factor_qwen.py
  验证: AI提供评分, 不参与交易链

Phase 6 (1周): 实盘验证
  miniQMT, ≤10万, 单一策略, 人工监控
```


---

## 设计声明

V2.8.6 设计母库不动。本文件是 Production 运行架构终版。

7个模块。AI是插件。Strategy→Risk→Execution硬链不可绕过。

基于 国金QMT + L2数据 实战。不做基础研究, 不做迭代工作。

**From Design Library to Live Trading.**

Version: V1.0 | Status: Discussion
END OF AQF-T PRODUCTION FINAL
