# AQF-T Production Validation Standard V1.0


**定位:** 工程质量门 (Quality Gate)
**原则:** 不讨论架构。只定义每个Stage的进入/退出条件。
**适用:** 所有模块、所有策略、所有模型


---

## Stage 1: 数据可信 (Data Validation)

### Entry: 数据源已接入
### Exit (全部通过):

```
L2数据:
  ✅ 连续72小时无丢包 (丢包率 < 0.01%)
  ✅ Tick时间戳单调递增 (无乱序)
  ✅ 十档盘口 bid1<bid2<...<bid10, ask1<ask2<...<ask10 (无逻辑错误)

QMT同步:
  ✅ QMT时间与交易所时间偏差 < 100ms
  ✅ 行情延迟 P99 < 500ms

数据完整性:
  ✅ 涨停池与交易所公告一致 (偏差 < 1只/日)
  ✅ 龙虎榜与交易所公告一致
  ✅ 股票代码100%统一 (SH.600519格式)

因子:
  ✅ 100个因子计算结果与V2.8.6公式一致 (抽样验证, 偏差<0.01%)

财务数据:
  ✅ 无未来函数 (公告日期 ≤ 数据可用日期)
  ✅ 复权因子连续 (前后复权价格无跳空)

Data Health Score = (Freshness×0.25 + Integrity×0.25 + Completeness×0.20 + Latency×0.15 + Consistency×0.15)
  ✅ ≥ 95分 → Stage 2
  ❌ < 95分 → 修复后重测
```

## Stage 2: 回测可信 (Backtest Validation)

### Entry: Stage 1 全部通过
### Exit (全部通过):

```
无信息泄露:
  ✅ 无Look-Ahead Bias (每个Bar只用该Bar之前的数据)
  ✅ 无未来函数 (因子计算不依赖未来数据)
  ✅ Train/Val/Test时间顺序正确 (Train最早, Test最晚)

Walk-Forward Analysis (防过拟合黄金标准):
  方法: 滚动窗口训练-验证
    Window 1: Train 2020-2022 → Test 2023 Q1
    Window 2: Train 2020-2023Q1 → Test 2023 Q2
    Window 3: Train 2020-2023Q2 → Test 2023 Q3
    ...滚动至2026 Q2
  验证: 所有Window的IC/Sharpe均值 > 单次Train/Test
         各Window间IC波动 < 30% (模型稳定)

幸存者偏差:
  ✅ 回测包含已退市股票 (非仅存活股)
  ✅ IC计算包含"买入失败"样本 (非仅已成交)

交易规则:
  ✅ T+1正确模拟 (当日买→次日才能卖)
  ✅ 涨停无法成交 (BUY at limit_up → fill_prob=0.05)
  ✅ 跌停无法卖出 (SELL at limit_down → fill_prob=0.05)
  ✅ 手续费真实 (佣金0.025%+印花税0.1%+过户费)
  ✅ 滑点≥20bps (非0滑点理想回测)

收益率最后验证:
  ✅ Path B LGBM: IC > 0.05, ICIR > 0.3
  ✅ Path A: 回封板信号逻辑正确 (非验证收益率)

模型融合方案对比 (数据决定, 不提前选):
  方案A: LGBM单独 (基准)
  方案B: LGBM + XGBoost 加权融合 (当前设计, 各0.5)
  方案C: LGBM + XGBoost Stacking (CJoE 2024最优, Sharpe 1.23)
    基学习器: XGBoost + LightGBM
    次级学习器: AdaBoost or Logistic Regression
  验证: 哪个IC/Sharpe最高用哪个
```

## Stage 3: 模拟盘 (Paper Trading)

### Entry: Stage 2 全部通过
### Exit (全部通过, ≥30个交易日):

```
流程完整性:
  ✅ 信号→下单→成交→仓位更新→日志 全链路无断点
  ✅ QMT接收到100%的信号 (无漏单)
  ✅ 成交回报100%写入数据库
  ✅ Review记录100%覆盖每笔交易

风控:
  ✅ Risk审批100%执行 (无绕过)
  ✅ Kill Switch触发后100%停止交易 (测试触发)
  ✅ 退潮期0笔买入 (验证Regime覆盖)

系统稳定性:
  ✅ 30天无异常退出
  ✅ 30天无数据库损坏
  ✅ QMT重连成功率 > 99% (断开测试)

⚠️ 注意: 模拟盘验证的是"系统有没有Bug", 不是"赚不赚钱"
```

## Stage 4: 小资金实盘 (Live Trading)

### Entry: Stage 3 全部通过
### Exit (渐进式, 每个Phase独立验收):

```
Phase 4.1: 仅Path A (2周, ≤5万)
  ✅ 无系统崩溃
  ✅ 无风控违规
  ✅ 实盘成交率 > 80% (对比模拟盘)
  ✅ 实盘滑点 ≤ 模拟盘滑点×1.5

Phase 4.2: Path A+B (4周, ≤8万)
  ✅ 两条路径无互相干扰
  ✅ 仓位总和 ≤ 上限
  ✅ A vs B绩效可对比

Phase 4.3: 动态仓位 (4周, ≤10万)
  ✅ Regime切换时仓位正确调整
  ✅ Decision优先规则生效 (A>B)

Phase 4.4: Learning在线 (4周)
  ✅ AI输出为只读 (未绕过Risk)
  ✅ AI置信度与实盘结果趋势一致
```

## Stage 5: 稳定运行 (Production Ready)

### Entry: Stage 4 全部通过
### Exit:

```
连续运行:
  ✅ ≥90天无崩溃
  ✅ ≥90天无漏单
  ✅ ≥90天无重复下单
  ✅ ≥90天无数据库损坏
  ✅ Kill Switch可用性100% (月度测试)

绩效基准:
  ✅ 夏普 > 1.0
  ✅ 最大回撤 < 20%
  ✅ 胜率 > 45%
```

## 模块级验证

```
Perception:
  炸板分类: 洗盘/诱多 准确率 > 70% (≥100样本)
  回封确认: 高分(>0.7)次日溢价显著 > 低分(<0.5)

Regime:
  退潮判断后10日内平均收益 < 0 (确实应该停止)
  高潮判断后10日内平均收益 > 回暖期

Risk:
  0次超仓漏检
  0次Kill Switch失效
  APPROVE/REJECT日志100%完整

Execution:
  成交率 > 85%
  平均滑点 < 30bps
  撤单成功率 > 95%

Knowledge Hub:
  100%交易可回放 (逐笔还原)
  100%交易可归因 (知道盈亏来源)
  100%经验入库 (成功/失败案例)
```

## 回退条件

```
Stage 2中发现前视偏差 → 回退Stage 1 (数据问题)
Stage 3中连续3次漏单 → 回退Stage 2 (信号问题)
Stage 4中日亏损>5% → 立即停止, 回退Stage 3
Stage 5中任何铁律违规 → 立即停止, 人工审查
```

---

**本文件是AQF-T Production的质量门。所有模块/策略/模型必须逐Stage通过。**
