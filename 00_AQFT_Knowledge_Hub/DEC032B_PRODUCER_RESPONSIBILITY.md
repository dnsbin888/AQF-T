# DEC-032B: Producer Responsibility

Version: V1.0.0
Status: DESIGN — 待评审
Date: 2026-08-03
Part of: DEC-032 Evidence Intelligence Design (M2)
Based on: DEC-032A Evidence Ontology

---

## 一、核心原则

**One Producer, One Responsibility.** 每个 Producer 只回答一个问题。不做一个"什么都会"的万能模型。

## 二、Producer 职责定义

### 2.1 Trend Producer

| 属性 | 值 |
|------|-----|
| **Domain** | Trend Evidence |
| **问题** | 趋势是否成立？方向是什么？ |
| **当前实现** | TrendML (LightGBM) |
| **输出** | 方向(LONG/SHORT/NEUTRAL) + 趋势强度 + 置信度 |
| **特征域** | MA/EMA/ADX/趋势线/MACD方向/多周期排列 |
| **不回答** | 买不买 / 什么时候买 / 买多少 |

### 2.2 Momentum Producer

| 属性 | 值 |
|------|-----|
| **Domain** | Momentum Evidence |
| **问题** | 趋势是否正在加速？力度如何？ |
| **当前实现** | MomentumML (XGBoost) |
| **输出** | 加速度 + 动量强度 + 置信度 |
| **特征域** | RSI/ROC/CCI/KDJ/量比/涨速 |
| **不回答** | 趋势方向 / 龙头判定 / 风险 |

### 2.3 Board Producer

| 属性 | 值 |
|------|-----|
| **Domain** | Board Evidence |
| **问题** | 回封是否确认？封板质量如何？ |
| **当前实现** | Path A (AQF-T Perception) |
| **输出** | 炸板分类 + 回封确认 + 封板质量 |
| **特征域** | 封单强度/撤单率/盘口深度/炸板时间 |
| **不回答** | 趋势 / 龙头地位 |

### 2.4 Leadership Producer

| 属性 | 值 |
|------|-----|
| **Domain** | Leadership Evidence |
| **问题** | 是否为真龙头？板块地位如何？ |
| **当前实现** | 潜龙 Dragon 8维 (待注册) |
| **输出** | 龙头评分 + 梯队位置 + 板块地位 |
| **特征域** | 涨停时间/连板数/板块涨停家数/题材热度 |
| **不回答** | 趋势 / 动量 / 买点 |

### 2.5 Regime Producer

| 属性 | 值 |
|------|-----|
| **Domain** | Regime Evidence |
| **问题** | 现在处于什么市场阶段？能不能做？ |
| **当前实现** | AQF-T RegimeEngine |
| **输出** | 四阶段(冰点/回暖/高潮/退潮) + 操作模式 + 置信度 |
| **特征域** | 炸板率/涨停梯队/赚钱效应/情绪周期 |
| **不回答** | 买哪个 / 什么时候卖 |

### 2.6 Risk Producer

| 属性 | 值 |
|------|-----|
| **Domain** | Risk Evidence |
| **问题** | 当前风险水平如何？是否值得持仓？ |
| **当前实现** | 潜龙 PreTradeChecker (待注册) |
| **输出** | 风险评分 + 风险等级 + 仓位建议上限 |
| **特征域** | 波动率/相关性/集中度/回撤 |
| **不回答** | 买哪个 / 趋势方向 |

### 2.7 Exit Producer

| 属性 | 值 |
|------|-----|
| **Domain** | Exit Evidence |
| **问题** | 退出依据是否成立？ |
| **当前实现** | AQF-T ExitPipeline |
| **输出** | 退出信号 + 退出类型 + 置信度 |
| **特征域** | 炸板/龙头结束/题材死亡/到期/止损线 |
| **不回答** | 买不买 |

### 2.8 Formula Producer

| 属性 | 值 |
|------|-----|
| **Domain** | Formula Evidence |
| **问题** | 技术面是否有信号？ |
| **当前实现** | TDX Formula Watcher |
| **输出** | 公式信号 + 信号等级 + 公式名称 |
| **特征域** | 通达信自定义公式 |
| **不回答** | 基本面 / 资金面 |

## 三、禁止清单

```
❌ 一个 Producer 输出两种 Domain 的 Evidence
❌ 一个 Producer 同时回答"趋势"和"买点"
❌ Producer 直接输出 BUY/SELL
❌ Producer 内部包含 Fusion 逻辑
```

---

*DEC-032B Producer Responsibility V1.0 — 待老板评审*
