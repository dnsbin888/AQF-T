# AQFT Risk Runtime Design


# AQF-T风险运行系统设计


Version:

V2.8.6


Status:

Running System Design


Classification:

AQF-T实时风险控制运行体系设计文件


Date:

2026-07-26


---

# 第一章 Risk Runtime定位


## 1.1 Risk Runtime目标


Risk Runtime负责：

将AQF-T风险管理设计体系转换为实时风险控制能力。


主要职责：

- 风险检测
- 风险计算
- 风险评估
- 风险决策
- 风险限制
- 风险预警
- 风险恢复


核心目标：

在任何交易行为发生前，识别风险、评估风险、控制风险、阻止异常交易。



---

## 1.2 风险控制原则


AQF-T遵循Risk First Principle：


任何交易请求必须经过Risk Runtime。


禁止：

- Strategy绕过Risk
- Execution绕过Risk



---

## 1.3 与AQF-T架构关系


05_Risk

      ↓

13_Code_Framework

      ↓

18_Risk_Runtime  ← 本文件

      ↓

06_Execution

      ↓

Trading System



---

# 第二章 Risk Runtime总体架构


```
                 Risk Runtime
                       │
       ┌───────────────┼───────────────┐
       │               │               │
 Risk Monitor   Risk Engine   Risk Decision
       │               │               │
       └───────────────┼───────────────┘
                       ↓
              Risk Control Service
                       ↓
             Execution Runtime
```



---

# 第三章 Risk Manager风险管理系统


## 3.1 Risk Manager定位


负责统一管理所有风险规则。


包括：

- 市场风险
- 策略风险
- 仓位风险
- 流动性风险
- 操作风险



---

## 3.2 Risk Lifecycle


风险状态：


NORMAL → WARNING → LIMITED → BLOCKED → RECOVERING → NORMAL



---

# 第四章 Risk Engine风险计算引擎


## 4.1 风险计算流程


Trading Signal → Position State → Market Condition → Risk Calculation → Risk Score



---

## 4.2 风险指标体系


### 市场风险

Volatility / Beta / Market Exposure


### 仓位风险

Position Size / Concentration / Leverage


### 流动性风险

Volume Impact / Spread / Liquidity Score


### 策略风险

Strategy Drawdown / Signal Failure / Performance Drift



---

# 第五章 Risk Decision Engine


## 5.1 风险决策定位


根据风险结果决定交易是否允许。



---

## 5.2 决策输出


统一格式：

- risk_decision — APPROVE / ADJUST / REJECT
- risk_score — 风险评分
- reason — 决策理由
- timestamp — 时间戳
- version — 规则版本



---

## 5.3 决策流程


Trading Request → Risk Evaluation → Risk Score → Decision → Execution Permission



---

# 第六章 Risk Limit系统


## 6.1 Limit Manager


管理交易边界。


包括：

- 单笔限制 — 最大交易金额 / 最大仓位
- 账户限制 — 最大风险暴露 / 最大回撤
- 策略限制 — 策略资金比例 / 策略风险额度



---

## 6.2 Limit配置


统一管理：

- max_position — 最大仓位
- max_drawdown — 最大回撤
- max_loss — 最大亏损
- max_exposure — 最大风险暴露



---

# 第七章 Real-Time Risk Monitor


## 7.1 实时监控内容


### Portfolio

当前资产 / 当前仓位 / 盈亏状态


### Market

波动率 / 流动性


### Strategy

信号质量 / 策略表现



---

## 7.2 风险告警


触发流程：

Normal → Threshold Trigger → Alert → Action


Action包括：

- Warning — 预警
- Reduce Position — 降低仓位
- Stop Trading — 停止交易



---

# 第八章 Risk Event系统


## 8.1 Risk Event来源


包括：

- Market Event
- Position Event
- Strategy Event
- Execution Event



---

## 8.2 Event处理流程


Receive Event → Risk Analysis → Generate Decision → Publish Result



---

# 第九章 Risk API设计


### 风险检查接口

POST /risk/check

输入：signal / position / market_state

输出：decision（APPROVE / ADJUST / REJECT）+ risk_score


### 风险状态接口

GET /risk/status


### 风险报告接口

GET /risk/report



---

# 第十章 Risk Runtime监控体系


监控指标：


### 风险指标

VaR / Drawdown / Exposure / Volatility


### 系统指标

Risk Latency / Decision Accuracy / Reject Rate



---

# 第十一章 风险异常恢复


流程：

Risk Failure → Detect → Activate Safe Mode → Block New Orders → Restart Risk Service → Health Check → Resume



---

# 第十二章 Emergency Control（紧急控制）


## 12.1 Kill Switch


提供紧急停止交易能力。


触发条件：

- 系统异常
- 市场极端波动
- 风控失效



---

## 12.2 Safe Mode


进入SAFE MODE：

- 禁止新增仓位
- 允许风险平仓
- 保留监控



---

# 第十三章 Risk Runtime目录结构


```
18_Risk_Runtime/

├── manager/
│   └── risk_manager.py

├── engine/
│   └── risk_engine.py

├── evaluator/
│   └── risk_evaluator.py

├── limits/
│   └── risk_limit.py

├── decision/
│   └── risk_decision.py

├── monitor/
│   └── risk_monitor.py

├── event/
│   └── risk_event.py

├── api/
│   └── risk_api.py

├── emergency/
│   └── kill_switch.py

├── reports/
│   └── risk_report.py

└── tests/
```



---

# 第十四章 Risk Runtime测试体系


### Unit Test

验证风险计算和风险规则。


### Integration Test

验证：Strategy Runtime → Risk Runtime → Execution Runtime


### Stress Test

模拟极端行情、黑天鹅事件、高频交易压力。


### Failure Test

验证风控服务故障、数据异常、网络中断。



---

# 第十五章 AQF-T风险闭环


完整流程：


Data Runtime → AI Runtime → Strategy Runtime → Risk Runtime → Execution Runtime → Trading Result → Risk Feedback → Model Learning


形成安全智能交易闭环。



---

# 第十六章 P3-05完成标准


| 能力 | 状态 |
|------|------|
| 实时风险计算 | ✅ |
| 风险规则执行 | ✅ |
| 交易审批控制 | ✅ |
| 风险限制管理 | ✅ |
| 风险告警 | ✅ |
| Kill Switch | ✅ |
| 异常恢复 | ✅ |
| 风险报告 | ✅ |



---

# 第十七章 Risk Runtime冻结声明


本文件定义：

AQF-T风险运行系统。


后续：

交易执行；

模拟交易；

生产部署；


必须基于本风险控制体系。



Version:

V2.8.6


Status:

Running System Design


END OF AQFT RISK RUNTIME DESIGN
