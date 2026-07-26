# AQFT Human-AI Collaborative Governance Design V3.6.0


# AQF-T 人机协同治理系统详细设计


Version: V3.6.0 | Status: Detailed Engineering Design
Date: 2026-07-26

> 参考: 2025 HITL Best Practices / Kensho 4原则 / NexTrade审批网关 / 三Agent合规框架 / Delegation Frontier


---

# 第一章 HITL 架构原则


借鉴 2025 年行业共识:

```
原则1: HITL是正式状态转换, 不是事后补丁
原则2: 生成Agent ≠ 验证Agent (分离关注点)
原则3: 纵深防御, 不是单一检查点
原则4: 全过程可审计, 每条决策有追溯
原则5: AI始终可中断, 可完全回退到人工
```

---

# 第二章 六级自主权限 (Delegation Frontier)


借鉴 Delegation Frontier 框架:

| 等级 | 模式 | 适用场景 | 示例 |
|:---:|------|---------|------|
| L0 | Human Only | Kill Switch恢复/极端行情 | 需要完全人工控制 |
| L1 | AI Suggestion | 盘后分析/复盘 | AI建议, 仅供参考 |
| L2 | Human Approve | 重要交易决策 | Dragon Strategy > 5%仓位 |
| L3 | Conditional Auto | 普通调仓 | 风控框架内自动执行 |
| L4 | Autonomous+Monitor | 量化执行 | Market Order, 人工后台监控 |
| L5 | Full Autonomous | 暂不启用 | AQF-T V4.0目标 |

游资默认: **L2** (AI建议+人工审批)。重要决策不自动执行。

---

# 第三章 纵深防御 (5层)


借鉴 2025 Defense-in-Depth 模式:

```
Layer 1: Input Guard
  防提示注入 / 长度校验 / 敏感词过滤

Layer 2: Governance Rules Engine
  编译自然语言策略 → 时序逻辑约束(LTL/CTL)
  例: "退潮期禁止BUY" → 运行时自动拦截

Layer 3: Critic Agent (验证)
  独立于生成Agent: 生成Agent提方案 → Critic Agent审合规
  借鉴三Agent框架: Human+Claude+GPT4, 领域约束嵌入策略生成

Layer 4: Human Approval Gate
  正式阻塞状态转换。执行必须获取显式审批Token
  借鉴 NexTrade: intent formulation → approval → execution

Layer 5: Risk Guard + Compliance Logger
  确定性风控(仓位/止损) + 结构化审计日志
```

---

# 第四章 审批工作流


借鉴 NexTrade 审批网关模式:

```
AI Decision Engine → 生成 TradingSignal
       │
       ▼
  Critic Agent 验证 (Layer 3)
       │ 通过
       ▼
  人工审批界面:
    信号详情 + AI推理链 + 风险评估 + 历史类似案例
       │
       ├── APPROVE → Execution
       ├── REJECT  → 记录原因 + 反馈给AI
       └── MODIFY  → 修改参数后重新提交
```

---

# 第五章 审计日志


借鉴 2025 合规标准:

```
AuditRecord (JSON, UTC时间戳):
  timestamp: 审批时间
  user_id: 审批人
  session_id: 会话ID
  decision_id: AI决策ID
  ai_recommendation: AI建议
  human_decision: APPROVE/REJECT/MODIFY
  override_reason: (如修改)原因
  risk_context: 审批时的风险评估快照
```

满足: MiFID II(交易报告) + 数据保护 + 金融内控要求。

---

# 第六章 可解释性


借鉴 Kensho(S&P Global) 4原则:

```
透明操作: AI必须通过步骤化推理展示决策过程
共享上下文: AI与人类使用相同工具和数据源
完全控制权: 人类可以撤销/修改/回退任何AI操作
无干扰存在: AI融入自然工作流, 不制造噪音
```

游资审批界面设计:
```
┌──────────────────────────────────────┐
│ AQF-T 交易审批                        │
│                                      │
│ AI建议: BUY SH.600519 200股           │
│ 策略: Dragon Strategy (龙头战法)      │
│ 置信度: 82%                          │
│                                      │
│ 推理链:                              │
│  ① 情绪周期: 回暖期                    │
│  ② 题材热度: AI产业链 0.82            │
│  ③ 龙头判定: 连板3+题材涨停7+封单5%    │
│  ④ 风险评估: Score=25 APPROVE        │
│                                      │
│ 历史类似: 2023 AI行情(胜率68%)         │
│                                      │
│ [APPROVE]  [REJECT]  [MODIFY]       │
└──────────────────────────────────────┘
```

---

# 第七章 分阶段部署


借鉴 2025 "Small Wins" 方法:

```
Phase 1 (当前): Retrieval — 盘后分析/复盘/建议
Phase 2: Judgment — 信号生成 + 人工审批
Phase 3: Autonomy — L3/L4条件自动 + 持续监控
```

不可跳阶段。

---

# 第八章 API


| 端点 | 方法 | 功能 |
|------|:---:|------|
| POST /governance/approval/request | POST | 提交审批 |
| POST /governance/approval/{id}/decide | POST | 审批决定 |
| GET /governance/audit/log | GET | 审计日志 |
| GET /governance/dashboard | GET | 治理看板 |
| POST /governance/override | POST | 紧急人工干预 |

---

# 第九章 设计冻结声明


本文件定义 AQF-T Human-AI Governance V3.6.0。

借鉴 2025 HITL Best Practices / Kensho 4原则 / NexTrade审批网关 / 三Agent合规框架 / Delegation Frontier。

核心: AI建议, 人类决策, 系统约束, 全过程可审计。

Version: V3.6.0 | Status: Detailed Engineering Design
END OF AQFT HUMAN-AI COLLABORATIVE GOVERNANCE DESIGN
