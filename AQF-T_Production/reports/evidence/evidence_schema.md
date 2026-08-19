# AVP Evidence Table — Schema v1.1 (PA APPROVED)

> 55 字段的完整定义。不在此表内的字段不进入 Evidence Table。
> v1.0: 50 列 T+0 快照 (FROZEN 08-09)
> v1.1: +5 列 Outcome 回填 (PA 批准 08-09) — 证据闭环

## AQF-T Decision (6)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `regime_phase` | status.json → regime.phase | str | 回暖期/退潮期/震荡期/冰点期/高潮期 |
| `regime_score` | status.json → regime.score | float | AQF-T 情绪分 0-100 |
| `regime_mode` | status.json → regime.mode | str | normal / stop / critical |
| `path_a` | status.json → regime.path_a | bool | Path A (打板) 是否开放 |
| `path_b` | status.json → regime.path_b | bool | Path B (反转) 是否开放 |
| `max_position_pct` | status.json → regime.max_position_pct | float | 最大仓位比例 |

## Pipeline (5)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `candidates` | status.json → candidates | int | 候选标的数 |
| `signals` | status.json → signals | int | 生成信号数 |
| `fills` | status.json → fills | int | 实际成交数 |
| `rejected` | status.json → rejected | int | 被 Gate/风控拒绝数 |
| `data_source` | status.json → data_source | str | SIMULATOR / AKSHARE_EOD / QMT_LIVE |

## Sensor — Margin (4)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `margin_trend` | sensor.json → margin.trend | str | expanding / contracting / stable |
| `margin_strength` | sensor.json → margin.strength_score | float | 两融强度 0-100 |
| `margin_bal_5d_pct` | sensor.json → margin.balance_change_5d_pct | float | 融资余额 5日变化 % |
| `margin_bal_20d_pct` | sensor.json → margin.balance_change_20d_pct | float | 融资余额 20日变化 % |

## Sensor — Institution (3)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `inst_flow` | sensor.json → lhb.institution_flow | str | positive / negative / neutral |
| `inst_net` | sensor.json → lhb.institution_net | float | 机构净买入 (万元) |
| `inst_participation_pct` | sensor.json → lhb.institution_participation_pct | float | 机构参与度 % |

## Sensor — ETF (4)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `etf_appetite` | sensor.json → etf.risk_appetite | str | recovering / risk_off / neutral |
| `etf_risk_spread` | sensor.json → etf.risk_spread | float | 小盘-大盘涨跌幅差 % |
| `etf_large_chg` | sensor.json → etf.avg_large_cap_chg | float | 大盘 ETF 平均涨跌 % |
| `etf_small_chg` | sensor.json → etf.avg_small_cap_chg | float | 小盘 ETF 平均涨跌 % |

## Sensor — Southbound (1)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `southbound_trend` | sensor.json → southbound.trend | str | southbound_increase / decrease / stable |

## Sensor — Sentiment Market (6)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `sent_mkt_score` | sensor.json → sentiment.market_sentiment.score | float | 市场情绪分 0-100 |
| `sent_mkt_label` | sensor.json → sentiment.market_sentiment.label | str | 极乐/乐观/中性/悲观/恐慌 |
| `sent_advance_pct` | sensor.json → sentiment.market_sentiment.advance_ratio_pct | float | 上涨占比 % |
| `sent_breadth_pct` | sensor.json → sentiment.market_sentiment.breadth_pct | float | >MA20 占比 % |
| `sent_limit_up` | sensor.json → sentiment.market_sentiment.limit_up | int | 涨停家数 |
| `sent_limit_down` | sensor.json → sentiment.market_sentiment.limit_down | int | 跌停家数 |

## Sensor — Sentiment Cycle (3)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `sent_cycle_stage` | sensor.json → sentiment.cycle.stage | str | startup / ferment / climax / retreat |
| `sent_cycle_scale` | sensor.json → sentiment.cycle.position_scale | float | 仓位系数 0-1 |
| `sent_cycle_advice` | sensor.json → sentiment.cycle.advice | str | 游资口诀文本 |

## Sensor — Sentiment Aggregated (6)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `sent_confidence` | sensor.json → sentiment.sentiment_confidence.value | float | 情绪综合置信 0-100 |
| `sent_confidence_status` | sensor.json → sentiment.sentiment_confidence.status | str | favorable / neutral / unfavorable |
| `sent_extreme_state` | sensor.json → sentiment.sentiment_extreme.state | str | overheat / hot / normal / cold / panic |
| `sent_vel_1d` | sensor.json → sentiment.sentiment_velocity.change_1d | float | 情绪 1日变化 |
| `sent_vel_5d` | sensor.json → sentiment.sentiment_velocity.change_5d | float | 情绪 5日变化 |

## Sensor — LLM (2) [OBSERVE ONLY]

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `llm_score` | sensor.json → sentiment.llm_sentiment.score | int | DeepSeek 评分 -100~+100 |
| `llm_label` | sensor.json → sentiment.llm_sentiment.label | str | LLM 情绪标签 |

## Sensor — Summary (2)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `sensor_risk_appetite` | sensor.json → summary.risk_appetite | str | expanding / contracting / mixed |
| `sensor_confidence` | sensor.json → summary.confidence | float | 综合环境置信 0-100 |

## Health (3)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `health_overall` | daily_report → health.overall | str | OK / WARNING / CRITICAL |
| `lgbm_loaded` | daily_report → health.models.lgbm_trend | bool | LGBM 模型是否加载 |
| `xgb_loaded` | daily_report → health.models.xgb_timing | bool | XGB 模型是否加载 |

## Account (3)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `account_cash` | daily_report → account.cash | float | 现金 |
| `account_positions` | daily_report → account.positions | int | 持仓数 |
| `account_total_value` | daily_report → account.total_value | float | 总资产 |

## Signals (2)

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `signal_symbols` | daily_report → signals[].symbol | str | 信号标的 (逗号分隔) |
| `signal_strategies` | daily_report → signals[].strategy | str | 信号策略 (逗号分隔) |

## Outcome — T+N 回填 (5) [v1.1 NEW]

> **设计目的**: 让 Evidence Table 从"系统怎么想"升级为"系统想得对不对"。
> T+0 提取时为空，T+N 天后由 `backfill_results()` 使用 akshare 沪深300 数据回填。

| 字段 | 来源 | 类型 | 说明 |
|------|------|:--:|------|
| `T1_return` | akshare → 沪深300 次日涨跌 | float | T+1 市场收益率 % |
| `T3_return` | akshare → 沪深300 3日涨跌 | float | T+3 市场累计收益率 % |
| `T5_return` | akshare → 沪深300 5日涨跌 | float | T+5 市场累计收益率 % (主验证窗口) |
| `max_dd_5d` | akshare → 沪深300 5日高点到低点 | float | 5日内最大回撤 % (风控核心指标) |
| `benchmark_5d` | akshare → 沪深300 5日涨跌 | float | 同期基准收益 % (= T5_return，沪深300 即为基准) |

### 如何使用 Outcome 验证三个 PA 假设

**假设 1 — Gate 是否有价值？**
```
比较: Gate开放日 vs Gate关闭日 → T5_return, max_dd_5d
成立条件: Gate开放日 T5_return 更高, max_dd 更低
```

**假设 2 — XGB Risk 是否保护？**
```
比较: 高risk过滤 vs 低risk通过 → max_dd_5d, T5_return
成立条件: 过滤组 max_dd 显著更小 (不看过收益，只看少亏)
```

**假设 3 — Regime 是否有效？**
```
比较: 退潮期 vs 高潮期 → T5_return
成立条件: 退潮期 T5_return 显著为负 → regime 正确识别了危险
```

## 生命周期

| 阶段 | 说明 |
|------|------|
| 实时 | date / regime / gate / sensor 字段 → pipeline 完成时写入 |
| T+0 | signals / fills / account → pipeline 完成时写入 |
| T+1~T+5 | Outcome 字段 → `backfill_results()` 在 run_daily.py finally 中自动回填 |
| T+N 回填 | LGBM_IC / XGB_filter / CatBoost_lift → 需要未来数据回填 (待实现) |

## AVP 规则

- ✅ v1.1 新增 5 个 Outcome 字段 — PA 批准 (08-09)，属于"证据完整性"
- ❌ 除此之外 Schema 冻结，不增不减不改
- ❌ 不计算任何"准确率"派生字段 (Outcome 是事实，不是评价)
- ✅ 字段来源和含义以此文档为准
- 📝 未来 TODO: Model Evidence Snapshot (lgbm_version, xgb_version, feature_hash) — Post-AVP
