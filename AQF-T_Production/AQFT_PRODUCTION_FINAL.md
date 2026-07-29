# AQF-T Production — 最终完美方案


**Version:** V1.0 Final | **Date:** 2026-07-29
**前置:** V2.8.6设计母库(不动) + 国金QMT + L2数据(已开通)
**定位:** A股游资/个人量化 全自动交易系统

---

## 零、设计来源

```
本方案综合三种视角:

  视角1 (游资):     回封板实战经验, 市场感知, 龙头战法
  视角2 (AI架构):   V2.8.6冻结基线, 四维模型, 宪法治理
  视角3 (工程):     Production精简, 路径分叉, 统一框架
```

---

## 一、最终架构

```
                    Constitution (交易制度)
                         │
                  Market Regime (总开关)
                   每天第一个运行
                  输出: 能不能做? 做多少?
                         │
                       Data
                  QMT L2 + akshare
                         │
              ┌──────────┴──────────┐
              │                     │
          Path A                  Path B
          回封板                   半路/接力
              │                     │
         Perception              ML引擎
              │                     │
      板块地位→炸板分类        B1 Trend (LGBM)
      →回封确认→进场           B2 Theme (规则)
                               B3 Intraday (XGBoost确认)
              │                     │
              └──────────┬──────────┘
                         │
                    Risk (统一审批)
                  APPROVE/ADJUST/REJECT
                         │
                    Execution (QMT)
                         │
                      Review
                   归因→经验→学习
```

## 二、两条赚钱路径

```
Path A — 回封板 (确定性最高, 胜率70-85%)

  漏斗: 涨停池→炸板池→洗盘型判定→回封确认(3标准≥2)→进场

  "不是预测涨停, 是判断资金是否完成重新合力"

  核心变量: 板块地位 / 炸板原因(洗盘vs诱多) / 承接力度
           / 封单恢复速度 / 情绪周期

  不需要LGBM/XGBoost — 微观结构判断比统计模型更准
  用: Perception规则引擎 (V2.8.6 08_Combat_Intelligence)


Path B — 半路/接力 (统计模型)

  B1 Trend:   突破平台+放量+趋势加速 → LGBM三目标预测
  B2 Theme:   龙头涨停, 资金找补涨 → 情绪因子+板块强度
  B3 Intraday: 盘中强势→冲板 → XGBoost L2确认封板概率

  LGBM三目标标签: 机会评分 = 爆发概率 - 风险概率 + 资金认可度
  XGBoost定位: 确认器 (Confirmation Model), 非决策者
```

## 三、两条路的关系

```
共享:
  市场感知 ✅  (Market Regime退潮→两条路都停)
  Risk审批 ✅  (统一限额/熔断/KillSwitch)
  QMT执行 ✅  (同一账户)
  Review复盘 ✅ (分路径统计绩效)

各自:
  信号来源不同 (Perception规则 vs ML统计)
  参数不同 (回封参数 vs Alpha参数)

冲突处理:
  仓位达上限时 Path A > Path B (A确定性更高)
  退潮期两条路都禁止买入
```

## 四、四维模型 (Learning层)

```
LightGBM    → B1 Trend   → 趋势预测 (日K+100因子, 三目标标签)
XGBoost     → B3 + 确认  → L2择时 + 盘口质量确认 (确认器, 非决策者)
Regime引擎  → 总开关     → 情绪周期+梯队+北向 → 所有策略读取
LLM API     → 事件分析   → DeepSeek/Qwen 非结构化文本

不是Ensemble投票, 是Pipeline串联, 各做各的事
```

## 五、全自动交易循环

```
盘中 (9:30-15:00, 每5分钟):

  ① Market Regime: 今天能不能做?
     退潮→全停 | 冰点→仅B2 | 回暖→A+B | 高潮→A+B满仓

  ② 数据更新: QMT L2 + akshare实时

  ③ 涨停池→炸板池:
     Path A: 炸板分类→回封确认→进场(如满足)
     Path B: 异动监控→LGBM→确认→进场(如满足)

  ④ Risk审批: 每条信号→APPROVE/ADJUST/REJECT
     退潮→REJECT全部买入

  ⑤ QMT执行: APPROVE→下单 | REJECT→记录

  ⑥ 成交→Review记录→Experience积累
```

## 六、验证路线

```
Phase 0: 系统冻结 ✅
Phase 1: 离线回测 (B1 LGBM回测, 3年历史)
Phase 2: 模拟盘 (B1先→A后→同时, 1-2月)
Phase 3: 实盘 (≤10万, 人工监督, 两条路对比)
```

## 七、三条铁律

```
1. AI不直接下单 (Learning只提供评分/建议)
2. Risk最高否决权 (Strategy→Risk→Execution硬链不可绕过)
3. 退潮期两条路都禁止买入 (Market Regime总开关)
```

---

**架构冻结。进入工程验证。**
