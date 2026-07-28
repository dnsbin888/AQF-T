# Market Perception — 市场感知模块 (游资核心)


**来源:** V2.8.6 08_Combat_Intelligence (冻结资产) + Production 补齐

---

## 感知体系全景

```
竞价感知 ──→ 梯队感知 ──→ 板型感知 ──→ 对手感知 ──→ 足迹感知 ──→ 合力感知
 9:15-25      盘中实时      封板时        持续          持续         多信号共振
```

---

## 一、竞价感知 (9:15-9:25) — Production 新增

```
← V2.8.6 07_Data: AuctionData Schema (字段已定义)

竞价分析维度:
  9:15-9:20 试撮合阶段 (可撤单, 虚假信号多)
  9:20-9:25 不可撤单阶段 (真实意图)

  竞价信号:
    封单变化: 9:20后封单稳定或增加 → 真实强势
             9:20后封单骤降 → 诱多, 开盘可能回落
    量能: 竞价成交量 > 昨日同时段2倍 → 资金关注
    价格: 高开3-7% → 最佳接力区间
          高开>7% → 追高风险
          低开>3% → 弱势

  竞价输出:
    auction_strength: 0-1      竞价强度
    is_trap_risk: bool         诱多风险
    recommended_action: WAIT|READY|CAUTION
```

## 二、涨停梯队感知 — Production 新增

```
实时计算:
  涨停梯队:
    首板数量 / 二板数量 / 三板数量 / 四板数量 / 五板+数量

  梯队健康度:
    金字塔型 (首板多→高标少) → 健康, 接力生态好
    倒金字塔 (高标多→首板少) → 危险, 后继无力
    断层 (某档为0) → 情绪断裂

  晋级率:
    首板→二板晋级率 > 30% → 情绪强
    首板→二板晋级率 < 15% → 情绪弱

  龙头识别:
    全市场最高连板 → 总龙头
    题材内最高连板 → 题材龙头
```

## 三、板型感知 — V2.8.6 08_Combat (已有, 直接引用)

```
← LimitUp_Intelligence/02_Board_Type_Model

五种板型:
  一字板   Seal=0.99  Turnover<1%   → Wait for volume
  换手板   Seal=0.80+ Turnover5-15% → Leader Candidate ★
  烂板     Seal<0.60  Turnover>20%  → Risk↑, avoid
  回封板   Seal=0.70+ Turnover10-20% → Conditional (早>午>尾)
  天地板   Seal=0.00  Turnover>25%  → Risk Extreme

SealQuality = 封单持续性×0.40 + 封单变化稳定性×0.35 + 撤单低比例×0.25

← LimitUp_Intelligence/03_OrderFlow_Model

板上资金行为:
  缩量封板 → Bullish (卖盘枯竭, 持仓者惜售)
  放量封板 → Neutral (资金交换, 观察方向)
  放量炸板 → Bearish (派发, 有人在出货)

封单轨迹:
  递增 → Strong (接力资金持续进场)
  稳定 → Normal
  衰减 → Warning (撤单或抛压增加)
  骤降 → Critical (可能炸板)

BreakPressure = 炸板次数×0.40 + 炸板深度×0.30 + 回封耗时×0.30
  Score > 0.70 → High risk
```

## 四、对手感知 — V2.8.6 08_Combat (已有, 直接引用)

```
← Opponent_Model/02_Participant_State

五种参与者:
  Institution  大资金/慢速/数周-数月 → Build→Hold→Distribute
  Hot Money    中等/快速/1-5天      → Launch→Relay→Exit
  Quant        不定/超快/日内        → 机械翻转
  Retail       小/滞后/不定          → 追涨/恐慌
  Mixed        无法判断               → Unknown

ParticipantState 对象:
  dominant_participant: Hot_Money (confidence 0.78)
  intent: Relay (intent_probability 0.72)
  expected_action: Continue_Holding
  opponent_pressure: {buy:65, sell:35, continuation:0.68, trap:0.12}

意图状态: Accumulating | Holding | Rotating | Distributing | Panic_Selling
每个意图附带 probability (never 1.0)

关键原则 (C-012边界宪法):
  对手模型可解读参与者行为, 但不可直接生成交易决策
```

## 五、量化足迹感知 — V2.8.6 08_Combat (已有, 直接引用)

```
← Quant_Footprint/01_Architecture

五种算法模式:
  F1 Passive Liquidity    双边挂单, 点差维持  → Risk↓
  F2 Momentum Ignition    连续追价, 放大波动  → 追高风险↑
  F3 Mean Reversion       快速反向, 拉高即卖  → 突破持续性↓
  F4 Spoofing-like        挂单-撤单模式       → Trap↑ (Hypothesis only)
  F5 HF Rotation          大量小单, 快速换手  → Noise↑

活跃度: NONE → LOW → MEDIUM → HIGH → DOMINANT

关键原则 (C-013边界宪法):
  可推断算法模式, 不可声称识别具体机构/账户/非法活动
```

## 六、资金合力感知 — Production 新增

```
多维度共振检测:

  合力信号 (3个以上维度同时指向同一方向 → 强信号):
    维度1: 板型 = 换手板 (Leader Candidate)
    维度2: 对手 = Hot Money + Intent=Relay
    维度3: 足迹 = F1/F2 (非Spoofing)
    维度4: 封单轨迹 = 递增 or 稳定
    维度5: 板上量 = 缩量封板 (Bullish)

  合力指数 = 满足维度数 / 5
    ≥ 0.8 → Strong合力 (跟!)
    0.6 → Moderate (观察)
    < 0.4 → Weak or Trap (回避)
```

## 七、情绪拐点预警 — Production 新增

```
拐点信号 (高潮→退潮转折):

  预警信号 (≥2触发 → 降仓):
    炸板率 从<20% 骤升至>40%
    连板高度 从≥7 骤降至≤4
    涨停家数 从前日>80 骤降至<50
    天地板出现 (任何一只)
    龙头炸板 (总龙头开板)
    题材涨停家数 从前日>10 骤降至<5

  拐点确认:
    连续2天满足≥2预警信号 → 确认进入退潮期
    触发: 仓位强制降至20%, 禁止所有买入
```

## 八、集成到决策 Pipeline

```
完整五维决策:

  Perception(六层感知) → Alpha(LGBM) → Timing(XGBoost) → Regime(情绪) → Event(LLM)

Perception 输出 MarketPerception:
  auction:        竞价强度 + 诱多风险
  ladder:         涨停梯队 + 晋级率 + 龙头
  board:          板型 + 封单质量 + 炸板压力
  opponent:       主导参与者 + 意图 + 对手压力
  footprint:      算法模式 + 活跃度
  convergence:    资金合力指数
  inflection:     情绪拐点预警

影响:
  → Dragon入场模式: 换手板→二板接力 / 一字板→等换手再进
  → 仓位调节: 合力强→满仓 / 足迹F4→降仓 / 拐点预警→强制降
  → Risk Score: 烂板+30 / 天地板+50 / Spoofing+30
```

## 九、引用来源

```
V2.8.6 冻结资产 (直接引用):
  08_Combat_Intelligence/LimitUp_Intelligence/      (5种板型+封单+订单流)
  08_Combat_Intelligence/Opponent_Model/            (5种参与者+意图)
  08_Combat_Intelligence/Quant_Footprint/           (5种足迹+活跃度)
  07_Data/AQFT_Data_Design_V2.8.6.md               (AuctionData Schema)

Production 补齐:
  竞价感知 / 涨停梯队 / 合力检测 / 情绪拐点预警
```
