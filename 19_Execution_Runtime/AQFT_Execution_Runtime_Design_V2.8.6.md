# AQFT Execution Runtime Design


# AQF-T交易执行运行系统设计


Version:

V2.8.6


Status:

Running System Design


Classification:

AQF-T实时交易执行运行体系设计文件


Date:

2026-07-26


---

# 第一章 Execution Runtime定位


## 1.1 Execution Runtime目标


Execution Runtime负责将AQF-T执行体系转换为实时交易执行能力。


主要职责：

- 订单生命周期管理
- 执行策略优化
- Broker/API抽象
- 成交监控
- 滑点控制
- 执行反馈闭环


核心运行链：

Strategy Signal → Risk Approval → Order Execution → Broker Interface → Trade Result → Feedback



---

## 1.2 与AQF-T架构关系


06_Execution（设计层）→ execution/（代码框架层）→ 19_Execution_Runtime（运行层）← 本文件 → Broker / Market → Feedback System



---

## 1.3 执行原则


- Risk Runtime审批通过后执行
- 所有订单必须记录
- 异常自动保护
- 执行结果必须反馈



---

# 第二章 Execution Runtime总体架构


Order Manager → Execution Engine → Broker Interface → Execution Monitor → Feedback System



---

# 第三章 Order Manager订单管理系统


## 3.1 订单生命周期


CREATED → VALIDATED → SUBMITTED → ACCEPTED → PARTIALLY_FILLED → FILLED → COMPLETED


异常状态：REJECTED / CANCELLED / FAILED / EXPIRED



---

## 3.2 订单数据结构


- order_id / symbol / side(BUY/SELL) / quantity / price
- type(MARKET/LIMIT/STOP) / status
- risk_approval / strategy_signal / timestamp



---

## 3.3 订单安全验证


提交前必须验证：

- Risk状态 APPROVED
- 资金可用
- 仓位未超限
- 交易时段有效
- 订单参数合法



---

# 第四章 Execution Engine执行引擎


## 4.1 执行策略


- Market Order — 市价执行
- Limit Order — 限价执行
- TWAP — 时间加权均价
- VWAP — 成交量加权均价
- Smart Execution — 智能执行



---

## 4.2 执行流程


Receive Order → Validate → Select Strategy → Execute → Monitor Fill → Confirm → Report



---

# 第五章 Broker Interface交易接口层


## 5.1 Broker Abstract Layer


提供统一交易接口，隔离具体券商实现。


## 5.2 支持接口


- Market Data API — 行情订阅
- Order API — 下单/撤单/改单
- Account API — 账户/持仓/资金
- Trade API — 成交查询


## 5.3 接口原则


统一抽象 / 可替换 / 可扩展 / 支持QMT等国内券商 / 支持未来多市场



---

# 第六章 Order Router订单路由


市价单→快速通道 / 限价单→标准通道 / 大单→TWAP/VWAP / 风控紧急单→优先通道



---

# 第七章 Execution Monitor执行监控


监控：订单状态 / 成交进度 / 延迟 / 异常订单 / Broker连接状态


告警触发：订单超时 / Broker断开 / 成交价异常 / 重复订单



---

# 第八章 Slippage Control滑点控制


- 超过阈值→暂停执行
- 严重滑点→撤单重发
- 连续滑点→切换执行方式
- 极端滑点→暂停策略



---

# 第九章 Settlement结算系统


Trade Confirmation → Position Update → P&L Calculation → Cash Update → Record



---

# 第十章 Execution Feedback执行反馈


反馈至各模块：成交价/量 / 滑点 / 手续费 / 执行延迟


闭环：Execution Result → Data Runtime → AI Learning → Strategy Optimization → Risk Calibration



---

# 第十一章 Emergency Handler紧急处理


紧急情况：Broker断开 / 重复成交 / 订单状态异常 / 持仓异常


处理流程：Detect → Cancel All Orders → Stop Execution → Alert → Manual Review



---

# 第十二章 Execution API设计


- POST /order/create — 创建订单
- POST /order/cancel — 撤销订单
- GET /order/status — 查询订单
- GET /position — 查询持仓
- GET /account — 查询账户
- GET /execution/report — 执行报告



---

# 第十三章 Execution Runtime目录结构


19_Execution_Runtime/
├── order/       (order_manager / order_validator)
├── broker/      (broker_abstract / qmt_adapter / simulator_adapter)
├── executor/    (execution_engine / market_executor / smart_executor)
├── router/      (order_router)
├── monitor/     (execution_monitor)
├── slippage/    (slippage_control)
├── settlement/  (settlement)
├── feedback/    (execution_feedback)
├── emergency/   (emergency_handler)
├── api/         (execution_api)
└── tests/



---

# 第十四章 Execution Runtime测试体系


- Unit Test — 订单管理和执行逻辑
- Integration Test — Risk Runtime → Execution Runtime → Broker
- Simulation Test — 模拟Broker完整执行流程
- Stress Test — 高并发下单和极端行情



---

# 第十五章 P3-06完成标准


| 能力 | 状态 |
|------|------|
| 订单生命周期管理 | ✅ |
| 执行策略(Market/Limit/TWAP/VWAP/Smart) | ✅ |
| Broker抽象层 | ✅ |
| 订单路由 | ✅ |
| 滑点控制 | ✅ |
| 结算系统 | ✅ |
| 执行反馈 | ✅ |
| 紧急处理 | ✅ |



---

# 第十六章 Execution Runtime冻结声明


本文件定义AQF-T交易执行运行体系。

后续模拟交易、生产部署、实盘运行必须基于本执行运行体系。



Version:

V2.8.6


Status:

Running System Design


END OF AQFT EXECUTION RUNTIME DESIGN
