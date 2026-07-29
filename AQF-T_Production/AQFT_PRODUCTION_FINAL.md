# AQF-T Production — V1.0 最终架构

**Version:** V1.0 Final | **Date:** 2026-07-29
**评分:** 9.3→10 (修正后)


---

## 最终架构

```
                    Constitution (交易制度)
                          │
                   Market Regime (总开关)
                    今天能不能赚钱?
                          │
                        Data (QMT L2 + akshare)
                          │
                    Perception (8层感知)
                          │
                 ┌────────┴────────┐
                 │                 │
             Path A            Path B
           回封板(规则)       ML预测(统计)
          Perception驱动    LGBM+XGBoost
                 │                 │
                 └────────┬────────┘
                          │
                     Decision Core
              (融合/优先级/冲突解决/仓位分配)
                          │
                        Risk (合法?超仓?熔断?)
                          │
                     Execution (QMT)
                          │
                   Knowledge Hub
        Review/Experience/Training/Model Registry

     ┌──────────────────────────┐
     │    Learning (旁路服务)     │
     │                          │
     │  Offline: 训练/回测/数据集  │
     │  Online:  预测/确认/记忆    │
     │  LLM:     DeepSeek/Qwen   │
     └──────────────────────────┘
```

## 关键修正 (V1.0 Final)

```
1. Decision Core 独立
   旧: Strategy → Risk (Risk既审合规又选标的)
   新: Strategy → Decision(选谁/多少) → Risk(合法/超仓/熔断)
   职责分离: Decision负责融合, Risk负责防线

2. Regime 不属于 Learning
   旧: Learning四维包含Regime
   新: Market Regime独立, 属于Decision Layer上游
   Regime是规则+统计+经验, 不是AI学习的产物

3. Review → Knowledge Hub
   旧: Review(复盘)
   新: Knowledge Hub (归因+经验+训练+模型评估+绩效+Model Registry)
   未来所有模型依赖这里

4. Learning 拆 Offline/Online
   旧: Learning一个模块
   新: Offline(训练/回测/数据集) + Online(预测/确认/记忆) + LLM
   防止膨胀成新的"AI Brain"
```

## 主链 (不可绕过)

```
Market Regime → Perception → Path A/B → Decision → Risk → Execution → QMT
                                                       ↑
                                              Learning (旁路, 只提供评分/建议)
```

## 与V2.8.6的关系

```
V2.8.6 = 设计知识库, 保留不动
Production = 实盘运行系统

V2.8.6中冻结的研究资产:
  World Model / Belief State / Counterfactual / Multi-Agent
  → 不进入交易主链
  → 未来通过回测+模拟盘证明有效 → 作为可插拔研究模块引入
```

---

**Architecture Final. Engineering Verification Begins.**
