# Phase C1: Producer Feature Ownership 正式分家

Version: V1.0.0
Status: ✅ FROZEN — Capability Evolution Baseline
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
| 特征域 | L1盘中: 分时涨速/量比/换手加速/封板时间/开板/委比委差/买一卖一/分钟K |
| 因子 | bull_line, chase_v2, momentum_score + L1 intraday features |
| 实现 | XGBoost (需重训) |
| 频率 | 分钟级 |
| L2状态 | NOT_AVAILABLE — 外部商业约束(¥5500/年), ROI未证明, 转为Optional Capability |

## 执行步骤 (修订版 V1.1 — 拆分 L2 数据管线)

### C1-1: Contract Freeze ✅ FROZEN
- Registry 中声明 TrendML/MomentumML 的目标特征域
- migration_phase: TrendML=ACTIVE, MomentumML=CONTRACT_ONLY
- 零风险, 不改 Runtime

### C1-2a: L2 Data Acquisition ⏳
- 接入 xtdata Level2 数据 (逐笔成交/十档盘口)
- Data Readiness Gate (DRG-1): 连续5交易日, 完整率>99%
- 验证: 时间戳连续/不丢盘口/不丢逐笔/重连恢复

### C1-2b: L2 Feature Engineering ⏳
- 从 L2 数据提取特征: 封单强度/撤单率/盘口失衡/成交速度
- DRG-2: 特征分布正常, 无NaN/异常值

### C1-3: Data Readiness Validation ⏳
- DRG-3: Feature Drift 监测
- DRG-4: 延迟监测 (<100ms)
- 连续运行验证

### C1-4: Momentum v2 Training ⏳
- 仅用 L2 + 实时特征训练新的 XGBoost 模型
- 回测验证 vs 旧模型
- 必须 DRG-1~4 全部 PASS 才能进入

### C1-5: Shadow / A-B Validation ⏳
- 旧 Momentum 维持 Decision
- 新 Momentum 只产生 Shadow Decision, 不交易
- 连续30天对比: Evidence Quality / WinRate / Return / Stability
- 赢了 → 替换; 输了 → 回滚

### Data Readiness Gate (DRG) — 新增
| Gate | 检查项 | 标准 |
|:--:|------|------|
| DRG-1 | L2 Availability | 连续5日完整率>99% |
| DRG-2 | Data Completeness | 0 丢盘口, 0 丢逐笔 |
| DRG-3 | Feature Stability | 无 NaN, 分布正常 |
| DRG-4 | Feature Drift | PSI < 0.1 |
| DRG-5 | Latency | P99 < 100ms |
**所有 DRG PASS 才能进 C1-4 训练。**

## Architecture Rule

> **No Training Without DRG PASS.**
> Data quality is governed before model quality.
> 任何 Producer 训练前，必须先通过全部 DRG Gate。

## Capability Lifecycle（统一状态机）

```
CONTRACT_ONLY   → 仅 Contract 声明, 无数据/无训练
DATA_READY      → L2 数据可用, DRG-1/2 PASS
FEATURE_READY   → 特征工程完成, DRG-3/4/5 PASS
MODEL_READY     → 模型训练完成, 回测验证 PASS
SHADOW_READY    → Shadow 30天对比, Decision Quality 达标
PRODUCTION      → 正式上线

当前:
  TrendML:     PRODUCTION
  MomentumML:  CONTRACT_ONLY (→ 目标 PRODUCTION via L2)

## Producer Status Table

| Producer | Lifecycle | DRG | Shadow | Production |
|----------|:---------:|:---:|:------:|:----------:|
| TrendML | PRODUCTION | PASS | — | ACTIVE |
| MomentumML | CONTRACT_ONLY | — | — | NO |
| TDX Formula | PRODUCTION | PASS | — | ACTIVE |
| Path A | PRODUCTION | PASS | — | ACTIVE |
| Regime | PRODUCTION | PASS | — | ACTIVE |
| ExitPipeline | PRODUCTION | PASS | — | ACTIVE |
| CatBoost | ARCHIVED | — | — | NO |

*C2/C3 扩展: 未来新增 Producer (SentimentML/BoardML/FlowML) 均沿用此表*
```

---

*Phase C1 V1.0 — 2026-08-02*
