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
Entry: QMT接通 + L2接通 + AKShare正常 + 数据库正常

Exit:
  数据完整率 > 99.9%
  重复数据 = 0
  缺失自动恢复
  时间同步正常
  异常全部报警
  Data Health Score ≥ 95

Rollback: 任何数据异常 → 停止进入M2
```

### M2 L2 Replay

```
Entry: M1通过

Exit:
  Replay结果 = 实时Decision (误差 < 1%)
  Path A 回封板可完整回放

Rollback: Replay与实时不一致 → 回M1
```

### M3 Decision Trace

```
Entry: M2通过

Exit:
  每笔交易可回答:
    为什么买? (Path/Score/Reason)
    为什么没买? (Risk REJECT/Regime/Timing)
    为什么Risk拒绝?
    为什么Execution失败?
    为什么盈利/亏损?

Rollback: 任何交易无法回答 → 回M2
```

### M4 Execution Metrics

```
Entry: M3通过

Exit:
  每日自动生成Execution Report:
    Fill Rate / Latency / Slippage / Reject / Cancel / Timeout
  执行问题可定位

Rollback: 任何执行异常未记录 → 回M3
```

### M5 Strategy Validation

```
Entry: M4通过
Exit:
  不追求最高准确率, 追求模型稳定性
  LGBM: IC日间波动 < 30%
  回封板: 信号稳定性 > 月度衰减 < 10%
  通过CPCV+DSR+PBO

Rollback: 模型不稳定 → 回M4
```

### M6 Paper Trading

```
Entry: M5通过
Exit:
  连续20+交易日自动运行
  无人工干预 / 无异常退出 / 无数据中断 / 无Risk失效

Rollback: 任何中断 → 回M5
```

### M7 Live Trading

```
Entry: M6通过
Exit Phase 1 (首月): 连续运行/自动下单/自动止损/自动恢复
Exit Phase 2: 收益达标

Rollback: 任何铁律违规 → 立即停止, 人工审查
```

## 贯穿KPI: System Reliability

```
Availability        ≥ 99.9%
Decision Success    ≥ 99%
Risk Success        100%
Replay一致率        ≥ 99%
Data Quality        ≥ 99.9%
Execution Success   ≥ 98%
Crash               0
Memory Leak         0
```

---

**从这一刻起: 先证明系统可靠, 再证明策略赚钱。**
