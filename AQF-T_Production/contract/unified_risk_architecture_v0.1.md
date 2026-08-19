# Unified Risk Architecture v0.2

> Status: Draft | Layer: AQF-T Decision OS · Governance
> Principle: Two engines, one authority chain. Different time scales, unified semantics.
> Changes v0.2: Protected Asset taxonomy + Risk Registry + Risk Service + Learning in Authority + State loop

---

## 〇、问题定义

潜龙和 AQF-T 各有一套风控，但它们保护的不是同一个对象：

| 系统 | 核心问题 | 保护对象 |
|------|------|------|
| 潜龙 | 我的账户还能不能继续交易？ | Portfolio State |
| AQF-T | 这一笔交易还能不能发？ | Decision/Order |

融合前必须回答四个问题：
1. 谁负责监控风险？（Continuous Risk）
2. 谁负责审批交易？（Decision Risk）
3. 谁拥有最终否决权？（Authority）
4. 阈值由谁提供、谁消费？（Threshold Provider）

---

## 一、Protected Asset Taxonomy（保护资产分类）

> Risk 是原因，Asset 是对象。真正保护的是资产，不是风险。

### 1.1 六类 Protected Asset

```
Protected Asset Taxonomy V1.0
│
├── Portfolio Asset（组合资产）
│   ├── PA-001 Drawdown      — 峰值回撤超限
│   ├── PA-002 Daily Loss     — 日亏损超限
│   ├── PA-003 Monthly Loss   — 月回撤超限
│   └── PA-004 Concentration  — 行业/单票集中度超限
│   Owner: 潜龙 (Continuous Monitor)
│
├── Decision Asset（决策资产）
│   ├── DA-001 Regime         — 退潮期买入
│   ├── DA-002 Sentiment      — 情绪周期不匹配
│   ├── DA-003 Evidence       — 多源证据矛盾
│   └── DA-004 Confidence     — ML置信度不足
│   Owner: AQF-T (Event Gate)
│
├── Execution Asset（执行资产）
│   ├── EA-001 Price          — 成交价偏离过大
│   ├── EA-002 T+1            — 日内回转
│   ├── EA-003 Limit          — 涨跌停不可交易
│   └── EA-004 Size           — 手数/金额异常
│   Owner: 潜龙 (Pre-Trade Check)
│
├── Market Asset（市场资产）
│   ├── MA-001 Regime         — 市场状态切换
│   ├── MA-002 Volatility     — 波动率突增
│   └── MA-003 Breadth        — 市场宽度崩溃
│   Owner: Both
│
├── Infrastructure Asset（设施资产）
│   ├── IA-001 Data           — 行情断开
│   ├── IA-002 QMT            — QMT连接异常
│   ├── IA-003 Drift          — 持仓不一致
│   └── IA-004 Resource       — 系统资源不足
│   Owner: 潜龙 (System Monitor)
│
└── Compliance Asset（合规资产）
    ├── CA-001 Blacklist      — 黑名单标的
    ├── CA-002 Suspension     — 停牌标的
    └── CA-003 New Share       — 新股未满60日
    Owner: 潜龙 (Stock Filter)
```

### 1.2 两系统职责矩阵

| Protected Asset | 潜龙 | AQF-T |
|------|:--:|:--:|
| Portfolio Asset | **OWNER** | Consumer |
| Decision Asset | Consumer | **OWNER** |
| Execution Asset | **OWNER** | — |
| Market Asset | Monitor | Consumer |
| Infrastructure Asset | **OWNER** | — |
| Compliance Asset | **OWNER** | — |

---

## 二、Risk Timeline（风险时间轴）

### 2.1 两条时间线

```
Continuous Risk (潜龙)              Event Risk (AQF-T)
══════════════════════              ══════════════════
每5分钟轮询                          每笔下单触发
    │                                    │
    ▼                                    ▼
Portfolio State                     Decision Request
(权益/回撤/日亏/连亏)                  (信号+证据+仓位)
    │                                    │
    ▼                                    ▼
阈值比对                             证据融合
    │                                    │
    ▼                                    ▼
分级响应                             准入判断
(黄/橙/红)                            (通过/降权/拒绝)
    │                                    │
    └──────────────┬─────────────────────┘
                   ▼
           Execution Permission
                   │
                   ▼
              Order Engine
```

### 2.2 统一为闭环（State 驱动）

```
State (Portfolio / Market / Risk)
    │
    ▼
Monitor (Continuous, 每5分钟)
    │
    ▼
Risk Assessment (潜龙 auto_breaker)
    │
    ▼
Signal → Decision (AQF-T Event Gate)
    │
    ▼
Pre-Trade Check (潜龙)
    │
    ▼
Execution
    │
    ▼
Feedback → State Update → Monitor (loop)
```

### 2.3 时间线不冲突

- 潜龙在盘前/盘中/盘后持续运行
- AQF-T 只在收到信号时触发
- 两者在不同时间尺度上工作，不竞争
- 任何一方触发 → Execution 层统一拦截

---

## 三、Authority Hierarchy（最终裁决权）

### 3.1 六级权威链

```
L0  Constitution (宪法)
     │  最高约束: 安全第一、T+1红线、禁止补仓
     │  任何系统不得违反
     ▼
L1  Global Stop (总闸)
     │  Owner: 潜龙
     │  能力: 全局停止所有交易
     │  触发: 回撤>15% / 日亏>5% / 连亏5笔
     │  范围: ALL channels
     ▼
L2  Risk Engine (风控引擎)
     │  Owner: 潜龙 (Continuous) + AQF-T (Event)
     │  能力: 分级限制
     │  🟡 钉钉提醒 → 🟠 关QMT快速 → 🔴 关总闸
     ▼
L3  Decision Engine (决策引擎)
     │  Owner: AQF-T
     │  能力: 拒绝/降权特定决策
     │  范围: 单笔交易
     ▼
L4  Learning (学习系统)
     │  Owner: 潜龙
     │  能力: 模型启用/退役/切换，因子生命周期管理
     │  未来扩展: 模型重训、自动退役
     ▼
L5  Strategy (策略)
     │  Owner: 策略自身
     │  能力: 策略级止盈止损、仓位管理
     │  范围: 策略内部
```

### 3.2 冲突裁决规则

```
CR-001: KillSwitch > Everything
  总闸开启时，任何系统不得放行任何买入订单。
  卖出订单永不拦截 (FIA 2024)。

CR-002: Continuous > Event
  如果潜龙熔断已触发，AQF-T 无需再评估该笔交易。
  AQF-T 应在评估前先查询 KillSwitch 状态。

CR-003: Risk > Decision
  Risk Engine 的 APPROVE 是 Decision 的必要条件，
  不是充分条件。Decision 不能绕过 Risk。

CR-004: Constitution > All
  任何自动化决策不得违反系统宪法。
  违反宪法的订单 → 无条件 REJECT。
```

### 3.3 AQF-T 集成规则

```
AQF-T 每次 Decision 前:
  1. 查询潜龙 KillSwitch 状态
     if ACTIVE → 不评估, 直接返回 REJECT(KillSwitch)
  
  2. 查询潜龙 Market Regime
     if 退潮期 → BUY 返回 REJECT(Regime)
  
  3. 查询潜龙 Risk Metrics
     if Portfolio Risk ALERT → 降权处理(半仓)
  
  4. 评估 Decision Risk (AQF-T 自身逻辑)
  
  5. 返回 Decision → 潜龙 Pre-Trade Check → Execution
```

---

## 四、Risk Service（风险服务）

> 替代 Threshold Provider。不是只提供阈值数字，而是提供统一风险接口。

### 4.1 Risk Service 接口

```
Risk Service
│
├── Thresholds
│   ├── GET /v1/risk/thresholds           — 全部阈值(按regime)
│   └── GET /v1/risk/thresholds/{param}   — 单个阈值
│
├── State
│   ├── GET /v1/risk/portfolio-state      — 当前组合状态
│   ├── GET /v1/risk/killswitch            — 总闸状态
│   └── GET /v1/risk/market-regime         — 市场状态
│
├── Breadth
│   ├── GET /v1/risk/market-breadth       — 市场宽度
│   └── GET /v1/risk/sector-heat          — 板块热度
│
└── Health
    ├── GET /v1/risk/data-status           — 行情连接状态
    └── GET /v1/risk/qmt-status            — QMT连接状态
```

### 4.2 当前阈值（Provider = 潜龙，Production Validated）

| 参数 | sideways | bull | bear |
|------|:--:|:--:|:--:|
| 日亏黄线 | 2% | 3% | 1.5% |
| 日亏红线 | 5% | 8% | 3.5% |
| 连亏黄线 | 2笔 | 2笔 | 2笔 |
| 连亏红线 | 5笔 | 5笔 | 5笔 |
| 回撤黄线 | 7% | 10% | 5% |
| 回撤红线 | 15% | 18% | 12% |
| 月回撤红线 | 12% | 15% | 10% |
| 行业集中黄线 | 20% | 25% | 15% |
| 行业集中红线 | 25% | 30% | 20% |
| 单票上限 | 20% | 20% | 15% |

### 4.3 AQF-T 消费方式

```
AQF-T 每次启动:
  thresholds = RiskService.GET /v1/risk/thresholds

  若 Risk Service 不可用:
    → 使用 AQF-T 内置兜底值 (更保守)
    → 单票10% / 总仓40% / 行业25%
    → 钉钉告警

  潜龙内部升级(如改回撤红线15%→12%):
    → Risk Service 自动返回新值
    → AQF-T 无需改动
```

---

## 五、两系统语义映射

| 概念 | 潜龙 | AQF-T | 统一术语 |
|------|------|------|------|
| 总闸 | circuit_breaker | KillSwitch.active | **Global Stop** |
| 分级 | yellow/orange/red | — | **Risk Level** |
| 回撤 | drawdown_pct | MAX_DRAWDOWN | **Peak Drawdown** |
| 日亏 | daily_loss | MAX_DAILY_LOSS | **Daily Loss** |
| 连亏 | consecutive_loss | — | **Losing Streak** |
| 行情断 | — | DATA_DISCONNECT | **Data Disconnect** |
| QMT异常 | — | QMT_ERROR | **QMT Error** |
| 恢复 | 手动复位 | release() | **Manual Reset** |

---

## 六、Risk Registry（风险注册表）

> 所有 Protected Asset 统一注册，不属于任何单一模块。

### 6.1 Registry 条目格式

```json
{
  "id": "PR-001",
  "protected_asset": "Portfolio.Drawdown",
  "asset_type": "Portfolio",
  "owner": "潜龙",
  "consumer": "AQF-T",
  "authority_level": "L1",
  "provider": "RiskService",
  "threshold": {"sideways": 15, "bull": 18, "bear": 12},
  "status": "ACTIVE",
  "evidence": "Runtime"
}
```

### 6.2 当前已注册条目

| ID | Protected Asset | Owner | Consumer | Authority |
|------|------|:--:|:--:|:--:|
| PR-001 | Peak Drawdown | 潜龙 | AQF-T | L1 |
| PR-002 | Daily Loss | 潜龙 | AQF-T | L2 |
| PR-003 | Losing Streak | 潜龙 | — | L2 |
| PR-004 | Monthly Drawdown | 潜龙 | — | L2 |
| PR-005 | Sector Concentration | 潜龙 | AQF-T | L2 |
| PR-006 | Single Position | 潜龙 | AQF-T | L2 |
| PR-007 | Data Disconnect | 潜龙 | AQF-T | L1 |
| PR-008 | QMT Error | 潜龙 | — | L1 |
| PR-009 | Position Drift | 潜龙 | — | L1 |
| PR-010 | Regime Downgrade | Both | AQF-T | L3 |

### 6.3 与其他 Registry 的关系

```
Capability Registry
├── Feature    (65 factors)
├── Protection (11 capabilities)
├── Learning   (3 models)
├── Risk       (10 entries)  ◄── 新增
└── Governance (CR-001~CR-006)
```

---

## 七、Capability Graph（能力依赖图）v0.3 预留

```
Feature (chip_v2)
    │
    ▼
Producer (TrendDetection)
    │
    ▼
Evidence (trend_evidence)
    │
    ▼
Decision (BUY signal)
    │
    ▼
Portfolio State (position added)
    │
    ▼
Risk Engine (drawdown monitor)
    │
    ▼
Global Stop (circuit_breaker)
```

未来任何 Feature 变更，可通过 Graph 追溯最终影响哪个 Protected Asset。

---

## 八、Version Compatibility

```
Risk Service 当前版本: 2.0

消费者兼容性:
  AQF-T       >= 2.8  → 兼容
  Protection  >= 1.0  → 兼容
  Learning    >= 1.0  → 兼容

升级规则:
  MAJOR: Protected Asset 增删 / Authority 层级变更 → Consumer 需更新
  MINOR: 阈值调整 / 新增接口 → 向后兼容
  PATCH: 文档修正 → 完全兼容

降级策略:
  Risk Service 不可用 → Consumer 使用内置兜底值(更保守)
  → 钉钉告警 "Risk Service 降级"
```

---

## 九、版本路线

```
v0.1 — 十层对齐（已完成）        2026-08-04
v0.2 — Protected Asset + Risk    2026-08-04
       Registry + Risk Service
       + Learning Authority
       + State Loop
v0.3 — Capability Graph          待定
v1.0 — FROZEN                    生产验证后
```

## 九、当前 Capability Registry 全景

```
Decision OS · Capability Registry
│
├── Feature     (65 factors, L1 audited)
├── Protection  (11 capabilities, FROZEN)
├── Learning    (3 models, v0.1 DRAFT)
├── Risk        (10 entries, v0.2 DRAFT)  ◄── 新增
└── Governance  (CR-001~CR-006)
```

---

*Unified Risk Architecture v0.2 — 2026-08-04*
*Two engines, one authority chain. Protected Assets, not risk objects.*
