# AQFT Strategy Design V3.6.0


# AQF-T 策略体系详细设计


Version: V3.6.0
Status: Detailed Engineering Design
Classification: AQF-T 交易策略核心设计文件
Date: 2026-07-26


---

# 第一章 策略体系定位


## 1.1 系统定位

Strategy 模块是 AI Brain 的智能输出与 Risk/Execution 之间的转换层。

```
AI Brain (Fusion Output) → Strategy Engine → Trading Signal → Risk → Execution
```

Strategy 不做独立预测。它接收 AI Brain 的四引擎输出（Prediction + Sentiment + Risk + Fusion），结合市场环境和策略规则，生成具体的可执行交易信号。

## 1.2 目标用户

主要服务于 A 股游资及个人量化交易。策略体系覆盖：
- 短线打板（首板/二板/龙头）
- 波段趋势（N字反包/趋势延续）
- 情绪套利（情绪周期择时）
- 防御保护（降仓/空仓）

---

# 第二章 策略总体架构


```
AI Brain (Fusion Output + Sentiment Output)
                    │
                    ↓
          Strategy Selector
     (根据 Market Regime + 情绪周期 选择策略组合)
                    │
    ┌───────┬───────┼───────┬───────┬───────────┐
    │       │       │       │       │           │
  Trend   Dragon  Volume  Sentiment Defensive  Arbitrage
 Strategy Strategy Strategy Strategy Strategy  Strategy
    │       │       │       │       │           │
    └───────┴───────┼───────┴───────┴───────────┘
                    ↓
          Signal Fusion Engine
                    ↓
          Trading Signal Output
                    ↓
              05_Risk (审批)
```

---

# 第三章 策略类型体系


## 3.1 Trend Strategy — 趋势策略

### 定位
识别市场主要趋势，适用于情绪周期的高潮期和回暖期中后段。

### 信号条件
```
买入条件 (任一满足):
  - MA5 上穿 MA20 + 成交量放大 > 1.5倍
  - 股价突破布林上轨 + MACD金叉
  - AI Prediction: trend=UP + probability > 0.65

卖出条件 (任一满足):
  - MA5 下穿 MA20
  - 股价跌破布林中轨
  - AI Prediction: trend=DOWN + probability > 0.60
  - 持仓收益 < -5% (止损)

持仓周期: 5-20 个交易日
仓位: 20-30%
适用 Regime: World-001(牛市扩散), World-002(牛市加速), Recovery
```

## 3.2 Dragon Strategy（龙头战法）⭐ 游资核心

### 定位
识别市场龙头股，捕捉连板机会。适用于情绪周期的回暖期和高潮期。

### 龙头识别条件
```
龙头判定 (至少满足3项):
  1. 连板高度 ≥ 3 板 (在所属题材中最高)
  2. 所属题材当日涨停 ≥ 5 家
  3. 封单额/流通市值 > 5%
  4. 龙虎榜显示 ≥ 2 家知名游资席位买入
  5. 集合竞价封单 > 5000万 且流通市值 < 50亿
  6. 首板次日高开 ≥ 5% 且成交额放大

买入信号:
  - 首板打板: 早盘快速拉升(9:30-10:00)触及涨停 + 题材热度 > 0.7
  - 二板接力: 首板次日集合竞价高开3%-7% + 开盘30分钟不炸板
  - 弱转强: 前日炸板或尾盘回落 + 次日竞价高开快速翻红 + 量比 > 3

卖出信号:
  - 炸板: 涨停板打开 > 10分钟
  - 竞价转弱: 次日集合竞价低开 > 3%
  - 题材退潮: 同题材涨停家数降至 < 3家
  - 连板中断: 不再连板当日尾盘卖出
  - 异动警告: 10日涨幅接近100% 或 30日涨幅接近200%

持仓周期: 1-5 个交易日
仓位: 10-20%（单票高风险）
适用 Regime: World-001, World-002, World-008(政策驱动)
适用情绪周期: 回暖期, 高潮期
```

## 3.3 Volume-Price Strategy — 量价策略

### 定位
利用成交量和价格行为的规律。适用于震荡市和情绪周期的回暖初期。

### 信号条件
```
买入条件:
  - N字反包: 前3-5日下跌或横盘 + 今日放量上涨(成交量>前5日均量2倍) + 收复前日阴线
  - 缩量回调买入: 上升趋势中缩量回调至MA20 + 今日放量企稳
  - 分时承接: 低开-3%以内 + 15分钟内翻红 + 分时单笔 > 1000手

卖出条件:
  - 放量滞涨: 成交量放大但价格不涨
  - 高位放量长上影
  - 量价背离: 价格新高但成交量递减

持仓周期: 3-10 个交易日
仓位: 15-25%
适用 Regime: World-003(牛市尾部), World-006(熊市筑底), World-010(震荡等待)
```

## 3.4 Sentiment Strategy — 情绪策略

### 定位
利用市场情绪波动。直接使用 AI Brain Sentiment Engine 的输出。

### 信号条件
```
情绪周期择时:
  冰点期 → 回暖期 转换时: 试错买入, 仓位 1-2 成
  回暖期: 逐步加仓, 仓位 3-5 成
  高潮期: 重仓龙头, 仓位 5-7 成
  高潮期 → 退潮期 转换时: 减仓至 1-2 成
  退潮期: 空仓或轻仓防御

情绪极值信号:
  情绪值 < 15 (极度恐慌): 逆势低吸信号
  情绪值 > 85 (过度狂热): 止盈离场信号
  炸板率 > 50%: 暂停所有买入
```

## 3.5 Defensive Strategy — 防御策略

### 定位
降低极端风险，保护资金。在所有市场环境中作为兜底策略。

### 触发条件
```
自动触发 (任一满足):
  - 日内亏损 > 2%
  - 持仓回撤 > 5%
  - 市场跌停家数 > 50
  - 情绪周期 = 退潮期
  - Risk Engine 决策 = REJECT

防御动作:
  - 降仓: 总仓位降至 ≤ 20%
  - 空仓: 清空所有短线持仓
  - 对冲: 买入防御性品种(如国债ETF)
```

---

# 第四章 策略-Regime-情绪周期 适配矩阵


| Market Regime | 情绪周期 | 推荐策略 | 仓位上限 |
|:-------------|:------:|---------|:---:|
| World-001 牛市扩散 | 回暖/高潮 | Dragon + Trend | 70% |
| World-002 牛市加速 | 高潮 | Dragon + Trend + Sentiment | 70% |
| World-003 牛市尾部 | 退潮预警 | Volume-Price + Sentiment | 40% |
| World-004 熊市初期 | 退潮 | Defensive | 20% |
| World-005 熊市恐慌 | 冰点 | 空仓 | 0% |
| World-006 熊市筑底 | 冰点/回暖 | Volume-Price (试错) | 20% |
| World-007 流动性收缩 | 退潮 | Defensive | 10% |
| World-008 政策驱动 | 回暖/高潮 | Dragon + Trend | 60% |
| World-009 风险释放 | 退潮/冰点 | Defensive | 10% |
| World-010 震荡等待 | 回暖 | Volume-Price + Sentiment | 30% |

---

# 第五章 信号标准格式


## 5.1 TradingSignal 统一格式

```
TradingSignal:
  signal_id: str                  # 信号唯一ID
  timestamp: UTC

  source:
    strategy: str                 # 策略名称
    ai_fusion_score: float        # AI Brain Fusion Score
    sentiment_phase: str          # 情绪周期阶段

  target:
    symbol: str                   # SH.600519
    action: BUY | SELL | HOLD
    quantity: int                 # 建议股数 (100的整数倍)
    price_type: MARKET | LIMIT
    limit_price: float            # 限价(如有)

  confidence:
    signal_confidence: 0-1
    ai_confidence: 0-1

  risk_context:
    suggested_position_pct: float # 建议仓位比例
    stop_loss_pct: float          # 止损比例
    take_profit_pct: float        # 止盈比例

  reasoning:
    regime: str                   # 当前Market Regime
    sentiment: str                # 当前情绪周期
    key_factors: [str]            # 关键决策因素

  metadata:
    strategy_version: str
    model_versions: {engine: version}
```

---

# 第六章 Signal Fusion（信号融合）


## 6.1 融合机制

当多个策略同时发出信号时，按以下规则融合：

```
融合优先级 (游资场景):
  1. 情绪周期约束 (最高优先)
     - 退潮期: 忽略所有买入信号
     - 高潮期: Dragon > Trend > 其他
     - 冰点期: Volume-Price(试错) > 其他(轻仓)

  2. 信号一致性加分
     - 2+个策略同时看多同一标的 → confidence +0.10
     - 策略方向冲突 → 降低仓位

  3. AI置信度加权
     - AI Fusion Score > 0.80 → 原仓位
     - AI Fusion Score 0.60-0.80 → 仓位 × 0.7
     - AI Fusion Score < 0.60 → 忽略该信号

  4. 风险约束
     - Risk Score > 60 → 忽略买入信号
     - 总仓位已达上限 → 不再新增
```

## 6.2 信号冲突处理

```
当策略之间出现冲突时:

Dragon Strategy: BUY   +   Sentiment Strategy: SELL
  → Supervisor判断: 情绪周期=退潮期 → 采用SELL
  → Supervisor判断: 情绪周期=高潮期 → 采用BUY(降低仓位30%)

Trend Strategy: BUY    +   Risk Intelligence: HIGH_RISK
  → Risk优先 → REJECT
```

---

# 第七章 策略生命周期管理


## 7.1 策略状态机

```
CREATED → BACKTESTING → PAPER_TRADING → APPROVED → ACTIVE → PAUSED → RETIRED
                                                    ↓
                                                MONITORING
```

## 7.2 上线标准

| 指标 | 阈值 |
|------|:---:|
| 回测夏普比率 | > 1.2 |
| 回测最大回撤 | < 20% |
| 胜率 | > 45% |
| 盈亏比 | > 2.0 |
| 样本外验证期 | ≥ 6个月 |
| 模拟交易期 | ≥ 1个月 |

## 7.3 策略降级/淘汰

```
自动降级触发:
  - 连续5笔亏损
  - 月度回撤 > 15%
  - 策略信号 > 50% 被 Risk Engine REJECT
  - Market Regime 变化导致策略适配度下降

自动淘汰触发:
  - 连续10笔亏损
  - 季度夏普 < 0.5
  - 最大回撤 > 30%
```

---

# 第八章 策略参数管理


## 8.1 参数表

| 参数 | 默认值 | 范围 | 适用策略 | 说明 |
|------|:---:|:---:|---------|------|
| ma_short | 5 | 3-10 | Trend | 短期均线周期 |
| ma_long | 20 | 10-60 | Trend | 长期均线周期 |
| volume_ratio | 1.5 | 1.2-3.0 | Volume-Price | 放量倍数阈值 |
| consecutive_boards_min | 3 | 2-5 | Dragon | 最低连板数 |
| seal_amount_ratio | 5% | 3%-10% | Dragon | 封单/流通市值 |
| gap_up_min | 3% | 1%-5% | Dragon | 竞价高开最小幅度 |
| gap_up_max | 7% | 5%-9% | Dragon | 竞价高开最大幅度 |
|炸板_exit_minutes | 10 | 5-20 | Dragon | 炸板后等待分钟数 |
| sentiment_floor | 15 | 10-25 | Sentiment | 情绪值抄底阈值 |
| sentiment_ceiling | 85 | 75-90 | Sentiment | 情绪值止盈阈值 |
| stop_loss_pct | -5% | -3%~-8% | 所有 | 硬止损 |
| position_max | 70% | 50%-80% | 所有 | 总仓位上限 |
| single_position_max | 20% | 10%-25% | Dragon | 单票仓位上限 |

所有参数版本化管理，修改必须记录：修改时间、修改原因、测试结果。

---

# 第九章 接口设计


## 9.1 输入 (来自 AI Brain)

```
POST /strategy/signal

Request:
  fusion_output: FusionOutput      # AI Brain 综合输出
  sentiment_output: SentimentOutput # AI Brain 情绪输出
  world_state: MarketWorldState    # World Model 当前状态
  portfolio: PortfolioState        # 当前持仓
```

## 9.2 输出 (发送至 Risk)

```
Response:
  signals: [TradingSignal]        # 生成的交易信号列表
  strategy_context:
    active_strategies: [str]      # 当前活跃策略
    regime: str
    sentiment_phase: str
    recommended_position: float
```

## 9.3 策略管理 API

| 端点 | 方法 | 功能 |
|------|:---:|------|
| /strategy/list | GET | 查询所有策略及状态 |
| /strategy/{id}/activate | POST | 激活策略 |
| /strategy/{id}/pause | POST | 暂停策略 |
| /strategy/{id}/retire | POST | 退役策略 |
| /strategy/{id}/params | PUT | 更新策略参数 |
| /strategy/performance | GET | 各策略绩效报告 |

---

# 第十章 策略风险原则


```
任何策略的买入信号必须经过:

Strategy (生成信号)
    ↓
Risk Engine (审批)
    ├── APPROVE → Execution
    ├── ADJUST → 修改仓位后 → Execution
    └── REJECT → 放弃

禁止:
  - 策略绕过 Risk 直接驱动 Execution
  - 退潮期执行 Dragon Strategy
  - 单票仓位超过上限
  - 总仓位超过上限
```

---

# 第十一章 设计冻结声明


本文件定义 AQF-T Strategy V3.6.0 详细设计。

六大策略类型覆盖游资核心场景：Trend（趋势）、Dragon（龙头战法）、Volume-Price（量价）、Sentiment（情绪）、Defensive（防御）。

策略适配矩阵定义了每种 Market Regime + 情绪周期组合下的最优策略选择和仓位上限。

所有信号统一为 TradingSignal 格式，经过 Signal Fusion 融合后，必须通过 Risk Engine 审批才能执行。

Version: V3.6.0
Status: Detailed Engineering Design
END OF AQFT STRATEGY DESIGN
