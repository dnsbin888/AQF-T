# AQFT Version Control


# AQF-T版本控制体系


Version:

V2.8.6


Status:

Project Management


Classification:

AQF-T版本治理规范文件


Date:

2026-07-26


---

# 第一章 版本管理目标


## 1.1 管理目标


保证：

- 版本唯一
- 变更可追踪
- 历史可回溯
- 发布可控制



---

# 第二章 版本体系


## 2.1 版本格式


采用：

Semantic Versioning


格式：

Major.Minor.Patch


例如：

V2.8.6



---

## 2.2 版本号含义


Major（主版本）：

重大架构变化。


Minor（次版本）：

新增能力。


Patch（修订版本）：

Bug修复与优化。



---

# 第三章 AQF-T版本阶段


## 3.1 当前版本


V2.8.6


状态：

Architecture Frozen



---

## 3.2 未来版本


V2.9.x


Engineering Development


V3.0.0


Production System



---

# 第四章 版本发布流程


## 4.1 发布流程


开发

↓

测试

↓

审核

↓

Tag

↓

Release

↓

部署



---

## 4.2 Tag规范


格式：


v<major>.<minor>.<patch>


示例：


v2.8.6
v2.8.7
v3.0.0



---

# 第五章 Git版本管理


## 5.1 分支模型


Branch：

- main — 生产分支
- develop — 开发分支
- feature/* — 功能分支
- release/* — 发布分支
- hotfix/* — 紧急修复分支



---

## 5.2 Commit规范


格式：


<type>: <subject>



类型：

- feat — 新功能
- fix — 修复
- docs — 文档
- refactor — 重构
- test — 测试
- chore — 构建/工具



---

# 第六章 变更管理


## 6.1 变更记录


所有变化必须记录：

- 修改内容
- 修改原因
- 修改人员
- 影响范围



---

## 6.2 重大变更


架构或核心逻辑变更：

必须：

- 设计评审
- 影响评估
- 测试验证
- 审批确认



---

# 第七章 回滚机制


## 7.1 版本保留


任何正式版本：

必须：

保留历史版本。



---

## 7.2 快速恢复


异常时：

支持快速回滚至上一稳定版本。



---

# 第八章 版本冻结原则


## 8.1 冻结版本


已冻结版本：

禁止随意修改。


任何修改必须：

评估 → 测试 → 批准。



---

## 8.2 历史保护


所有历史版本：

永久保存。


不得删除。



---

END OF AQFT VERSION CONTROL
