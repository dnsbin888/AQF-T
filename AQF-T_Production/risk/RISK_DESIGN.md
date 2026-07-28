# 04 Risk — 风控引擎 (最高否决权)

## 风险评分

```
Risk Score = Market×0.25 + Position×0.25 + Strategy×0.20 + Sentiment×0.15 + Liquidity×0.15

Market:     volatility_score×0.40 + trend_reversal×0.30 + systemic×0.30
Position:   position_ratio×0.50 + concentration×0.30 + leverage×0.20
Strategy:   drawdown×0.40 + consecutive_losses×0.30 + signal_quality×0.30
Sentiment:  情绪周期×0.50 + 炸板率×0.30 + 题材退潮×0.20 (游资核心)
Liquidity:  volume_decline×0.40 + spread_widening×0.30 + turnover_decline×0.30
```

## 决策

```
Risk Score < 30  → APPROVE (正常执行)
Risk Score 31-55 → APPROVE (仓位×0.8)
Risk Score 56-75 → ADJUST  (仓位×0.5)
Risk Score > 75  → REJECT  (禁止)

情绪周期覆盖:
  退潮期 + BUY信号 → REJECT (无论分数)
  冰点期 + Dragon  → REJECT (禁止打板)
  高潮期           → 可满仓70%
```

## 下单前7项检查

```
① Risk状态 = APPROVE/ADJUST
② T+1: SELL时持仓可卖数量≥卖出量
③ 涨跌停: BUY非涨停封死 / SELL非跌停封死
④ 资金: BUY时可用资金 ≥ 价格×数量+预估费
⑤ 仓位: 持仓 ≥ 卖出量
⑥ 手数: 股数%100==0
⑦ 时段: 9:30-11:30 | 13:00-15:00
```

## L2增强

```
虚假信号: 超大单流入 BUT 小单也流入 → Risk Score +20
对倒嫌疑: 大单成交 BUT 无放量 → 标记
涨停风控: 封单系数<3 → 禁止打板 | 撤单率>30% → 建议撤单
```

## Kill Switch

```
触发: 日亏>5% / 总回撤>15% / 连续5笔亏损 / 跌停>500家 / 手动
动作: 撤所有订单 + 停所有策略 + 市价清仓 + 断Broker + 通知
恢复: 人工确认 + 最低冷却30分钟
```
