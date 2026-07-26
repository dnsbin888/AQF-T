# AQFT Distributed Intelligence Core V3.2.0


# AQF-T 分布式智能核心设计

Version: V3.2.0 | Status: Runtime Engineering | Date: 2026-07-26

---

## 第一章 定位

V3.1.1 完成了分布式服务骨架（8个独立进程，各自返回固定数据）。

V3.2.0 的目标：让服务之间真正协同 — 形成 Intelligence Pipeline。

---

## 第二章 Intelligence Pipeline

```
Market Data Service (:8106)
    │  MarketEvent → Event Bus
    ↓
World Model Service (:8102)
    │  WorldState → Event Bus
    ↓
Agent Council (:8101)
    │  AgentConsensus → Event Bus
    ↓
Decision Engine (:8103)
    │  Decision → Event Bus
    ↓
Risk Engine (:8104)
    │  RiskDecision(APPROVE/ADJUST/REJECT) → Event Bus
    ↓
Execution Runtime
    │  OrderResult → Event Bus
    ↓
Memory Service (:8105)
    │  Experience Stored
    ↓
Learning Engine
    │  Model/Strategy Update
    ↓
(Back to World Model)
```

---

## 第三章 Event Bus — AQF-T 神经系统

基于 Redis Pub/Sub，所有服务通过事件通信。

事件类型：MarketEvent / WorldStateEvent / AgentConsensusEvent / DecisionEvent / RiskDecisionEvent / ExecutionEvent / MemoryEvent

---

## 第四章 Intelligence Orchestrator

不再是各服务独立返回。Orchestrator 按 Intelligence Pipeline 顺序调用各服务，形成完整决策链。

---

## 第五章 部署

V3.2.0: 本机 8 进程 + Redis Event Bus
V3.3.0: Docker Compose 容器化
V4.0.0: K8s 分布式集群

---

Version: V3.2.0
END OF AQFT DISTRIBUTED INTELLIGENCE CORE DESIGN
