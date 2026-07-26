# AQFT Strategy Runtime Design


# AQF-T策略运行系统设计


Version:

V2.8.6


Status:

Running System Design


Classification:

AQF-T实时策略运行体系设计文件


Date:

2026-07-26


---

# 第一章 Strategy Runtime定位


## 1.1 Strategy Runtime目标


Strategy Runtime负责：

将AQF-T策略工程体系转换为实时交易决策能力。


主要职责：

- 策略加载
- 策略调度
- 信号生成
- 策略组合
- 参数管理
- 策略评价
- 策略优化


目标实现：

Data Runtime → AI Runtime → Strategy Runtime → Trading Signal → Risk Runtime

形成智能策略运行闭环。



---

## 1.2 与AQF-T架构关系


04_Strategy

      ↓

13_Code_Framework

      ↓

17_Strategy_Runtime  ← 本文件

      ↓

05_Risk

      ↓

06_Execution



---

# 第二章 Strategy Runtime总体架构


```
                 Strategy Runtime
                        │
        ┌───────────────┼───────────────┐
        │               │               │
 Strategy Manager   Signal Engine   Portfolio Engine
        │               │               │
        └───────────────┼───────────────┘
                        ↓
              Strategy Decision Service
                        ↓
                  Risk Runtime
```



---

# 第三章 Strategy Manager策略管理系统


## 3.1 Strategy Loader


负责：

- 策略加载
- 策略初始化
- 策略版本管理


加载流程：

Strategy Registry → Strategy Loader → Parameter Loading → Runtime Ready



---

## 3.2 策略版本管理


所有策略必须记录：

- Strategy ID
- Version
- Author
- Created Date
- Parameter Version
- Performance Score
- Status


示例：

- Trend_Strategy_v1.0.0
- Quant_Strategy_v2.1.0
- Defensive_Strategy_v1.5.0



---

# 第四章 Signal Engine信号生成系统


## 4.1 Signal Engine定位


负责将AI预测结果、市场数据、策略规则转换为交易信号。



---

## 4.2 信号生成流程


Market Data → Feature Input → AI Prediction → Strategy Logic → Signal Output



---

## 4.3 信号标准格式


统一输出：

- strategy — 策略标识
- symbol — 交易标的
- timestamp — 时间戳
- action — BUY / SELL / HOLD
- confidence — 置信度
- score — 信号评分
- reason — 决策理由
- version — 策略版本



---

# 第五章 策略运行模式


## 5.1 Rule-Based Strategy


基于技术指标、规则组合、条件判断。


例如：MA突破策略。



---

## 5.2 AI Enhanced Strategy


输入AI Prediction，输出Strategy Signal。



---

## 5.3 Quant Strategy


基于因子模型、统计模型、数学优化。



---

## 5.4 Hybrid Strategy


融合AI Prediction + Quant Factor + Risk Constraint → Final Signal



---

# 第六章 Strategy Engine


## 6.1 Strategy Execution Flow


Receive Market Event → Update State → Run Strategy → Generate Signal → Evaluate Confidence → Send Risk Check



---

## 6.2 策略状态管理


INIT → READY → RUNNING → PAUSED → STOPPED



---

# 第七章 Portfolio Strategy Runtime


## 7.1 Portfolio Manager


负责多策略组合、资金分配、权重调整。



---

## 7.2 Portfolio Allocation


支持：

- Equal Weight — 平均分配
- Risk Weight — 根据风险调整
- AI Allocation — 根据预测动态调整



---

# 第八章 Strategy Parameter Runtime


## 8.1 参数管理


参数来源：

Parameter Module → Strategy Runtime → Strategy Instance



---

## 8.2 参数内容


包括：

- 交易周期
- 指标参数
- 仓位比例
- 止损比例
- 信号阈值



---

## 8.3 参数优化接口


支持：

- Grid Search
- Bayesian Optimization
- AI Optimization



---

# 第九章 Strategy Evaluation Runtime


## 9.1 Performance Monitor


实时评价：


### 收益

Return


### 风险

Volatility / Drawdown


### 效率

Sharpe Ratio / Win Rate



---

## 9.2 策略评分


Strategy Score = Return + Risk Adjustment + Stability



---

# 第十章 Strategy Service API


提供：


### Signal API

POST /strategy/signal

输入：Market State

输出：Trading Signal


### Strategy Status

GET /strategy/status


### Performance

GET /strategy/performance



---

# 第十一章 Strategy Runtime监控


监控：


### 策略状态

Running / Warning / Paused / Failed


### 信号质量

Signal Accuracy / Signal Frequency / Signal Drift


### 策略漂移

检测：Performance Drift / Market Regime Change



---

# 第十二章 策略异常恢复


流程：

Strategy Failure → Detect → Disable Strategy → Fallback Strategy → Restart → Validation → Resume



---

# 第十三章 Strategy Runtime目录结构


```
17_Strategy_Runtime/

├── manager/
│   ├── loader.py
│   └── registry.py

├── engine/
│   ├── strategy_engine.py
│   └── scheduler.py

├── signal/
│   ├── generator.py
│   └── validator.py

├── strategies/
│   ├── trend/
│   ├── value/
│   ├── quant/
│   ├── sentiment/
│   └── defensive/

├── portfolio/
│   ├── allocator.py
│   └── optimizer.py

├── parameter/
│   └── strategy_parameter.py

├── evaluation/
│   └── performance_monitor.py

├── api/
│   └── strategy_api.py

├── monitoring/
│   └── strategy_monitor.py

└── tests/
```



---

# 第十四章 Strategy Runtime测试体系


### Strategy Unit Test

验证策略逻辑和信号生成。


### Integration Test

验证：AI Runtime → Strategy Runtime → Risk Runtime


### Backtest Test

验证历史收益和风险表现。


### Stress Test

验证极端行情和高波动环境。



---

# 第十五章 Strategy Runtime交易闭环


完整流程：


Market Data → Data Runtime → Feature Store → AI Runtime → Strategy Runtime → Trading Signal → Risk Runtime → Execution Runtime → Trading Result → Evaluation → Strategy Optimization


形成AQF-T智能策略进化闭环。



---

# 第十六章 P3-04完成标准


| 能力 | 状态 |
|------|------|
| 策略自动加载 | ✅ |
| 策略实时运行 | ✅ |
| 多策略管理 | ✅ |
| 信号生成 | ✅ |
| 参数管理 | ✅ |
| 策略评价 | ✅ |
| 策略监控 | ✅ |
| 异常恢复 | ✅ |



---

# 第十七章 Strategy Runtime冻结声明


本文件定义：

AQF-T策略运行系统。


后续：

风险控制；

交易执行；

模拟交易；

生产部署；


必须基于本策略运行体系。



Version:

V2.8.6


Status:

Running System Design


END OF AQFT STRATEGY RUNTIME DESIGN
