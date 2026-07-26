# AQFT Runtime Foundation Design V3.6.0


# AQF-T 运行系统基础详细设计


Version: V3.6.0
Status: Detailed Engineering Design
Classification: AQF-T 运行环境基础设施设计文件
Date: 2026-07-26


---

# 第一章 定位

Runtime Foundation 是 AQF-T 从设计到运行的桥梁。负责系统启动、服务编排、配置管理、日志、调度、事件通信和异常恢复。

```
设计文档 → Runtime Foundation → 各模块运行实例 → 协同工作
```

---

# 第二章 系统启动序列


## 2.1 启动流程

```
Step 0: 环境检查
  - Python版本 ≥ 3.11
  - 依赖包完整性检查
  - 磁盘空间 > 1GB
  - 数据目录可写

Step 1: 加载系统配置 (config/system.yaml)
  → 失败: 终止启动, 输出错误

Step 2: 初始化日志系统
  → 创建 logs/ 目录
  → 配置: 按日滚动 + 保留30天 + 控制台同步输出

Step 3: 初始化数据库连接
  → SQLite: data/aqft.db (默认)
  → 验证: 执行 SELECT 1
  → 失败: 重试3次 → 终止

Step 4: 加载参数快照 (08_Parameter)
  → 加载最新ACTIVE参数
  → 失败: 使用默认参数 + 告警

Step 5: 启动数据服务 (07_Data / 15_Data_Runtime)
  → 验证数据源连通性
  → 失败: 降级模式, 仅本地缓存 + 告警

Step 6: 启动 AI Brain (03_AI_Brain / 16_AI_Runtime)
  → 加载模型到内存
  → 验证: 执行一次空推理
  → 失败: 终止, AI是核心依赖

Step 7: 启动 Strategy (04_Strategy / 17_Strategy_Runtime)
  → 加载活跃策略列表
  → 验证: 策略参数完整性

Step 8: 启动 Risk (05_Risk / 18_Risk_Runtime)
  → **必须成功** (安全核心)
  → 失败: 终止启动, Risk不可绕过

Step 9: 启动 Execution (06_Execution / 19_Execution_Runtime)
  → 连接Broker (Paper Trading模式下为模拟Broker)
  → 失败: Execution标记为standby

Step 10: 启动 Scheduler (定时任务)
Step 11: 系统状态 → READY

启动总耗时目标: < 30秒
```

## 2.2 启动检查清单

```
[ ] 配置文件有效
[ ] 数据库连接正常
[ ] AI模型加载成功
[ ] 参数快照加载成功
[ ] Risk模块在线 (强制)
[ ] 数据服务至少1个数据源可用
[ ] 日志系统初始化成功
[ ] Scheduler启动成功
```

---

# 第三章 服务管理


## 3.1 服务清单及依赖

| 服务 | 依赖 | 启动优先级 | 关键度 |
|------|------|:---:|:---:|
| DataService | — | 1 | 核心 |
| ParameterService | — | 1 | 核心 |
| AIBrainService | DataService | 2 | 核心 |
| StrategyService | AIBrainService | 3 | 核心 |
| RiskService | StrategyService | 4 | **强制** |
| ExecutionService | RiskService | 5 | 业务 |
| SchedulerService | — | 6 | 辅助 |
| MonitoringService | — | 6 | 辅助 |

## 3.2 服务状态机

```
INIT → STARTING → RUNNING → DEGRADED → STOPPING → STOPPED
                 │          │
                 │          └→ 部分功能失效但仍可用
                 └→ ERROR → RESTARTING → STARTING
```

| 状态 | 说明 | 触发 |
|------|------|------|
| INIT | 初始状态 | 系统启动 |
| STARTING | 正在启动 | 依赖检查+加载 |
| RUNNING | 正常运行 | 健康检查通过 |
| DEGRADED | 降级运行 | 部分功能失效 |
| ERROR | 异常 | 致命错误 |
| RESTARTING | 重启中 | 自动恢复 |
| STOPPED | 已停止 | 人工/自动停止 |

## 3.3 健康检查

```
Health Check:
  频率: 每10秒
  超时: 3秒
  内容: /health 端点返回 + 依赖服务状态

连续3次失败 → DEGRADED
连续10次失败 → ERROR → 自动重启
重启3次仍失败 → 停止重启 + 告警
```

---

# 第四章 配置管理


## 4.1 system.yaml 完整结构

```
system:
  name: AQF-T
  version: 3.6.0
  mode: paper_trading   # development | paper_trading | production

server:
  host: 127.0.0.1
  port: 8080

database:
  type: sqlite
  path: data/aqft.db

modules:
  data:
    enabled: true
    source: akshare          # akshare | qmt | tushare
  ai_brain:
    enabled: true
    model_path: models/
  strategy:
    enabled: true
    active: [trend, dragon, volume_price, sentiment, defensive]
  risk:
    enabled: true
    kill_switch_active: true
    max_position: 0.70
    stop_loss: -0.05
  execution:
    enabled: true
    mode: paper_trading      # paper_trading | qmt_live
    broker: simulated

logging:
  level: INFO                # DEBUG | INFO | WARNING | ERROR
  dir: logs/
  retention_days: 30

scheduler:
  market_update_interval: 1s
  feature_update_interval: 60s
  risk_scan_interval: 10s
  model_prediction_interval: 300s

alerts:
  daily_loss_threshold: -0.02
  drawdown_threshold: -0.10
```

## 4.2 配置优先级

```
命令行参数 > 环境变量 > system.yaml > 代码默认值

示例:
  export AQFT_MODE=production     → 覆盖 system.yaml mode
  --risk.max_position=0.50         → 最高优先级
```

---

# 第五章 日志规范


## 5.1 统一日志格式

```
[2026-07-26 10:30:15.123] [INFO] [risk_engine] Risk check: symbol=SH.600519 score=25 decision=APPROVE

格式: [时间] [级别] [模块] 消息
```

## 5.2 日志文件

| 文件 | 内容 | 级别 | 轮转 |
|------|------|:---:|:---:|
| system.log | 系统级别日志 | INFO+ | 每日 |
| ai.log | AI Brain 日志 | DEBUG+ | 每日 |
| strategy.log | 策略信号日志 | INFO+ | 每日 |
| risk.log | 风控决策日志 | INFO+ | 每日 |
| execution.log | 订单执行日志 | INFO+ | 每日 |
| data.log | 数据管道日志 | INFO+ | 每日 |
| error.log | 所有ERROR/CRITICAL | ERROR+ | 每日 |

## 5.3 日志级别使用规则

```
DEBUG:   开发调试, 详细变量值
INFO:    正常运行, 关键决策点
WARNING: 异常但可恢复
ERROR:   需要人工介入
CRITICAL: 系统级故障, 必须立即处理
```

---

# 第六章 Scheduler 定时任务


## 6.1 任务定义

| 任务 | 频率 | 优先级 | 说明 |
|------|:---:|:---:|------|
| market_data_update | 每秒 | P0 | 拉取最新行情Tick |
| sentient_refresh | 每分钟 | P0 | 更新情绪指标 |
| risk_scan | 每10秒 | P0 | 风险实时扫描 |
| model_prediction | 每5分钟 | P1 | AI预测更新 |
| feature_refresh | 每分钟 | P1 | 特征重新计算 |
| position_sync | 每30秒 | P1 | 持仓/资金同步 |
| strategy_evaluation | 每小时 | P2 | 策略绩效评估 |
| parameter_optimization | 每日盘后 | P2 | 参数优化建议 |
| data_cleanup | 每日凌晨 | P3 | 日志清理/数据归档 |
| model_retrain_check | 每周 | P3 | 检查是否需要重训练 |

## 6.2 交易日特殊调度

```
盘前 (9:00-9:25):
  - 数据预加载
  - T+1刷新 (available = locked + available)
  - 竞价数据采集

盘中 (9:30-15:00):
  - 全任务运行

盘后 (15:00-16:00):
  - 龙虎榜数据拉取
  - 日K线更新
  - 策略绩效计算

非交易日:
  - 仅: model_retrain_check, data_cleanup
```

---

# 第七章 Event Bus 拓扑


## 7.1 事件类型及流向

```
MarketDataEvent
  → World Model (行情更新)
  → Risk Engine (实时监控)

SentimentEvent
  → Strategy (情绪周期更新)
  → Risk (情绪风险评分)

TradingSignalEvent
  → Risk (审批)

RiskDecisionEvent
  → Execution (执行)
  → Experience (记录)

OrderEvent
  → Portfolio Manager (更新持仓)
  → Experience (交易记录)

ExecutionResultEvent
  → Data (存储)
  → AI Brain (反馈学习)
  → Strategy (绩效更新)

AlertEvent
  → 所有模块 (告警广播)
```

---

# 第八章 异常恢复


## 8.1 分级恢复策略

| 级别 | 场景 | 恢复策略 | 超时 |
|------|------|---------|:---:|
| L1 | 数据源暂时断开 | 使用缓存, 自动重连 | 60s |
| L2 | 单个服务异常 | 自动重启该服务 | 30s |
| L3 | 多个服务异常 | 按依赖顺序重启 | 120s |
| L4 | 数据库异常 | 切换备份, 暂停写入 | 300s |
| L5 | 系统级故障 | Safe Mode + 人工介入 | — |

## 8.2 自动恢复流程

```
检测异常 → 记录日志 → 判断级别 → 
  L1-L3: 自动重启 → 健康检查 → 恢复 → 记录恢复日志
  L4-L5: 告警 + Safe Mode → 等待人工
```

---

# 第九章 运行安全


```
不可绕过:
  - Risk服务不可被关闭或绕过
  - 参数变更必须走审批流程
  - 日志记录不可被删除

运行时保护:
  - 生产模式下禁止 DEBUG 级别日志(防信息泄露)
  - 配置热更新仅允许非关键参数
  - Kill Switch 优先级最高, 可中断任何操作
```

---

# 第十章 系统 API


| 端点 | 方法 | 功能 |
|------|:---:|------|
| /system/status | GET | 完整系统状态 |
| /system/health | GET | 健康检查 |
| /system/services | GET | 所有服务状态 |
| /system/config | GET | 当前配置 |
| /system/config/reload | POST | 重载配置 |
| /system/restart/{service} | POST | 重启指定服务 |
| /system/logs/{module} | GET | 查询模块日志 |
| /system/version | GET | 版本信息 |

---

# 第十一章 设计冻结声明


本文件定义 AQF-T Runtime Foundation V3.6.0 详细设计。

11步启动序列、8服务依赖管理、10项定时任务、7类事件流向、5级异常恢复。

让 AQF-T 从 29 个设计模块变成 1 个可运行系统。

Version: V3.6.0
Status: Detailed Engineering Design
END OF AQFT RUNTIME FOUNDATION DESIGN
