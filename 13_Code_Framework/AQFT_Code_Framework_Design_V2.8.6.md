# AQFT Code Framework Design


# AQF-T代码基础框架设计


Version:

V2.8.6


Status:

Engineering Implementation


Classification:

AQF-T软件代码基础架构文件


Date:

2026-07-26


---

# 第一章 代码框架定位


## 1.1 系统定位


Code Framework模块负责：

将AQF-T工程规范转换为实际软件项目结构。


目标：

- 建立统一代码入口
- 明确模块边界
- 支撑AI模型扩展
- 支撑策略扩展
- 支撑交易执行
- 支撑自动测试
- 支撑未来团队开发



---

## 1.2 与整体架构关系


02_Constitution

        ↓

01_Architecture

        ↓

03-09 Module Design

        ↓

10_Engineering

        ↓

13_Code_Framework  ← 本文件

        ↓

P3 Running System



---

# 第二章 AQF-T项目代码总体结构


```
AQF-T/

├── src/               # 核心代码
├── ai_brain/          # AI智能模块
├── strategy/          # 策略模块
├── risk/              # 风险模块
├── execution/         # 执行模块
├── data/              # 数据模块
├── parameter/         # 参数模块
├── test/              # 测试模块
├── config/            # 配置中心
├── scripts/           # 工具脚本
├── docs/              # 文档
├── logs/              # 运行日志
├── requirements.txt   # Python依赖
├── pyproject.toml     # 项目配置
├── main.py            # 系统入口
└── README.md          # 项目说明
```



---

# 第三章 src核心代码层


## 3.1 src定位


src作为系统核心运行入口。


负责：

- 公共接口
- 数据结构
- 系统服务
- 通用组件



## 3.2 结构


```
src/

├── core/              # 核心运行逻辑
├── schema/            # 统一数据模型
├── interfaces/        # 接口定义
├── services/          # 系统服务
├── utils/             # 工具函数
└── exceptions/        # 异常定义
```



---

# 第四章 AI Brain代码框架


对应：

03_AI_Brain + 11_AI_Implementation



```
ai_brain/

├── prediction/
│   ├── models/
│   ├── inference.py
│   └── trainer.py

├── sentiment/
│   ├── nlp_model.py
│   └── sentiment_engine.py

├── risk_intelligence/
│   └── risk_predictor.py

├── fusion/
│   ├── weighted.py
│   ├── voting.py
│   └── stacking.py

├── learning/
│   ├── optimizer.py
│   └── feedback.py

└── registry/
    └── model_registry.py
```



---

# 第五章 Strategy代码框架


对应：

04_Strategy



```
strategy/

├── trend/
│   └── trend_strategy.py

├── value/
│   └── value_strategy.py

├── quant/
│   └── quant_strategy.py

├── sentiment/
│   └── sentiment_strategy.py

├── defensive/
│   └── defensive_strategy.py

├── engine/
│   └── strategy_engine.py

└── interface/
    └── strategy_base.py
```



---

# 第六章 Risk代码框架


对应：

05_Risk



```
risk/

├── evaluator/
│   └── risk_evaluator.py

├── limits/
│   └── risk_limit.py

├── monitor/
│   └── risk_monitor.py

├── decision/
│   └── risk_decision.py

└── interface/
    └── risk_base.py
```



核心输出：

APPROVE / ADJUST / REJECT



---

# 第七章 Execution代码框架


对应：

06_Execution



```
execution/

├── order/
│   ├── order.py
│   └── order_manager.py

├── broker/
│   └── broker_interface.py

├── executor/
│   └── execution_engine.py

├── monitor/
│   └── execution_monitor.py

└── feedback/
    └── execution_feedback.py
```



订单状态：

Created → Submitted → Accepted → Filled → Completed



---

# 第八章 Data代码框架


对应：

07_Data + 12_Data_Engineering



```
data/

├── ingestion/
│   └── data_collector.py

├── pipeline/
│   └── data_pipeline.py

├── storage/
│   └── data_storage.py

├── feature/
│   └── feature_engineering.py

├── quality/
│   └── quality_check.py

└── service/
    └── data_service.py
```



---

# 第九章 Parameter代码框架


对应：

08_Parameter



```
parameter/

├── manager/
│   └── parameter_manager.py

├── version/
│   └── version_control.py

├── optimizer/
│   └── parameter_optimizer.py

├── validator/
│   └── parameter_validator.py

└── config/
    └── parameter_schema.py
```



---

# 第十章 配置体系


目录：

config/


配置文件：

- system.yaml
- model.yaml
- strategy.yaml
- risk.yaml
- execution.yaml
- data.yaml


原则：

代码与参数分离。



---

# 第十一章 测试代码框架


对应：

09_Test



```
test/

├── unit/
├── integration/
├── backtest/
├── simulation/
├── stress/
└── performance/
```



测试覆盖：

AI / Strategy / Risk / Execution / Data / Parameter



---

# 第十二章 软件启动入口


主入口：

main.py


启动流程：


Load Config

↓

Initialize Data

↓

Start AI Brain

↓

Generate Strategy

↓

Risk Validation

↓

Execute

↓

Feedback



形成AQF-T运行闭环。



---

# 第十三章 日志体系


目录：

logs/


日志文件：

- system.log
- ai.log
- strategy.log
- risk.log
- execution.log
- data.log


要求：

所有核心模块必须产生运行日志。



---

# 第十四章 异常处理体系


统一异常定义：

src/exceptions/


异常类型：

- DataException
- ModelException
- StrategyException
- RiskException
- ExecutionException


原则：

异常不能静默失败。



---

# 第十五章 Docker部署准备


支持：

- Dockerfile
- docker-compose.yml


基础服务：

AQF-T Application + Database + Message Queue + Monitoring



---

# 第十六章 CI/CD代码连接


代码流程：


Developer Commit → Git Repository → CI Pipeline → Test → Build → Deploy



---

# 第十七章 P2完成后的最终代码结构


```
AQF-T/

├── ai_brain/
├── strategy/
├── risk/
├── execution/
├── data/
├── parameter/
├── test/
├── config/
├── src/
├── scripts/
├── docs/
├── logs/
└── main.py
```



---

# 第十八章 P2阶段完成状态


## P2 Engineering Implementation


| 模块 | 状态 |
|------|------|
| Software Engineering Standard | ✅ |
| Project Management | ✅ |
| AI Engineering | ✅ |
| Data Engineering | ✅ |
| Code Framework | ✅ |



---

# 第十九章 工程冻结声明


本文件定义：

AQF-T代码基础框架。


后续：

代码开发；

模块实现；

系统运行；


必须遵循本框架。



Version:

V2.8.6


Status:

Engineering Implementation


END OF AQFT CODE FRAMEWORK DESIGN
