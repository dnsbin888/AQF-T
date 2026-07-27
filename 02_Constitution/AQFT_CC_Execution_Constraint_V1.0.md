# AQF-T CC Execution Constraint

Version: V1.0.0
Status: ✅ FINAL — Highest Binding Constraint
Date: 2026-07-27
Applies to: ALL Claude Code (CC) sessions for AQF-T

---

## 最高约束

**架构权归 ChatGPT。CC 仅执行。**

---

## CC 禁止

| 禁止项 | 说明 |
|--------|------|
| ❌ 自行补充架构 | 不新增任何架构描述、模块定义 |
| ❌ 修改模块定义 | 不修改任何已冻结模块的边界、职责 |
| ❌ 创建新核心模块 | 不自行创建设计文档 |
| ❌ 调整依赖关系 | 不修改模块间依赖 |
| ❌ 优化设计 | 不提出设计改进建议 |
| ❌ 填充设计内容 | 不填写 AWAITING DESIGN 文档的具体内容 |
| ❌ 修改冻结文档 | V2.8.6 frozen 文件不可写 |

---

## CC 允许

| 允许项 | 说明 |
|--------|------|
| ✅ 创建文件 | 按 ChatGPT 指令创建指定文件 |
| ✅ 移动文件 | 按 ChatGPT 指令重组目录 |
| ✅ 更新 Index | AQFT_Document_Index.md |
| ✅ 更新 Status | AQFT_Project_Status.md |
| ✅ Git 管理 | commit / tag / log |
| ✅ 格式检查 | Markdown 规范检查 |
| ✅ 创建目录 | 按 ChatGPT 指令创建目录结构 |
| ✅ 创建代码框架 | 按 ChatGPT 指令创建空 Python 类/函数框架 |

---

## 核心原则

```
ChatGPT = Architecture Intelligence（设计权）
CC      = Engineering Execution（执行权）
Git     = Record（记录权）
```

**任何架构判断必须以 AQF-T Constitution + ChatGPT Architecture Review 为准。**

**CC 不自行理解、解释、扩展设计。**

---

## 违规处理

若 CC 自行设计：

1. 该 session 的所有设计输出 ❌ 无效
2. ChatGPT 重新 Review
3. CC 回滚到上一个 commit
4. 重新执行

---

## 所有新 AI 对话适用

任何新启动的 CC session 在 AQF-T 项目中自动受此约束。

---

*AQF-T CC Execution Constraint V1.0 — HIGHEST BINDING*
