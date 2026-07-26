# AQFT Strategy Runtime Design V3.6.0


# AQF-T 策略运行系统详细设计


Version: V3.6.0 | Status: Detailed Engineering Design
Date: 2026-07-26

> 参考: Backtrader 事件驱动引擎 + FinRL-X 权重中心化接口 + Qlib AI-Native Pipeline


---

# 第一章 架构


采用行业标准的三层架构：

```
Signal Layer (策略逻辑) → Portfolio Layer (权重向量) → Execution Layer (订单生成)
```

核心借鉴 **FinRL-X 的 Weight-Centric Interface**：策略层输出统一的目标组合权重向量，而非具体交易信号。策略构建与执行引擎彻底解耦，回测→模拟→实盘使用完全相同接口。

借鉴 **Backtrader 的 Cerebro 事件驱动引擎**：逐K线/逐Tick模拟真实交易流程，数据Feed→策略逻辑→撮合引擎→经纪商，串行回调。

---

# 第二章 策略加载


## 2.1 策略注册表

```
Strategy Registry:
  trend_following:
    class: TrendStrategy
    params: {ma_short:5, ma_long:20}
    status: active
    regime_fit: [World-001, World-002]

  dragon_leader:                      # ⭐ 游资核心
    class: DragonStrategy
    params: {consecutive_min:3, seal_ratio:0.05, gap_up_min:0.03, gap_up_max:0.07}
    status: active
    regime_fit: [World-001, World-002, World-008]

  volume_price:
    class: VolumePriceStrategy
    params: {volume_ratio:1.5, n_reversal_days:4}
    status: active
    regime_fit: [World-003, World-006, World-010]

  sentiment_cycle:
    class: SentimentStrategy
    params: {ice_exposure:0.2, climax_exposure:0.7}
    status: active
    regime_fit: [ALL]

  defensive:
    class: DefensiveStrategy
    params: {max_daily_loss:-0.02, recession_exposure:0.1}
    status: active
    regime_fit: [World-004, World-005, World-007, World-009]
```

## 2.2 动态策略选择

```
每个Bar/Tick:
  1. World Model → 当前 Regime ID + 情绪周期阶段
  2. 匹配策略适配矩阵 → 活跃策略列表 + 仓位上限
  3. 各策略并行执行 → 独立信号
  4. Signal Fusion → 统一 TradingSignal
  5. → Risk Runtime 审批
```

---

# 第三章 信号生成 (借鉴 Backtrader Cerebro 模式)


## 3.1 事件驱动执行流程

```
Data Feed (K线/Tick) → Strategy.next() 回调 → 生成 Signal → Broker 模拟/真实执行
```

## 3.2 权重中心化输出 (借鉴 FinRL-X)

```
策略层输出:
  不输出 "BUY 600519 100股"
  而是输出 目标权重向量: {600519: 0.15, 000858: 0.10, CASH: 0.75}

执行层根据权重差异自动生成订单:
  当前权重 vs 目标权重 → 计算差异 → 生成买卖订单
```

优势: 回测/模拟/实盘使用完全相同的权重→订单转换逻辑。

---

# 第四章 调度


| 频率 | 策略 | 说明 |
|:---:|------|------|
| 每Tick(3s) | Dragon | 涨停监控 |
| 每分钟 | Volume-Price | 量价信号 |
| 每5分钟 | Trend + Sentiment | 趋势+情绪 |
| 每小时 | 绩效评估 | 策略权重调整 |

---

# 第五章 API


| 端点 | 方法 | 功能 |
|------|:---:|------|
| POST /strategy/signal | POST | 生成信号 |
| GET /strategy/list | GET | 策略列表+状态 |
| POST /strategy/{id}/activate | POST | 激活 |
| POST /strategy/{id}/pause | POST | 暂停 |
| GET /strategy/performance | GET | 绩效报告 |

---

# 第六章 设计冻结声明


本文件定义 AQF-T Strategy Runtime V3.6.0。借鉴 Backtrader 事件驱动 + FinRL-X 权重中心化接口 + Qlib AI Pipeline。

Version: V3.6.0 | Status: Detailed Engineering Design
END OF AQFT STRATEGY RUNTIME DESIGN
