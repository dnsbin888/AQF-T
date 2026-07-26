# AQFT Multi-Agent Trading System Design V3.6.0


# AQF-T 多智能体交易系统详细设计


Version: V3.6.0 | Status: Detailed Engineering Design
Date: 2026-07-26

> 参考: TradingGroup(2025) 五Agent+自反思+数据合成 / HedgeAgents 会议协调 / Jarvis LangGraph+NATS


---

# 第一章 架构


借鉴 2025 年三套标杆系统：

```
TradingGroup 五Agent链:  News→Report→Forecast→Style→Decision
HedgeAgents 会议机制:     BAC预算会/ESC经验分享会/EMC极端行情会
Jarvis 基础设施:          LangGraph Supervisor + NATS JetStream + Redis + PostgreSQL
```

AQF-T 融合架构:

```
                    Supervisor Agent (LangGraph Orchestrator)
                         │
    ┌────────┬───────┬───┴───┬───────┬────────┐
    │        │       │       │       │        │
 Market  Sentiment Forecast  Risk   Decision  Analyst
 Agent    Agent    Agent    Agent    Agent    Agent
 (感知)   (情绪)   (预测)   (风控)   (决策)   (复盘)
    │        │       │       │       │        │
    └────────┴───────┴───┬───┴───────┴────────┘
                         │
              Event Bus (NATS/Redis Pub-Sub)
                         │
              Shared Memory (向量检索 + 经验库)
```

---

# 第二章 五Agent分工 (借鉴 TradingGroup)


## 2.1 Market Agent (感知)

```
职责: 市场状态感知 + 题材识别 + 涨停梯队
输入: Data Runtime → 实时行情+涨停+龙虎榜
输出: MarketContext → 所有Agent
模式: 每Tick运行,广播
```

## 2.2 Sentiment Agent (情绪)

```
职责: 情绪周期判断 + 题材热度评分
输入: MarketContext + 新闻舆情 + 社交情绪
处理: 情绪值公式 + 四阶段分类
输出: SentimentReport (冰点/回暖/高潮/退潮 + 情绪值 + 题材热度)
模式: 每分钟
```

## 2.3 Forecast Agent (预测)

```
职责: 趋势预测 + 龙头识别
输入: MarketContext + SentimentReport + 技术指标
模型: LightGBM + LLM推理
输出: ForecastOutput (方向+概率+龙头标的)
模式: 每5分钟

借鉴 TradingGroup Hybrid Gate:
  rule_gate: RSI>80 → 强制SELL (硬拦截)
  llm_gate: LLM判断是否追涨 (软判断)
  final = rule_gate AND llm_gate
```

## 2.4 Risk Agent (风控)

```
职责: 风险评估 + 限额检查
借鉴 TradingGroup 动态风险管理:
  stop_loss = ATR-20 × 2 × style_coefficient
  take_profit = ATR-20 × 3 × style_coefficient
  style_coefficient: aggressive=1.0 | balanced=0.8 | conservative=0.6
输出: RiskAssessment (APPROVE/ADJUST/REJECT + 动态止盈止损)
模式: 实时(每10秒)
```

## 2.5 Decision Agent (决策)

```
职责: 综合决策 + 信号输出
输入: ForecastOutput + SentimentReport + RiskAssessment
融合: 加权投票 + LLM推理
输出: TradingSignal
模式: 事件驱动(上游Agent输出即触发)

借鉴 HedgeAgents 会议模式:
  BAC (Budget Allocation): 每日盘前,资金分配
  EMC (Extreme Market): 极端行情时,紧急决策
  ESC (Experience Sharing): 每周,经验分享+策略调整
```

---

# 第三章 自反思机制 (借鉴 TradingGroup 核心创新)


```
Self-Reflection Loop:

每个Agent决策后:
  ① 记录: 输入+输出+逻辑链(Chain-of-Thought)
  ② 标注: 实际结果 → 成功/失败
  ③ 提取: 成功模式 + 失败根因
  ④ 注入: 下次类似场景的LLM上下文中

示例:
  Forecast Agent 预测 BUY → 实际下跌
  → 反思: "当时RSI=85超买+北向流出+情绪退潮, 不应买入"
  → 下次 RSI>80+情绪退潮 → LLM上下文中包含此教训
```

---

# 第四章 数据合成管道 (借鉴 TradingGroup PEFT)


```
Agent决策日志 → 自动标注(方向准确率/超额收益) → 筛选高质量轨迹 → 
  → LLM微调数据 → PEFT(LoRA)训练 → 模型升级

目标: 从交易经验中持续提升模型能力
周期: 每500条高质量轨迹 → 一次LoRA微调
```

---

# 第五章 基础设施 (借鉴 Jarvis 生产栈)


```
LLM推理: Ollama(本地,Qwen3-8B) → 云端API fallback
Agent框架: LangGraph (有向图编排 + interrupt()人工审批)
消息总线: Redis Pub-Sub (轻量级, 够用)
状态存储: PostgreSQL (对话历史 + 交易审计 + RLS行级安全)
向量检索: pgvector (经验检索, 按租户隔离)
```

---

# 第六章 人工审批网关


借鉴 Jarvis LangGraph interrupt():

```
Decision Agent 输出 TradingSignal
  → LangGraph interrupt()
  → 人工审批界面:
      信号详情 + AI推理链 + 风险评估 + 历史类似案例
  → 人工: APPROVE / REJECT / MODIFY
  → 继续执行或回退

可配置: L0(纯人工) / L2(人工审批) / L4(自动+监控)
```

---

# 第七章 API


| 端点 | 方法 | 功能 |
|------|:---:|------|
| POST /agent/council/decide | POST | 多Agent联合决策 |
| GET /agent/{name}/status | GET | 单个Agent状态 |
| GET /agent/reflection/report | GET | 自反思报告 |
| POST /agent/approval/{decision_id} | POST | 人工审批 |

---

# 第八章 设计冻结声明


本文件定义 AQF-T Multi-Agent System V3.6.0。

借鉴 TradingGroup 五Agent+自反思+数据合成 / HedgeAgents 会议协调 / Jarvis LangGraph+NATS 生产栈。

核心创新: 自反思机制(决策→结果→标注→教训→下次注入) + 数据合成管道(500条轨迹→LoRA微调) + Hybrid Gate(规则硬拦截+LLM软判断)。

Version: V3.6.0 | Status: Detailed Engineering Design
END OF AQFT MULTI-AGENT TRADING SYSTEM DESIGN
