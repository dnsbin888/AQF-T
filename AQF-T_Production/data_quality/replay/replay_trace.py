"""
M2.4 Replay Trace — 自动生成Replay证据
Replay Report + Pattern Trigger + Candidate + Decision + Risk + Execution
"""
import json
from datetime import datetime
from data_quality.replay.replay_loader import ReplaySession
from data_quality.replay.replay_perception import PerceptionSnapshot
from data_quality.replay.replay_decision import ReplayDecision


class ReplayTrace:
    """Replay证据链 — 全程可审计"""

    def __init__(self, session: ReplaySession):
        self.session = session
        self.snapshots: list[PerceptionSnapshot] = []
        self.decisions: list[ReplayDecision] = []
        self.pattern_triggers: dict[str, int] = {}  # {pattern: count}

    def record_snapshot(self, snap: PerceptionSnapshot):
        self.snapshots.append(snap)
        for pattern, score in snap.pattern_scores.items():
            self.pattern_triggers[pattern] = self.pattern_triggers.get(pattern, 0) + 1

    def record_decision(self, decision: ReplayDecision):
        self.decisions.append(decision)

    def generate_report(self) -> str:
        """生成Replay审计报告"""
        patterns = "\n".join(f"    {k}: {v} triggers" for k, v in self.pattern_triggers.items())
        return f"""
================================================================
  AQF-T M2 Replay Trace Report
  Replay ID: {self.session.config.replay_id}
  Dataset:   {self.session.config.dataset_version}
  Engine:    {self.session.config.engine_version}
  Generated: {datetime.now().isoformat()}
================================================================

一、Replay概况
  Total Ticks:    {self.session.total_ticks}
  Errors:         {self.session.errors}
  Snapshots:      {len(self.snapshots)}
  Decisions:      {len(self.decisions)}

二、Consistency & Determinism
  Tick Hashes:    {len(self.session.tick_hashes)} (唯一序列)
  Verify:         Replay两次应完全一致

三、Pattern Triggers
{patterns}

四、决策样本 (最近3条)
{chr(10).join(f'  [{d.timestamp.isoformat()}] Selected: {d.selected}, Position: {d.position_pct}, Confidence: {d.confidence}' for d in self.decisions[-3:])}

五、审计声明
  本Replay由AQF-T M2引擎生成。
  同一Dataset+Config+GitCommit必须产生相同结果。
================================================================
"""

    def export_json(self, filepath: str):
        """导出JSON — 供Knowledge Hub存储"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "replay_id": self.session.config.replay_id,
                "total_ticks": self.session.total_ticks,
                "snapshots": len(self.snapshots),
                "decisions": len(self.decisions),
                "patterns": self.pattern_triggers,
                "tick_hashes": self.session.tick_hashes[:100],  # 前100个
                "timestamp": datetime.now().isoformat(),
            }, f, indent=2, ensure_ascii=False)
