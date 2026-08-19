# AQF-T 实时化差距分析

**文档类型**: 只读技术盘点
**日期**: 2026-08-08
**执行人**: CC
**审批**: PA
**状态**: 待 PA 架构评审

---

## 0. 核心发现

**AQF-T 实时化的瓶颈不在"缺少数据源"，而在"适配器已写好但没接线"。**

`data/market_data_adapter.py`（235行）已经封装了 akshare 真实数据获取，输出格式与 Pipeline 兼容。但 `paper_runner.py` 完全不引用它——`run_single_day()` 第 241 行硬编码 `MarketDataSimulator()`。

最小改造路径：修改 `paper_runner.py` 的 `run_single_day()`，让它在真实数据可用时走 `MarketDataAdapter`，不可用时回退 `MarketDataSimulator`。

但逐层看，每一层都有需要注意的细节问题。

---

## 1. 逐层差距对照

### ① 真实行情输入

| 项目 | 现状（模拟） | 目标（真实） | 差距 | 改造难度 |
|------|------------|------------|------|:--:|
| 全市场统计 | `MarketDataSimulator.generate_market_stats()` 随机数 | `MarketDataAdapter.fetch_market_stats()` → akshare 真实涨停/跌停/炸板 | **纯接线** — 适配器已就绪，`paper_runner.py` 不引用 | ⭐ 低 |
| 监控列表 | 硬编码 10 只股票池 | 从真实涨停池/活跃股动态选取 | **需要新建** watchlist 选取逻辑（从 akshare 涨停池取前 N 只） | ⭐⭐ 中 |
| 个股行情 | `random.uniform()` 模拟价格/量比/MA | akshare `stock_zh_a_hist()` → 真实日K + MA + 量比 | **部分可用** — 适配器 `_fetch_stock_from_akshare()` 已实现 MA/量比，但 `theme_heat`/`sector_score` 仍硬编码 | ⭐⭐ 中 |
| 事件文本 | 硬编码 6 条假新闻随机抽 | 真实新闻/公告（已有 LLM 情绪层可复用） | **可桥接** — `llm_sentiment.py` 已在 V2 侧产出真实新闻情绪 | ⭐⭐ 中 |
| 盘中实时价 | 无（模拟器用随机 walk） | QMT `quote_cache.json` 实时价 | **有条件** — 需 QMT Bridge 运行；akshare 无盘中实时价 | ⭐⭐⭐ 高 |

**关键决策点**：
- **只用 akshare**：可覆盖 ①~④（EOD 数据），但不能做盘中实时。适合"每日收盘后自动跑一次"的模式。
- **加 QMT**：可覆盖盘中实时价 + L2 数据，但引入 QMT 进程依赖。

**建议 Phase 1 先用 akshare（EOD 模式），Phase 2 再加 QMT 实时。**

---

### ② 真实市场统计

| 字段 | akshare 来源 | 可用性 | 备注 |
|------|------------|:--:|------|
| `limit_up_count` | `stock_zt_pool_em` | ✅ | 涨停池，盘后可用 |
| `limit_down_count` | `stock_zt_pool_dtgc_em` | ✅ | 跌停池 |
| `max_board_height` | 涨停池 `连板数` 列 | ✅ | |
| `zhatban_rate` | 涨停池 `炸板次数` 列 | ✅ | |
| `board_ladder` | 涨停池 `连板数` 分组 | ✅ | |
| `promotion_rate` | 2板+/首板 比值 | ✅ | |
| `north_bound_net` | `stock_hsgt_north_net_flow_in_em` | ✅ | 北向资金 |
| `margin_balance_change` | **无** | ❌ | akshare 不提供融资余额变化，适配器硬编码 0.0 |

**GAP**: `margin_balance_change = 0.0` 会导致 MarketRegimeEngine 的 `margin_trend` 永远为"平稳"。
**影响**: 极低。融资余额在 Regime 评分公式中权重很小（仅用于判定趋势方向，不参与 score 计算）。
**缓解**: 接受 0.0，或从 tushare `margin_detail` 接口补充。

---

### ③ 真实 Pattern 输入

AQF-T 的两个已实现 Pattern 都需要个股层面的真实数据：

#### SectorFlow（板块资金流）

| 需要字段 | akshare 来源 | 可用性 |
|----------|------------|:--:|
| `sector_limit_up_change` | 涨停池按行业分组 | ✅ |
| `sector_fund_flow` | `stock_individual_fund_flow` | ⚠️ 需逐股调用 |
| `sector_pct` | 板块指数 `stock_board_industry_index_ths` | ✅ |
| `sector_volume_change` | 同上 | ✅ |
| `is_leader` | 需要涨停池排名 + 人工逻辑 | ⚠️ 需实现判定逻辑 |

#### RelativeStrength（相对强度）

| 需要字段 | 来源 | 可用性 |
|----------|------|:--:|
| `stock_5d_return` | akshare `stock_zh_a_hist` 5日收盘 | ✅ |
| `market_5d_return` | 沪深300 / 上证指数 5日 | ✅ |
| `sector_5d_return` | 板块指数 5日 | ⚠️ 需映射股票→板块→指数 |
| `leader_5d_return` | 需先判定龙头再取价 | ⚠️ 同上 |

#### DragonStrategy（龙头6条件）

| 条件 | 需要数据 | 来源 | 可用性 |
|------|---------|------|:--:|
| board_count ≥ 3 | 连板数 | 涨停池 | ✅ |
| sector_limit_up ≥ 5 | 板块涨停数 | 涨停池按行业分组 | ✅ |
| seal_ratio ≥ 5% | 封单/流通盘 | QMT L2 | ❌ 无 QMT 不可得 |
| longhu_seats ≥ 2 | 龙虎榜席位 | akshare `stock_lhb_detail_em` | ✅ |
| auction_amount | 集合竞价量 | QMT 分钟线 | ❌ 无 QMT 不可得 |
| gap_up ≥ 5% | 开盘涨幅 | akshare 日K open vs pre_close | ✅ |

**结论**: DragonStrategy 6 条件中 2 个依赖 L2/分钟线（seal_ratio、auction_amount）。无 QMT 时只能跑 4 条件版本（降级模式），这在 DragonStrategy 代码中已隐含支持（≥3 条件 → 龙头）。

#### LimitUpPerception（回封板感知）

| 需要数据 | 来源 | 可用性 |
|----------|------|:--:|
| break_drop_pct | 炸板回落幅度 | QMT 实时 | ❌ |
| white_above_yellow | 均价线关系 | QMT 实时 | ❌ |
| buy_absorption | 承接力度 | QMT L2 | ❌ |
| reseal_1min_vol | 回封量 | QMT L2 | ❌ |
| break_to_reseal_min | 炸板→回封时间 | QMT 实时 | ❌ |

**结论**: **LimitUpPerception 全部依赖 QMT 实时/L2 数据。** 无 QMT 时 Path A（回封板）实际上无法运行真实数据。这是整个实时化中最大的单点缺口。

---

### ④ 真实 Regime

**结论: 无代码差距。** AQF-T `MarketRegimeEngine.evaluate()` 已兼容适配器输出格式：
- 第 61 行 `market_stats.get("zhatban_rate", market_stats.get("炸板率", 0))` — 同时兼容中英文 key
- 所有字段映射正确

唯一注意：`margin_balance_change = 0.0` 导致 `margin_trend` 恒为"平稳"，但影响极小。

---

### ⑤ 真实 Signal

| 组件 | 现状 | 真实数据影响 |
|------|------|------------|
| Path A (回封板) | `LimitUpPerception` + `DragonStrategy` | ⚠️ 需要 L2 数据才能产出有效信号 |
| Path B (半路) | `predictor_lgb` → 规则回退(MA5>MA20+量比>1.2) | ✅ MA/量比可从 akshare 计算，规则回退可运行 |
| Path B (事件) | `event_llm` → 规则回退(关键词匹配) | ✅ 可接入 LLM 情绪层产出 |
| DecisionCore | 评分→排序→去重→分配 | ✅ 与数据源无关 |

**结论**: Path B 用 akshare 数据 + 规则回退可以跑。Path A 无 QMT 时信号质量严重下降。Phase 1 可接受（PA 说"不碰决策逻辑"）。

---

### ⑥ 真实 Paper Simulator

| 项目 | 差距 | 严重度 |
|------|------|:--:|
| 仓位持久化 | `PaperBroker` 纯内存，重启即丢失 | 中 |
| T+1 解锁 | 需手动调用 `daily_refresh()` | 中 |
| 与 V2 Paper 对比 | AQF-T 和 V2 各自独立记录，无法交叉验证 | 低（AVP 期间不需要） |

**建议**: Phase 1 先加 JSON 文件持久化（参考 V2 `paper_engine.py`），最小改动。

---

### ⑦ Dashboard

| 项目 | 差距 | 改造难度 |
|------|------|:--:|
| 环境标识 | 硬编码 "SIMULATOR" | ⭐ 低（读 config 或检测数据源） |
| 自动刷新 | 无，需手动 F5 | ⭐ 低（加 `<meta http-equiv="refresh">` 或 JS polling） |
| 数据源显示 | 无 | ⭐ 低（dashboard 已有 `status()` 框架） |

---

## 2. 跨层问题

### A. 无自动调度（最大单点缺失）

AQF-T 没有任何定时触发机制。`main.py` 是纯手动 CLI。要实现"每个交易日自动跑一次"，需要：

**方案 A**: Windows Task Scheduler，每天 15:30 触发 `python main.py --cmd run`（推荐 Phase 1）
**方案 B**: `while True` 循环 + `clock.is_trading_hours()` + 收盘触发
**方案 C**: 集成到 V2 Flask 服务中（❌ AVP 禁止）

### B. 数据新鲜度校验

Pipeline 不检查 `market_stats` 是否"今天的"。如果 akshare 调用失败回退到 fallback（静态默认值），Pipeline 会静默使用过期数据产出报告。

**需要**: `run_daily()` 前加 `data_freshness` 检查。

### C. 依赖缺失

`requirements.txt` 缺少 `akshare`。需要加到依赖列表。

### D. 盘中 vs 盘后

| 模式 | 可用数据 | 可运行时段 |
|------|---------|----------|
| 纯 akshare | 日K、涨停池（EOD） | 仅 15:00 后 |
| QMT + akshare | 实时价、L2、日K | 9:30-15:00 盘中 |

**如果只用 akshare，AQF-T 只能收盘后跑（T+0 EOD 模式），不能盘中实时决策。**

---

## 3. 最小改造路径

### Phase 1（3-5 天）: akshare EOD 模式 → 每日收盘自动报告

```
修改文件:
├── paper_runner.py          ← 核心改造：run_single_day() 接入 MarketDataAdapter
├── requirements.txt         ← 加 akshare
├── main.py                  ← 加 --cmd run --source real|sim
└── (可选) Windows Task       ← 15:30 自动触发
```

**改造内容**:
1. `run_single_day()` 加 `use_real_data=True` 参数
2. 真实模式 → `MarketDataAdapter.fetch_market_stats()` + `fetch_watchlist(从涨停池取前20只)`
3. 模拟模式 → 回退 `MarketDataSimulator`（保持兼容）
4. 加数据新鲜度检查
5. Dashboard 标识从 "SIMULATOR" → "AKSHARE_EOD"

**验收标准**:
- 收盘后运行 `python main.py --cmd run --source real`
- Dashboard 显示的涨跌停数、炸板率、连板高度与东方财富一致
- Regime 判断基于真实数据
- 每日报告写入 `reports/daily/YYYYMMDD_report.json`

**不改**: 决策逻辑、Pattern 算法、仓位公式、V2 连接、QMT 连接。

### Phase 2（AVP Day 20 后评估）: QMT 实时模式 → 盘中可运行

- 接入 QMT `quote_cache.json` 实时价
- 接入 QMT L2 数据（解锁 Path A 回封板）
- 盘中实时 Regime 更新
- Dashboard 实时刷新

### Phase 3（AVP 后决策）: 自动化 + 持久化

- Windows Task Scheduler 自动调度
- PaperBroker 仓位 JSON 持久化
- 与 V2 双脑对比报告

---

## 4. 风险清单

| 风险 | 概率 | 影响 | 缓解 |
|------|:--:|:--:|------|
| akshare 接口变更/限流 | 中 | 数据获取失败→回退 fallback 静态值 | 保留 fallback + 日志告警 |
| akshare 数据延迟（15:00 后 N 分钟才有当日涨停数据） | 高 | 15:30 触发时数据可能尚未更新 | 加重试 + 等待逻辑 |
| Path A（回封板）无 L2 数据产出空信号 | 确定 | Phase 1 只有 Path B 产出信号 | 明确标注 Phase 1 仅 Path B |
| 模拟→真实切换后 Regime 判断剧变 | 中 | 此前"高潮期 70%"是基于随机数，真实数据可能完全不同 | 记录首次切换差异，不惊慌 |
| Owner 误以为 AQF-T 已可做实盘决策 | 低 | 违反 AVP 纪律 | Dashboard 显式标注"不参与决策" |

---

## 5. 边界确认（PA 审批项）

- [ ] Phase 1 只做 Data → Pipeline → Report → Dashboard，不碰决策逻辑
- [ ] AQF-T 不接 V2，不接 QMT 执行通道
- [ ] Pattern 算法不改（Dragon/Perception/SectorFlow 代码不动）
- [ ] Regime 算法不改（MarketRegimeEngine 代码不动）
- [ ] 仓位公式不改
- [ ] Phase 2 等到 AVP Day 20 后再评估
- [ ] V2 AVP 继续 Day 5/20，不受影响

---

## 关联

- [[VB-007-aqft-realtime-architecture]] — 实时化价值验证
- [[情绪证据层-v1.0]] — 三层情绪架构
- [[dual-brain-architecture-v1]] — 双脑架构
- `D:\quant_framework\market_regime.py` — V2 侧市场状态（已接 QMT 实时价）
- `D:\AQF-T\AQF-T_Production\data\market_data_adapter.py` — 适配器（已就绪，未接线）
