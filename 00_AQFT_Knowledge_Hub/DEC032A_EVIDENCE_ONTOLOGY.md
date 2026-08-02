# DEC-032A: Evidence Ontology

Version: V1.0.0
Status: DESIGN — 待评审
Date: 2026-08-03
Part of: DEC-032 Evidence Intelligence Design (M2)
Based on: DEC-029 Evidence First / DEC-031 EFL v1.0

---

## 一、Ontology 是什么

**Evidence Ontology 是 AQF-T 的证据词典。** 定义了系统世界中所有合法的证据域（Evidence Domain）。

不是模型分类。不是算法分类。是"这个证据在回答什么市场问题"的分类。

## 二、核心原则

**One Producer, One Responsibility.** 一个 Producer 只属于一个 Domain，只回答一个问题。

## 三、Evidence Universe V1.0

```
Evidence Universe
│
├── Market Evidence（市场状态域）
│   ├── Regime Evidence       — 现在处于什么市场阶段？
│   ├── Emotion Evidence      — 市场情绪如何？
│   └── Breadth Evidence      — 市场宽度/参与度？
│
├── Trend Evidence（趋势域）
│   └── Trend Evidence        — 趋势是否成立？方向是什么？
│
├── Momentum Evidence（动量域）
│   └── Momentum Evidence     — 趋势是否正在加速？力度如何？
│
├── Liquidity Evidence（流动性域）
│   ├── Volume Evidence       — 成交量是否异常？
│   └── OrderFlow Evidence    — 订单流结构如何？
│
├── Capital Flow Evidence（资金域）
│   ├── Northbound Evidence   — 北向资金流向？
│   ├── Institutional Evidence— 机构资金行为？
│   └── Retail Evidence       — 散户资金行为？
│
├── Board Evidence（盘口域）
│   ├── Leader Evidence       — 这是龙头吗？
│   ├── Seal Evidence         — 封板质量如何？
│   └── Break Evidence        — 炸板风险多大？
│
├── Leadership Evidence（龙头域）
│   ├── Dragon Evidence       — 龙头8维评分
│   ├── Ladder Evidence       — 梯队完整性
│   └── Sector Evidence       — 板块地位
│
├── Risk Evidence（风险域）
│   ├── Exposure Evidence     — 敞口风险
│   ├── Concentration Evidence— 集中度风险
│   └── Drawdown Evidence     — 回撤风险
│
├── Execution Evidence（执行域）
│   ├── Fill Evidence         — 成交质量
│   ├── Slippage Evidence     — 滑点
│   └── Latency Evidence      — 延迟
│
├── Exit Evidence（退出域）
│   ├── Risk Exit Evidence    — 风险驱动的退出
│   ├── Strategy Exit Evidence— 策略驱动的退出
│   └── Expiry Evidence       — 时间驱动的退出
│
└── Macro Evidence（宏观域）★ 未来
    ├── Policy Evidence       — 政策信号
    ├── Global Evidence       — 全球市场联动
    └── Event Evidence        — 事件冲击
```

## 四、Producer 与 Domain 的映射

| Domain | 现有 Producer | 未来 Producer |
|--------|:------------:|:------------:|
| Trend Evidence | TrendML (LGBM) | Transformer, Rule Engine |
| Momentum Evidence | MomentumML (XGBoost) | CatBoost, RL Model |
| Formula Evidence | TDX Formula | — |
| Board Evidence | Path A (AQF-T) | L2 Model |
| Regime Evidence | Regime (AQF-T) | Macro Model |
| Exit Evidence | ExitPipeline (AQF-T) | — |
| Capital Flow Evidence | — (潜龙有数据，未注册) | Northbound ML |
| Liquidity Evidence | — | OrderFlow Analyzer |
| Leadership Evidence | — | Dragon Scorer |

## 五、冻结规则

1. 任何新 Evidence 必须先在此 Ontology 注册 Domain
2. 一个 Producer 只能属于一个 Domain
3. 新增 Domain 需 Architecture Review
4. Domain 结构仅可 Append，不可修改已有定义

---

*DEC-032A Evidence Ontology V1.0 — 待老板评审*
