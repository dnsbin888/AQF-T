# AQFT Distributed Runtime Architecture V3.1.1


# AQF-T 分布式智能运行时架构


Version: V3.1.1
Status: Runtime Engineering Design
Date: 2026-07-26


---

## 第一章 设计目标

将 AQF-T 35 个智能模块从单体原型拆分为独立运行的分布式服务节点。

每个 P5 模块对应一个独立进程，通过 API Gateway + Message Bus 协同工作。

---

## 第二章 分布式拓扑

```
                    Browser (:8080)
                         │
                  AQF-T Gateway (:8080)
                         │
                  Service Registry (:8100)
                         │
    ┌────────┬───────┬───┴───┬───────┬────────┐
    │        │       │       │       │        │
  Agent   World   Decision  Risk   Memory   Market
  (:8101) Model   (:8103)  (:8104) (:8105)  Data
          (:8102)                            (:8106)
    │        │       │       │       │        │
    └────────┴───────┴───┬───┴───────┘        │
                         │                    │
                  Message Bus (:8200) ←───────┘
                         │
                  Database (data/aqft.db)
```

---

## 第三章 服务端口分配

| 服务 | 端口 | 职责 |
|------|------|------|
| Gateway | 8080 | 统一入口 + Web Console |
| Service Registry | 8100 | 服务发现与健康检查 |
| Agent Service | 8101 | Multi-Agent 协调 |
| World Model Service | 8102 | World Model 五层认知 |
| Decision Service | 8103 | AGI 决策引擎 |
| Risk Service | 8104 | 风险控制 (Kill Switch) |
| Memory Service | 8105 | Simulation Memory |
| Market Data Service | 8106 | 市场数据接入 |
| Message Bus | 8200 | 服务间异步通信 |

---

## 第四章 服务通信协议

### REST API (同步)
- Gateway → 各服务：HTTP/JSON
- 健康检查：GET /health

### Message Bus (异步)
- Event: MarketEvent / RiskEvent / DecisionEvent
- 格式：JSON over Redis/NATS

### 统一响应格式
```json
{
  "service": "world_model",
  "version": "3.1.1",
  "status": "OK",
  "data": {},
  "timestamp": ""
}
```

---

## 第五章 本机启动方式

```
# 开发模式 — 所有服务本地启动
python services/start_all.py

# 或逐个启动
python world_model_service.py  &
python decision_service.py     &
python risk_service.py         &
python agent_service.py        &
python memory_service.py       &
```

---

## 第六章 部署路线

| 阶段 | 部署方式 |
|------|---------|
| V3.1.1 | 本机多进程（开发） |
| V3.2.0 | Docker Compose（单机容器化） |
| V3.3.0 | Kubernetes（分布式集群） |
| V4.0.0 | GPU + 云端部署 |

---

Version: V3.1.1
Status: Runtime Engineering Design
END OF AQFT DISTRIBUTED RUNTIME ARCHITECTURE
