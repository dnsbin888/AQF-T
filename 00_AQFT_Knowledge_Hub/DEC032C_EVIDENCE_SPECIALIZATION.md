# DEC-032C: Evidence Specialization

Version: V1.0.0
Status: DESIGN — 待评审
Date: 2026-08-03
Part of: DEC-032 Evidence Intelligence Design (M2)
Based on: DEC-032A Ontology / DEC-032B Responsibility

---

## 一、问题诊断

### 现状

```
Feature Pool (MA/EMA/RSI/ROC/Volume/Northbound/...)
        │
        ├──→ LGBM   → 学到一切 → Score → BUY
        └──→ XGBoost → 学到一切 → Score → BUY
```

**问题**:
- 两个 Producer 回答同一个问题："该不该买？"
- 特征高度重叠 → 相关性趋近 0.9
- Triple Vote 实际上是"同一个观点投了两次票"
- 无法归因"这个决定主要受趋势影响还是动量影响"

### 目标

```
Trend Feature Pool (MA/EMA/ADX/Slope/...)
        │
        └──→ TrendML    → Trend Evidence    → "趋势向上，强度 0.82"

Momentum Feature Pool (RSI/ROC/CCI/KDJ/...)
        │
        └──→ MomentumML → Momentum Evidence → "加速中，力度 0.77"

Board Feature Pool (封单/撤单/盘口/...)
        │
        └──→ Path A     → Board Evidence     → "回封确认，质量 0.91"

Regime Feature Pool (炸板率/梯队/赚钱效应/...)
        │
        └──→ Regime     → Regime Evidence    → "高潮期，置信度 0.94"
```

## 二、Feature Ownership 分配

### 2.1 TrendML

| 特征类别 | 具体因子 | 来源 |
|----------|----------|------|
| 均线排列 | MA5/MA10/MA20/MA60 多头排列 | OHLCV |
| 趋势强度 | ADX / DI+/DI- | OHLCV |
| 均线斜率 | MA20斜率 / MA60斜率 | OHLCV |
| 突破确认 | N日高点突破 / 布林带上轨 | OHLCV |
| 趋势持续性 | 连续上涨天数 / 回调幅度 | OHLCV |

### 2.2 MomentumML

| 特征类别 | 具体因子 | 来源 |
|----------|----------|------|
| 超买超卖 | RSI / Williams %R | OHLCV |
| 动量变化 | ROC / CCI / KDJ | OHLCV |
| 量价配合 | 量比 / 量价背离 | OHLCV |
| 涨速 | 涨幅排序 / 涨速 | OHLCV |
| 加速度 | ROC二阶导 | OHLCV |

### 2.3 Board Producer (Path A)

| 特征类别 | 具体因子 | 来源 |
|----------|----------|------|
| 封单质量 | 封单量/流通盘 / 撤单率 | L2 |
| 炸板分类 | 炸板时间/回封时间/炸板幅度 | L2 |
| 盘口深度 | 买一量/卖一量 / 排队深度 | L2 |
| 联动性 | 跟风封板数 / 板块效应 | L2+板块 |

### 2.4 Regime Producer

| 特征类别 | 具体因子 | 来源 |
|----------|----------|------|
| 情绪周期 | 炸板率 / 涨停家数 / 连板高度 | 全市场 |
| 赚钱效应 | 昨日涨停今日表现 / 打板胜率 | 全市场 |
| 题材热度 | 板块涨停数 / 题材持续性 | 板块数据 |
| 资金情绪 | 北向净流入 / 融资余额变化 | 外部数据 |

### 2.5 Leadership Producer

| 特征类别 | 具体因子 | 来源 |
|----------|----------|------|
| 涨停时间 | 最早涨停时间排序 | L1 |
| 连板高度 | 当前连板数 / 历史最高 | L1 |
| 板块地位 | 板块内涨停数 / 市值占比 | 板块数据 |
| 题材共振 | 所属题材热度叠加 | 题材数据 |
| 分歧程度 | 换手率 / 炸板次数 | L1+L2 |

### 2.6 Capital Flow Producer

| 特征类别 | 具体因子 | 来源 |
|----------|----------|------|
| 北向资金 | 北向净买入 / 持仓变化 | northbound |
| 龙虎榜 | 席位类型 / 买入占比 / 机构参与 | 龙虎榜 |
| 主力动向 | 大单流向 / 主力净买 | L2 |
| 融资融券 | 融资余额变化 / 融券余额 | 外部数据 |

## 三、过渡策略

Phase 2 不一次性重训所有模型。分步过渡：

### Step 1: 命名对齐（零影响）
- TrendML 输出标记为 `trend_evidence`
- MomentumML 输出标记为 `momentum_evidence`
- 不改特征、不改模型、不改信号

### Step 2: 特征域划分（不训练）
- 在 Registry 中注册每个 Producer 的 Feature Pool
- 不实际限制模型输入（保持兼容）

### Step 3: 分步重训（需回测验证）
- 先 TrendML: 仅用 Trend Feature Pool 重训
- 保持 MomentumML 原样
- 回测对比 → 确认 Evidence Diversity 提升
- 再 MomentumML: 仅用 Momentum Feature Pool 重训
- 回测对比

### Step 4: 相关性验收
- 目标: Trend Evidence 与 Momentum Evidence 相关性 < 0.7
- 验收: 60天 Replay Evidence Diversity 报告

## 四、成功标准

| 指标 | 当前 | 目标 |
|------|:--:|:--:|
| Producer 间相关性 | ~0.9 | < 0.7 |
| Evidence Diversity | 低（同一问题） | 高（不同视角） |
| 归因能力 | 无法区分 | 每个决策可追溯到具体 Evidence |
| Producer 可替换性 | 不可替换 | 内部算法可替换，对外身份不变 |

---

*DEC-032C Evidence Specialization V1.0 — 待老板评审*
