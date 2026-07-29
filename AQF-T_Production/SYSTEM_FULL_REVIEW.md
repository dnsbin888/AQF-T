# AQF-T Production V1.0 — 全系统评审报告


**日期:** 2026-07-29 | **定位:** 自包含, GPT可独立理解全貌


---

## 零、三阶段演进

```
V2.8.6 (设计母库, 不动)
  22模块/88文档/569KB
  World Model/Counterfactual/Multi-Agent — 冻结, 不进入Production

AQF-T Production (当前)
  42文件/~160KB/29次Git提交
  架构冻结, 进入工程验证

Research Lab (未来)
  新模型/策略 — 回测→模拟→实盘验证通过 → Production插件
```

---

## 一、最终架构

```
            Constitution (四条铁律 + 两条质量原则)
                  │
           Market Regime (总开关: 今天能不能做?)
                  │
                Data (QMT L2 + akshare)
                  │
            Perception (8层感知)
                  │
         ┌────────┴────────┐
         │                 │
     Path A            Path B
   回封板(规则)       ML预测(统计)
  Perception驱动    B1/B2/B3
         │                 │
         └────────┬────────┘
                  │
             Decision Core
      (统一Candidate→排序→冲突→仓位)
                  │
                Risk (最高否决权)
                  │
             Execution (国金QMT)
                  │
           Knowledge Hub
    (归因/经验/训练/注册/策略生命周期)

 ┌──────────────────────────┐
 │    Learning (旁路, 纯建议) │
 │  Offline: 训练/回测/数据集  │
 │  Online: 预测/确认/记忆    │
 │  LLM: DeepSeek/Qwen      │
 └──────────────────────────┘
```

## 二、治理体系

### 四条铁律
```
1. AI不直接下单
2. Risk最高否决权
3. 退潮期两条路全停
4. 未经三级验证不进Production
```

### 两条质量原则
```
1. 任何里程碑不得以人工解释代替工程证据
2. 任何功能必须具备: Trust + Stability + Explainability + Reproducibility
```

### 工程原则
```
新策略必须先通过P0验证链:
  Data Quality → L2 Replay → Decision Trace → Execution Metrics
  四项全过 → Backtest → Paper → Live
```

## 三、工程主计划 (M1→M7)

```
M1 Data Quality         Exit: 完整率>99.9%, 重复=0, Health≥95
M2 L2 Replay            Exit: 一致率>99%, 100+案例
M3 Decision Trace       Exit: 100%可回答, 完整率=100%
M4 Execution Metrics    Exit: 每日报告, 100%可追溯
M5 Strategy Validation  Exit: Walk-Forward 3月稳定, DSR>0, PBO<10%
M6 Paper Trading        Exit: 连续20日, 0中断
M7 Live Trading         Exit: 连续运行, 自动恢复

每M含: Entry / Exit(全部量化) / Deliverables / Rollback
```

## 四、双KPI

```
System KPI (系统坏了?):
  Availability≥99.9% / Crash=0 / MemoryLeak=0 / Latency<500ms

Validation KPI (模型可信?):
  Replay一致率≥99% / 可复现 / DecisionTrace=100%
  Walk-Forward 3月稳定 / DSR>0 / PBO<10% / Data Score≥95
```

## 五、验证标准 (Stage 1-5)

```
Stage 1: 数据可信 — Data Health Score≥95, 无未来函数
Stage 2: 回测可信 — Walk-Forward+CPCV, 无Look-Ahead
Stage 3: 模拟盘   — ≥30日, 数据持久, Decision Trace完整
Stage 4: 实盘     — ≤10万, 渐进, Execution Metrics达标
Stage 5: 生产就绪 — ≥90日稳定, System KPI全达标
```

## 六、行业对标 (30次提交已完成)

```
P0 (实盘前):
  L2 Replay / Execution Metrics / Decision Trace / 数据质量自动化

P1 (V1.1):
  CPCV+DSR+PBO / Execution四分解 / Portfolio Risk

P2 (Research Lab):
  Monte Carlo / RL / World Model — 不进Production
```

## 七、文件清单 (42个)

```
设计文档(18): FINAL/ROADMAP/VALIDATION/BENCHMARK/UNIFIED/RELIABILITY/AUTOMATION + 各模块
代码(20): market_regime/decision_core/knowledge_hub/arbitration/perception/backtest
          paper_broker/model_registry/event_bus/system_monitor/plugin_interface
          dragon/sentiment/lgb/xgb/llm/qmt_l2_loader/pre_trade/factor_attribution
配置(1): system.yaml
入口(1): main.py
```

## 八、当前状态

```
架构:     9.9/10  冻结
验证体系: 8.5/10  本轮补齐P0
工程实现: 等待编码
```

---

**从这一刻起: 不再讨论架构。只讨论验证。先证明系统可靠, 再证明策略赚钱。**
