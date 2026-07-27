# AQF-T Limit-Up Microstructure Intelligence Architecture

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2 | Module: 08_Combat_Intelligence
Created: 2026-07-28

---

## 1. Purpose

涨停不是价格事件。涨停是资金行为事件。

AQF-T 当前看到 "price=+10%"。需要看到的是：一字板/换手板/烂板回封/尾盘板/天地板 — 每种含义完全不同。

## 2. Architecture

```
World Model S(t)+B(t)+R(t) + MarketClock + LimitUpState → Decision Intelligence
```

## 3. Five Board Types

| Type | Meaning | Decision Impact |
|------|---------|-----------------|
| 一字板 | 极度强势，无法参与 | 不追，等换手 |
| 换手板 | 健康换手，持续最强 ★ | Leader Candidate |
| 烂板 | 封不住，分歧大 | Risk↑, 次日低开风险 |
| 回封板 | 分歧转一致，质量取决于时间 | 早>午>尾 |
| 天地板 | 极端反转 | Risk Extreme, Exit |

## 4. Key Metrics

SealQuality(封单持续+变化速度+撤单比例), BreakPressure(炸板次数+时间+回封速度), BoardVolume(接力vs出货)

## 5. Integration

Position Health, Failure Library (F006: 高潮接力失败), Decision (Confidence/Risk/Position adjustment)

## 6. Deliverables

```
08_Combat_Intelligence/LimitUp_Intelligence/
├── 01_Architecture/     ← This document
├── 02_Board_Type_Model/
├── 03_OrderFlow_Model/
├── 04_Decision_Interface/
└── 05_Test_Cases/
```

*Phase 2 ★★★★★ A-Share Combat Intelligence.*
