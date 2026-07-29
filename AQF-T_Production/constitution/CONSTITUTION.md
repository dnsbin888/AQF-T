# 01 Constitution — 交易制度

## 四条铁律

```
1. AI不直接下单
2. Risk最高否决权 (Strategy→Decision→Risk→Execution硬链不可绕过)
3. 退潮期两条路都禁止买入 (Market Regime总开关)
4. 未经回测→模拟盘→小资金实盘三级验证的能力, 不得进入Production主链
```

## 工程原则

```
任何新策略/模型/插件, 必须先通过P0验证基础设施, 再进入回测/模拟/实盘:

  New Strategy → Data Quality → L2 Replay → Decision Trace → Execution Metrics
     → 四项全部通过 → Backtest → Paper → Live

  验证链回答四个问题:
    Data Quality:     数据是真的吗?
    L2 Replay:        历史上真的能做出来吗?
    Decision Trace:   系统当时为什么这么决定?
    Execution Metrics: 即使判断正确, 是否真正执行到了?
```

## 不可违反

```
1. 单票仓位 ≤ 10%
2. 日亏损 ≥ 3% → 停止当日交易
3. 总回撤 ≥ 15% → Safe Mode (仅允许平仓)
4. 退潮期 → 总仓位强制 ≤ 20%，禁止Dragon Strategy
5. Risk 不可绕过，不可关闭
6. AI 不可直接下单
7. 所有交易必须记录：时间/标的/方向/数量/价格/信号来源/风控结果/盈亏
```

## 交易主链 (硬编码)

```
Strategy → Risk → Execution
   ↑         ↑
   └── Learning (只提供评分/建议/经验)
```

## 14 边界宪法 (引用 V2.8.6: 02_Constitution)

```
C004: Strategy   — 生成信号，不执行交易
C005: Portfolio  — 组合管理，单票≤10%
C006: Position   — 仓位管理，T+1不可卖当日买入
C007: Order      — 只执行 Risk APPROVE/ADJUST 的订单
C008: QMT        — 唯一实盘通道
C010: Market     — 识别当前Regime+情绪周期
C011: LimitUp    — 涨停封单系数<3禁止打板
C012: Participant— 识别主力/游资/量化/散户行为
C015: Confidence — AI输出必须附带置信度
```
