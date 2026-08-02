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

## Phase 1 Gate 系统

每完成一个 P0，必须通过对应 Gate 才能进入下一任务。任何 Gate 未通过 → 整个 Phase 暂停。

| P0 | Gate | 必须满足 |
|:--:|------|----------|
| P0-0 | **G0** | Registry Validation 100% 通过（7项校验全绿） |
| P0-1 | **G1** | Decision Equivalence Test = 100%（新旧 Replay 逐笔一致） |
| P0-2 | **G2** | 双编号唯一性验证（无重复 ID） |
| P0-3 | **G3** | Evaluation 与历史数据一致（不改变任何历史分数） |
| P0-4 | **G4** | Evidence Health 不影响任何交易输出（可关闭验证） |
| P0-5 | **G5** | Exit Reason 全覆盖 + Replay 一致 |

## Pluggable 原则

Phase 1 所有新增模块必须可插拔：

```
ENABLE_EVIDENCE = False        → 系统恢复今天状态
ENABLE_EVALUATION = False      → 系统恢复今天状态
ENABLE_HEALTH = False          → 系统恢复今天状态
```

**不是删代码，是关闭模块。** 所有 Feature Toggle 集中在 `evidence_registry.py` 的 `ENABLE_EVIDENCE` 总开关。

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
    "trend_ml": {
      "producer_id": "trend_ml",
      "evidence_type": "trend_evidence",
      "responsibility": "趋势是否成立？",
      "implementation": {"algorithm": "LightGBM", "version": "v2.8.6"},
      "lifecycle": "ACTIVE",
      "owner": "潜龙"
    },
    "momentum_ml": {
      "producer_id": "momentum_ml",
      "evidence_type": "momentum_evidence",
      "responsibility": "是否存在持续加速？",
      "implementation": {"algorithm": "XGBoost", "version": "v2.8.6"},
      "lifecycle": "ACTIVE",
      "owner": "潜龙"
    },
    "catboost_ml": {
      "producer_id": "catboost_ml",
      "evidence_type": "ml_signal",
      "responsibility": "多模型投票(已退役)",
      "implementation": {"algorithm": "CatBoost", "version": "v2.8.6"},
      "lifecycle": "ARCHIVED",
      "archived_reason": "标签退化+stacking泄露 (2026-07-12)",
      "owner": "潜龙"
    },
    "tdx_formula": {
      "producer_id": "tdx_formula",
      "evidence_type": "formula_evidence",
      "responsibility": "通达信公式技术信号",
      "implementation": {"algorithm": "TDX", "version": "v1"},
      "lifecycle": "ACTIVE",
      "owner": "潜龙"
    },
    "path_a": {
      "producer_id": "path_a",
      "evidence_type": "board_evidence",
      "responsibility": "回封板确认",
      "implementation": {"algorithm": "AQF-T Perception", "version": "v1"},
      "lifecycle": "ACTIVE",
      "owner": "AQF-T"
    },
    "regime": {
      "producer_id": "regime",
      "evidence_type": "regime_evidence",
      "responsibility": "市场状态判断",
      "implementation": {"algorithm": "AQF-T RegimeEngine", "version": "v1"},
      "lifecycle": "ACTIVE",
      "owner": "AQF-T"
    },
    "exit_pipeline": {
      "producer_id": "exit_pipeline",
      "evidence_type": "exit_evidence",
      "responsibility": "策略退出信号",
      "implementation": {"algorithm": "AQF-T ExitPipeline", "version": "v1"},
      "lifecycle": "ACTIVE",
      "owner": "AQF-T"
    }
  }
}
```

**规则**:
- 任何新 Producer 必须先注册
- `producer_id` 是稳定身份（内部实现可替换，身份不变）
- `lifecycle`: ACTIVE → DEPRECATED → ARCHIVED（不删除，保留历史追溯）
- `responsibility`: 回答"这个 Producer 解决什么问题"，而非"用什么算法"

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

## Phase 2 候选: DEC-032 — Evidence Specialization

> Phase 1 只改身份（Identity），不改能力（Behavior）。Phase 2 进入真正的 ML 架构重组。

### 核心原则

- **Evidence Specialization > Feature Ownership** — 先定义 Producer 回答什么问题，再决定用什么特征
- **Implementation Independence** — `producer_id` 稳定，内部算法可替换
- **Evidence Diversity > Low Correlation** — 目标是不同的证据视角，不是低相关性数字

### DEC-032 目录（GPT 待设计）

1. Producer Identity — 稳定身份 vs 可变实现
2. Producer Responsibility — 每个 Producer 回答什么市场问题
3. Evidence Boundary — 不同 Evidence 之间的领地边界
4. Evidence Diversity — 互补性度量（非相关性）
5. Implementation Independence — 算法可替换，Contract 不变
6. Feature Ownership — 特征分配到 Producer（最后一步，非第一步）

### 与 Phase 1 的关系

```
Phase 1: 零影响交易结果
  ├── 改命名: LGBM→TrendML, XGB→MomentumML
  ├── 改身份: Evidence Registry 注册
  └── 不改: 因子/模型/信号

Phase 2: 允许影响交易结果（需完整回测+模拟验证）
  ├── 重分配: 因子归属到不同 Producer
  ├── 重训练: 各自用专属因子子集
  ├── 相关性: 从 ~0.9 降到 <0.7（作为副作用，非目标）
  └── 算法升级: 内部实现可替换
```

---

*Phase 1 执行计划 V1.2 — 2026-08-02 APPROVED*
*DEC-032 候选已标记 — Phase 2 GPT 正式设计*
*下一步: CC 从 P0-0 Evidence Registry 开始落盘*