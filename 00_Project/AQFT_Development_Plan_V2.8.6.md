# AQFT Development Plan


# AQF-T开发计划


Version:

V2.8.6


Status:

Project Management


Classification:

AQF-T研发执行计划文件


Date:

2026-07-26


---

# 第一章 当前状态


## 1.1 已完成


- P0 — 系统架构 ✅
- P1 — 核心设计 ✅
- P2-01 — 软件工程规范 ✅



---

## 1.2 当前阶段


进入：

Engineering Implementation



---

# 第二章 P2开发计划


## 2.1 P2-02 项目管理体系


目标：

建立研发治理。


输出：

- Roadmap — 路线图
- Version Control — 版本控制
- Development Plan — 开发计划（本文件）



---

## 2.2 P2-03 AI工程实现


目录：

11_AI_Implementation/


建设：


### Model Framework

模型统一接口。


### Feature Pipeline

特征生成。


### Model Registry

模型管理。


### Training Pipeline

训练流程。


### Inference Service

预测服务。



---

## 2.3 P2-04 数据工程


目录：

12_Data_Engineering/


建设：

- 数据采集
- 数据仓库
- Feature Store
- 数据质量系统



---

## 2.4 P2-05 软件骨架


建立：


AQF-T/

├── src/
├── ai_brain/
├── strategy/
├── risk/
├── execution/
├── data/
├── parameter/
├── test/
└── config/



---

# 第三章 开发管理流程


## 3.1 开发流程


需求

↓

设计

↓

开发

↓

测试

↓

评审

↓

合并

↓

发布



---

## 3.2 代码审查


所有代码：

提交前必须经过审查。



---

## 3.3 测试要求


每个模块：

必须有：

- 单元测试
- 集成测试



---

# 第四章 质量要求


## 4.1 模块交付标准


所有模块：

必须满足：

1. 有设计文档
2. 有代码实现
3. 有单元测试
4. 有运行日志
5. 有版本记录



---

## 4.2 文档要求


代码与文档同步更新。


禁止：

先写代码后补文档。



---

# 第五章 风险与约束


## 5.1 开发约束


所有开发：

必须遵守：

- AQF-T System Constitution
- AQF-T Architecture Design
- AQF-T Engineering Standard



---

## 5.2 风险控制


开发过程中：

任何交易相关功能：

必须经过Risk模块验证。



---

# 第六章 研发冻结声明


本文件定义：

AQF-T研发实施计划。


后续：

工程开发；

模块实现；

版本发布；


必须遵循本计划。



Version:

V2.8.6


Status:

Project Management


END OF AQFT DEVELOPMENT PLAN
