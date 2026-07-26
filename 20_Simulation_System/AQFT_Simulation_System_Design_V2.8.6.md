# AQFT Simulation System Design V3.6.0


# AQF-T 模拟交易系统详细设计


Version: V3.6.0 | Status: Detailed Engineering Design
Date: 2026-07-26

> 参考: DolphinDB 模拟撮合引擎 + Backtrader Broker模型 + 行业统一引擎架构


---

# 第一章 统一引擎架构


借鉴行业最佳实践: **回测与模拟交易共享同一撮合核心**，通过插件化数据源和时钟实现切换。

```
同一引擎核心:
  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
  │ Data Feed   │────▶│ Strategy     │────▶│ Risk Check  │
  │ (历史/实时)  │     │ Engine       │     │ (Pre-Trade) │
  └─────────────┘     └──────────────┘     └──────┬──────┘
                                                   │
  ┌─────────────┐     ┌──────────────┐             │
  │ Performance │◀────│ Portfolio    │◀────────────┘
  │ Report      │     │ Manager      │
  └─────────────┘     └──────┬───────┘
                              │
                    ┌─────────┴─────────┐
                    │  Matching Engine  │
                    │  (同一撮合核心)    │
                    └───────────────────┘

回测模式: HistoricalDataFeed + BatchClock → 同一撮合核心 → 历史绩效
模拟模式: RealtimeDataFeed + RealtimeClock → 同一撮合核心 → 模拟绩效
```

---

# 第二章 撮合引擎 (借鉴 DolphinDB 订单簿匹配)


## 2.1 撮合层级

| 层级 | 模式 | 适用 |
|:---:|------|------|
| L1 | 理想撮合: 按行情价直接成交 | 快速验证 |
| L2 | 滑点撮合: 市价±随机滑点 | 日常模拟 |
| L3 | 盘口撮合: 按买卖一档成交 | 打板模拟 |
| L4 | 订单簿撮合: 按深度逐档成交 | 大单模拟 |

AQF-T 默认使用 **L3 盘口撮合**（游资打板场景需要精确的封板/炸板模拟）。

## 2.2 撮合规则

```
市价单 BUY:
  fill_price = ask1 × (1 + slippage)
  成交概率 = 95% (正常), 10% (涨停封死)

市价单 SELL:
  fill_price = bid1 × (1 - slippage)
  成交概率 = 95% (正常), 10% (跌停封死)

限价单 BUY:
  成交条件: price ≤ 当前价
  fill_price = min(limit_price, ask1)

限价单 SELL:
  成交条件: price ≥ 当前价
  fill_price = max(limit_price, bid1)
```

## 2.3 A股特有撮合规则

```
涨停封死: BUY → fill_probability = 0.05 (几乎买不到)
跌停封死: SELL → fill_probability = 0.05 (几乎卖不出)
T+1: 当日买入 → 标记locked → 次日才可卖
```

## 2.4 滑点模型

| 模型 | 公式 | 场景 |
|------|------|------|
| 固定 | ±5bps | 流动性好的大票 |
| 成交量比例 | slippage = order_size/avg_volume × 0.1 | 小票 |
| 波动率自适应 | slippage = base × (1 + volatility/avg_vol) | 高波动 |

---

# 第三章 模拟交易模式


借鉴行业 Shadow Mode 最佳实践:

```
Paper Trading:
  行情: 真实实时行情 (QMT/akshare)
  撮合: 本地模拟撮合引擎
  资金: 虚拟资金
  风控: 完整风控链路运行
  目的: 验证策略逻辑+风控有效性, 零资金风险
  要求: ≥ 1个月 + 与回测偏差 < 30%
```

---

# 第四章 虚拟组合管理 (借鉴 Backtrader Broker)


```
VirtualPortfolio:
  cash: float                         # 可用资金
  frozen_cash: float                  # 冻结资金(挂单中)
  positions: {symbol: Position}
  total_value: float                  # 总权益
  peak_value: float                   # 历史峰值(算回撤)
  realized_pnl: float
  unrealized_pnl: float

每笔成交后更新:
  ① 扣除手续费
  ② 更新持仓/均价
  ③ 更新现金
  ④ 更新权益曲线
  ⑤ 检查回撤是否触发熔断
```

---

# 第五章 审计轨迹


借鉴行业标准，每笔模拟成交记录 8 项元数据:

```
SimulationRecord:
  timestamp: 精确成交时间
  symbol: 标的
  side: BUY/SELL
  fill_price: 成交价(含滑点)
  fill_quantity: 成交股数
  fee_detail: {commission, stamp_tax, transfer_fee}
  position_before: 持仓快照前
  position_after: 持仓快照后
  cash_after: 成交后资金
  slippage_bps: 滑点(基点)
```

---

# 第六章 回测模式


```
Backtest:
  输入: 历史数据 (3年+), 初始资金, 策略参数
  约束: T+1 + 涨跌停 + 真实费率 + 滑点
  输出: 权益曲线 + 绩效指标 + 交易明细

评价指标:
  年化收益 / 夏普比率 / 最大回撤 / 胜率 / 盈亏比 / Calmar比率
```

---

# 第七章 API


| 端点 | 方法 | 功能 |
|------|:---:|------|
| POST /simulation/start | POST | 启动模拟交易 |
| POST /simulation/stop | POST | 停止 |
| GET /simulation/status | GET | 模拟状态 |
| GET /simulation/portfolio | GET | 虚拟组合 |
| POST /backtest/run | POST | 运行回测 |
| GET /backtest/result/{id} | GET | 回测结果 |

---

# 第八章 设计冻结声明


本文件定义 AQF-T Simulation System V3.6.0。借鉴 DolphinDB 订单簿撮合引擎 + Backtrader Broker 组合管理 + 行业统一引擎架构(回测=模拟=同一核心)。

Version: V3.6.0 | Status: Detailed Engineering Design
END OF AQFT SIMULATION SYSTEM DESIGN
