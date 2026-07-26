# AQFT Execution Design V3.6.0


# AQF-T 交易执行体系详细设计


Version: V3.6.0
Status: Detailed Engineering Design
Classification: AQF-T 交易执行核心设计文件
Date: 2026-07-26


---

# 第一章 执行体系定位


Execution 模块是 AQF-T 从智能决策到实际交易行为的执行层。只执行经 Risk 批准的指令。

```
Risk Decision (APPROVE/ADJUST) → Order Manager → Execution Engine → Broker Interface → Market
                                                                           ↓
                                                                    Execution Feedback → Data → AI Learning
```

**核心原则: 准确、安全、高效。不修改决策，不绕过风控。**

---

# 第二章 订单管理系统


## 2.1 订单状态机

```
CREATED → PRE-CHECK → SUBMITTED → ACCEPTED → PARTIALLY_FILLED → FILLED → COMPLETED
    │         │           │           │               │             │
    │         │           │           │               │             └→ SETTLEMENT
    │         │           │           │               └→ 继续等待成交
    │         │           │           └→ 部分成交 (大单拆分)
    │         │           └→ REJECTED (交易所拒单)
    │         └→ REJECTED (风控二次确认失败)
    └→ CANCELLED (用户/策略撤单)

异常终点: REJECTED / CANCELLED / FAILED / EXPIRED
```

## 2.2 A股特殊状态

```
涨跌停状态:
  LIMIT_UP_LOCKED: 涨停封死, 买盘排队, 可能无法成交
  LIMIT_DOWN_LOCKED: 跌停封死, 卖盘无法成交

T+1状态:
  TODAY_BOUGHT_LOCKED: 当日买入, 不可卖出
  AVAILABLE_TOMORROW: 次日才可卖

停牌状态:
  SUSPENDED: 暂停交易, 订单自动失效
```

## 2.3 订单数据结构

```
Order:
  order_id: str                  # AQFT-ORD-00001
  symbol: str                    # SH.600519
  exchange: str                  # SH/SZ/BJ

  side: BUY | SELL
  quantity: int                  # 股数 (100的整数倍)
  price: float                   # 委托价
  type: MARKET | LIMIT

  risk_approval_id: str          # 风险审批ID (必填)
  strategy_signal_id: str        # 策略信号ID (可追溯)

  status: OrderStatus
  filled_quantity: int           # 已成交
  filled_avg_price: float        # 成交均价
  fee: float                     # 手续费
  slippage: float                # 滑点

  a_share_specific:
    t_plus_one_locked: bool      # T+1锁定
    limit_up_locked: bool        # 涨停锁定
    limit_down_locked: bool      # 跌停锁定
    is_suspended: bool           # 停牌

  created_at: datetime
  updated_at: datetime
```

---

# 第三章 下单前安全验证


## 3.1 七项必检

```
下单前强制执行:

① Risk检查: risk_approval_id 有效 + risk_decision = APPROVE/ADJUST
② T+1检查: SELL方向 → 持仓股今日是否可卖
③ 涨跌停检查: 
    BUY → 是否涨停封死
    SELL → 是否跌停封死
④ 资金检查: BUY → 资金 = 价格×股数 + 预估手续费
⑤ 仓位检查: 持仓 ≥ 卖出股数
⑥ 手数检查: 股数 % 100 == 0
⑦ 交易时段: 9:30-11:30 | 13:00-15:00 (集合竞价9:15-9:25)
```

## 3.2 验证失败处理

```
① Risk未通过 → REJECTED, 不尝试
② T+1锁定 → REJECTED, "T+1限制: 可卖X股"
③ 涨跌停 → CANCELLED, "涨停封死/跌停封死"
④ 资金不足 → REJECTED, 降低数量至可买→重新提交
⑤ 仓位不足 → REJECTED
⑥ 手数不对 → 自动调整为100的整数倍
⑦ 非交易时段 → 挂单等到开盘自动提交
```

---

# 第四章 Broker 接口层


## 4.1 QMT/miniQMT 适配

```
BrokerAdapter (统一抽象):
  connect() → bool
  disconnect()
  submit_order(order: Order) → OrderResult
  cancel_order(order_id: str) → bool
  query_order(order_id: str) → Order
  query_position(symbol: str) → Position
  query_account() → Account
  subscribe_quote(symbols: list[str])

QMT实现 (xtquant):
  - 行情: xtdata.subscribe_quote() / get_market_data()
  - 下单: xttrader.order_stock()
  - 撤单: xttrader.cancel_order_stock()
  - 查询: query_stock_asset() / query_stock_positions()

模拟实现 (无QMT时):
  - 行情: akshare
  - 下单: 本地模拟撮合 (用于Paper Trading)
```

## 4.2 执行策略

| 策略 | 适用场景 | 说明 |
|------|---------|------|
| Market Order | 游资快速追涨/止损 | 市价成交, 速度快, 滑点风险 |
| Limit Order | 低吸/埋伏 | 限价成交, 可能不成交 |
| TWAP | 大单(>50万) | 时间加权均价, 降低冲击 |
| Smart | 根据盘口动态选择 | 自适应滑点/流动性 |

游资场景以 Market Order 为主（速度优先）。

---

# 第五章 A股交易规则执行


## 5.1 T+1 规则

```
当日买入 → T+1日才可卖出

系统维护:
  positions[symbol] = {shares, available, locked}

  BUY: locked += shares (当日不可用)
  next_day: available = locked + available, locked = 0
  SELL: 只能从 available 中卖出
```

## 5.2 涨跌停规则

```
板块      涨跌幅    涨停价             跌停价
主板      ±10%    prev_close×1.10    prev_close×0.90
创业板    ±20%    prev_close×1.20    prev_close×0.80
科创板    ±20%    prev_close×1.20    prev_close×0.80
北交所    ±30%    prev_close×1.30    prev_close×0.70
ST        ±5%     prev_close×1.05    prev_close×0.95

涨停时BUY: 订单排队, 可能不成交
跌停时SELL: 订单排队, 可能不成交
```

## 5.3 真实费率

```
买入费用 = 佣金(0.025%, 最低5元) + 过户费(0.001%)
卖出费用 = 佣金(0.025%, 最低5元) + 印花税(0.1%) + 过户费(0.001%)

交易前预扣: 下单时预估费用, 确保资金充足
交易后实扣: 以成交回报为准
```

## 5.4 交易单位

```
最小交易: 100股(1手)
股数必须是100的整数倍

科创板: 最小200股, 超过200后可以1股递增
```

---

# 第六章 执行监控


## 6.1 监控指标

```
订单级:
  - 订单延迟: submit → accepted 时间
  - 成交延迟: submit → filled 时间
  - 滑点: 委托价 vs 成交价

执行级:
  - 成交率: filled / submitted
  - 撤单率: cancelled / submitted
  - 拒单率: rejected / submitted

Broker级:
  - 连接状态: connected / disconnected
  - 心跳延迟
```

## 6.2 异常告警

```
触发条件:
  - 订单超过30秒未成交 (Market Order)
  - 连续3笔拒单
  - Broker连接断开
  - 重复订单(同一信号生成两个订单)
  - 成交价格异常(偏离>5%)

处理:
  → 记录日志 + 上报告警 + 必要时触发 Kill Switch
```

---

# 第七章 成交反馈


## 7.1 反馈数据流

```
Order FILLED → 反馈至:
  ① Data 模块 (存储交易记录)
  ② Experience Engine (经验学习)
  ③ Portfolio Manager (更新持仓/资金)
  ④ Strategy (策略绩效更新)
```

## 7.2 交易记录

```
TradeRecord:
  order_id: str
  symbol: str
  side: BUY | SELL
  quantity: int
  price: float               # 成交价
  amount: float              # 成交金额
  fee: float                 # 实扣手续费
  slippage_bps: float        # 滑点(基点)
  strategy: str              # 来源策略
  ai_confidence: float       # AI置信度
  risk_score: float          # 风险评分
  pnl: float                 # 盈亏(卖出时计算)
  timestamp: datetime
```

---

# 第八章 异常处理与恢复


## 8.1 常见异常及处理

| 异常 | 处理 |
|------|------|
| 网络断开 | 重连3次 → 失败则暂停执行 → 告警 |
| 重复订单 | 检测到重复 → 取消新订单 |
| 部分成交 | 剩余部分继续等待, 15分钟后自动撤单 |
| Broker返回错误 | 记录错误码 → 按错误类型重试或放弃 |
| 账户状态异常 | 暂停所有执行 → 人工确认 |

## 8.2 执行暂停与恢复

```
暂停触发:
  - Broker连接断开 > 60秒
  - 连续拒单 > 5笔
  - Kill Switch激活
  - 人工暂停

恢复流程:
  - 连接恢复 + 健康检查 + 撤掉过期订单 + 人工确认 → 恢复执行
```

---

# 第九章 接口设计


## 9.1 执行接口

| 端点 | 方法 | 功能 |
|------|:---:|------|
| /execution/order | POST | 提交订单 |
| /execution/order/{id} | GET | 查询订单 |
| /execution/order/{id}/cancel | POST | 撤单 |
| /execution/orders | GET | 当日所有订单 |
| /execution/position | GET | 当前持仓 |
| /execution/account | GET | 账户信息 |
| /execution/trades | GET | 成交记录 |

## 9.2 输入（来自 Risk）

```
POST /execution/order
Request:
  signal: TradingSignal
  risk_decision: RiskDecision
```

## 9.3 输出

```
Response:
  order: Order (含order_id + 状态 + 预估费用)
```

---

# 第十章 实盘部署要求


```
实盘前必须完成:
  ✅ 模拟交易 ≥ 1个月 (Paper Trading)
  ✅ QMT连接稳定性测试 ≥ 72小时
  ✅ 所有异常场景覆盖测试
  ✅ Kill Switch 有效性验证
  ✅ 限额/熔断测试

首发实盘:
  - 小额资金 (≤10万)
  - 单一策略
  - 人工在旁边监控
```

---

# 第十一章 设计冻结声明


本文件定义 AQF-T Execution V3.6.0 详细设计。

Execution 模块是 AQF-T 从智能决策到真实交易的执行层。只执行经 Risk 批准的指令。

A股特有规则（T+1/涨跌停/真实费率/手数）在下单前强制验证。

Version: V3.6.0
Status: Detailed Engineering Design
END OF AQFT EXECUTION DESIGN
