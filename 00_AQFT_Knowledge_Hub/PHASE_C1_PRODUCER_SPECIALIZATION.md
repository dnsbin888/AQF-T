# Phase C1: Producer Feature Ownership 正式分家

Version: V1.0.0
Status: PLAN — 待执行
Date: 2026-08-02
Based on: DEC-032C Evidence Specialization + GPT Capability Phase Design

---

## 目标

将 TrendML (LGBM) 与 MomentumML (XGB) 从"同一因子、不同算法"升级为"不同因子、不同Domain"。

## 当前状态

```
LGBM: 8因子 (qmt_composite/fund_v2/chip_v2/momentum_score/chase_v2/trend_score/bull_line/defensive_v2)
XGB:  8因子 (bull_line/chase_v2/momentum_score/fund_v2/defensive_v2/trend_score/chip_v2/qmt_composite)

重叠: 100%
Evidence Diversity: 低
```

## 目标状态

### TrendML — Trend Producer

| 属性 | 值 |
|------|-----|
| Domain | trend_evidence |
| 问题 | 趋势是否成立？ |
| 特征域 | 资金/筹码/趋势/板块/行业/QMT综合 |
| 因子 | qmt_composite, fund_v2, chip_v2, trend_score, 行业动量, 板块强度 |
| 实现 | LightGBM (保持现有) |
| 频率 | 日线 |

### MomentumML — Momentum Producer

| 属性 | 值 |
|------|-----|
| Domain | momentum_evidence |
| 问题 | 现在是否正在加速？ |
| 特征域 | L2盘口/逐笔/封单/撤单/炸板/成交速度 |
| 因子 | bull_line, chase_v2, momentum_score + L2实时特征 |
| 实现 | XGBoost (需重训) |
| 频率 | 分钟级/Tick级 |

## 执行步骤

### Step 1: Registry 定义 (今天, 零风险)
- 更新 evidence_registry.json 中 trend_ml / momentum_ml 的 feature_domain

### Step 2: TrendML 补齐因子 (Phase C4)
- 恢复缺失的17个因子 → TrendML 以完整24因子重训

### Step 3: MomentumML L2接入 (需要QMT L2数据)
- xgb_factor_weight.py 增加 L2 特征计算
- 接入 xtdata Level2 数据 (逐笔/十档)

### Step 4: MomentumML 重训
- 仅用 L2 + 实时特征训练新的 XGBoost 模型
- 回测验证 vs 旧模型

### Step 5: 相关性验收
- 目标: Trend Evidence 与 Momentum Evidence 相关性 < 0.7
- 验收: 60天 Replay Evidence Diversity 报告

---

*Phase C1 V1.0 — 2026-08-02*
