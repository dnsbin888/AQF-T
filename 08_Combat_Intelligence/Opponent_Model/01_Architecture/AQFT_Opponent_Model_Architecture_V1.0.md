# AQF-T Opponent Model Architecture

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2 | Module: 08_Combat_Intelligence
Created: 2026-07-28

---

## 1. Purpose

AQF-T knows WHAT the market is doing. Opponent Model answers: **WHO is driving this?**

价格涨跌是表象。谁在买、为什么买、什么时候卖——这才是 A 股博弈的核心。

## 2. Architecture

```
World Model: S(t)+B(t)+R(t)+Clock+LimitUp + OpponentModel → Decision Intelligence
```

Opponent Model belongs to World Model. It interprets behavior. It does NOT generate trading decisions.

## 3. Five Participant Types

| Type | Style | Holding | Signal |
|------|-------|:------:|--------|
| Institution | Slow, continuous, large | Build→Hold→Distribute | 稳定建仓 |
| Hot Money | Fast, concentrated, emotional | Launch→Relay→Exit | 接力兑现 |
| Quant | Mechanical, reactive | Intraday flip | 高频博弈 |
| Retail | Chasing, panicking | Late entry/exit | 一致性 |
| Mixed | Unclear | — | 无法判断 |

## 4. Key Principle

不是龙虎榜数据库。不依赖具体席位。以行为模式推断为核心。所有输出概率化(confidence, intent_probability, pressure_score)。

## 5. C-012 Candidate

Opponent Model may interpret participant behavior. Shall never generate trading decisions.

## 6. Deliverables

```
08_Combat_Intelligence/Opponent_Model/
├── 01_Architecture/          ← This document
├── 02_Participant_State/
├── 03_Behavior_Inference/
├── 04_Decision_Interface/
└── 05_Test_Cases/
```
