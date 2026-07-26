# AQFT Risk Runtime Design V3.6.0


# AQF-T 风控运行系统详细设计


Version: V3.6.0 | Status: Detailed Engineering Design
Date: 2026-07-26

> 参考: FIA 2024 Automated Trading Risk Controls + Alpha Arena 3-Tier Escalation + ml4t/live SafeBroker


---

# 第一章 四层纵深防御 (Defense-in-Depth)


借鉴 FIA 2024 最佳实践，AQF-T Risk Runtime 采用四层独立风控:

```
Layer 1: Pre-Trade (下单前) → 限额检查 → 通过/拒绝
Layer 2: Real-Time (实时) → NAV/回撤/风险评分 → 降仓/熔断
Layer 3: Kill Switch (紧急) → 系统级停止 → 撤单+停策略
Layer 4: Post-Trade (盘后) → 审计/合规/报告
```

## 1.1 Layer 1: Pre-Trade 实时门控

借鉴 ml4t/live SafeBroker 模式。每个订单在提交前强制执行:

```
✅ 单笔上限 (fat-finger): max_order_value, max_order_shares
✅ 价格偏离: max_price_deviation_pct (防误操作)
✅ 数据新鲜度: max_data_staleness_seconds (防过期数据)
✅ 频率限制: max_orders_per_minute
✅ 仓位上限: max_position_value, max_total_exposure
✅ 并发仓位: max_positions
✅ T+1 限制 (A股特有)
✅ 涨跌停限制 (A股特有)
```

## 1.2 Layer 2: Real-Time 监控

```
每10秒扫描:
  - NAV计算 (当前权益 vs 峰值权益)
  - Drawdown监控 (当前回撤 vs 阈值)
  - 日亏损累计 (当日盈亏 vs max_daily_loss)
  - 风险评分更新 (Risk Score公式)

触发动作:
  Tier 0: DD < 5% → 仅监控
  Tier 1: DD ≥ 5% → 强制平仓该策略 + 暂停该策略
  Tier 2: DD ≥ 10% → 系统级熔断
```

## 1.3 Layer 3: Kill Switch

```
激活条件:
  - DD ≥ 10% (自动)
  - 日亏损 ≥ 5% (自动)
  - 连续5笔亏损 (自动)
  - 手动触发

执行:
  ① 撤销所有未成交订单
  ② 停止所有策略
  ③ 市价清仓所有持仓
  ④ 断开Broker下单通道
  ⑤ 通知发出
  ⑥ 状态持久化(重启后仍保持)

恢复: 必须人工确认 + 最低冷却30分钟
```

## 1.4 Layer 4: Post-Trade

```
每日盘后:
  ✅ 订单对账 (信号→订单→成交)
  ✅ 风控日志审计
  ✅ 限额合规检查
  ✅ 生成风控日报
```

---

# 第二章 状态持久化 (借鉴 SafeBroker)


风控状态必须跨重启持久化:

```
RiskState (持久化到数据文件):
  trading_date: 当前交易日
  session_start_equity: 当日初始权益
  daily_pnl: 当日累计盈亏
  peak_nav: 历史峰值NAV
  kill_switch_active: bool
  kill_switch_reason: str
  active_positions: snapshot
  pending_orders: snapshot

启动恢复:
  加载RiskState → 对账 → 不一致 → fail_on_reconciliation_mismatch → 人工介入
```

---

# 第三章 Shadow Mode (推荐部署模式)


借鉴行业最佳实践。首次部署必须先进入 Shadow Mode:

```
Shadow Mode:
  ✅ 所有风控检查完整运行
  ✅ 订单标记为虚拟成交 (不提交真实Broker)
  ✅ VirtualPortfolio 本地跟踪持仓/资金
  ✅ 零资金风险

退出条件:
  Shadow Mode ≥ 1个月 + 无风控逻辑bug + 人工审批
```

---

# 第四章 API


| 端点 | 方法 | 功能 |
|------|:---:|------|
| POST /risk/check | POST | Pre-Trade检查 |
| GET /risk/status | GET | 实时风控状态 |
| POST /risk/kill_switch | POST | 手动触发Kill Switch |
| POST /risk/kill_switch/clear | POST | 清除Kill Switch(需授权) |
| GET /risk/report/daily | GET | 风控日报 |
| GET /risk/report/reconciliation | GET | 对账报告 |

---

# 第五章 设计冻结声明


本文件定义 AQF-T Risk Runtime V3.6.0。借鉴 FIA 2024 四层纵深防御 + Alpha Arena 三级升级 + SafeBroker 状态持久化 + Shadow Mode 部署模式。

Version: V3.6.0 | Status: Detailed Engineering Design
END OF AQFT RISK RUNTIME DESIGN
