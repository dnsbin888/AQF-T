# AQF-T Quant Footprint Decision Interface V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 2

---

## Design Evidence

| Item | Value |
|------|-------|
| Core Concept | Algorithmic activity → Decision adjustment |
| Evidence Level | B (industry: algo-aware execution) + C (A股经验) |

---

## 1. Decision Input

`Decision(S,B,R,Clock,LimitUp,Opponent,QuantFootprint) → conf/risk/position/execution_style`

## 2. Decision Impact Matrix

| Footprint | Activity | Conf Δ | Risk Δ | Position Δ | Execution Style |
|-----------|:------:|:------:|:------:|:----------:|-----------------|
| F1 Passive Liq | HIGH | +0.03 | −5% | — | LIMIT |
| F2 Momentum Ignition | HIGH | −0.08 | +10% | −20% | TWAP |
| F3 Mean Reversion | HIGH | −0.05 | +5% | −10% | LIMIT |
| F4 Spoofing-like | HIGH | −0.15 | +20% | −50% | WAIT |
| F5 HF Rotation | DOMINANT | −0.05 | +5% | — | TWAP |
| DOMINANT (any) | DOMINANT | −0.10 | +15% | −30% | TWAP |

## 3. Opponent + Footprint Fusion

Institution.conf=0.82 + QuantFootprint=DOMINANT(0.91) → "Institution可能, 但算法主导" → conf−0.05, risk+10%.

## 4. Examples

**Momentum Ignition HIGH**: conf−0.08, risk+10%, pos−20%, TWAP. 算法在推动突破，谨慎追入.

**Spoofing-like HIGH**: conf−0.15, risk+20%, pos−50%, WAIT. 疑似诱导行为，暂停交易.
