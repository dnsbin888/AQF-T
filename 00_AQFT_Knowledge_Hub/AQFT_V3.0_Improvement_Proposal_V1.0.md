# AQF-T V3.0 改进方案

Version: V1.0.0 | Date: 2026-07-28
Based on: 私募/游资/个人量化行业对标 + AQF-T V2.9→V3.0 全量审计
原则: 适配 AQF-T 蓝图 | A股优先 | 可落地 | 不破坏现有架构

---

## 一、总体判断

### AQF-T 当前定位

经过行业对标后确认：AQF-T 不是量化策略框架，而是**面向A股的自主认知型量化智能系统蓝图**。

| 维度 | 行业对比 | 改进方向 |
|------|:------:|------|
| 认知深度 | **领先** — S(t)→B(t)→R(t)→Ω 无对标物 | 保持，不削弱 |
| 执行层 | **补齐中** — P0 刚完成 6 模块 | Phase 1-2 继续 |
| 经验层 | **建设中** — P1-001/002 刚建立 | 接入 Memory |
| 游资实战 | **部分对齐** — 情绪/龙头/仓位正确 | 补微结构/对手盘/时段 |
| 多智能体 | **缺失** — Bridgewater/QuantAgents 领先 | Phase 3 引入 |
| 对抗验证 | **缺失** — 行业标准实践 | 加入测试体系 |
| 工程自动化 | **未启动** | V3.0 编码阶段引入 |

### 改进原则

1. **不破坏认知链** — S(t)→B(t)→R(t)→Ω 是核心壁垒，所有改进围绕它
2. **A股优先** — 涨停微结构 > 对手盘 > 时段 > 量化感知
3. **渐进式** — Phase 1 补经验 → Phase 2 补实战 → Phase 3 补智能体
4. **个人工作站** — 所有改进不突破 CPU/RAM 预算

---

## 二、Phase 1 改进（当前阶段：补齐经验闭环）

### 改进1: 冷启动策略 — P0

**问题**: Memory 空状态时，Retrieval 返回什么？Decision 如何运作？

**对标**: 个人量化系统上线首日无历史数据，必须定义默认行为。

**方案**:
```
MEM-001 新增 ColdStartMode:
  - Retrieval 返回 "no_experience" 
  - Decision 仅使用 Fusion（不依赖 Memory 增强）
  - Episode 积累到 100 → 自动激活 Episodic Memory
  - Pattern 在 N≥30 → 自动开始提取
  - 冷启动期间 Risk 自动 +10 作为安全边际
```

### 改进2: 失败经验优先采集 — P1

**问题**: Pattern Extractor 容易关注成功案例，但**避免错误比寻找机会更重要**。

**对标**: 屠龙刀复盘系统强调"失败案例分析"；游资"先学不亏钱"。

**方案**:
```
MEM-003 新增 FailurePatternLibrary:
  - 假突破模式 (Expansion信号→快速回落到Neutral)
  - 龙头高潮接力失败 (Mania进入→次日退潮)
  - 情绪退潮误判 (误判Recovery→实际继续Ice)
  - 流动性陷阱 (放量突破→次日缩量跌回)

  Failure Pattern优先级: 
    - 触发自动 Risk +15
    - 匹配时 Decision confidence ×0.7
```

### 改进3: Market Clock 注入 — P1

**问题**: State Model 知道 Regime 但不知道时段。9:35 和 14:55 是完全不同的世界。

**对标**: 游资"早盘不追、尾盘不赌"；个人量化系统"时段行为差异显著"。

**方案**:
```
WM-02 State Model 新增 SessionPhase:
  - 09:15-09:25 集合竞价 (Auction)
  - 09:30-10:00 早盘确认 (OpenDrive)  
  - 10:00-11:30 上午趋势 (MorningTrend)
  - 13:00-14:30 下午整理 (AfternoonConsolidation)
  - 14:30-15:00 尾盘定价 (ClosePricing)

每个时段维护独立统计特征:
  - 早盘: 成交量最大, 方向确认价值最高
  - 尾盘: 次日预期定价, 反转风险最高
  
注入到 Decision: 同一信号在早盘 vs 尾盘 → 不同 Action Bias
```

---

## 三、Phase 2 改进（实战能力增强）

### 改进4: 涨停板微结构 — P0（A股实战）

**问题**: World Model 只看到"连板高度=8，炸板率=25%"，看不到板型区分。

**对标**: 龙祺天"一字板vs换手板vs回封板完全不同"；屠龙刀"连板全周期精析"。

**方案**:
```
WM-02 S4 (Sentiment State) 新增 LimitUpMicrostructure:

  board_type: 一字板 | 换手板 | 回封板 | 烂板 | 尾盘板 | 天地板
  
  一字板: 极度强势, 次日大概率继续一字 → 不适合追
  换手板: 健康换手, 持续性最强 → 龙头最佳介入点
  回封板: 分歧转一致, 烂板回封质量取决于回封时间(早>午>尾)
  烂板: 封不住, 次日大概率低开 → 退出信号
  天地板: 极端反转, Risk 自动 Extreme

  seal_strength_trajectory: 封单变化率 (不只是当前值)
  board_volume_profile: 板上成交特征 (是否有人在板上出货)
  
注入 Decision:
  换手板+早盘回封+封单增强 → confidence +0.10
  尾盘板+封单衰减 → confidence -0.20
  天地板 → 自动 ExitCandidate
```

### 改进5: 对手盘分析雏形 — P1

**问题**: Participant State 只是标签 (institution: accumulating)，缺少席位行为分析。

**对标**: 游资"龙虎榜席位行为是核心决策依据"。

**方案**:
```
新增 Participant_Analyzer (WM扩展):

  龙虎榜席位画像:
    - 锁仓型席位 (买后3-5天不卖)
    - 一日游席位 (次日必砸)
    - 量化席位 (高频T+0行为)
    
  对手盘判断:
    - 今日买盘: 机构建仓 vs 游资接力 vs 散户追涨?
    - 明日抛压: 龙虎榜买入席位中一日游比例?
    - 板上出货: 封单中是否有席位在偷偷卖出?

  输入 Decision:
    锁仓型席位主导 → confidence +0.05
    一日游席位占比>50% → confidence -0.15
    量化席位活跃 → 警惕假突破
```

### 改进6: 量化行为感知 — P2

**问题**: 量化占成交额30-35%，能反向狙击传统游资模式。AQF-T 完全没有量化感知。

**对标**: 2025年量化冲击下游资策略被迫进化。

**方案**:
```
WM-02 S6 (Microstructure State) 新增 QuantFootprint:

  - 高频报撤单率 (量化典型特征: >50%撤单率)
  - 订单流模式 (量化: 频繁小单, 对称买卖)
  - 异常波动模式 (量化狙击: 突破后快速反向)
  
  QuantActivityScore: 0(无量化) ~ 100(量化主导)
  
  注入 Decision:
    QuantActivityScore > 70 → 谨慎追突破 (量化可能反向狙击)
    QuantActivityScore > 70 + 涨停板 → 警惕板上量化出货
```

---

## 四、Phase 3 改进（高级智能）

### 改进7: 多智能体辩论 — P1

**问题**: 单一 Reasoning Engine 容易产生认知偏差。

**对标**: Bridgewater 多头/空头辩论系统; QuantAgents 4-agent 协作。

**方案**:
```
新增 Agent_Debate_Engine:

  Bull_Agent: "为什么应该做多?"
  Bear_Agent: "为什么应该谨慎?"
  Risk_Agent: "风险在哪里?"
  Decision_Agent: 综合辩论结果 → 输出 Consensus

  辩论流程:
    [1] 各 Agent 独立分析 (基于相同 World Model 输入)
    [2] 2轮对抗辩论 (Bull vs Bear, 各提出论据+反驳)
    [3] Risk_Agent 评估风险维度
    [4] Decision_Agent 综合 → Consensus + Disagreement_Notes

  价值: 避免单一认知偏差。
  示例: Bull 看到 Expansion+资金流入; Bear 看到情绪过热+量化活跃
        → Consensus: Increase但降confidence + 设更紧止损
```

### 改进8: 对抗性场景验证 — P1

**问题**: VERIFY-008 只有 6 个离散场景，0 个对抗性场景。

**对标**: QuantAgents 双维度反馈; Bridgewater 严格时间戳防先知偏差。

**方案**:
```
V3.0 测试体系新增 Adversarial Scenario Engine:

  对抗场景类型 (20+):
    假突破系列:
      - Expansion信号→次日回落到Neutral
      - 放量突破→缩量跌回
      - 龙头确认→次日炸板
    假反转系列:
      - 疑似Recovery→继续Ice
      - 疑似退潮→次日修复
    量化狙击系列:
      - 突破追入→量化反向砸盘
      - 涨停排队→量化板上出货
    连续周期:
      - Ice→Recovery→Warming→Climax→Recession→Ice (完整5日)
      - 反复震荡 (Neutral⇄Recovery 3次)

  每场景验证:
    - Regime 是否正确切换?
    - Belief 是否漂移?
    - Confidence 是否崩溃?
    - Risk Veto 是否正确触发?
```

### 改进9: 统计校准层 — P2

**问题**: Confidence 模型未经过真实数据校准。

**对标**: Bridgewater 统计校准层; AlphaGPT IC 校准提升。

**方案**:
```
新增 Confidence_Calibration_Engine:

  历史回测:
    - 系统说 "80%概率成功" → 实际成功率?
    - 如果实际=78% → 可信 (偏差2%)
    - 如果实际=45% → 需修正 (过度自信)
    
  校准输出:
    - Per-Regime 校准因子
    - Per-Action 校准因子
    - Per-ConfidenceLevel 校准因子
    
  应用: 下次 Decision 的 confidence 经过校准因子调整
```

---

## 五、优先级路线图

```
Phase 1 (当前):
  ✅ P1-001 Observation
  ✅ P1-002 Experience  
  ⏳ P1-003 Decision Outcome Analysis
  🆕 改进1: 冷启动策略
  🆕 改进2: 失败经验优先
  🆕 改进3: Market Clock

Phase 2 (实战):
  🆕 改进4: 涨停板微结构 ★★★
  🆕 改进5: 对手盘分析雏形
  🆕 改进6: 量化行为感知
  🆕 改进7: 多智能体辩论

Phase 3 (高级):
  🆕 改进8: 对抗性场景引擎
  🆕 改进9: 统计校准层
```

---

## 六、不变的核心

以下 AQF-T 核心设计**不需要改进**——它们是行业壁垒：

1. **S(t)→B(t)→R(t)→Ω 认知链** — 行业无对标
2. **Belief-Observation 分离** — 独有设计
3. **结构化 Counterfactual (无LLM)** — CPU-friendly 优势
4. **Pattern→Knowledge 自动提升+反例推翻** — 超越向量检索
5. **Regime-Aware 全链路** — A股刚需
6. **8 Constitution Rules** — 工程治理基线
7. **个人工作站 GREEN 预算** — 机构方案不可比

---

*AQF-T V3.0 Improvement Proposal V1.0 — COMPLETE*
