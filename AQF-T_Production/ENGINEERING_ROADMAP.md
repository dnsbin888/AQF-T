# AQF-T Production — 工程验证路线图


**架构已冻结。只讨论验证，不讨论架构。**

**第四条铁律: 未经回测→模拟盘→小资金实盘三级验证的能力, 不得进入Production主链。**

---

## P0 — 实盘前必须完成

```
L2 Replay (GPT研究验证 → 从P1提升):
  回封板策略核心依赖L2微观结构
  没有L2 Replay = 无法回测Path A
  行业标准: hftbacktest / QuantReplay 已成熟
  定位: 验证基础设施, 非策略模块

Execution Metrics (GPT研究验证):
  滑点/成交率/撤单率/超时率
  Signal→Decision→Order→Fill 全链路延迟
  每日自动生成Execution Report

Decision Trace (GPT建议新增):
  Candidate→Path→Score→Decision→Risk→Execution→Result
  每笔交易完整轨迹 → Knowledge Hub可直接回答:
    为什么买? 为什么没买? 哪个环节失效?

数据质量自动化:
  Data Health Score (Freshness/Integrity/Completeness/Latency/Consistency)
  自动计算+告警, ≥95分才进Stage 2
```

## P1 — V1.1 升级

```
CPCV + DSR + PBO:
  行业标准: CPCV > Walk-Forward (2024 Arian et al. 实证)
  Walk-Forward已成熟, CPCV进一步防数据挖掘偏差

Execution Quality 四分解:
  滑点分解: spread/impact/timing/opportunity

Portfolio Risk (游资简化版):
  行业/题材集中度 + 持仓相关性 + Beta暴露

在线模型评估:
  模型漂移检测 / 数据漂移检测 / 自动重训练触发
```

## P2 — Research Lab

```
Monte Carlo / Multi-Asset / RL / World Model
全部不进Production主链, 验证通过→插件接入
```

---

## Stage 1: 数据可信 (最高优先级)

```
目标: 所有输入可信

验证项:
  QMT Level-2 数据完整性检查
  行情时间同步 / 数据缺失检测
  交易日历统一
  股票代码统一 (SH.600519 / SZ.000858)
  因子计算一致性验证 (100因子)

完成标准:
  ✅ QMT L2数据连续3天无断流
  ✅ 日线数据与交易所公告一致
  ✅ 100因子计算结果与V2.8.6公式一致
  ✅ 数据质量日报自动生成
```

## Stage 2: 统一回测引擎

```
目标: 交易规则一致性

验证项:
  A股 T+1 / 涨跌停限制 / 涨停无法成交
  排板成交模拟 / 滑点≤20bps / 手续费+印花税
  集合竞价 / 午间休市 / 停牌处理 / ST/新股限制

完成标准:
  ✅ Path B LGBM回测 (3年历史, IC>0.05)
  ✅ Path A回封板逻辑验证
  ✅ 回测与模拟盘偏差 < 30%
```

## Stage 3: 模拟盘 (≥30个交易日)

```
目标: 验证流程, 非验证收益

验证项:
  Decision是否正确输出Candidate
  Risk是否正确拦截 / Execution是否一致
  QMT是否稳定 / 日志是否完整
  信号频率/成交率/风控拒绝率

完成标准:
  ✅ 连续30个交易日无异常退出
  ✅ 风控100%生效 / 日志完整可追溯
```

## Stage 4: 小资金实盘 (≤10万)

```
Phase 4.1: 仅Path A (2周)
Phase 4.2: Path A+B (4周)
Phase 4.3: 动态仓位 (4周)
Phase 4.4: Learning在线参与 (4周)

每阶段: 无崩溃/无风控违规/KillSwitch有效
```

## Stage 5: Research Lab → Production

```
新模型/策略进入Production唯一路径:
  Research Lab → 回测(≥3年) → 模拟盘(≥30天) 
  → 实盘(≤10万,≥3月) → 证明有效 → Production插件
```

---

**从这一刻起: 不再讨论架构。只讨论验证。**
