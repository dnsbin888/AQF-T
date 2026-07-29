"""
M2.3 Replay Decision — Candidate→排序→Decision (可复现)
验证: 同一Replay → 同一Candidate → 同一Decision (Consistency)
"""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from data_quality.replay.replay_perception import PerceptionSnapshot


@dataclass
class ReplayCandidate:
    """回放Candidate — 与实时Candidate格式完全一致"""
    symbol: str
    strategy: str              # Path A / Path B
    score: float
    confidence: float
    pattern_scores: dict = field(default_factory=dict)
    reason: str = ""

    def hash(self) -> str:
        content = f"{self.symbol}{self.strategy}{self.score:.4f}{self.confidence:.4f}"
        return hashlib.md5(content.encode()).hexdigest()


@dataclass
class ReplayDecision:
    """回放Decision — 可复现"""
    timestamp: datetime
    candidates: list[ReplayCandidate]
    selected: str              # 选中的symbol
    position_pct: float
    confidence: float
    reason: str = ""

    def hash(self) -> str:
        parts = [self.selected, str(self.position_pct), str(self.confidence)]
        for c in self.candidates:
            parts.append(c.hash())
        return hashlib.md5("".join(parts).encode()).hexdigest()


class ReplayDecisionEngine:
    """Replay Decision引擎"""

    def decide(self, snapshots: list[PerceptionSnapshot]) -> ReplayDecision:
        """从PerceptionSnapshot生成Candidate → Decision"""
        candidates = []
        for snap in snapshots[-3:]:  # 最近3个
            score = (snap.anchor_score * 0.30 + snap.reseal_quality * 0.30 +
                     snap.ladder_score * 0.25 + 0.15)
            candidates.append(ReplayCandidate(
                symbol=snap.symbol,
                strategy="Path A" if snap.board_type == "换手板" else "Path B",
                score=round(score, 2),
                confidence=round(score * 0.9, 2),
                pattern_scores=snap.pattern_scores,
                reason=f"{snap.board_type}, {snap.leader_identity}",
            ))

        # 排序 + 选择最高分
        candidates.sort(key=lambda c: c.score, reverse=True)
        selected = candidates[0] if candidates else None

        return ReplayDecision(
            timestamp=snapshots[-1].timestamp if snapshots else datetime.now(),
            candidates=candidates,
            selected=selected.symbol if selected else "",
            position_pct=round(selected.score * 0.15, 2) if selected else 0.0,
            confidence=selected.confidence if selected else 0.0,
            reason=selected.reason if selected else "",
        )


def verify_consistency(snapshots_a: list[PerceptionSnapshot],
                       snapshots_b: list[PerceptionSnapshot]) -> bool:
    """验证: 同数据 → 同Decision"""
    engine = ReplayDecisionEngine()
    d1 = engine.decide(snapshots_a)
    d2 = engine.decide(snapshots_b)
    return d1.hash() == d2.hash()
