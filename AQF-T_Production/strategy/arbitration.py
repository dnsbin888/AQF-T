"""
Hypothesis Arbitration — 多信号冲突裁决
← V2.8.6 08_Combat_Intelligence/Hypothesis_Arbitration

不是投票。是证据加权融合。
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ArbitrationResult:
    action: str                    # BUY / HOLD / SELL
    confidence: float              # 0-1
    position_pct: float            # 建议仓位
    consistency: float             # 信号一致性
    mode: str                      # full / conservative / wait / no_decision
    reason: str


class HypothesisArbitrator:
    """
    多信号冲突裁决 — V2.8.6 C-014边界宪法

    不是辩论, 是认知仲裁。
    融合多条证据, 不解生成新假设。
    """

    # 证据等级权重 (C-014)
    EVIDENCE_WEIGHTS = {
        "A+": 0.50,  # 最高: 回封确认(高质量)
        "A":  0.30,  # 高: Perception判断
        "B":  0.15,  # 中: LGBM统计模型
        "C":  0.05,  # 低: 经验规则
    }

    def arbitrate(self, signals: dict) -> ArbitrationResult:
        """
        四条证据输入:
          perception:  {action, confidence, evidence_level}
          alpha_lgbm:  {action, confidence, evidence_level}
          timing_xgb:  {action, confidence, evidence_level}
          regime:      {operation_mode, max_position}
        """
        # ── Stage 1: 收集证据 ──
        evidence = []
        for name, sig in signals.items():
            if sig and sig.get("confidence", 0) > 0.5:
                evidence.append({
                    "source": name,
                    "action": sig["action"],
                    "confidence": sig["confidence"],
                    "weight": self.EVIDENCE_WEIGHTS.get(sig.get("evidence_level", "C"), 0.05),
                })

        if not evidence:
            return ArbitrationResult("HOLD", 0.0, 0.0, 0.0, "no_decision",
                                     "所有信号置信度不足")

        # ── Stage 2: 一致性检查 ──
        actions = [e["action"] for e in evidence]
        buys = sum(1 for a in actions if a == "BUY")
        sells = sum(1 for a in actions if a == "SELL")
        holds = sum(1 for a in actions if a == "HOLD")

        total = len(evidence)
        if buys == total:
            consistency = 1.0
        elif sells == total:
            consistency = 1.0
        elif buys > 0 and sells > 0:
            consistency = 0.0   # 方向冲突
        else:
            consistency = max(buys, sells, holds) / total

        # ── Stage 3: 冲突裁决 ──
        regime_mode = signals.get("regime", {}).get("operation_mode", "normal")
        max_pos = signals.get("regime", {}).get("max_position_pct", 0.5)

        if consistency >= 0.9:
            # 全票通过 → 全仓
            action = actions[0]
            weighted_conf = sum(e["confidence"] * e["weight"] for e in evidence)
            position = max_pos
            mode = "full"
            reason = f"全票通过({total}/{total}), 一致性={consistency:.1f}"

        elif consistency >= 0.6:
            # 多数支持 → 半仓
            action = max(set(actions), key=actions.count)
            weighted_conf = sum(e["confidence"] * e["weight"] for e in evidence) * 0.7
            position = max_pos * 0.5
            mode = "conservative"
            reason = f"多数支持({buys}B/{sells}S/{holds}H), 降半仓"

        elif consistency >= 0.3:
            # 有分歧 → 轻仓或等待
            if buys > sells:
                action = "HOLD"
                weighted_conf = 0.3
                position = max_pos * 0.15
                mode = "wait"
                reason = f"分歧({buys}B/{sells}S/{holds}H), 轻仓试错"
            else:
                action = "HOLD"
                weighted_conf = 0.2
                position = 0.0
                mode = "wait"
                reason = f"分歧偏空({buys}B/{sells}S/{holds}H), 观望"

        else:
            # 完全冲突 → 不交易
            action = "HOLD"
            weighted_conf = 0.0
            position = 0.0
            mode = "wait"
            reason = f"完全冲突({buys}B/{sells}S/{holds}H), 放弃"

        # ── Regime否决 (最高优先级) ──
        if regime_mode == "stop":
            return ArbitrationResult("HOLD", 0.0, 0.0, consistency, "no_decision",
                                     "Regime=退潮, 禁止交易")
        if regime_mode == "defensive" and action == "BUY":
            return ArbitrationResult("HOLD", weighted_conf, 0.0, consistency, "wait",
                                     "Regime=防御, 禁止买入")
        if regime_mode == "cautious":
            position *= 0.5

        return ArbitrationResult(action, round(weighted_conf, 2), round(position, 2),
                                 round(consistency, 2), mode, reason)
