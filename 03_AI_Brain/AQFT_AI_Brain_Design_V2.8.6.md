# AQFT AI Brain Design V3.6.0


# AQF-T 智能核心详细设计


Version: V3.6.0
Status: Detailed Engineering Design
Classification: AQF-T 智能决策核心设计文件
Date: 2026-07-26


---

# 第一章 AI Brain 定位


## 1.1 系统定位


AI Brain 是 AQF-T 智能决策核心。

它不是单一模型，而是由四个专业引擎组成的多模型融合智能系统：

- **Prediction Engine**（预测引擎）：市场趋势与方向判断
- **Sentiment Engine**（情绪引擎）：市场情绪与题材热度识别
- **Risk Intelligence**（风险智能）：潜在风险预测
- **Fusion Engine**（融合引擎）：多源信号综合决策

## 1.2 目标用户场景

AI Brain 主要服务于 A 股游资/个人量化交易场景：

- 早盘 9:15-9:25：解析集合竞价数据，输出早盘情绪
- 盘中 9:30-15:00：实时监控涨停梯队、题材轮动、资金流向
- 尾盘 14:30-15:00：评估次日预期，输出持仓建议
- 盘后：更新情绪周期、龙虎榜分析、经验学习

---

# 第二章 AI Brain 总体架构


```
                    Market Data
                         │
              ┌──────────┼──────────┐
              │          │          │
        行情数据      资金数据      情绪数据
        (Tick/K线)  (北向/融资)  (涨停/龙虎榜/新闻)
              │          │          │
              └──────────┼──────────┘
                         ↓
                   Feature Pipeline
                         │
        ┌────────────────┼────────────────┐
        │                │                │
  Prediction Engine  Sentiment Engine  Risk Intelligence
        │                │                │
        └────────────────┼────────────────┘
                         ↓
                   Fusion Engine
                         │
                    Decision Output
                         │
                   Strategy Module
```

## 2.1 与 AQF-T 整体架构的关系

```
07_Data → 03_AI_Brain → 04_Strategy → 05_Risk → 06_Execution
```

AI Brain 的上游是数据层（07_Data），下游是策略层（04_Strategy）。AI Brain 自身不直接执行交易。

---

# 第三章 Prediction Engine（预测引擎）


## 3.1 功能定位

预测市场未来状态。回答三个核心问题：

| 问题 | 输出 |
|------|------|
| 市场方向？ | 趋势方向 + 概率 |
| 涨跌概率？ | 上涨概率 0-1 |
| 当前处于什么阶段？ | Regime ID + 置信度 |

## 3.2 输入 Schema

```
PredictionInput:
  symbol: str                     # 股票代码 (如 SH.600519)
  market_data:
    price_series: [float]         # 最近60日收盘价
    volume_series: [int]          # 最近60日成交量
    turnover_rate: float          # 换手率
    amplitude: float              # 振幅
  technical_indicators:
    ma_5: float
    ma_20: float
    ma_60: float
    macd_dif: float
    macd_dea: float
    macd_bar: float
    rsi_14: float
    boll_upper: float
    boll_mid: float
    boll_lower: float
    atr_14: float
  market_context:
    index_trend: str              # 大盘趋势 (UP/DOWN/NEUTRAL)
    sector_trend: str             # 板块趋势
    market_regime: str            # 来自 World Model 的 Regime ID
  limit_up_context:               # A股特有：涨停环境
    limit_up_count: int           # 全市场涨停家数
    consecutive_boards: int       # 最高连板高度
   炸板率: float                  # 炸板率 0-1
```

## 3.3 输出 Schema

```
PredictionOutput:
  symbol: str
  timestamp: UTC

  trend:
    direction: UP | DOWN | NEUTRAL
    probability: 0-1

  price_target:
    expected_return_5d: float
    expected_return_20d: float

  regime_confidence:
    regime_id: str
    confidence: 0-1

  risk_flag:
    reversal_risk: 0-1
    volatility_risk: 0-1

  model_metadata:
    model_name: str
    model_version: str
    inference_time_ms: float
```

## 3.4 推荐模型

| 优先级 | 模型 | 用途 | 理由 |
|:---:|------|------|------|
| 首选 | **LightGBM** | 趋势方向预测 | A股量化最有效的传统模型；训练快、可解释、因子重要性一目了然 |
| 次选 | XGBoost | 涨跌概率预测 | 与LightGBM互补，适合Ensemble |
| 增强 | Transformer | 时序模式识别 | 捕捉复杂时间依赖关系 |
| 轻量 | Logistic Regression | 基准模型 | 用于对比和校准 |

## 3.5 训练流程

```
Historical Data (3年+日线/60分钟)
       ↓
Feature Engineering (技术指标 + 市场环境 + Regime特征)
       ↓
Train/Val/Test Split (70/15/15)
       ↓
LightGBM Training (early_stopping=50)
       ↓
Model Evaluation (AUC > 0.65, IC > 0.05)
       ↓
Model Registry (版本管理)
       ↓
Online Inference
```

## 3.6 API

```
POST /ai/predict

Request: PredictionInput
Response: PredictionOutput
```

---

# 第四章 Sentiment Engine（情绪引擎）⭐ 游资核心


## 4.1 功能定位

识别市场情绪状态。**这是游资最重要的 AI 模块。**

回答三个核心问题：

| 问题 | 输出 |
|------|------|
| 当前市场情绪处于什么阶段？ | 情绪周期阶段 + 情绪值 |
| 题材热度如何？ | 题材强度评分 |
| 市场参与者是什么状态？ | 游资/机构/散户 行为分析 |

## 4.2 A股情绪数据源

```
SentimentDataSource:

  涨停数据:                         # ⭐ 游资核心
    涨停家数: int                   # 全市场涨停数量
    连板高度: int                   # 最高连板数
    连板梯队: {2板:N, 3板:N, 4板:N, 5+板:N}
    封板强度: 0-1                   # 封单额/成交额
    炸板率: 0-1                     # 炸板数/摸板数
    首板晋级率: 0-1                 # 昨日首板今日连板比例

  资金数据:
    北向资金净流入: float           # 沪深股通
    融资余额变化: float             # 两融
    主力净流入: float               # 大单资金
    龙虎榜净买入: float             # 游资席位

  新闻舆情:
    政策新闻: [{title, sentiment, impact}]
    行业新闻: [{title, sentiment, sector}]
    个股公告: [{symbol, title, sentiment}]

  市场情绪:
    涨停家数: int
    跌停家数: int
    上涨家数: int
    下跌家数: int
    连板高度: int
    炸板率: float
```

## 4.3 情绪周期模型（游资四阶段）

```
情绪周期四阶段:

冰点期 (Ice):
  特征: 跌停 > 30家, 连板高度 ≤ 2, 炸板率 > 50%
  策略: 试错首板, 仓位 1-2 成
  情绪值: < 20

回暖期 (Warming):
  特征: 反包板出现, 炸板率 < 30%, 连板高度 ≥ 3
  策略: 接力二板, 加仓主线
  情绪值: 20-50

高潮期 (Climax):
  特征: 连板 ≥ 7, 跟风批量涨停, 涨停 > 80家
  策略: 龙头锁仓, 挖掘补涨, 仓位 7 成
  情绪值: 50-80

退潮期 (Recession):
  特征: 天地板出现, 中位股A杀, 炸板率 > 40%
  策略: 空仓或轻仓, 管住手
  情绪值: > 80 (过热) 或快速下降
```

## 4.4 情绪值量化公式

```
情绪值 = 涨停家数 × 2 - 跌停家数 × 3 + 连板高度 × 5 + 北向资金方向 × 10

其中:
  北向资金方向: 净流入 > 10亿 → +1 / 净流出 > 10亿 → -1 / 其他 → 0

情绪区间:
  < 20: 冰点期
  20-50: 回暖期
  50-80: 高潮期
  > 80: 过热(警惕退潮)
```

## 4.5 题材热度模型

```
题材热度评分 = 政策级别 × 0.3 + 涨停家数 × 0.25 + 龙头高度 × 0.20 + 板块联动 × 0.15 + 资金强度 × 0.10

政策级别:
  国务院/中央 → 1.0
  部委 → 0.7
  地方政府 → 0.4

板块联动:
  核心龙头 + ≥ 3只跟风涨停 → 1.0
  核心龙头 + 1-2只跟风 → 0.6
  孤立涨停 → 0.2

资金强度:
  板块净流入 > 10亿 → 1.0
  板块净流入 3-10亿 → 0.6
  板块净流入 < 3亿 → 0.3
```

## 4.6 输出 Schema

```
SentimentOutput:
  timestamp: UTC

  sentiment_cycle:
    phase: Ice | Warming | Climax | Recession
    sentiment_score: 0-100
    confidence: 0-1

  limit_up_analysis:
    total_limit_up: int
    max_consecutive_boards: int
    board_ladder: {2: N, 3: N, 4: N, 5+: N}
    seal_strength: 0-1
   炸板率: 0-1
    first_board_promotion_rate: 0-1

  theme_analysis:
    top_themes: [{name, heat_score, leader_symbol, follower_count}]
    theme_rotation_signal: str

  capital_sentiment:
    north_bound_direction: Inflow | Outflow | Neutral
    margin_balance_trend: Increasing | Stable | Decreasing
    institutional_behavior: Accumulating | Distributing | Neutral
    retail_sentiment: Fearful | Neutral | Greedy

  participant_analysis:
    游资活跃度: 0-1
    机构参与度: 0-1
    散户情绪: 0-1
    量化占比估计: 0-1
```

## 4.7 API

```
POST /ai/sentiment

Request: { market_scope: "all" | "sector", sector_code: str }
Response: SentimentOutput
```

---

# 第五章 Risk Intelligence（风险智能）


## 5.1 功能定位

AI 辅助风险预测。不是替代 Risk 模块（05_Risk），而是提供 AI 视角的风险预警。

## 5.2 输入

```
RiskIntelligenceInput:
  position: {symbol, shares, cost}
  market_volatility: float
  liquidity_score: 0-1
  historical_drawdown: float
  sentiment_phase: str              # 来自 Sentiment Engine
  regime_id: str                    # 来自 World Model
  concentration_risk: 0-1           # 持仓集中度
  limit_up_context:                 # A股涨停风险
    if_holding_limit_up_stock: bool # 是否持有涨停股
    consecutive_boards: int         # 持仓涨停股的连板数
   炸板_risk: 0-1                  # 持仓股的炸板风险
```

## 5.3 输出

```
RiskIntelligenceOutput:
  risk_score: 0-100
  risk_level: Low | Medium | High | Extreme
  warning_signals: [str]            # 具体预警信号
  recommended_action: str           # AI建议（仅供参考，最终由05_Risk裁决）
  confidence: 0-1
```

## 5.4 API

```
POST /ai/risk

Request: RiskIntelligenceInput
Response: RiskIntelligenceOutput
```

---

# 第六章 Fusion Engine（融合引擎）


## 6.1 功能定位

融合 Prediction + Sentiment + Risk + Experience 的结果，形成综合判断。

## 6.2 融合算法

```
Fusion Score = 
  Prediction Output × 0.30 +
  Sentiment Signal × 0.30 +
  Risk Assessment × 0.25 +
  Experience Memory × 0.15

其中:
  Prediction Output: 预测引擎的方向+概率
  Sentiment Signal: 情绪周期+题材热度
  Risk Assessment: AI风险评分
  Experience Memory: 类似市场环境的经验参考
```

## 6.3 权重动态调整

```
权重根据 Market Regime 动态调整:

Bull Market:
  Prediction: 0.35, Sentiment: 0.25, Risk: 0.20, Experience: 0.20

Bear Market:
  Prediction: 0.20, Sentiment: 0.20, Risk: 0.40, Experience: 0.20

High Volatility:
  Prediction: 0.20, Sentiment: 0.25, Risk: 0.35, Experience: 0.20
```

## 6.4 输出 Schema

```
FusionOutput:
  timestamp: UTC

  final_signal:
    direction: BUY | SELL | HOLD
    confidence: 0-1
    score: 0-100

  component_scores:
    prediction_contribution: float
    sentiment_contribution: float
    risk_contribution: float
    experience_contribution: float

  reasoning_trace: [str]       # 可解释决策链
  alternative_scenarios: [str] # 备选方案

  model_metadata:
    engines_used: [str]
    fusion_method: weighted | voting | stacking
```

## 6.5 API

```
POST /ai/fusion

Request: { prediction, sentiment, risk, experience }
Response: FusionOutput
```

---

# 第七章 Learning Engine（学习引擎）


## 7.1 功能定位

根据交易结果反馈持续优化模型。

## 7.2 学习来源

```
LearningDataSource:
  历史交易结果:
    - 预测方向 vs 实际方向
    - 情绪判断 vs 实际周期
    - 风险评分 vs 实际回撤

  失败案例分析:
    - 炸板案例
    - 天地板案例
    - 假突破案例
    - 情绪误判案例

  市场变化:
    - Regime切换
    - 波动率突变
    - 流动性变化
```

## 7.3 学习闭环

```
Trading Result → Performance Evaluation → Error Analysis → 
Model Retraining → Validation → Model Registry → Deployment → 
Better Prediction
```

---

# 第八章 模型治理


## 8.1 模型生命周期

```
Development → Testing → Validation → Production → Archived
```

## 8.2 模型必须记录的元数据

```
ModelMetadata:
  model_id: str
  model_name: str
  model_type: LightGBM | XGBoost | Transformer | ...
  version: str
  training_date: date
  training_dataset_version: str
  feature_list: [str]
  hyperparameters: dict
  evaluation_metrics: {AUC, IC, Sharpe, ...}
  status: development | testing | validation | production | archived
  deployed_at: datetime
  deployed_by: str
```

## 8.3 上线标准

| 指标 | 阈值 |
|------|:---:|
| AUC | > 0.65 |
| IC (Rank) | > 0.05 |
| 最大回撤 | < 20% |
| 夏普比率 | > 1.0 |
| 样本外验证 | 至少3段不同周期 |

## 8.4 禁止事项

```
- 未经验证的模型进入生产
- 模型版本被覆盖
- 训练数据被删除
- AI输出绕过Risk模块
```

---

# 第九章 输入输出总接口


## 9.1 对外 API 汇总

| 端点 | 方法 | 功能 | 输入 | 输出 |
|------|:---:|------|------|------|
| /ai/predict | POST | 趋势预测 | PredictionInput | PredictionOutput |
| /ai/sentiment | POST | 情绪分析 | {scope, sector} | SentimentOutput |
| /ai/risk | POST | 风险预测 | RiskIntelligenceInput | RiskIntelligenceOutput |
| /ai/fusion | POST | 综合决策 | 四个引擎输出 | FusionOutput |
| /ai/model/status | GET | 模型状态 | — | ModelMetadata[] |
| /ai/model/retrain | POST | 重新训练 | {model_id} | TrainingResult |

---

# 第十章 与 AQF-T 其他模块的关系


| 上游模块 | 提供的数据 | AI Brain 如何使用 |
|---------|----------|----------------|
| 07_Data | 行情/涨停/龙虎榜/新闻 | 所有引擎的原始输入 |
| 24_World_Model | Regime ID + Market State Vector | Prediction 和 Fusion 的上下文 |

| 下游模块 | 接收的输出 | 如何使用 |
|---------|----------|----------------|
| 04_Strategy | Fusion Output + Sentiment Output | 生成具体交易信号 |
| 05_Risk | Risk Intelligence Output | 辅助风险决策 |
| 22_Evolution | 预测结果 vs 实际 | 模型持续学习 |

---

# 第十一章 设计冻结声明


本文件定义 AQF-T AI Brain V3.6.0 详细设计。

AI Brain 由四个专业引擎组成：Prediction（预测）、Sentiment（情绪）、Risk Intelligence（风险智能）、Fusion（融合），加上 Learning Engine（学习）形成完整的智能决策闭环。

核心设计原则：
- 多模型融合，禁止单一模型决策
- 所有 AI 输出必须提供解释
- AI 输出不能直接执行交易（必须经过 Strategy → Risk → Execution）
- 模型必须版本化管理

Version: V3.6.0
Status: Detailed Engineering Design
END OF AQFT AI BRAIN DESIGN
