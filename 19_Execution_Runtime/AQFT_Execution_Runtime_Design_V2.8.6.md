# AQFT Execution Runtime Design V3.6.0


# AQF-T 交易执行运行系统详细设计


Version: V3.6.0 | Status: Detailed Engineering Design
Date: 2026-07-26

> 参考: Backtrader Broker模型 + DolphinDB低延迟CEP + 行业Broker Adapter模式


---

# 第一章 架构


```
Risk Decision (APPROVE/ADJUST) → Order Manager → Execution Engine → Broker Gateway → Market
                                                      │
                                               Execution Monitor
                                                      │
                                               Feedback → Data/Experience
```

核心原则: 执行层不修改决策。只负责安全、高效地把订单送达市场。

---

# 第二章 订单管理 (借鉴 Backtrader Broker)


## 2.1 完整订单状态机

```
CREATED → PRE_CHECK → SUBMITTED → ACCEPTED → PARTIALLY_FILLED → FILLED → SETTLED
    │         │           │           │               │             │
    │         │           │           │               │             └→ 结算完成
    │         │           │           │               └→ 继续等待剩余
    │         │           │           └→ 部分成交(大单拆分)
    │         │           └→ REJECTED(交易所拒单)
    │         └→ REJECTED(Pre-Check失败: T+1/涨跌停/资金)
    └→ CANCELLED(用户/策略撤单)

异常终点: FAILED / EXPIRED
```

## 2.2 Pre-Check (下单前7项检查)

借鉴 FIA 2024 标准:
```
① 风控审批: risk_decision = APPROVE/ADJUST
② T+1: SELL方向 → 持仓可卖数量 ≥ 卖出数量
③ 涨跌停: BUY → 非涨停封死 / SELL → 非跌停封死
④ 资金: BUY → 可用资金 ≥ 价格×数量 + 预估费
⑤ 仓位: SELL → 持仓 ≥ 卖出数量
⑥ 手数: 股数 % 100 == 0
⑦ 交易时段: 9:30-11:30 | 13:00-15:00
```

---

# 第三章 Broker 适配 (借鉴行业多Broker模式)


借鉴 vnpy/WonderTrader 的 Broker Adapter 模式:

```
BrokerInterface (统一抽象):
  connect()
  disconnect()
  submit_order(order) → OrderResult
  cancel_order(order_id)
  query_order(order_id) → Order
  query_position(symbol) → Position
  query_account() → Account
  subscribe_quote(symbols)

实现:
  QMTLiveAdapter: xtquant → 真实下单 (实盘)
  PaperTradeAdapter: 本地模拟撮合 (模拟交易)
  BacktestAdapter: 历史数据回放 (回测)

切换: 修改 config/system.yaml → execution.mode
```

## 3.1 QMT实盘适配

```
连接: xtquant.XtQuantTrader(path, session_id)
行情: xtdata.subscribe_quote() / get_market_data()
下单: trader.order_stock(account, stock_code, order_type, price, volume)
撤单: trader.cancel_order_stock(account, order_id)
查询: query_stock_asset() / query_stock_positions() / query_stock_orders()
```

---

# 第四章 执行算法


| 算法 | 适用 | 说明 |
|------|------|------|
| Market | 游资追涨/止损 | 市价成交,速度优先 |
| Limit | 低吸/埋伏 | 限价成交,价格优先 |
| TWAP | 大单(>50万) | 时间加权,拆分执行 |
| VWAP | 大单+流动性好 | 成交量加权 |

游资场景以 Market Order 为主。大单自动降级为 TWAP。

---

# 第五章 连接管理


```
心跳检测: 每5秒 ping Broker
重连策略: 断开 → 1s/3s/10s/30s/60s 指数退避重连
超时: 连续5次失败 → 告警 + 暂停新订单 + 保留行情
恢复: 重连成功 → 健康检查 → 同步订单状态 → 恢复执行
```

---

# 第六章 监控


借鉴行业低延迟监控:

| 指标 | 告警阈值 |
|------|:---:|
| 订单延迟(提交→接受) | > 100ms |
| 成交延迟(提交→成交) | > 5s (Market单) |
| 滑点 | > 50bps |
| 拒单率 | > 5% |
| Broker连接 | 断开>10s |

---

# 第七章 API


| 端点 | 方法 | 功能 |
|------|:---:|------|
| POST /execution/order | POST | 提交订单 |
| GET /execution/order/{id} | GET | 查询订单 |
| POST /execution/order/{id}/cancel | POST | 撤单 |
| GET /execution/position | GET | 当前持仓 |
| GET /execution/account | GET | 账户信息 |
| GET /execution/trades | GET | 成交记录 |

---

# 第八章 设计冻结声明


本文件定义 AQF-T Execution Runtime V3.6.0。借鉴 Backtrader Broker 订单管理 + vnpy/WonderTrader Broker Adapter 模式 + DolphinDB CEP 低延迟架构 + FIA 2024 Pre-Trade标准。

Version: V3.6.0 | Status: Detailed Engineering Design
END OF AQFT EXECUTION RUNTIME DESIGN
