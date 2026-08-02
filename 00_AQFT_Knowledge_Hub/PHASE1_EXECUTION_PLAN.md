# Phase 1 执行计划: 潜龙 → Capability Platform

Version: V1.0.0
Status: ✅ APPROVED
Date: 2026-08-02
Based on: DEC-029 Evidence-First Integration Architecture
Authority: GPT (设计) + 老板 (批复) + CC (执行)

---

## 核心原则

> **Observability before Optimization**
> 先提升可观测性，再优化决策。所有改动只增强"解释自己"的能力，不改变交易决策逻辑。

## Phase 1 验收标准

- 相同输入 → 相同决策（买/卖/仓位不变）
- **Decision Equivalence Test: 新旧系统 Replay → 决策 Binary Compare = 100% identical（非 99.8%）**
- 所有新增模块支持 Feature Toggle，关闭后系统照常交易
- 新增字段向后兼容（`confidence=None` 时照常运行）
- 禁止修改任何已有输出字段的语义

---

## 第一周: 潜龙工程债

### P0-0: Evidence Registry（半天，最先做）

**目标文件**: 新建 `evidence_registry.json`

**定位**: 所有 Evidence Producer 的统一注册表。必须先注册，再生产。

```json
{
  "registry_version": "v1",
  "producers": {
    "LGBM":       {"type": "ml_signal",    "version": "v1", "health": true, "owner": "潜龙"},
    "XGBoost":    {"type": "ml_signal",    "version": "v1", "health": true, "owner": "潜龙"},
    "CatBoost":   {"type": "ml_signal",    "version": "v1", "health": true, "owner": "潜龙"},
    "TDX":        {"type": "formula_signal","version": "v1", "health": true, "owner": "潜龙"},
    "PathA":      {"type": "path_a_signal", "version": "v1", "health": true, "owner": "AQF-T"},
    "Regime":     {"type": "market_regime", "version": "v1", "health": true, "owner": "AQF-T"},
    "ExitPipeline":{"type": "exit_event",   "version": "v1", "health": true, "owner": "AQF-T"}
  }
}
```

**规则**: 任何新 Producer 必须先在此注册，否则不承认其 Evidence。

### P0-1: ML Evidence Producer（原 Signal Attribution）

**目标文件**: 新建 `evidence_builder.py`（不修改 `ml_daily_report.py` 核心逻辑）

**定位**: 不是"增强输出"，而是 Evidence 体系第一个 Producer。只做三件事：
```
ML Signal → Evidence Object → Evidence Store
```

**不在 Producer 里做**: Fusion / Decision / Arbitration / Weight

**验收标准**:
- 旧版 Signal → 新版 Signal+Evidence，交易结果 Binary Compare = **100% 逐笔一致**
- Evidence 可单独关闭 (`ENABLE_EVIDENCE=false` → 系统恢复今天状态)
- LGBM/XGB/CatBoost 全部通过同一个 `evidence_builder.build()` 产出 Evidence

**五个问题**（每个 Evidence 必须能回答）:
1. 谁产生？（producer）
2. 什么时候产生？（timestamp）
3. 为什么产生？（top_features + reason）
4. 可信度是多少？（confidence + ic + calibration）
5. 后来证明它对了吗？（evaluation，P0-3 回填）

```json
{
  "evidence_id": "EVD-20260802-000013",
  "type": "ml_signal",
  "producer": "LGBM",
  "symbol": "000001",
  "timestamp": "2026-08-02T09:35:00",
  "signal": {
    "direction": "LONG",
    "strength": 0.72,
    "confidence": 0.82,
    "level": 5
  },
  "context": {
    "ic_20d": 0.31,
    "calibration": 0.84,
    "drift_score": 0.18,
    "drift_level": "LOW",
    "feature_version": "v2.8.6",
    "model_version": "lgbm_v3.2"
  },
  "version": {
    "contract_version": "evidence.v1",
    "git_commit": "b9b1e71"
  }
}
```

**红线**: 不修改 `score`/`buy_signal`/`level` 字段语义，只新增。

### P0-2: Evidence ID 系统

**目标文件**: 新建 `evidence_id.py`

**双编号体系**:
- 人类可读: `AQFT-{YYYYMMDD}-{6位序号}` → `AQFT-20260802-000018`
- 机器索引: UUID v7 (时间有序)

**元数据**: 每个 Evidence 带 `producer` / `contract_version` / `git_commit` / `parent_id`

### P0-3: Online Evaluation

**目标文件**: 新建 `signal_eval.py`

**评估维度**:
- `rolling_hit_rate`: 1d / 5d / 20d / 60d / lifetime
- `rolling_return` / `rolling_sharpe` / `rolling_max_drawdown`

**不只是评估模型，也评估 Evidence 可信度**:
- 每个 Evidence Producer (LGBM/XGB/TDX/Path A/Regime) 独立评估
- 输出: `evidence_trustworthiness = f(hit_rate, sharpe, stability)`
- 未来直接决定 AQF-T Evidence Fusion 权重

**存储**: `data/signal_eval.json`，每日收盘更新

### P0-4: Evidence Health (Drift Detection)

**目标文件**: 新建 `evidence_health.py`

**定位**: 不是 ML 专属的 Drift Detection，而是所有 Evidence Producer 的健康监控
- ML 模型: IC趋势 / 特征分布偏移 / 预测分布偏移
- TDX 公式: 信号密度变化 / 选股重合度
- Path A: 回封确认率趋势
- 未来任何 Producer 都可注册到此模块

**输出**:
- `drift_score`: 连续值 0-1（保留精度，不损失信息）
- `drift_level`: LOW (<0.2) / MEDIUM (0.2-0.5) / HIGH (>0.5)
- `health_status`: healthy / watch / danger

### P0-5: Exit Attribution（第四个做）

**目标文件**: `auto_exit_monitor.py`

**改动**: 增加二级退出原因分类

```json
{
  "exit_reason": {
    "category": "risk",
    "sub_category": "atr_stop",
    "trigger_price": 10.52,
    "entry_price": 11.08,
    "pnl_pct": -5.05,
    "holding_days": 4
  }
}
```

**分类体系**:
- `risk.atr_stop` / `risk.hard_stop` / `risk.drawdown`
- `strategy.break_exit` / `strategy.leader_end` / `strategy.pattern_invalid`
- `execution.timeout` / `execution.cancel`
- `manual.operator`
- `system.killswitch` / `system.expiry`

---

## 第二周: Contract 定义

### Contracts 目录

```
D:\AQF-T\contracts\
├── evidence_contract_v1.json      ← Evidence Schema (DEC-029 §4)
├── health_contract_v1.json        ← Health + Capabilities (DEC-029 §5.3)
├── decision_contract_v1.json      ← Request/Response/Fallback (DEC-029 §5.1-5.2)
├── producer_contract_v1.json      ← Producer 注册规范
└── ontology_v1.json               ← 统一语义层 (非字段映射，是概念对齐)
```

### Contract 顺序

1. **Evidence Contract** — 所有 Producer 输出格式（DEC-029 §4 的正式化）
2. **Health Contract** — 比 Decision 更底层（AQF-T DOWN → Decision 不存在）
3. **Decision Contract** — 依赖 Evidence + Health
4. **Producer Contract** — Producer 注册/发现/版本规范
5. **Ontology** — 统一语义层。潜龙的 `BUY_SIGNAL` 和 AQF-T 的 `ENTRY_SIGNAL` 不互相转换，而是共同映射到 `ENTRY_INTENT`。未来任何系统的字段都映射到此 Ontology，这是 Evidence Fusion 真正的基础。

**原则**: 只定义，不实现。

---

## 不改的事

- ❌ 不新增交易功能
- ❌ 不写融合代码
- ❌ 不修改 QMT
- ❌ 不修改 AQF-T Frozen 模块
- ❌ 不修改已有字段语义
- ❌ 不修改决策逻辑（相同输入=相同输出）

---

## 依赖关系

```
Evidence Registry (P0-0)
        ↓
ML Evidence Producer (P0-1) ──→ Evidence ID (P0-2)
        ↓
Online Evaluation (P0-3)
        ↓
Evidence Health (P0-4)
        ↓
Exit Attribution (P0-5)
```

**演进链**: Producer → Evidence → Identity → Evaluation → Health → Attribution

## Phase 1 成功标准

以后系统里的任何信息，都能回答五个问题：

1. **谁产生？** (producer)
2. **什么时候产生？** (timestamp)
3. **为什么产生？** (top_features + reason)
4. **可信度是多少？** (confidence + ic + calibration)
5. **后来证明它对了吗？** (evaluation，回填)

---

*Phase 1 执行计划 V1.0 — 2026-08-02 APPROVED*
*下一步: CC 逐个模块落盘，每个模块完成后 git commit*