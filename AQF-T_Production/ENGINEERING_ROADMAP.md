# AQF-T Production — 工程主计划


**定位:** 七个工程里程碑 (非七个任务)
**原则:** 先证明系统可靠, 再证明策略赚钱
**KPI:** System Reliability > Strategy Return


---

## 里程碑总览

```
M1 Data Quality        数据可信
M2 L2 Replay           验证可信
M3 Decision Trace      决策可解释
M4 Execution Metrics   执行可评估
M5 Strategy Validation 策略可证明
M6 Paper Trading       系统可自动运行
M7 Live Trading        系统可真实赚钱

上游→下游依赖: M1→M2→M3→M4→M5→M6→M7
任何M未通过→禁止进入下一M
```

## 每个M的准入/退出/回退

### M1 Data Quality

```
M1不是"数据接通", 是"数据可信被证明"。

实施顺序 (5个子里程碑, 不是5个模块):
  M1.1 Connectivity  →  QMT/L2/AKShare/DB全部接通并监控
  M1.2 Validation    →  每条Tick/Bar经过校验 (价格/量/时间/盘口)
  M1.3 Recovery      →  中断→检测→补齐→恢复 全自动
  M1.4 Monitoring    →  Data Health Score每日自动计算
  M1.5 Evidence      →  四类证据齐全

Entry: QMT+L2+AKShare+DB全部接通

Exit (四类证据齐全):
  Data Health Report (每日自动)
  Validation Report (价格/量/时间/盘口校验通过)
  Recovery Test Report (中断恢复测试通过)
  Latency Statistics (延迟统计)
  Data Health Score ≥ 95 (量化)

Deliverables:
  Evidence/DataHealthReport_*.pdf
  Evidence/MissingTickReport_*.csv
  Evidence/RecoveryLog_*.json
  Evidence/LatencySummary_*.csv

M1 实施顺序 (按依赖, 非按文件数):

  Day1: 统一数据模型 (Tick/OrderBook/Bar/DataQualityResult)
        所有源→统一内部格式→进入Validator
  Day2: validator.py (规则注册制: Price/Timestamp/Volume/OrderBook/Symbol/CrossSource)
  + CrossSourceConsistencyRule (QMT vs akshare, severity: critical→FAIL)
  Day3: anomaly_detector.py (检测异常, 不修复: Gap/Duplicate/Drift/Freeze/Jump)
  Day4: recovery_manager.py (PASS/RETRY/SWITCH_BACKUP/FAIL)
  FAIL = 默认fail-fast (停止传播, 禁止下游)
  severity: critical→FAIL / warning→RETRY / info→PASS
  (不新增FAIL_FAST模式, 不新增模块)
  Day5: health_monitor.py (DataHealthSnapshot 统一指标)
  Day6: quality_report.py (每日自动: Health/Validation/Anomaly/Recovery/Latency)

编码实践:
  配置驱动 (max_latency_ms/max_price_jump_pct/max_missing_ticks)
  测试先行 (正常Tick/重复/倒退/Bid>Ask/成交量倒退/L2中断恢复)

本周验收:
  ✅ 5个核心组件框架完成
  ✅ 主要校验规则+单元测试覆盖
  ✅ 第一版Data Health Report生成
  ✅ 至少1种异常Recovery流程验证
  ✅ M1工程证据齐全 (日志+报告+测试结果)

Rollback: 任何数据异常未报警 → 停止进入M2
```

### M2 L2 Replay

```
Entry: M1通过

Exit:
  Replay结果 = 实时Decision (误差 < 1%) (量化)
  Path A 回封板完整回放 (量化)
  回放覆盖≥100个历史炸板案例 (量化)

Deliverables:
  Replay Report (每次回放)
  Replay一致率报告
  Case Library (回封板案例库)

Rollback: Replay与实时不一致 >1% → 回M1
```

### M3 Decision Trace

```
Entry: M2通过

Exit:
  100%交易可回答: 为什么买/没买? Risk为什么拒绝? Execution为什么失败? (量化)
  Decision Trace完整率 = 100% (量化)
  Decision Audit Report自动生成 (量化)

Deliverables:
  Decision Trace Database
  Decision Audit Report (每日)

Rollback: 任何交易无法回答 → 回M2
```

### M4 Execution Metrics

```
Entry: M3通过

Exit:
  每日自动Execution Report (量化)
  Fill Rate/Latency/Slippage/Reject/Cancel/Timeout 全部可查 (量化)
  Execution异常100%可追溯 (量化)

Deliverables:
  Execution Daily Report
  Latency Report / Fill Report

Rollback: 任何执行异常未记录 → 回M3
```

### M5 Strategy Validation

```
Entry: M4通过
Exit:
  连续3个月Walk-Forward稳定 (IC波动<30%) (量化)
  DSR > 0 (量化)
  PBO < 10% (量化)
  不追求最高准确率, 追求模型稳定性

Deliverables:
  Strategy Validation Report
  Walk-Forward Report / CPCV Report

Rollback: 模型不稳定 → 回M4
```

### M6 Paper Trading

```
Entry: M5通过
Exit:
  连续20+交易日自动运行 (量化)
  0次人工干预 / 0次异常退出 (量化)
  0次数据中断 / 0次Risk失效 (量化)

Deliverables:
  Paper Trading Daily Log
  System Reliability Report

Rollback: 任何中断 → 回M5
```

### M7 Live Trading

```
Entry: M6通过
Exit Phase 1 (首月):
  连续运行 / 自动下单 / 自动止损 / 自动恢复 (全部量化)
  System Reliability KPI 全部达标
Exit Phase 2: 收益达标

Deliverables:
  Live Trading Daily Report
  System Reliability Dashboard

Rollback: 任何铁律违规 → 立即停止, 人工审查
```

## 贯穿KPI

### System KPI (系统坏了?)
```
Availability        ≥ 99.9%
Crash               0
Memory Leak         0
Execution Latency   P99 < 500ms
```

### Validation KPI (模型/策略可信?)
```
Replay一致率        ≥ 99%
Replay可复现        同数据同结果 (Reproducibility)
Decision Trace完整率 100%
Walk-Forward稳定    连续3月IC波动<30%
DSR                 > 0
PBO                 < 10%
Data Quality Score  ≥ 95
```

---

**从这一刻起: 先证明系统可靠, 再证明策略赚钱。**
**没有工程证据, 不算通过Exit。**
