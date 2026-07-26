# AQFT Parameter Design V3.6.0


# AQF-T 参数治理体系详细设计


Version: V3.6.0
Status: Detailed Engineering Design
Classification: AQF-T 参数治理核心设计文件
Date: 2026-07-26


---

# 第一章 参数治理定位


Parameter 模块是 AQF-T 系统所有可调变量的管理中心。确保参数变更可追溯、可回滚、可审计。

```
Parameter Center → AI/Strategy/Risk/Execution 各模块读取 → 运行时使用
                   ↑
              参数变更: 评估→测试→审批→发布→监控
```

---

# 第二章 参数分类体系


## 2.1 AI模型参数

| 参数 | 默认值 | 范围 | 说明 |
|------|:---:|------|------|
| prediction_confidence_threshold | 0.65 | 0.50-0.90 | 预测置信度最低阈值 |
| fusion_prediction_weight | 0.30 | 0.10-0.50 | Prediction在Fusion中的权重 |
| fusion_sentiment_weight | 0.30 | 0.10-0.50 | Sentiment在Fusion中的权重 |
| fusion_risk_weight | 0.25 | 0.10-0.40 | Risk在Fusion中的权重 |
| fusion_experience_weight | 0.15 | 0.05-0.30 | Experience在Fusion中的权重 |
| model_retrain_interval_days | 30 | 7-90 | 模型重训练间隔 |
| drift_warning_threshold | 0.10 | 0.05-0.20 | 模型漂移告警阈值 |

## 2.2 Strategy 参数

| 参数 | 默认值 | 范围 | 适用策略 | 说明 |
|------|:---:|------|---------|------|
| ma_short | 5 | 3-10 | Trend | 短期均线 |
| ma_long | 20 | 10-60 | Trend | 长期均线 |
| volume_ratio_threshold | 1.5 | 1.2-3.0 | Volume-Price | 放量倍数 |
| consecutive_boards_min | 3 | 2-5 | Dragon | 龙头最低连板 |
| seal_amount_ratio | 0.05 | 0.03-0.10 | Dragon | 封单/流通市值 |
| gap_up_min | 0.03 | 0.01-0.05 | Dragon | 竞价高开最小 |
| gap_up_max | 0.07 | 0.05-0.09 | Dragon | 竞价高开最大 |
|炸板_exit_minutes | 10 | 5-20 | Dragon | 炸板后等待 |
| n_reversal_days | 4 | 2-7 | Volume-Price | N字反包观察天数 |
| stop_loss_pct | -0.05 | -0.03~-0.08 | ALL | 硬止损比例 |
| take_profit_pct | 0.15 | 0.08-0.30 | ALL | 止盈比例 |

## 2.3 Risk 参数

| 参数 | 默认值 | 范围 | 说明 |
|------|:---:|------|------|
| max_total_position | 0.70 | 0.20-0.80 | 总仓位上限 |
| max_single_position | 0.20 | 0.10-0.25 | 单票仓位上限 |
| max_dragon_position | 0.15 | 0.05-0.20 | Dragon单票上限 |
| max_daily_loss | -0.02 | -0.01~-0.05 | 日内亏损熔断 |
| max_monthly_drawdown | -0.10 | -0.05~-0.15 | 月度回撤熔断 |
| max_total_drawdown | -0.20 | -0.10~-0.30 | 总回撤熔断 |
| max_consecutive_losses | 5 | 3-10 | 连续亏损暂停 |
| sentiment_ice_exposure | 0.20 | 0.10-0.30 | 冰点期仓位上限 |
| sentiment_recession_exposure | 0.20 | 0.00-0.20 | 退潮期仓位上限 |
| risk_score_medium_threshold | 30 | 20-40 | 中风险阈值 |
| risk_score_high_threshold | 55 | 45-65 | 高风险阈值 |
| risk_score_extreme_threshold | 75 | 65-85 | 极端风险阈值 |

## 2.4 Execution 参数

| 参数 | 默认值 | 范围 | 说明 |
|------|:---:|------|------|
| order_timeout_seconds | 30 | 15-60 | 市价单超时 |
| max_slippage_bps | 50 | 20-100 | 最大滑点(基点) |
| partial_fill_timeout_minutes | 15 | 5-30 | 部分成交等待 |
| max_retry_count | 3 | 1-5 | 最大重试次数 |
| reconnect_interval_seconds | 5 | 2-15 | Broker重连间隔 |

---

# 第三章 参数生命周期


## 3.1 状态机

```
DRAFT → TESTING → APPROVED → ACTIVE → DEPRECATED → ARCHIVED
                  │                      │
                  └→ REJECTED            └→ ROLLED_BACK
```

## 3.2 各状态说明

| 状态 | 说明 | 可用范围 |
|------|------|---------|
| DRAFT | 参数提案, 尚未测试 | 不可用 |
| TESTING | 在回测/模拟环境中验证 | 仅模拟环境 |
| APPROVED | 审批通过, 待发布 | 待切换 |
| ACTIVE | 当前生产运行参数 | 生产环境 |
| DEPRECATED | 被新版本替代, 但仍可回滚 | 仅回滚 |
| ARCHIVED | 历史归档 | 不可用 |
| ROLLED_BACK | 从ACTIVE回滚到旧版本 | — |
| REJECTED | 测试或审批不通过 | 不可用 |

---

# 第四章 参数变更管理


## 4.1 变更流程

```
提出变更 → 影响评估 → 回测验证 → 模拟交易验证 → 审批 → 发布 → 监控
```

## 4.2 变更记录

```
ParameterChange:
  change_id: str
  parameter_name: str
  old_value: any
  new_value: any
  reason: str
  backtest_result: dict        # {sharpe_before, sharpe_after, drawdown_before, drawdown_after}
  simulation_result: dict
  risk_impact: Low | Medium | High
  approver: str
  changed_at: datetime
  status: APPROVED | REJECTED | ROLLED_BACK
```

## 4.3 审批分级

```
风险影响 Low:
  - Strategy参数微调 (阈值±10%以内)
  - Execution参数调整
  → 自动审批

风险影响 Medium:
  - Strategy参数大幅调整 (>20%)
  - Risk参数微调
  → 人工审批

风险影响 High:
  - Risk核心参数 (max_total_position / max_drawdown / stop_loss_pct)
  - AI模型权重调整
  → 人工审批 + Risk Constitution检查
```

---

# 第五章 参数版本管理


## 5.1 版本化要求

```
所有参数变更必须记录:
  - 参数名 + 版本号
  - 参数值
  - 生效时间
  - 变更人
  - 变更原因
  - 测试结果
```

## 5.2 回滚机制

```
ACTIVE参数异常 → 自动/手动触发回滚 → 恢复到上一个ACTIVE版本

触发条件:
  - 发布后30分钟内: 回撤 > 正常水平2倍 → 自动回滚
  - 发布后24小时内: 胜率下降 > 20% → 建议回滚
  - 人工判断异常 → 手动回滚
```

## 5.3 参数快照

```
每个交易日开盘前自动保存当前所有ACTIVE参数快照:
  ParameterSnapshot:
    date: 2026-07-26
    parameters: {name: {value, version}}
    created_by: auto_daily
```

---

# 第六章 参数优化集成


## 6.1 与 Auto Optimization (P4-02) 集成

```
Auto Optimization 输出候选参数 → Parameter Center 接收 → 创建DRAFT → TESTING → 审批 → ACTIVE
```

## 6.2 优化约束

```
参数优化必须遵守:
  - 安全边界: Risk核心参数不得突破 Risk Constitution
  - 回测验证: 至少3段不同周期样本外测试
  - 模拟验证: ≥ 1个月Paper Trading
  - 渐变原则: 高风险参数一次调整幅度 ≤ 20%
```

---

# 第七章 参数安全


## 7.1 禁止事项

```
- 未经测试的参数直接进入ACTIVE
- Risk核心参数被自动修改
- 参数历史版本被删除
- 生产环境参数被直接修改(必须走变更流程)
```

## 7.2 紧急修改

```
紧急情况(市场极端波动等)下:
  - 允许临时覆盖 Risk 参数(提高风险阈值)
  - 必须人工操作 + 双人确认
  - 临时覆盖有时间限制(最多24小时)
  - 自动记录 + 事后审计
```

---

# 第八章 接口设计


| 端点 | 方法 | 功能 |
|------|:---:|------|
| /parameter/list | GET | 所有参数及当前值 |
| /parameter/{name} | GET | 单个参数详情 |
| /parameter/{name}/history | GET | 参数变更历史 |
| /parameter/{name}/propose | POST | 提出参数变更 |
| /parameter/{name}/approve | POST | 审批参数变更 |
| /parameter/{name}/rollback | POST | 回滚参数 |
| /parameter/snapshot | GET | 今日参数快照 |
| /parameter/snapshot/{date} | GET | 历史参数快照 |

---

# 第九章 设计冻结声明


本文件定义 AQF-T Parameter V3.6.0 详细设计。

覆盖 AI/Strategy/Risk/Execution 四大类 30+ 参数。参数变更流程: 提出→评估→回测→模拟→审批→发布→监控。

高风险参数变更需人工审批 + Risk Constitution 检查。

Version: V3.6.0
Status: Detailed Engineering Design
END OF AQFT PARAMETER DESIGN
