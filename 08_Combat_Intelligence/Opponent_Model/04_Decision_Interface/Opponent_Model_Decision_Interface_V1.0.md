# AQF-T Opponent Model Decision Interface V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## 1. Decision Input Upgrade

`Decision(S,B,R,Clock,LimitUp) → Decision(S,B,R,Clock,LimitUp,Opponent)`

## 2. Decision Impact Matrix

| Scenario | Conf Δ | Risk Δ | Position Δ | Rationale |
|----------|:------:|:------:|:----------:|-----------|
| Institution Accumulating | +0.05 | −5% | Full | 稳定建仓，短期不砸 |
| Hot Money Relaying | +0.03 | +5% | Normal | 接力进行中 |
| Hot Money Distributing | −0.10 | +15% | −30% | 兑现压力高 |
| Quant Dominant | −0.05 | +10% | −20% | 警惕假突破 |
| Retail Chasing | −0.10 | +10% | −20% | FOMO 追涨 |
| Trap Detected | −0.15 | +20% | −50% | 疑似诱多 |

## 3. Examples

**Institution Accumulating**: conf+0.05, risk−5%, Full position. 机构连续建仓，短期抛压小。

**Hot Money Exiting**: conf−0.10, risk+15%, position−30%. 游资兑现信号。

**Quant + LimitUp**: conf−0.05, risk+10%. 警惕板上量化出货。

## 4. F007 New Failure Pattern

Opponent Misjudgment: 误判机构建仓实为游资对倒 → 错误进入. Constraint: Opponent.confidence < 0.60 → ignore Opponent signal.
