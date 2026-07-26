# AQFT Data Design


# AQF-T数据体系设计


Version:

V2.8.6


Status:

Architecture Design


Classification:

AQF-T核心数据体系设计文件


Date:

2026-07-26


---

# 第一章 数据体系定位


## 1.1 系统定位


Data模块是AQF-T系统的数据基础设施。


负责：

- 数据采集
- 数据存储
- 数据管理
- 数据治理
- 数据服务


Data模块为：

AI Brain；

Strategy；

Risk；

Execution；

提供统一数据支撑。



---

# 第二章 数据体系总体架构


AQF-T数据体系：



External Data Source

    ↓

Data Acquisition

    ↓

Raw Data Layer

    ↓

Standard Data Layer

    ↓

Feature Data Layer

    ↓

Model Service

    ↓

Feedback Data



---

# 第三章 数据来源体系


## 3.1 市场数据


Market Data


包括：


- 股票行情
- K线数据
- 成交数据
- 盘口数据
- 资金流数据



用途：

市场状态分析。



---

## 3.2 基本面数据


Fundamental Data


包括：

- 财务数据
- 公司信息
- 行业数据
- 估值数据



用途：

价值分析。



---

## 3.3 另类数据


Alternative Data


包括：


- 新闻
- 舆情
- 社交信息
- 市场情绪数据



用途：

情绪分析。



---

## 3.4 交易反馈数据


Trading Feedback Data


包括：

- 历史订单
- 成交记录
- 盈亏结果
- 风险事件



用途：

系统学习。



---

# 第四章 数据分层设计


## 4.1 原始数据层


Raw Data Layer


保存：

未经处理的原始数据。


特点：

完整保存。



---

## 4.2 标准数据层


Standard Data Layer


负责：

数据清洗；

格式统一；

字段标准化。



---

## 4.3 特征数据层


Feature Data Layer


用于：

AI模型输入。


包括：

- 技术指标
- 市场状态
- 情绪指标
- 风险指标



---

## 4.4 结果数据层


Result Data Layer


保存：

- 交易结果
- 模型预测
- 策略表现
- 风险记录



---

# 第五章 数据治理体系


## 5.1 数据质量管理


保证：

- 准确性
- 完整性
- 一致性
- 时效性



---

## 5.2 数据版本管理


所有重要数据：

必须记录版本。


包括：

- 数据来源
- 更新时间
- 修改记录



---

## 5.3 数据追溯机制


任何模型结果：

必须能够追溯：

数据来源。


实现：

Data Lineage。



---

# 第六章 数据接口设计


## 输入


外部数据源


↓


Data模块



---

## 输出


提供：


Data Service


发送至：


AI Brain


Strategy


Risk


Execution



---

# 第七章 数据安全设计


包括：


## 权限控制


不同模块：

不同访问权限。



---

## 数据备份


重要数据：

定期备份。



---

## 数据隔离


开发；

测试；

生产；


数据环境隔离。



---

# 第八章 数据生命周期管理


流程：


采集

↓

存储

↓

处理

↓

使用

↓

归档

↓

删除



---

# 第九章 数据服务能力


未来支持：


- 实时数据服务
- 历史数据查询
- 特征计算服务
- 模型数据接口
- 多市场数据接入



---

# 第十章 数据扩展原则


新增数据源必须：

1. 定义数据格式

2. 明确数据质量标准

3. 建立接口规范

4. 纳入版本管理



---

# 第十一章 数据体系与AI闭环


数据：

↓

AI Brain

↓

Strategy

↓

Risk

↓

Execution

↓

Feedback

↓

Data更新



形成：

持续学习数据闭环。



---

# 第十二章 数据设计冻结声明


本文件定义：

AQF-T数据体系。


后续：

数据库设计；

数据接口；

数据服务；

数据治理；


必须遵守本设计。



Version:

V2.8.6


Status:

Architecture Design


END OF AQFT DATA DESIGN
