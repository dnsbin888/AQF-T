# AQF-T API Specification V3.6.0


# AQF-T 接口规范


Version: V3.6.0 | Status: Engineering Specification | Date: 2026-07-26

---

## 统一规范

- Base URL: `http://127.0.0.1:8080/api/v1`
- Content-Type: `application/json`
- 时间: UTC ISO 8601
- 股票代码: `SH.600519` / `SZ.000858` / `BJ.8xxxxx`
- 错误格式: `{"error": {"code": "ERROR_CODE", "message": "详情"}}`

---

## 数据服务 (07_Data)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/data/realtime/{symbol}` | 实时行情 |
| GET | `/data/kline/{symbol}?period=1d&start=&end=` | K线 |
| GET | `/data/limit_up/today` | 今日涨停列表 |
| GET | `/data/limit_up/ladder` | 涨停梯队 |
| GET | `/data/longhu/today` | 今日龙虎榜 |
| GET | `/data/auction/{symbol}` | 集合竞价 |
| GET | `/data/capital/north_bound` | 北向资金 |
| GET | `/data/sentiment/overview` | 情绪全景 |
| GET | `/data/feature/{symbol}` | 特征向量 |

## AI服务 (03_AI_Brain / 16_AI_Runtime)

| 方法 | 端点 | Request | Response |
|------|------|---------|----------|
| POST | `/ai/predict` | `{symbol, market_data, indicators}` | `{trend, probability, confidence}` |
| POST | `/ai/sentiment` | `{scope}` | `{phase, sentiment_score, theme_analysis}` |
| POST | `/ai/risk` | `{position, market_context}` | `{risk_score, risk_level, warnings}` |
| POST | `/ai/fusion` | `{prediction, sentiment, risk}` | `{action, confidence, reasoning_trace}` |
| GET | `/ai/model/status` | — | 所有模型状态 |

## 策略服务 (04_Strategy / 17_Strategy_Runtime)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/strategy/signal` | 生成交易信号 |
| GET | `/strategy/list` | 策略列表 |
| POST | `/strategy/{id}/activate` | 激活 |
| POST | `/strategy/{id}/pause` | 暂停 |

## 风控服务 (05_Risk / 18_Risk_Runtime)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/risk/check` | Pre-Trade审批 |
| GET | `/risk/status` | 实时风控状态 |
| POST | `/risk/kill_switch` | 手动Kill Switch |
| POST | `/risk/kill_switch/clear` | 清除(需授权) |

## 执行服务 (06_Execution / 19_Execution_Runtime)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/execution/order` | 提交订单 |
| GET | `/execution/order/{id}` | 查询订单 |
| POST | `/execution/order/{id}/cancel` | 撤单 |
| GET | `/execution/position` | 当前持仓 |
| GET | `/execution/account` | 账户信息 |

## 模拟/回测 (20_Simulation_System)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/simulation/start` | 启动模拟交易 |
| POST | `/backtest/run` | 运行回测 |
| GET | `/backtest/result/{id}` | 回测结果 |

## 系统 (14_Runtime)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/system/status` | 系统状态 |
| GET | `/system/health` | 健康检查 |

---

共计 **35 个 API 端点**, 覆盖 Data/AI/Strategy/Risk/Execution/Simulation/System 全部服务。

Version: V3.6.0 | Status: Engineering Specification
END OF AQFT API SPECIFICATION
