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
- 新增内容仅增加日志、证据、归因、统计、健康状态
- 所有新增模块可关闭（不影响现有交易流程）
- 新增字段向后兼容（`confidence=None` 时照常运行）
- 禁止修改任何已有输出字段的语义

---

## 第一周: 潜龙工程债

### P0-1: Signal Attribution（最先做）

**目标文件**: `ml_daily_report.py` / 新建 `evidence_builder.py`

**改动**: ML 信号输出从散字段升级为结构化 Evidence 对象

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

### P0-2: Evidence ID 系统 (P0.5)

**目标文件**: 新建 `evidence_id.py`

**格式**: `EVD-{YYYYMMDD}-{6位序号}`，全局唯一
- 每个 Evidence 带上 `producer` / `version` / `git_commit`
- 支持 Parent 引用（Signal-00021 → EVD-xxx）

### P0-3: Online Evaluation（第二个做）

**目标文件**: 新建 `signal_eval.py`

**输出**:
- `rolling_hit_rate`: 1d / 5d / 20d / 60d / lifetime
- `rolling_return`: 同期平均收益
- `rolling_sharpe`: 滚动夏普
- `rolling_max_drawdown`: 滚动最大回撤

**存储**: `data/signal_eval.json`，每日收盘后更新

### P0-4: Drift Detection（第三个做）

**目标文件**: 新建 `factor_drift.py`

**逻辑**: 基于 Online Evaluation 的 IC 趋势
- `drift_score`: 连续值（0-1，保留精度）
- `drift_level`: LOW (<0.2) / MEDIUM (0.2-0.5) / HIGH (>0.5)
- 检测指标: IC 趋势 / 特征分布偏移 / 预测分布偏移

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
└── mapping_table_v1.json          ← 潜龙字段 → Evidence 字段映射
```

### Contract 顺序

1. **Evidence Contract** — 所有 Producer 输出格式（DEC-029 §4 的正式化）
2. **Health Contract** — 比 Decision 更底层（AQF-T DOWN → Decision 不存在）
3. **Decision Contract** — 依赖 Evidence + Health
4. **Producer Contract** — Producer 注册/发现/版本规范
5. **Mapping Table** — 潜龙现有字段 → Evidence Schema 映射

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
Signal Attribution ──→ Online Evaluation ──→ Drift Detection
         │                                          │
         └──→ Evidence ID 系统                       │
                                                    │
Exit Attribution ←──────────────────────────────────┘
    (独立，但受益于统一的 Reason Code 体系)
```

---

*Phase 1 执行计划 V1.0 — 2026-08-02 APPROVED*
*下一步: CC 逐个模块落盘，每个模块完成后 git commit*