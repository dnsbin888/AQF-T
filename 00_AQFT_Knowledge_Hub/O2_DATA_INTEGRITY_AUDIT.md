# O2: Historical Data Integrity Audit

Version: V1.0.0
Date: 2026-08-03
Type: Operation Phase 2 — Data Audit
Status: COMPLETE

---

## O2-1: Historical Evidence Coverage

| 数据 | 数量 | 完整度 | 说明 |
|------|:--:|:--:|------|
| 历史交易总数 | 32 (8 buy + 24 sell) | — | 2026-07-17 ~ 2026-08-01 |
| Buy 有 signal_source | 8/8 | 100% | "auto" / "qmt" |
| Buy 有 reason | 8/8 | 100% | e.g. "信号5级(16.7%仓) [ML]" |
| Buy 有 date/time | 8/8 | 100% | |
| Buy 有 model_version | 0/8 | 0% | 🔴 致命缺口 |
| Buy 有 feature_snapshot | 0/8 | 0% | 🔴 |
| Buy 有 regime at trade time | 0/8 | 0% | 🔴 |
| Buy 有 confidence | 0/8 | 0% | 🔴 |

**结论**: 可以回答"买什么、多少钱、什么时候"，但**不能回答"为什么觉得可以买"**。

## O2-2: Decision Reconstruction Test

样本: 中国石油 2026-07-20

| 字段 | 状态 |
|------|:--:|
| Entry signal | ✅ "信号5级(16.7%仓) [ML]" |
| Signal source | ✅ auto |
| Price/qty/date | ✅ |
| Model version | ❌ UNKNOWN |
| Feature snapshot | ❌ UNKNOWN |
| Regime | ❌ UNKNOWN |
| Confidence | ❌ UNKNOWN |
| Producer (TrendML vs MomentumML) | ⚠️ 可从 reason 推断 |

**重建完整度: 60%** — 可以回答"做了什么"，不能回答"为什么做"。

## O2-3: Producer Evolution Map

```
TrendML (LGBM):
  2026-07-04  v? — 17 features
  2026-07-07  v? — 27 features (增加了10个因子)
  2026-07-09  v? — 27 features
  2026-07-12  v? — 24 features (删除了3个因子)
  2026-08-02  v2.8.6 — 24 features (当前)

MomentumML (XGBoost):
  2026-07-09  xgb_model.json (当前)
  历史备份: .bak_20260715, .bak_20260716

CatBoost:
  2026-07-04 ~ 2026-07-18  多次训练
  2026-07-12  ARCHIVED (标签退化+stacking泄露)
```

**缺口**: 模型版本号从未被记录到交易日志中。同一个 `lgbm_model.pkl` 在 07-04 和 07-12 之间是不同的模型（不同的特征数），但交易只记录了 `[ML]` 标签。

## O2-4: Data Debt Register

| ID | 债务 | 影响 | 等级 | 计划 |
|----|------|------|:--:|------|
| AD-005 | 历史交易缺失 model_version | 无法回溯 Evidence | MEDIUM | 从现在开始记录，不修复历史 |
| AD-006 | 历史交易缺失 regime | 无法评估 Decision 质量 | MEDIUM | 从现在开始记录 |
| AD-007 | 历史交易缺失 confidence | DEC-034 缺少校准数据 | MEDIUM | 从现在开始记录 |
| AD-008 | Producer 版本未与交易关联 | 历史回放不可复现 | HIGH | M3: Decision Trace 记录 runtime_version |
| AD-009 | ML Signal Track 仅 10 天 | Learning 样本不足 | LOW | 继续积累，30天后自然解决 |

## 结论

**不是 AQF-T 架构问题。是潜龙 Capability 层历史数据不完整。**

- 过去 32 笔交易: 有结果、缺证据
- 2026-08-02 起: Evidence Builder 已接入 → 以后每笔交易都带完整 Evidence
- 30 天后: 累积足够的 Evidence→Decision→Outcome 链，DEC-034 Learning 可以启动

**建议**: 不修复历史。从现在开始，每笔交易都记录完整 Evidence。30 天后第一次 Evidence Quality Review。

---

*O2 Data Integrity Audit V1.0 — 2026-08-03*
