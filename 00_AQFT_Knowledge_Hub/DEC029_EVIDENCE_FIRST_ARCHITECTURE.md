# DEC-029: Evidence-First Integration Architecture

Version: V1.0.0
Status: ✅ FROZEN — Architecture Decision
Date: 2026-08-02
Type: Architecture Decision Record (ADR-001)
Authority: GPT (Chief Architect) + 老板 (Project Owner) + CC (Secondary Audit)
Scope: AQF-T × 潜龙 融合架构 — 未来数年演进边界

---

## 一、设计原则 (Principles)

以下原则为架构级约束，不可轻易修改。任何违反这些原则的提案需经过 Architecture Review + 老板重新批准。

### P1: Evidence First

**一切模块输出 Evidence，不输出交易指令。**

- ML 模型输出的是 Evidence，不是 BUY/SELL
- Pattern 输出的是 Evidence，不是 BUY/SELL
- Regime 输出的是 Evidence，不是仓位系数
- Risk 输出的是 Evidence，不是 REJECT/APPROVE
- 全系统只有一个模块可以输出最终 Decision：**Evidence Fusion Engine**

### P2: Capability 与 Intelligence 解耦

- 潜龙负责 Capability（数据/训练/执行/展示/运维）
- AQF-T 负责 Intelligence（理解/识别/融合/决策/退出/解释）
- 任何一方升级不影响另一方

### P3: Platform Agnostic

- AQF-T 不依赖潜龙。未来可接入其他执行平台
- 潜龙不依赖 AQF-T。AQF-T 不可用时降级自决
- 桥接媒介：Trading Intelligence Contract（非直接代码调用）

### P4: Failure Isolation

- AQF-T 故障时，潜龙必须能独立完成交易
- 潜龙故障时，AQF-T 不崩溃（但无法执行）
- 任一系统不可用时，另一系统不受影响

### P5: Graceful Degradation

- AQF-T 不可用 → 潜龙降级到 Lv1-Lv5 自决
- AQF-T 置信度低 → 保守执行（半仓或观望）
- AQF-T 返回超时 → 潜龙自决（不等待）

### P6: Contract > API

- API（HTTP/gRPC）是实现细节
- Contract（TIC）定义接口语义、版本、能力协商
- 实现方式可变，Contract 稳定

---

## 二、职责边界 (Boundary)

### 潜龙 (Capability Platform)

| 领域 | 职责 |
|------|------|
| Data | 5路径行情采集(QMT/TDX/Sina/akshare/baostock)、数据治理 |
| ML Infrastructure | 因子管线、模型训练(Optuna)、IC跟踪、Drift检测、Calibration |
| Model Management | LGBM/XGBoost/CatBoost 模型版本管理 |
| Execution | QMT passorder、Flask审核通道、键盘F1-F8、同花顺联动 |
| UI | Flask多页面、Streamlit仪表盘、SSE推送 |
| Alert | 钉钉机器人(Webhook+指令解析) |
| Operations | 盘前检查、日终对账、备份、收盘报告 |
| Decision Fallback | AQF-T 不可用时，Lv1-Lv5 信号等级自决 |

### AQF-T (Trading Intelligence)

| 领域 | 职责 |
|------|------|
| Perception | Path A 回封板感知(炸板分类→回封确认→龙头判定) |
| Pattern | 市场模式识别(卡位/龙头/梯队/情绪/轮动/强度) |
| Regime | 四阶段情绪周期(冰点/回暖/高潮/退潮) + 操作模式映射 |
| Evidence Fusion | 多源 Evidence 加权融合 → 统一决策 |
| Decision | 最终决策输出(方向+仓位+置信度+推理链) |
| Exit Pipeline | 策略退出(炸板退出/龙头结束/题材死亡/依据失效) + 退出证据 |
| Evidence | Decision Record、Reasoning Trace、Outcome Evaluation(A-F) |
| Reasoning | 决策推理链：为什么/为什么不/什么会改变 |

### 红线 (Never)

```
❌ AQF-T 不直接调用 QMT
❌ AQF-T 不直接执行交易
❌ AQF-T 不训练 ML 模型
❌ 潜龙 不负责 Evidence Fusion
❌ 潜龙 不修改 AQF-T 内部逻辑
✅ 双方只交换 Contract
```

---

## 三、Evidence Taxonomy (证据分类体系)

所有模块的输出统一归类为以下 Evidence 类型：

```
Evidence Taxonomy V1.0
│
├── Market Evidence（市场证据）
│   ├── RegimeEvidence       — 市场状态判断
│   ├── SentimentEvidence    — 情绪周期
│   └── FlowEvidence         — 资金流向(北向/融资/龙虎榜)
│
├── Pattern Evidence（模式证据）
│   ├── LeaderEvidence       — 龙头8维
│   ├── PositionEvidence     — 卡位博弈
│   ├── LadderEvidence       — 梯队完整性
│   ├── SectorEvidence       — 板块轮动
│   └── StrengthEvidence     — 相对强度
│
├── ML Evidence（模型证据）
│   ├── PredictionEvidence   — 趋势预测(LGBM/XGBoost)
│   ├── TimingEvidence       — 时机信号
│   └── FactorEvidence       — 因子信号
│
├── Risk Evidence（风险证据）
│   ├── ExposureEvidence     — 仓位敞口
│   ├── ConcentrationEvidence— 集中度
│   ├── DrawdownEvidence     — 回撤
│   └── KillSwitchEvidence   — 熔断状态
│
├── Exit Evidence（退出证据）
│   ├── RiskExitEvidence     — 硬止损/回撤限制/退潮清仓
│   ├── StrategyExitEvidence — 炸板退出/龙头结束/题材死亡
│   └── ExpiryEvidence       — 持仓到期
│
└── Execution Evidence（执行证据）
    ├── FillEvidence          — 成交
    ├── RejectEvidence        — 拒绝
    ├── SlippageEvidence      — 滑点
    └── FeedbackEvidence      — 结果回传
```

---

## 四、Evidence Schema V1.0

所有系统（潜龙、AQF-T、未来系统）必须输出此格式：

```json
{
  "evidence_id": "EV_20260802_093500_001",
  "source": "LGBM",
  "category": "ML.Prediction",
  "symbol": "000001",
  "timestamp": "2026-08-02T09:35:00+08:00",

  "signal": {
    "direction": "LONG",
    "strength": 0.72,
    "confidence": 0.82
  },

  "context": {
    "model_version": "lgbm_v3.2",
    "feature_version": "v18",
    "ic_20d": 0.31,
    "regime_at_inference": "回暖期",
    "data_freshness": "2026-08-01",
    "calibration": "platt_scaling"
  },

  "trace": {
    "top_features": [
      {"name": "momentum_20d", "contribution": 0.28},
      {"name": "volume_breakout", "contribution": 0.22},
      {"name": "sector_relative", "contribution": 0.15}
    ],
    "reason": "多周期趋势共振 + 量价配合 + 板块领涨"
  },

  "version": "evidence.schema.v1"
}
```

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `evidence_id` | string | 全局唯一标识 |
| `source` | string | 来源模块/模型名称 |
| `category` | string | 证据分类(Taxonomy路径) |
| `timestamp` | string | ISO8601 时间戳 |
| `signal.direction` | string | LONG / SHORT / NEUTRAL |
| `signal.strength` | float | 信号强度 0-1 |
| `signal.confidence` | float | 置信度 0-1 |

### 可选字段

| 字段 | 说明 |
|------|------|
| `context.model_version` | 模型版本号 |
| `context.feature_version` | 特征版本号 |
| `context.ic_20d` | 20日IC值 |
| `trace.top_features` | 主要驱动特征列表 |
| `trace.reason` | 人类可读的理由 |

---

## 五、Trading Intelligence Contract (TIC V1.0)

### 5.1 Request Layer

```
POST /v1/regime/evaluate
  Request:  { market_stats: {...}, timestamp: "..." }
  Response: { regime, confidence, operation_mode, evidence: {...} }
  Fallback: 潜龙本地四因子判断

POST /v1/decision/evaluate
  Request:  { candidates: [Evidence, ...], positions: [...], account: {...} }
  Response: { decisions: [Decision, ...], confidence, reasoning_trace }
  Fallback: 潜龙 Lv1-Lv5 自决

POST /v1/exit/check
  Request:  { positions: [{symbol, entry_evidence, holding_days, ...}], regime }
  Response: { exit_orders: [ExitOrder, ...] }
  Fallback: 潜龙 ATR止损 + 移动止盈
```

### 5.2 Feedback Layer

```
POST /v1/feedback/execution
  Request:  { decision_id, fills: [FillEvidence, ...], rejects: [RejectEvidence, ...] }
  Response: { acknowledged: true }

POST /v1/feedback/exit
  Request:  { exit_order_id, fill: FillEvidence, hold_days, pnl }
  Response: { acknowledged: true, evaluation: { grade: "A-F", lesson: "..." } }
```

### 5.3 Health Layer

```
GET /v1/health
  Response: { status: "OK"|"DEGRADED"|"DOWN", uptime, version, latency_ms }

GET /v1/capabilities
  Response: {
    regime: true, pattern: true, exit: true, evidence_fusion: true,
    world_model: false, llm: false, cross_market: false
  }
```

### 5.4 Degradation Policy

| AQF-T 状态 | 潜龙行为 |
|------------|----------|
| OK, confidence > 0.6 | 使用 AQF-T 决策 |
| OK, confidence 0.4-0.6 | 保守执行(半仓) |
| OK, confidence < 0.4 | 仅使用 Regime 判断，信号自决 |
| DEGRADED (超时>3s) | 降级到 Lv1-Lv5 自决 |
| DOWN (无响应) | 完全自决 + 钉钉告警 |
| AQF-T 返回任何 Decision 之间 | 潜龙风控仍然检查每一项 |

---

## 六、Evidence Fusion Engine (EFE)

### 6.1 命名

全系统核心模块正式命名为 **Evidence Fusion Engine (EFE)**。

- Decision 不是独立引擎，Decision 是 EFE 的输出
- EFE 接收任意来源的 Evidence，输出统一 Decision
- EFE 是 AQF-T 中唯一可以生成交易指令的模块

### 6.2 融合公式 (参考)

```
Decision = EFE(Evidence_Set, Regime_Context, Risk_Constraints)

Where:
  Weighted_Score = Σ (Evidence.strength × Evidence.confidence × Regime_Weight)
  Final_Confidence = f(Weighted_Score, Evidence_Alignment, Risk_Buffer)
  Action = Select_Action(Weighted_Score, Final_Confidence, Regime.operation_mode)
```

### 6.3 目录结构 (建议)

以后 AQF-T_Production 模块组织可以朝此方向演进：

```
AQF-T_Production/
├── evidence/              ← 新：证据体系（替代分散的模块目录）
│   ├── market/            ← Regime / Sentiment / Flow
│   ├── pattern/           ← Leader / Position / Ladder / Sector / Strength
│   ├── ml/                ← Prediction / Timing / Factor（消费，非训练）
│   ├── risk/              ← Exposure / Concentration / Drawdown / KillSwitch
│   ├── exit/              ← RiskExit / StrategyExit / Expiry
│   └── execution/         ← Fill / Reject / Slippage / Feedback
├── fusion/                ← Evidence Fusion Engine (EFE)
│   ├── collector.py       ← 收集 Evidence
│   ├── aligner.py         ← 对齐 + 标准化
│   ├── weighter.py        ← Regime-自适应权重
│   ├── fuser.py           ← 加权融合
│   ├── resolver.py        ← 冲突消解
│   └── decider.py         ← 最终决策输出
├── decision/              ← Decision Record / Reasoning Trace
├── contract/              ← TIC 实现 (HTTP/gRPC)
├── runtime/               ← 不变
├── strategy/              ← 不变
├── risk/                  ← 不变
├── execution/             ← 不变
└── operations/            ← 运维脚本
```

---

## 七、Roadmap

```
Phase 1: Evidence Schema V1.0
├── 定义 Evidence Schema JSON 规范
├── Evidence Taxonomy 文档
├── 参考实现: evidence.py (Python dataclass + validator)
└── 产出: evidence_schema_v1.json + evidence.py

Phase 2: Signal Attribution
├── 潜龙 ML 信号格式化为 Evidence
├── 潜龙退出记录格式化为 Exit Evidence
├── 潜龙新增 /api/evidence/ml 端点
└── 产出: 潜龙侧 Evidence 输出就绪

Phase 3: Evidence Fusion Engine (EFE) 骨架
├── AQF-T 实现 collector + aligner + weighter
├── 接入潜龙 Evidence 端点
├── 模拟数据集成验证
└── 产出: EFE 原型 + 集成测试通过

Phase 4: Trading Intelligence Contract V1.0
├── Request Layer (regime/decision/exit)
├── Feedback Layer (execution/exit)
├── Health Layer (health/capabilities)
├── Degradation Policy 实现
└── 产出: TIC 完整实现 + 降级测试通过

Phase 5: QMT Data Bridge
├── AQF-T QMTProvider 实现
├── 潜龙 QMT 行情 → AQF-T MarketDataProvider
├── 真实数据 Replay 验证
└── 产出: QMT 数据通路就绪

Phase 6: Real-time Evidence Fusion
├── 盘中实时 Evidence 流
├── 潜龙 Dashboard 展示 AQF-T 决策
├── 钉钉推送 AQF-T 决策摘要
└── 产出: 全链路实时运行
```

---

## 八、决策追溯

### 讨论过程

| 阶段 | 产出 |
|------|------|
| 潜龙 vs AQF-T 深度比对 | `QIANLONG_VS_AQFT_BENCHMARK_V1.0.md` |
| 设计资产审计 | `DESIGN_ASSET_AUDIT_V1.0.md` |
| GPT 方案讨论 | 决策增强层 → Decision OS → Evidence First |
| CC 终审 | 四个修正 + Evidence Schema 优先 |
| 老板最终批复 | DEC-029 冻结 |

### 关键决议

| 决议 | 结论 |
|------|------|
| 是否合并代码 | ❌ 不合并 |
| 先做什么 | Evidence Schema，非 Decision API |
| 核心模块命名 | Evidence Fusion Engine (EFE) |
| ML 训练归属 | 潜龙 |
| AQF-T 是否唯一决策 | Phase1 否（潜龙保留降级），Phase2 逐渐过渡 |
| 接口名称 | Trading Intelligence Contract (TIC) |

---

## 九、相关文档

| 文档 | 路径 |
|------|------|
| CC 角色 V2.0 | `00_AQFT_Knowledge_Hub/CC_ROLE_V2.md` |
| 设计资产审计 | `00_AQFT_Knowledge_Hub/DESIGN_ASSET_AUDIT_V1.0.md` |
| 潜龙 vs AQF-T 比对 | `00_AQFT_Knowledge_Hub/QIANLONG_VS_AQFT_BENCHMARK_V1.0.md` |
| AI 入门指南 | `00_AQFT_Knowledge_Hub/AI_ONBOARDING.md` |
| 系统状态 | `00_AQFT_Knowledge_Hub/AQFT_SYSTEM_STATE.md` |
| 决策日志 | `00_AQFT_Knowledge_Hub/AQFT_DECISION_LOG.md` |

---

*DEC-029: Evidence-First Integration Architecture V1.0 — FROZEN*
*2026-08-02 | GPT + 老板 + CC 三方共识*
*本文件为架构级冻结文档，修改需 Architecture Review + 老板重新批准*
