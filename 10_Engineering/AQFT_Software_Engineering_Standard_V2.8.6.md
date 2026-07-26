# AQFT Software Engineering Standard


# AQF-T软件工程规范


Version:

V2.8.6


Status:

Engineering Standard


Classification:

AQF-T软件工程基础规范文件


Date:

2026-07-26


---

# 第一章 软件工程规范定位


## 1.1 工程目标


本规范定义AQF-T从架构设计向可维护、可扩展、可部署软件系统转换的工程基础标准。


目标：

- 统一代码组织方式
- 统一开发流程
- 保证架构设计落地
- 降低后期AI模型、策略、交易模块维护成本
- 支撑未来团队协作开发



---

## 1.2 架构遵循原则


所有代码实现：

必须遵循：


02_Constitution（系统宪法）


01_Architecture（系统架构）


03-09 各模块设计文档



禁止：

偏离架构设计的自由开发。



---

## 1.3 与AQF-T架构关系


Constitution

↓

Architecture

↓

Module Design

↓

Engineering Standard  ← 本文件

↓

Code Implementation

↓

Testing

↓

Deployment



---

# 第二章 软件项目目录规范


## 2.1 根目录结构


```
AQF-T/

├── src/               # 核心源代码
├── ai_brain/          # AI智能模块
├── strategy/          # 策略模块
├── risk/              # 风险模块
├── execution/         # 执行模块
├── data/              # 数据模块
├── parameter/         # 参数模块
├── test/              # 测试模块
├── config/            # 配置文件
├── docs/              # 文档
├── scripts/           # 工具脚本
├── 00_Project/        # 项目管理
├── 01_Architecture/   # 架构设计文档
├── 02_Constitution/   # 系统宪法
├── 99_Archive/        # 历史归档
├── requirements.txt   # Python依赖
├── pyproject.toml     # 项目配置
└── README.md          # 项目说明
```



---

## 2.2 模块目录规范


每个模块内部结构：


```
module_name/

├── __init__.py

├── core/              # 核心逻辑
├── models/            # 数据模型
├── services/          # 服务层
├── interfaces/        # 接口定义
├── utils/             # 工具函数
├── config/            # 模块配置
└── tests/             # 模块测试
```



---

## 2.3 文件命名规范


Python文件：

小写 + 下划线


示例：


risk_evaluator.py

strategy_manager.py

data_pipeline.py



配置文件：

小写 + 下划线 + .yaml


示例：


model_config.yaml

risk_params.yaml



---

# 第三章 Python开发规范


## 3.1 Python版本要求


Python 3.11+



---

## 3.2 编码规范


遵循：

PEP8标准。



核心要求：

- 缩进：4空格
- 行宽：最大120字符
- 导入：标准库 → 第三方 → 本地模块
- 命名：类用PascalCase，函数用snake_case



---

## 3.3 类型规范


所有公共函数：

必须使用Type Hint。


示例：


def evaluate_risk(
    signal: TradingSignal,
    portfolio: Portfolio
) -> RiskDecision:
    ...



---

## 3.4 文档规范


所有公共类和方法：

必须包含Docstring。


格式：

Google Style或NumPy Style。


内容包括：

- 功能描述
- 参数说明
- 返回值说明
- 异常说明



---

# 第四章 模块开发规范


## 4.1 AI Brain开发规范


遵循：

03_AI_Brain/AQFT_AI_Brain_Design_V2.8.6.md



开发要点：

- 模型必须可替换
- 输入输出标准化
- 模型版本管理
- 预测结果可解释



---

## 4.2 Strategy开发规范


遵循：

04_Strategy/AQFT_Strategy_Design_V2.8.6.md



开发要点：

- 策略可插拔
- 信号标准化
- 参数可配置
- 表现可评价



---

## 4.3 Risk开发规范


遵循：

05_Risk/AQFT_Risk_Design_V2.8.6.md



开发要点：

- 风险检查为强制步骤
- 否决权限不可绕过
- 风险阈值可配置
- 异常保护必须有



---

## 4.4 Execution开发规范


遵循：

06_Execution/AQFT_Execution_Design_V2.8.6.md



开发要点：

- 订单状态追溯
- 风险二次确认
- 接口可替换
- 异常安全保护



---

## 4.5 Data开发规范


遵循：

07_Data/AQFT_Data_Design_V2.8.6.md



开发要点：

- 数据分层存储
- 来源可追溯
- 质量可验证
- 版本可管理



---

# 第五章 软件接口规范


## 5.1 模块通信原则


模块之间：

通过标准接口通信。


原则：

- 低耦合
- 高内聚
- 接口稳定
- 实现可替换



---

## 5.2 输入输出定义


每个模块：

必须明确定义：

- 输入数据结构
- 输出数据结构
- 异常情况处理



---

## 5.3 数据结构规范


核心数据结构：

统一定义在：


src/schema/


各模块引用统一Schema。


禁止：

各模块自定义相同含义但不同格式的数据结构。



---

## 5.4 API设计原则


- 命名清晰
- 参数明确
- 返回值一致
- 错误处理规范
- 版本兼容



---

# 第六章 配置管理规范


## 6.1 配置文件管理


所有配置：

统一存放在：

config/


格式：

YAML。


分层：

- 默认配置
- 环境配置
- 运行时配置



---

## 6.2 环境变量管理


敏感信息：

通过环境变量管理。


包括：

- 数据库密码
- API密钥
- 交易账户信息


禁止：

在代码中硬编码敏感信息。



---

## 6.3 参数分离原则


代码与参数分离。


运行参数：

归Parameter模块管理。


系统配置：

归Config模块管理。



---

# 第七章 Git版本管理规范


## 7.1 分支模型


采用：

Trunk-Based或GitFlow。


分支类型：

- main — 生产分支
- develop — 开发分支
- feature/* — 功能分支
- release/* — 发布分支
- hotfix/* — 紧急修复分支



---

## 7.2 Commit规范


格式：


<type>: <subject>


类型：

- feat: 新功能
- fix: 修复
- docs: 文档
- refactor: 重构
- test: 测试
- chore: 构建/工具



示例：


feat: add risk evaluation engine
fix: correct position calculation
docs: update architecture document



---

## 7.3 Tag规范


版本Tag：


v<major>.<minor>.<patch>


示例：


v2.8.6
v2.8.7
v3.0.0



---

# 第八章 测试工程规范


## 8.1 单元测试


每个模块：

必须有单元测试。


测试框架：

pytest。



---

## 8.2 集成测试


验证：

模块间接口。



---

## 8.3 自动化测试


CI流程中：

自动运行全部测试。


提交代码前：

必须通过测试。



---

## 8.4 测试覆盖率


目标：

- 核心模块：≥80%
- 风险模块：≥90%
- 执行模块：≥90%



---

# 第九章 CI/CD流程


流程：



代码提交

↓

自动测试

↓

代码检查

↓

构建

↓

部署



---

# 第十章 软件安全规范


## 10.1 密钥管理


所有密钥：

通过环境变量注入。


不在代码中存储。


不在Git中提交。



---

## 10.2 数据安全


- 生产数据隔离
- 敏感数据加密
- 访问权限控制



---

## 10.3 交易安全


- 风险检查不可绕过
- 订单限额强制
- 异常自动熔断



---

# 第十一章 发布管理


## 11.1 Release流程


开发完成

↓

代码审查

↓

测试通过

↓

版本Tag

↓

Release Notes

↓

部署



---

## 11.2 Version管理


遵循：

Semantic Versioning。


Major.Minor.Patch



---

## 11.3 回滚机制


每次发布：

保留上一版本。


异常时：

支持快速回滚。



---

# 第十二章 工程规范冻结声明


本文件定义：

AQF-T软件工程基础规范。


后续：

代码开发；

模块实现；

系统部署；


必须遵守本规范。



Version:

V2.8.6


Status:

Engineering Standard


END OF AQF-T SOFTWARE ENGINEERING STANDARD
