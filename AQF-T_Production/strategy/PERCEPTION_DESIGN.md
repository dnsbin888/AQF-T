# Market Perception — 市场感知模块 (游资核心)


**来源:** V2.8.6 08_Combat_Intelligence (冻结资产, 直接引用)

---

## 三层感知体系

```
Layer 1: 涨停智能 (LimitUp Intelligence)
  ← 08_Combat_Intelligence/LimitUp_Intelligence

  五种板型识别:
    一字板  极度强势, 无法参与 → 不追, 等换手
    换手板  健康换手, 持续最强 ★ → Leader Candidate
    烂板    封不住, 分歧大 → Risk↑, 次日低开
    回封板  分歧转一致, 早>午>尾
    天地板  极端反转 → Risk Extreme, Exit

  封板质量: SealQuality (封单持续+变化速度+撤单比例)
  炸板压力: BreakPressure (炸板次数+时间+回封速度)
  板量分析: BoardVolume (接力vs出货判断)

Layer 2: 对手建模 (Opponent Model)
  ← 08_Combat_Intelligence/Opponent_Model

  五种参与者识别:
    Institution 机构 — 缓慢/持续/大量 → 稳定建仓
    Hot Money   游资 — 快速/集中/情绪 → 接力兑现
    Quant       量化 — 机械/反应性 → 日内翻转
    Retail      散户 — 追涨/恐慌 → 一致性
    Mixed       混合 — 无法判断 → Unknown

  关键原则:
    不是龙虎榜数据库, 不依赖具体席位
    行为模式推断, 所有输出概率化
    证据链: Large Order Ratio/VWAP/Holding Time/龙虎榜/盘口

Layer 3: 量化足迹 (Quant Footprint)
  ← 08_Combat_Intelligence/Quant_Footprint

  五种算法模式:
    F1 Passive Liquidity    双边挂单 → Risk↓
    F2 Momentum Ignition    连续追价 → 追高风险↑
    F3 Mean Reversion       快速反向 → 突破持续性↓
    F4 Spoofing-like        挂单-撤单 → Trap↑
    F5 HF Rotation          大量小单 → Noise↑

  活跃度: NONE → LOW → MEDIUM → HIGH → DOMINANT
```

## 感知输出

```
MarketPerception:

  limit_up_analysis:       ← Layer 1
    board_type: 一字板|换手板|烂板|回封板|天地板
    seal_quality: 0-1
    break_pressure: 0-1
    is_leader_candidate: bool

  opponent_analysis:       ← Layer 2
    dominant_type: Institution|HotMoney|Quant|Retail|Mixed
    intent_confidence: 0-1
    pressure_score: 0-1

  quant_footprint:         ← Layer 3
    footprint_type: F1|F2|F3|F4|F5
    activity_level: NONE|LOW|MEDIUM|HIGH|DOMINANT
    risk_impact: LOW|MEDIUM|HIGH|EXTREME
```

## 集成到决策 Pipeline

```
原四维:
  Alpha(LGBM) → Timing(XGBoost) → Regime(情绪) → Event(LLM)

加入感知:
  Perception(三层) → Alpha(LGBM) → Timing(XGBoost) → Regime → Event

Perception 作用:
  - 识别板型 → 影响 Dragon 策略的入场模式选择
  - 识别对手 → 影响仓位 (游资接力→可跟, 量化主导→回避)
  - 识别足迹 → 影响 Risk Score (F4 Spoofing → Risk+30)
```

## 引用来源

```
V2.8.6 冻结资产 (直接引用, 不重写):

  08_Combat_Intelligence/LimitUp_Intelligence/
    01_Architecture (5种板型)
    02_Board_Type_Model
    03_OrderFlow_Model
    04_Decision_Interface

  08_Combat_Intelligence/Opponent_Model/
    01_Architecture (5种参与者)
    02_Participant_State
    03_Behavior_Inference

  08_Combat_Intelligence/Quant_Footprint/
    01_Architecture (5种足迹)
    02_Footprint_State
    03_Inference_Engine
```
