# AQFT A-Share Reality Runtime Design V3.5.0


# AQF-T A股现实世界接入层架构设计


Version: V3.5.0
Status: Architecture Design
Classification: AQF-T A股实战化基础设施
Date: 2026-07-26


---

# 第一章 定位


## 1.1 核心目标


让 AQF-T 第一次接触真实 A 股市场。


V3.4.0 完成：Sense → Think → Act → Learn（合成市场环境）。

V3.5.0 完成：Synthetic World → **Real A-Share World**（真实数据 + 真实规则 + 真实交易环境）。



## 1.2 定位


32_AQFT_A_Share_Runtime 不是简单 Adapter。

它是 AQF-T 与真实市场之间的**边界系统** — 负责将 A 股市场的复杂性封装为标准化的 Event Stream，使上层 AI 模块无需关心数据来源。



---

# 第二章 总体架构


```
                  AQF-T Intelligence Brain
                         │
                World Model / Agent / Decision
                         │
                     Event Bus
                         │
═══════════════════════════════════════════════
              A-Share Reality Layer (V3.5.0)
═══════════════════════════════════════════════
                         │
                  Market Gateway
                         │
          ┌──────────────┼──────────────┐
          │              │              │
        QMT          xtquant       akshare
          │              │          (free)
          └──────────────┼──────────────┘
                         │
                  Market Data Engine
                         │
          ┌──────────────┼──────────────┐
          │         │         │         │
      Tick Feed  Minute   Daily   Alternative
                         │
                  A-Share Rule Engine
                         │
          ┌──────────────┼──────────────┐
          │         │         │         │
        T+1     Limit    Fee    Settlement
          │         Price
          └──────────────┼──────────────┘
                         │
                  Reality Simulator
                         │
                  Execution Runtime (V3.3)
```



---

# 第三章 数据流


## 3.1 完整链路


```
A股实时行情 → Market Gateway → Market Data Engine → Event Bus → World Model → Agent Council → Decision Engine → Risk Engine → Execution → Simulation/实盘 → 成交反馈 → Experience Engine → Learning
```


## 3.2 Event Schema


MarketTickEvent:

```
{
  "symbol": "SH.600519",
  "price": 1500.00,
  "volume": 5000000,
  "bid1": 1499.00,
  "ask1": 1501.00,
  "open": 1490.00,
  "high": 1510.00,
  "low": 1485.00,
  "prev_close": 1495.00,
  "timestamp": "2026-07-26T10:30:00"
}
```


LimitStateEvent:

```
{
  "symbol": "SH.600519",
  "limit_up": 1644.50,
  "limit_down": 1345.50,
  "at_limit": false
}
```



---

# 第四章 A股规则模型


## 4.1 T+1 引擎


- 当日买入 → 次日才能卖出
- Position 跟踪: available_shares / locked_shares
- 每日开盘前自动刷新


## 4.2 涨跌停引擎


| 板块 | 代码 | 涨跌幅 |
|------|------|--------|
| 主板 | 60xxxx/00xxxx | ±10% |
| 创业板 | 300xxx | ±20% |
| 科创板 | 688xxx | ±20% |
| 北交所 | 8xxxxx | ±30% |
| ST | *ST/ST | ±5% |


- 涨停: 买不进 (除非有人卖)
- 跌停: 卖不出 (除非有人买)


## 4.3 真实手续费


| 费用 | 买入 | 卖出 |
|------|------|------|
| 佣金 (0.025%, 最低5元) | ✅ | ✅ |
| 印花税 (0.1%) | ❌ | ✅ |
| 过户费 (0.001%) | ✅ | ✅ |


## 4.4 交易单位


- 最小交易单位: 100 股 (1手)
- 必须是 100 的整数倍



---

# 第五章 接口规范


## 5.1 MarketGateway 统一接口


```
class MarketGateway:
    def connect() -> bool
    def subscribe(symbols: list[str])
    def get_tick(symbol: str) -> MarketTick
    def get_history(symbol, start, end, period) -> list[dict]
    def get_stock_list(sector: str) -> list[str]
    def get_account() -> AccountInfo
```


## 5.2 数据源支持


| 数据源 | 类型 | 费用 | 用途 |
|--------|------|------|------|
| QMT/xtquant | 实盘 | 券商开户(≥10万) | 实时行情+交易 |
| akshare | 免费 | 免费 | 日线数据 |
| tushare pro | API | 免费/付费 | 历史+财务 |
| 东方财富 | 爬虫 | 免费 | 实时行情 |



---

# 第六章 与 V3.x 系统集成


## 6.1 与 Event Bus (V3.2) 集成


- MarketTickEvent → EventBus.publish(MARKET_DATA)
- 订阅者: World Model / Risk Engine / Experience Engine


## 6.2 与 Simulation Engine (V3.3) 升级


V3.3 随机模拟：

P(fill) = 0.95


V3.5 升级：

P(fill) = f(volume, order_size, spread, limit_state, liquidity)


## 6.3 与 Execution Runtime (V3.3) 集成


真实下单链路：

Decision → Risk(APPROVE) → QMT order_stock() → 成交反馈 → Portfolio Update → Experience



---

# 第七章 测试规范


- 交易日历正确性: 2026年节假日全覆盖
- T+1 规则: 当日买入次日才能卖出
- 涨跌停: 各板块涨跌幅限制正确
- 手续费: 与券商对账单误差 < 0.1%
- 数据接入: 至少1个数据源可用



---

# 第八章 实盘路线


| 阶段 | 内容 |
|------|------|
| V3.5.0 | akshare免费数据 + A股规则引擎 (当前) |
| V3.5.1 | QMT/xtquant 真实行情接入 |
| V3.5.2 | QMT 模拟交易 (Paper Trading) |
| V3.7.0 | QMT 实盘 (小额验证) |
| V4.0.0 | 全自动实盘 |



---

# 第九章 冻结声明


本文件定义 AQF-T A-Share Reality Runtime V3.5.0。


AQF-T 从 Synthetic Market 进入 Real A-Share Market。


这是 AQF-T 从 AI 交易系统实验平台走向 A 股实战量化基础设施的关键节点。



Version: V3.5.0
Status: Architecture Design
END OF AQFT A-SHARE REALITY RUNTIME DESIGN
