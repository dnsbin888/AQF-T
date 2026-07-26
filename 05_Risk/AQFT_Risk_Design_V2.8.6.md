# AQFT Risk Design V3.6.0


# AQF-T 风险控制体系详细设计


Version: V3.6.0
Status: Detailed Engineering Design
Classification: AQF-T 风险控制核心设计文件 — 最高否决权
Date: 2026-07-26


---

# 第一章 风险控制定位


## 1.1 宪法地位

Risk 模块是 AQF-T 系统安全核心。**拥有最高交易否决权限。**

```
任何交易请求必须经过 Risk 审批。禁止 Strategy 或 Execution 绕过 Risk。

优先级: 系统安全 > 风险控制 > 长期收益 > 短期收益
```

## 1.2 核心职责

| 职责 | 说明 |
|------|------|
| 风险识别 | 实时检测市场/策略/仓位/操作四层风险 |
| 风险评价 | 量化风险评分 (0-100) |
| 风险决策 | APPROVE / ADJUST / REJECT |
| 仓位控制 | 动态仓位上限管理 |
| 极端保护 | Kill Switch + Safe Mode |

---

# 第二章 风险控制架构


```
Strategy Signal → Risk Evaluation Engine → Risk Decision → Execution
                       │
                ┌──────┼──────┐
                │      │      │
           仓位检查  风险评分  市场环境
                │      │      │
                └──────┼──────┘
                       ↓
              ┌────────┴────────┐
              │                 │
         限额通过           限额触发
              │                 │
         APPROVE/ADJUST      REJECT
              │                 │
         Execution          Safe Mode/Kill Switch
```

---

# 第三章 风险评分模型


## 3.1 综合风险评分公式

```
Risk Score = 
  Market Risk × 0.25 +
  Position Risk × 0.25 +
  Strategy Risk × 0.20 +
  Sentiment Risk × 0.15 +
  Liquidity Risk × 0.15
```

## 3.2 各子项计算

### Market Risk（市场风险）

```
Market Risk = 
  volatility_score × 0.40 +
  trend_reversal_score × 0.30 +
  systemic_risk_score × 0.30

volatility_score = 当前波动率 / 历史平均波动率 × 100 (封顶100)
trend_reversal_score = AI Prediction reversal_risk × 100
systemic_risk_score = 跌停家数/100 × 100
```

### Position Risk（仓位风险）

```
Position Risk = 
  position_ratio × 0.50 +
  concentration × 0.30 +
  leverage × 0.20

position_ratio = 当前仓位 / 最大允许仓位 × 100
concentration = 最大单票仓位 / 单票上限 × 100
leverage = 融资余额 / 总资产 × 100
```

### Strategy Risk（策略风险）

```
Strategy Risk = 
  strategy_drawdown × 0.40 +
  consecutive_losses × 0.30 +
  signal_quality × 0.30

strategy_drawdown = 策略当前回撤 / 最大允许回撤 × 100
consecutive_losses = min(连续亏损笔数 / 5 × 100, 100)
signal_quality = (1 - 近期胜率) × 100
```

### Sentiment Risk（情绪风险）⭐ 游资核心

```
Sentiment Risk = 
  情绪周期风险 × 0.50 +
  炸板率风险 × 0.30 +
  题材退潮风险 × 0.20

情绪周期风险:
  高潮期 → 20
  回暖期 → 30
  冰点期 → 60
  退潮期 → 90

炸板率风险 = 当前炸板率 × 100

题材退潮风险:
  龙头炸板 → 80
  跟风批量回落 → 60
  题材涨停家数骤降 → 50
```

### Liquidity Risk（流动性风险）

```
Liquidity Risk = 
  volume_decline × 0.40 +
  spread_widening × 0.30 +
  turnover_decline × 0.30

volume_decline = (1 - 当前量/5日均量) × 100 (下限0)
spread_widening = (当前买卖价差/正常价差 - 1) × 100 (下限0)
turnover_decline = (1 - 当前换手率/正常换手率) × 100 (下限0)
```

---

# 第四章 风险等级


| 等级 | 分数 | 含义 | 默认动作 |
|:---:|:---:|------|------|
| Low | 0-30 | 风险可控 | APPROVE，正常执行 |
| Medium | 31-55 | 需关注 | APPROVE，降低仓位20% |
| High | 56-75 | 高风险 | ADJUST，降低仓位50% |
| Extreme | 76-100 | 极端风险 | REJECT，禁止开新仓 |

---

# 第五章 风险决策机制


## 5.1 决策流程

```
TradingSignal 输入
       │
       ▼
  ┌─────────────┐
  │ 限额检查     │ → 超限 → REJECT
  └─────────────┘
       │ 通过
       ▼
  ┌─────────────┐
  │ 风险评分     │ → Score > 75 → REJECT
  └─────────────┘
       │ Score ≤ 75
       ▼
  ┌─────────────┐
  │ 情绪周期检查  │ → 退潮期 + 买入信号 → REJECT
  └─────────────┘
       │ 通过
       ▼
  ┌─────────────┐
  │ 仓位调整     │ → Score 31-55 → 仓位×0.8
  │             │ → Score 56-75 → 仓位×0.5
  └─────────────┘
       │
       ▼
  APPROVE / ADJUST → Execution
```

## 5.2 决策输出

```
RiskDecision:
  decision: APPROVE | ADJUST | REJECT
  risk_score: 0-100
  risk_level: Low | Medium | High | Extreme
  adjusted_position_pct: float       # ADJUST后的仓位
  checks:
    position_limit: {limit, current, pass}
    drawdown_limit: {limit, current, pass}
    sentiment_check: {phase, action_allowed, pass}
    single_stock_limit: {limit, current, pass}
  reason: str
  timestamp: UTC
```

---

# 第六章 限额体系


## 6.1 限额参数表

| 限额类型 | 参数 | 默认值 | 触发动作 |
|---------|------|:---:|------|
| 总仓位上限 | max_total_position | 70% | 超限→REJECT |
| 单票仓位上限 | max_single_position | 20% | 超限→REJECT |
| Dragon单票上限 | max_dragon_position | 15% | 超限→REJECT |
| 日内亏损熔断 | max_daily_loss | -2% | 触发→停止当日交易 |
| 月度回撤熔断 | max_monthly_drawdown | -10% | 触发→降至20%仓位 |
| 最大回撤熔断 | max_total_drawdown | -20% | 触发→Safe Mode |
| 连续亏损笔数 | max_consecutive_losses | 5笔 | 触发→暂停策略 |
| 单笔风险上限 | max_single_risk | 总资金2% | 超限→ADJUST |

## 6.2 情绪周期限额覆盖

```
情绪周期覆盖（优先级高于默认限额）:

退潮期:
  max_total_position → 强制 20%
  max_dragon_position → 强制 0%（禁止打板）
  max_single_position → 强制 10%

冰点期:
  max_total_position → 强制 20%
  max_dragon_position → 强制 5%

高潮期:
  max_total_position → 默认 70%（可满仓）
  max_dragon_position → 默认 15%
```

---

# 第七章 游资特化风控 ⭐


## 7.1 炸板风险控制

```
炸板触发条件:
  - 持有涨停股，涨停板打开 > 10分钟
  - 持有涨停股，封单金额骤降 > 50%

触发动作:
  → 立即市价卖出该股
  → 暂停该策略30分钟
  → 检查同题材其他持仓
```

## 7.2 连板高位风险

```
连板高位风险 (适用于Dragon Strategy):

连板数 ≥ 7:  Risk Score + 20
连板数 ≥ 9:  Risk Score + 30, 仓位强制降至50%
连板数 ≥ 11: Risk Score + 40, 仓位强制降至30%

异动警告 (逼近监管红线):
  10日涨幅 > 80% →  Risk Score + 30
  30日涨幅 > 150% → Risk Score + 40, 建议清仓
  触及10天100%红线 → 强制清仓
```

## 7.3 题材退潮保护

```
题材退潮检测:
  - 龙头炸板
  - 板块涨停家数降至 < 3
  - 板块内跌停出现

触发动作:
  → 该题材所有持仓 Risk Score + 30
  → 暂停该题材新开仓
  → 现有持仓设置移动止盈
```

---

# 第八章 Kill Switch


## 8.1 触发条件

```
Kill Switch 触发 (任一满足):

系统级:
  - Risk 服务崩溃
  - 数据源全部断开 > 60秒
  - 出现重复订单 > 3笔
  - 账户连接断开

市场级:
  - 全市场跌停 > 500家
  - 市场熔断触发
  - 极端波动 (VIX类指标 > 历史3σ)

账户级:
  - 日亏损 > 5%
  - 总回撤 > 25%
```

## 8.2 执行动作

```
Kill Switch 激活后:
  ① 立即撤销所有未成交订单
  ② 停止所有策略信号生成
  ③ 市价清仓所有持仓（如可交易）
  ④ 断开 Broker 下单通道（保留行情）
  ⑤ 发送紧急通知
  ⑥ 进入 Safe Mode
```

## 8.3 Safe Mode

```
Safe Mode 状态下:
  ✅ 允许: 查看行情、查看持仓、风险监控
  ❌ 禁止: 开新仓、加仓、策略运行
  ⚠️ 限时: 允许风险平仓（需人工确认）

退出 Safe Mode:
  - 人工确认 + 系统健康检查通过
  - 最低冷却时间: 30分钟
```

---

# 第九章 仓位计算


## 9.1 凯利公式（基础仓位）

```
f* = (p × b - q) / b

其中:
  p = 胜率
  q = 1 - p
  b = 盈亏比

基础仓位 = f* × 总资金
```

## 9.2 A股适配调整

```
最终仓位 = 基础仓位 × 情绪系数 × 风险系数 × 流动性系数

情绪系数:
  高潮期: 1.0
  回暖期: 0.8
  冰点期: 0.4
  退潮期: 0.2

风险系数:
  Risk Score < 30: 1.0
  Risk Score 31-55: 0.7
  Risk Score 56-75: 0.4

流动性系数:
  正常: 1.0
  缩量: 0.7
  枯竭: 0（不交易）
```

## 9.3 单票仓位上限

```
单票最大仓位 = min(
  凯利仓位,
  单票上限 %,
  总资金 × 2% / |止损价 - 入场价| × 入场价  (单笔风险上限约束)
)

Dragon Strategy 额外: 单票 ≤ 15%
```

---

# 第十章 接口设计


## 10.1 风控检查

```
POST /risk/check

Request:
  signal: TradingSignal
  portfolio: PortfolioState
  market_context: MarketWorldState
  sentiment: SentimentOutput

Response:
  RiskDecision
```

## 10.2 管理接口

| 端点 | 方法 | 功能 |
|------|:---:|------|
| /risk/status | GET | 当前风险状态 |
| /risk/limits | GET | 查询限额配置 |
| /risk/limits | PUT | 更新限额（需审批） |
| /risk/kill_switch | POST | 手动激活 Kill Switch |
| /risk/safe_mode/exit | POST | 退出 Safe Mode |
| /risk/report | GET | 风险日报 |

---

# 第十一章 与各模块的关系


| 上游模块 | 提供 | Risk 使用 |
|---------|------|---------|
| 04_Strategy | TradingSignal | 审批对象 |
| 03_AI_Brain | SentimentOutput + RiskIntelligenceOutput | 风险评分输入 |
| 24_World_Model | MarketWorldState | 市场风险评估 |
| 07_Data | Portfolio + Account | 仓位风险计算 |

| 下游模块 | 接收 | 作用 |
|---------|------|------|
| 06_Execution | RiskDecision | 只有 APPROVE/ADJUST 才能执行 |

---

# 第十二章 设计冻结声明


本文件定义 AQF-T Risk V3.6.0 详细设计。

Risk 模块是 AQF-T 系统安全核心，拥有最高交易否决权。

任何交易必须经过 Risk 审批。任何情况下收益服从风险。

游资特化风控：炸板保护、连板高位风险、题材退潮保护、情绪周期限额覆盖。

Version: V3.6.0
Status: Detailed Engineering Design
END OF AQFT RISK DESIGN
