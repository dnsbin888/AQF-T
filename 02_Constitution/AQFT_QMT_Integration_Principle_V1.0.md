# AQF-T QMT Integration Principle V1.0

Version: V1.0.0
Status: ✅ FROZEN — Constitution-Level Principle
Date: 2026-07-27
Applies to: All V3.0+ QMT integration

---

## 核心定义

**AQF-T owns intelligence. QMT owns execution.**

AQF-T 是大脑。QMT 是神经末梢 + 手足。券商柜台是最终动作接口。

---

## Principle 1: QMT shall execute, not decide

QMT 负责执行，不负责决策。

QMT 提供：
- `xtdata` — 实时行情、Tick、Level-2、五档盘口、成交明细、历史数据
- `xttrader` — 下单、撤单、查持仓、查成交、查资金
- 风控硬闸 — 账户级仓位上限、亏损限额（双层保险的底层）

QMT 不提供（在 AQF-T 架构中禁用）：
- ❌ 策略编辑器 — AQF-T Brain 替代
- ❌ 回测引擎 — AQF-T Simulation System 替代
- ❌ 内置算法交易 — AQF-T Strategy Intelligence 替代
- ❌ 条件单/网格交易 — AQF-T Decision Engine 替代
- ❌ 任何形式的独立交易判断

---

## Principle 2: All trading intentions originate from AQF-T Decision Intelligence

交易意图的唯一来源是 AQF-T Decision Intelligence。

```
合法路径:
  World Model → Decision → Strategy → Risk → QMT Adapter → xttrader → 券商

禁止路径:
  QMT Strategy → Order                          ❌
  Data → QMT内置策略 → 交易                      ❌
  Prediction → QMT直接下单                       ❌
```

---

## Principle 3: QMT cannot bypass the Intelligence Chain

QMT 不得绕过 AQF-T 智能链的任何一环。

```
强制执行顺序:
  World Model (理解) → Decision (行动选择) → Strategy (行动方案)
  → Risk (安全约束) → QMT Adapter (执行转换) → xttrader (下单)
```

---

## Principle 4: QMT is replaceable

QMT 是可替换的执行后端。

如果未来接入 CTP、XTP、IBKR、港股/期货接口，只需替换 Execution Adapter，不得修改 AI Brain 任何模块。

```
AQF-T Brain (不变)
      ↓
Execution Adapter (可替换)
      ↓
Broker API (QMT / CTP / XTP / IBKR / ...)
```

---

## AQF-T 分层架构（最终版）

```
══════════════════════════════════════
         AQF-T BRAIN (Intelligence)
══════════════════════════════════════
  World Model          → 市场是什么
  Reasoning Engine     → 为什么
  Decision Intelligence → 应该做什么
  Memory System        → 过去经验
  Evolution System     → 持续优化
══════════════════════════════════════
      TRADING NERVOUS SYSTEM
══════════════════════════════════════
  Strategy Intelligence → 行动方案
  Position Engine       → 仓位管理
  Risk Runtime          → 安全约束
══════════════════════════════════════
         EXECUTION LAYER
══════════════════════════════════════
  QMT Adapter           → API 封装
  xttrader              → 下单/撤单
  券商柜台               → 成交
══════════════════════════════════════
```

---

## QMT 职责清单

| 允许 | 禁止 |
|------|------|
| ✅ 行情采集 (xtdata) | ❌ 行情解释 |
| ✅ 订单执行 (xttrader) | ❌ 交易决策 |
| ✅ 状态反馈 (成交/持仓/资金) | ❌ 信号生成 |
| ✅ 风控硬闸 (账户级限制) | ❌ 仓位判断 |
| ✅ 登录/重连/会话管理 | ❌ 龙头/情绪/Regime判断 |
| | ❌ 修改 AQF-T 的任何 Decision |

---

## V3.0 执行层模块结构

```
04_Execution_Layer/
├── AQFT_Execution_Engine       # 执行编排
├── Broker_Adapter              # 券商抽象层（可替换）
├── QMT_Adapter                 # QMT 专用适配器
│   ├── xtdata 封装             # 行情订阅
│   ├── xttrader 封装           # 下单/撤单
│   ├── 会话管理                # 登录/重连
│   └── 状态同步                # 成交/持仓/资金
└── tests/
```

---

## QMT 提供事实，AQF-T 产生认知

```
QMT 输出:   "AI科技板块涨停20家"
AQF-T:      "情绪周期=回暖, 主线=AI, 龙头确认概率=0.72, Regime=Expansion"

QMT 输出:   "603xxx 当前价 25.80, 卖一 25.81 500手"
AQF-T:      "封单强度 3.2%, 板上在出货, 建议 Reduce"

QMT 输出:   事实 (What)
AQF-T 输出: 认知 (What it means)
```

---

*AQF-T QMT Integration Principle V1.0 — FROZEN*
*Constitution-Level. Effective from V3.0.*
