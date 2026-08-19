# 信号矛盾深度分析：Regime vs Sentiment vs AI

**日期**: 2026-08-12
**触发**: Dashboard 显示 Regime(高潮期·80%仓位) 与 Sentiment(-26骤降) + AI(-20悲观) 严重矛盾
**分析人**: CC
**审批**: PA+EA

---

## 1. 矛盾现场还原

Dashboard 同时显示以下互相矛盾的信号：

| 信号源 | 数值 | 含义 | 对交易的建议 |
|--------|------|------|------------|
| **Regime** (AQF-T) | 高潮期 | 市场情绪高涨 | Gate 开放, 80%仓位, "重仓出击" |
| **Gate** (V2) | trade_allowed=true | 允许交易 | 无限制 |
| **Position Scale** (V2) | 0.80 | strong_bull | 单票 Lv5=12%×0.80=9.6% |
| **Sentiment** (实时) | score≈24, 骤降-26 | 情绪骤降 | "警惕恐慌蔓延" |
| **LLM Sentiment** | -20 | 悲观 | 新闻面偏空 |
| **涨跌统计** | 0涨/0跌 | 数据未加载或全平 | 无法判断 |

**核心矛盾**: 旧数据说"冲"，新数据说"逃"。

---

## 2. 根因：两条独立信号链，零交叉验证

### 2.1 决策链（控制交易）

```
stock_data.parquet(EOD Aug11)
  → V2 market_regime.detect_regime() → strong_bull, position_scale=0.80
  → AQF-T pipeline → MarketRegimeEngine.evaluate() → 高潮期
  → latest_status.json {trade_allowed: true, effective_from: "2026-08-12 09:25"}
  → V2 execution_gate.py → ALLOWED (只读 trade_allowed 布尔值)
  → V2 auto_trade_plan → 下单
```

### 2.2 观测链（只展示，不控制）

```
eastmoney 实时推送 (60s 刷新)
  → V2 realtime_sentiment.py → score, label, LU/LD
  → AQF-T market_sensor.py → SentimentSensor._collect_market()
  → latest_sensor.json (note: "AVP Shadow — 仅供参考，不参与交易决策")
  
DeepSeek API (1次/天)
  → V2 llm_sentiment.py → score -100~+100
  → latest_sensor.json (同上，不参与决策)
```

### 2.3 断裂点

```
┌─────────────────────────────────────────────────────┐
│                   DECISION PATH                      │
│  Regime(EOD) ──→ latest_status.json ──→ Gate ──→ 交易 │
│                      (16h stale)        (binary)      │
└─────────────────────────────────────────────────────┘
                         │
                    零交叉验证 ❌
                         │
┌─────────────────────────────────────────────────────┐
│                 OBSERVATION PATH                     │
│  Sentiment(60s) ──→ Dashboard 显示 ──→ 人类看到矛盾   │
│  LLM(1d)       ──→ Dashboard 显示                    │
│  Market Sensor ──→ latest_sensor.json (Shadow)       │
└─────────────────────────────────────────────────────┘
```

---

## 3. 数据新鲜度差距量化

| 信号 | 数据日期 | 输出时间 | 到次日09:25的延迟 | 盘中更新？ |
|------|---------|---------|-----------------|:--:|
| **AQF-T Regime** | Aug 11 EOD | Aug 11 17:09 | ~16h | ❌ 每天1次 |
| **V2 market_regime** | stock_data.parquet Aug 11 | EOD | ~16h | ❌ 每天1次 |
| **latest_status.json** | Aug 11 | Aug 11 17:09 | ~16h | ❌ 每天1次 |
| **Sentiment (实时)** | eastmoney 当前 | 当前 | ~60s | ✅ 60s轮询 |
| **LLM Sentiment** | 上次调用 | 上次调用 | 最长24h | ❌ 1次/天 |
| **Market Sensor** | 综合 | Aug 11 17:09 | ~16h | ❌ 每天1次 |

### 3.1 为什么 Regime 在 Aug 12 早上仍然显示"高潮期"

- `latest_status.json` 的 `effective_from` = `2026-08-12 09:25:00`，这是**正确的设计**（Regime Snapshot Contract P1.1）
- 但 `trade_allowed: true` 是基于 Aug 11 EOD 数据计算的
- 从 Aug 11 15:00 到 Aug 12 09:25 之间，**没有任何机制更新 Regime**
- 如果 Aug 12 开盘大幅低开/跳水，Regime 仍然"不知道"

### 3.2 为什么 Sentiment 能检测到变化

- `realtime_sentiment.py` 每 60 秒从 eastmoney 拉取实时数据
- 涨跌比、涨停/跌停数、指数变化 → 情绪分实时更新
- 骤降 -26 意味着：60 秒前到现在的情绪分暴跌 26 点
- 这在开盘跳水时是有效的实时预警

---

## 4. Gate 决策链检查

### 4.1 `execution_gate.py` 检查清单

```python
# Line 76-112: check_execution_permission()
# 检查项:
1. AQF-T status 文件可读?          ✅ 有 latest_status.json
2. effective_from 时间守卫?        ✅ 09:25 已过
3. trade_allowed == True?         ✅ 高潮期 → True
4. pipeline_status != "error"?    ✅ completed
# = 决策: ALLOWED
```

**情绪/AI 权重在 Gate 中**: **零。完全不参与。**

### 4.2 `market_regime.py` (V2) 仓位映射

```python
# Line 186-196: detect_regime()
# 输入: stock_data.parquet (EOD Aug 11)
# 输出: strong_bull → position_scale=0.80
# 情绪/AI 权重: 零。完全不参与。
```

### 4.3 `market_sensor.py` (AQF-T) 综合摘要

```python
# Line 692: _build_summary()
# 汇总 margin/lhb/etf/sentiment → risk_appetite + confidence
# 但 note: "AVP Shadow — 仅供参考，不参与交易决策"
# 输出到 latest_sensor.json，不写入 latest_status.json
```

---

## 5. 方案设计

### 5.0 约束条件（铁律）

| # | 约束 | 来源 |
|---|------|------|
| 1 | `Shadow=Observer` — Market Sensor 不控制交易 | AVP纪律 |
| 2 | `不得直接接入生产端` — 不修改 QMT 执行通道 | 用户指令 |
| 3 | `P1 Architecture FROZEN` — 7红线不可破 | P1封板 |
| 4 | `Regime Contract SD-CONTRACT-002` — 3档canonical | Regime封板 |
| 5 | `Gate = 唯一执行边界` — 不绕过 Gate | OBS-013 |
| 6 | `fail-closed` — AQF-T 不可达 → 禁止交易 | execution_gate.py |

### 5.1 方案 A：Sentiment Gate Override（推荐 ⭐）

**核心思想**: 在 Gate 层面增加一个 **Sentiment Safety Check**，当实时情绪与 Regime 严重矛盾时，Gate 降级但不关闭。

#### 架构

```
                    ┌──────────────┐
                    │  AQF-T Regime │  (EOD, 每天1次)
                    │  高潮期→OPEN  │
                    └──────┬───────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   execution_gate.py    │
              │   check_execution_     │
              │   permission()         │
              │                        │
              │  ① effective_from ✅   │
              │  ② trade_allowed ✅    │
              │  ③ 🆕 sentiment_check  │ ← 新增
              └────────┬───────────────┘
                       │
                       ▼
              ┌────────────────────────┐
              │  Sentiment Safety      │
              │  Check (只读, 不修改   │
              │  latest_status.json)   │
              │                        │
              │  if sentiment.crash     │
              │     AND regime==高潮期  │
              │     → DEGRADE to 0.5x  │
              │  if sentiment.panic     │
              │     → BLOCK            │
              └────────┬───────────────┘
                       │
                       ▼
              ┌────────────────────────┐
              │  Gate Decision:        │
              │  ALLOWED / DEGRADED /  │
              │  BLOCKED               │
              └────────────────────────┘
```

#### 具体规则

| 条件 | 动作 | 理由 |
|------|------|------|
| Regime=高潮期 AND Sentiment_score > 50 | ALLOWED (不变) | 一致看多 |
| Regime=高潮期 AND Sentiment_score 30-50 | ALLOWED (不变) | 小幅分歧，正常 |
| Regime=高潮期 AND Sentiment_score 15-30 | **DEGRADE** → position_scale×0.7 | 显著分歧，降仓 |
| Regime=高潮期 AND Sentiment_score < 15 | **DEGRADE** → position_scale×0.5 | 严重分歧，半仓 |
| Regime=高潮期 AND Sentiment_crash(Δ<-15) | **BLOCK** 新开仓 | 情绪骤降，暂停买入 |
| ANY Regime AND Sentiment.panic(百股跌停) | **BLOCK** 新开仓 | 极端恐慌 |

**注意**: DEGRADE 只降仓位不关 Gate，BLOCK 只阻止新开仓不强制卖出。

#### 实现

**新增文件**: `D:\quant_framework\sentiment_gate.py` (~80行)

```python
"""
Sentiment Safety Check — execution_gate.py 的情绪交叉验证层
==========================================================
原则:
  - 只读: 不修改 latest_status.json / latest_sensor.json
  - 只降不升: 可以在 Regime 看多时降级，不能在看空时升级
  - fail-open: Sentiment 不可达 → 跳过检查（不阻断 Regime 决策）
  
这是对 execution_gate.py 的补充，不是替代。
"""

def check_sentiment_safety() -> dict:
    """
    Returns:
      {
        "sentiment_ok": bool,       # 情绪是否与 Regime 一致
        "override": "none"|"degrade"|"block",
        "position_multiplier": 0.5-1.0,  # 仓位修正系数
        "reason": str
      }
    """
```

**修改文件**: `D:\quant_framework\execution_gate.py` — 在 `check_execution_permission()` 返回前增加 sentiment check 调用（~20行新增）

#### 优点
- ✅ 不修改 `latest_status.json`（满足 SD-CONTRACT-002）
- ✅ 不绕过 Gate（满足 OBS-013）
- ✅ Market Sensor 保持 Shadow（满足 AVP纪律）
- ✅ 只降不升（保守原则）
- ✅ fail-open（Sentiment 不可达时不影响交易）

#### 缺点
- 🟡 新增一个模块需要维护
- 🟡 Sentiment 数据源依赖 eastmoney（可能限流/不可达）

### 5.2 方案 B：Regime 盘中刷新（不推荐）

**核心思想**: 让 AQF-T pipeline 在盘中多次运行，实时更新 Regime。

#### 问题
- ❌ AQF-T pipeline 依赖 akshare EOD 数据，盘中无法获取当日涨停池
- ❌ 需要 QMT 实时数据 → 违反 "不得直接接入生产端"
- ❌ 改变 `latest_status.json` 盘中更新 → 违反 Regime Contract
- ❌ AQF-T MarketRegimeEngine 是为 EOD 设计的，不能简单改为盘中

### 5.3 方案 C：Dashboard 告警（最小方案）

**核心思想**: 不做架构改动，只在 Dashboard 显示矛盾告警。

#### 实现
- Dashboard 读取 `latest_status.json` (Regime) + `latest_sensor.json` (Sentiment)
- 当 `regime=高潮期 AND sentiment_score<30` 时，显示 🔴 红色告警条
- 当 `sentiment.change_1d < -15` 时，显示 ⚠️ 情绪骤降警告

#### 优点
- ✅ 零架构改动
- ✅ 零风险

#### 缺点
- ❌ 不解决根本问题 — 人类看到告警但 Gate 仍然放行
- ❌ 如果人类不在 Dashboard 前，告警无效

---

## 6. 推荐方案

### 推荐: **A + C 组合**

1. **立即**: 实现方案 C（Dashboard 告警）— 0 风险，今天可上线
2. **本周**: 实现方案 A（Sentiment Gate Override）— 解决根本问题
3. **AVP 后评估**: 是否需要更复杂的多信号融合模型

### 实施顺序

| 步骤 | 内容 | 文件 | 风险 |
|:--:|------|------|:--:|
| 1 | Dashboard 矛盾告警 | `dashboard.py` | 零 |
| 2 | 新建 `sentiment_gate.py` | 新文件 | 低（独立模块） |
| 3 | Gate 集成 sentiment check | `execution_gate.py` +20行 | 低（新增检查，不改现有逻辑） |
| 4 | Shadow 验证期 3 天 | 监控 Gate degrade/block 频率 | 零 |
| 5 | EA 审批后启用 | - | - |

---

## 7. 与现有架构的兼容性

| 架构文档 | 条款 | 兼容性 |
|---------|------|:--:|
| P1 Architecture FROZEN | 7红线 | ✅ 不碰 P1-①②③ |
| Regime Contract SD-CONTRACT-002 | 3档canonical | ✅ 不修改 Regime 判定逻辑 |
| Regime Snapshot Contract P1.1 | effective_from 时间守卫 | ✅ 不修改 latest_status.json |
| Market Sensor Shadow | "只采集不决策" | ✅ Sentiment 作为 Safety Check 而非决策输入 |
| Gate OBS-013 | "唯一边界检查点" | ✅ 在 Gate 内部增加检查，不绕过 |
| fail-closed | AQF-T 不可达 → 禁止 | ✅ Sentiment 不可达 → 跳过（fail-open） |

---

## 8. 不改清单（铁律）

- 🔒 `market_regime.py` — Regime 算法不动
- 🔒 `latest_status.json` 格式 — 不增加字段
- 🔒 `latest_sensor.json` — 只读不写
- 🔒 AQF-T `pipeline.py` — 不增加盘中运行
- 🔒 QMT 执行通道 — 不接入
- 🔒 `trade_config_master.json` — 不修改仓位公式
- 🔒 `auto_trade_plan.json` — 不修改信号生成

---

## 关联

- [[regime-contract-v1-20260811]] — SD-CONTRACT-002, 3-tier canonical
- [[regime-snapshot-contract-p1-1-20260811]] — effective_from 时间守卫
- [[sentiment-sensor-v1-20260809]] — P4接入·Shadow模式
- [[p1-architecture-frozen-20260812]] — P1-①②③全闭单·7红线
- [[gate-map-unified-20260812]] — canonical 3-tier {bull:1.0,chop:0.7,bear:0.0}
- `D:\quant_framework\execution_gate.py` — Gate 实现
- `D:\quant_framework\realtime_sentiment.py` — 实时情绪
- `D:\AQF-T\AQF-T_Production\market_sensor.py` — AQF-T Market Sensor

---

## 9. EA+FA 终审裁决 (2026-08-12)

### 核心判断

**这不是"Gate 错了"，而是发现了一个尚未经过因果验证的实时风险增量信号。**

两个系统在回答不同问题：
- **AQF-T Engine**: "根据 EOD Regime 规则，现在是否允许 Entry？"
- **Sensor**: "现在实时市场情绪是否正在恶化？"
- **LLM**: "当前新闻/信息环境偏不偏空？"

它们逻辑上不矛盾。真正的问题是：**系统缺少一个正式定义的"实时风险观察层"去表达两者之间的关系。**

这正好印证了 S2 设计的核心前提：**STRUCTURAL_BULL ≠ BROAD_BULL**。

### 逐项裁决

| 项目 | 裁决 | 理由 |
|------|:--:|------|
| AQF-T 判高潮期 | 🟢 规则上正确 | AQF-T Engine 根据其规定的 EOD Regime 规则正确判定 |
| Gate OPEN | 🟢 架构上正确 | AQF-T 是唯一 Regime Authority，Gate 逻辑一致 |
| 实时情绪恶化 | 🔴 值得关注 | 真实风险信号，但不等于 Gate 错误 |
| Engine 与 Sensor 分歧 | 🟡 真实架构现象 | 不同时间尺度的系统给出不同答案，正常 |
| Dashboard 没有区分决策/观察 | 🔴 应改善 | **已修复** — v1.3 分决策层/实时风险观察层 |
| Sensor 直接覆盖 Gate | 🔴 **不批准** | 违反 S2 v1.2 冻结架构，创造"第三套 Gate" |
| LLM 直接进入 Gate | 🔴 **不批准** | LLM 是语义解释信号，未经过统计校准 |
| S2 接入 Production Gate | 🔴 **现在不批准** | 必须先跨过 Attribution 因果门槛 |
| S2 Shadow Attribution | 🟢 **继续** | 这正是 S2 存在的理由 |
| 本案例进入 Attribution | 🟢 **强烈建议** | S2 第一批黄金样本 |

### 核心原则

1. **行为规则不能因为"看起来合理"就获得生产权限，必须先跨过 Attribution 的因果门槛。**
2. **AQF-T Engine 继续作为唯一 Regime Authority。Production Gate unchanged。**
3. **S2 是 Market Risk State Detector，不是生产 Gate。**
4. **LLM 输出是高层语义解释，不是经过统计校准的风险变量。**

### S2 Attribution 核心问题

> 在 AQF-T 已经 OPEN 的样本中，S2 HIGH 是否能够识别出一个显著更差的 Entry cohort？

- 如果 **S2 HIGH → Entry cohort 明显更差** → S2 有增量价值，值得讨论接入
- 如果 **S2 HIGH → Entry cohort ≈ NORMAL** → S2 应像 ELEVATED no-add 一样排除

### 批准实施项

| # | 项目 | 状态 |
|:--:|------|:--:|
| 1 | Dashboard 语义分层 (决策层/实时风险观察层) | ✅ 已完成 |
| 2 | `_build_context_reconciliation()` 新增 Gate OPEN + 情绪恶化冲突检测 | ✅ 已完成 |
| 3 | S2 Attribution 黄金样本记录 | ✅ 已完成 |
| 4 | 本分析文档 EA+FA 终审裁决记录 | ✅ 本次更新 |

### Attribution 样本

已记录至: `D:\quant_framework\data\p2_shadow\attribution_samples\2026-08-12_engine_open_sensor_deterioration.json`

追踪维度: T+1 / T+3 / T+5 的 Entry cohort return, MaxDD, hit-rate, benchmark return。

### 不改清单

- 🔒 AQF-T Engine — 唯一 Regime Authority
- 🔒 Production Gate — Sentinel Safety Gate 不创建
- 🔒 S2 — Shadow Observer，不接生产
- 🔒 LLM — 不进入 Gate 决策链
- 🔒 P1 Architecture FROZEN 7红线
