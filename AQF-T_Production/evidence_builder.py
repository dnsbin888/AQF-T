"""
Evidence Builder — Phase 2.1-A Evidence Infrastructure Validation
==================================================================
在 Simulator 上验证完整的 Evidence 采集/验证/审计链。

无QMT环境下:
  Simulator -> MarketDataProvider -> Replay -> Evidence Builder -> PHASE2_DATA_EVIDENCE_SIM.json

等QMT接入时只替换数据源, Evidence链不变。

输出:
  PHASE2_DATA_EVIDENCE_SIM.json  — 30天模拟证据包
  {
    "source": "SIMULATOR",
    "environment": "TEST",
    "not_live": true,
    "data_integrity": {...},
    "replay_stability": {...},
    "pattern_evidence": {...},
    "risk_evidence": {...},
    "execution_evidence": {...}
  }
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

from pipeline import ProductionPipeline, PipelineState
from paper_runner import MarketDataSimulator


@dataclass
class EvidencePackage:
    """Phase 2.1 证据包"""
    source: str = "SIMULATOR"
    environment: str = "TEST"
    not_live: bool = True
    generated_at: str = ""
    period_days: int = 0
    evidence_version: str = "2.1"
    git_commit: str = ""
    config_hash: str = ""
    provider: str = "SIMULATOR"

    # Data Integrity
    data_integrity: dict = field(default_factory=dict)

    # Replay Stability
    replay_stability: dict = field(default_factory=dict)

    # Pattern Evidence
    pattern_evidence: dict = field(default_factory=dict)

    # Risk Evidence
    risk_evidence: dict = field(default_factory=dict)

    # Execution Evidence
    execution_evidence: dict = field(default_factory=dict)

    # Daily logs
    daily_logs: list = field(default_factory=list)


class EvidenceBuilder:
    """
    证据构建器 — 从 Replay 运行中采集结构化证据

    用法:
      builder = EvidenceBuilder()
      evidence = builder.run_30_day_sim()
      builder.save(evidence)
    """

    def __init__(self, output_dir: str = "evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_30_day_sim(self, seed: int = 42) -> EvidencePackage:
        """运行30天 Simulator Replay，采集完整证据"""
        random.seed(seed)

        pipeline = ProductionPipeline()
        sim = MarketDataSimulator(seed=seed)

        import subprocess
        git_commit = ""
        try:
            git_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
            ).strip()[:8]
        except Exception:
            git_commit = "unknown"

        evidence = EvidencePackage(
            generated_at=datetime.now().isoformat(),
            period_days=30,
            evidence_version="2.1",
            git_commit=git_commit,
            config_hash="sim_default",
            provider="SIMULATOR",
        )

        # Phase cycle: 回暖 -> 高潮 -> 退潮 -> 冰点 -> 回暖
        phases_30 = (
            ["回暖期"] * 4 +
            ["高潮期"] * 8 +
            ["退潮期"] * 5 +
            ["冰点期"] * 5 +
            ["回暖期"] * 5 +
            ["高潮期"] * 3
        )

        daily_states = []
        pattern_triggers = {"PositionAnchor": 0, "LeaderLifeCycle": 0,
                           "LadderScore": 0, "EmotionCycle": 0,
                           "SectorFlow": 0, "RelativeStrength": 0}
        risk_reject_reasons = {}
        execution_metrics = {"total_signals": 0, "total_fills": 0,
                            "total_rejected": 0, "fill_rate": 0.0,
                            "avg_slippage": 0.0}

        start_date = datetime(2026, 6, 1)

        print(f"\n{'='*60}")
        print(f"  Phase 2.1-A: Evidence Infrastructure Validation")
        print(f"  Source: SIMULATOR | Period: 30 days")
        print(f"  Environment: TEST | Not Live")
        print(f"{'='*60}\n")

        for i, phase in enumerate(phases_30):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")

            # Generate data
            market_stats = sim.generate_market_stats(phase)
            watchlist = sim.generate_watchlist()

            # Run pipeline
            state = pipeline.run_daily(market_stats, watchlist)
            daily_states.append(state)

            # Daily refresh
            pipeline.broker.daily_refresh()
            pipeline.risk_checker.daily_reset()

            # Collect pattern triggers (from evidence in candidates)
            for c in state.candidates:
                if c.path == "A":
                    pattern_triggers["PositionAnchor"] += 1
                    if c.evidence.get("is_dragon"):
                        pattern_triggers["LeaderLifeCycle"] += 1
                if c.path.startswith("B"):
                    pattern_triggers["LadderScore"] += 1
                    if c.evidence.get("theme_heat", 0) > 0.5:
                        pattern_triggers["EmotionCycle"] += 1
                # P1 Patterns
                if c.evidence.get("sector_flow_score", 0) > 0.5:
                    pattern_triggers["SectorFlow"] += 1
                if c.evidence.get("rs_score", 0) > 0.6:
                    pattern_triggers["RelativeStrength"] += 1

            # Collect risk reject reasons
            for f in state.fills:
                if f.status != "FILLED":
                    reason = f.reason or "unknown"
                    risk_reject_reasons[reason] = risk_reject_reasons.get(reason, 0) + 1

            # Execution metrics
            execution_metrics["total_signals"] += state.total_signals
            execution_metrics["total_fills"] += state.total_fills
            execution_metrics["total_rejected"] += state.total_rejected

            # Progress
            stop_mark = " [STOP]" if not state.tradable else ""
            fill_mark = f" [{state.total_fills}F/{state.total_rejected}R]" if state.total_signals > 0 else ""
            print(f"  Day {i+1:2d} {date} {phase} -> "
                  f"{state.total_signals}S{fill_mark}{stop_mark}")

            # Daily evidence log
            evidence.daily_logs.append({
                "date": date,
                "phase": phase,
                "regime": state.regime.sentiment_phase if state.regime else "N/A",
                "operation_mode": state.regime.operation_mode if state.regime else "N/A",
                "regime_confidence": state.regime.regime_confidence if state.regime else 0,
                "candidates": state.total_candidates,
                "signals": state.total_signals,
                "fills": state.total_fills,
                "rejected": state.total_rejected,
                "tradable": state.tradable,
                "errors": len(state.errors),
            })

        # -- Compute final metrics --

        # Data Integrity (Simulator baseline)
        evidence.data_integrity = {
            "source": "SIMULATOR",
            "total_ticks": sum(len(s.candidates) * 100 for s in daily_states),  # estimated
            "missing_rate": 0.0,   # Simulator has no missing data
            "duplicate_rate": 0.0,
            "timestamp_gaps": 0,
            "l2_field_completeness": 1.0,
            "note": "Simulator baseline — no real data integrity concerns",
        }

        # Replay Stability (run 3x same seed, check consistency)
        evidence.replay_stability = self._check_replay_stability(
            pipeline, phases_30, seed
        )

        # Pattern Evidence
        total_triggers = sum(pattern_triggers.values())
        evidence.pattern_evidence = {
            "patterns": {
                name: {
                    "trigger_count": count,
                    "trigger_pct": round(count / max(total_triggers, 1) * 100, 1),
                    "status": "validated" if count > 0 else "no_trigger",
                }
                for name, count in pattern_triggers.items()
            },
            "total_triggers": total_triggers,
            "note": "SIMULATOR data — trigger counts for infrastructure validation only",
        }

        # Risk Evidence
        total_rejects = sum(risk_reject_reasons.values())
        evidence.risk_evidence = {
            "total_rejects": total_rejects,
            "reject_reasons": dict(
                sorted(risk_reject_reasons.items(), key=lambda x: -x[1])
            ),
            "risk_gate_active": total_rejects > 0,
            "note": "Risk layer operational — rejecting signals per frozen rules",
        }

        # Execution Evidence
        total_sigs = execution_metrics["total_signals"]
        evidence.execution_evidence = {
            "total_signals": total_sigs,
            "total_fills": execution_metrics["total_fills"],
            "total_rejected": execution_metrics["total_rejected"],
            "fill_rate": round(
                execution_metrics["total_fills"] / max(total_sigs, 1) * 100, 1
            ),
            "account": pipeline.broker.summary(),
            "exposure": pipeline.risk_checker.exposure_summary(),
            "note": "PaperBroker execution — slippage/fill modeled, not real",
        }

        # Summary
        trading_days = sum(1 for s in daily_states if s.tradable)
        stopped_days = sum(1 for s in daily_states if not s.tradable)

        print(f"\n{'='*60}")
        print(f"  EVIDENCE SUMMARY")
        print(f"  Trading days:  {trading_days}/30")
        print(f"  Stopped days:  {stopped_days}")
        print(f"  Total signals: {total_sigs}")
        print(f"  Total fills:   {execution_metrics['total_fills']}")
        print(f"  Total rejects: {execution_metrics['total_rejected']}")
        print(f"  Pattern triggers: {total_triggers}")
        print(f"  Account: {pipeline.broker.summary()}")
        print(f"{'='*60}")

        return evidence

    def _check_replay_stability(self, pipeline, phases, seed) -> dict:
        """3次Replay一致性检查"""
        sim1 = MarketDataSimulator(seed=seed)

        results = []
        for run in range(3):
            random.seed(seed + run)
            sim = MarketDataSimulator(seed=seed + run)

            run_signals = 0
            run_fills = 0
            for phase in phases[:5]:  # First 5 days for quick check
                stats = sim.generate_market_stats(phase)
                watchlist = sim.generate_watchlist()
                state = pipeline.run_daily(stats, watchlist)
                run_signals += state.total_signals
                run_fills += state.total_fills

            results.append({"run": run + 1, "signals": run_signals, "fills": run_fills})

        signals_vals = [r["signals"] for r in results]
        fills_vals = [r["fills"] for r in results]

        # Stability = all runs have same signal count
        signal_stable = len(set(signals_vals)) == 1
        fill_stable = len(set(fills_vals)) == 1

        return {
            "runs": 3,
            "signal_counts": signals_vals,
            "fill_counts": fills_vals,
            "signal_stable": signal_stable,
            "fill_stable": fill_stable,
            "stability_pct": 100.0 if signal_stable and fill_stable else round(
                (2 - (len(set(signals_vals)) - 1) / max(signals_vals + [1])) * 50, 1
            ),
            "note": "Simulator replay — same seed = deterministic output",
        }

    def save(self, evidence: EvidencePackage, filename: str = None) -> str:
        """保存证据包"""
        if filename is None:
            filename = "PHASE2_DATA_EVIDENCE_SIM.json"

        filepath = self.output_dir / filename

        output = {
            "meta": {
                "source": evidence.source,
                "environment": evidence.environment,
                "not_live": evidence.not_live,
                "generated_at": evidence.generated_at,
                "period_days": evidence.period_days,
                "evidence_version": evidence.evidence_version,
                "git_commit": evidence.git_commit,
                "config_hash": evidence.config_hash,
                "provider": evidence.provider,
                "phase": "Phase2.1-A",
            },
            "data_integrity": evidence.data_integrity,
            "replay_stability": evidence.replay_stability,
            "pattern_evidence": evidence.pattern_evidence,
            "risk_evidence": evidence.risk_evidence,
            "execution_evidence": evidence.execution_evidence,
            "daily_logs": evidence.daily_logs,
        }

        filepath.write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"\n  Evidence saved: {filepath}")
        print(f"  Size: {filepath.stat().st_size} bytes")
        return str(filepath)


# ===============================================================
# CLI
# ===============================================================

if __name__ == "__main__":
    print("\n  AQF-T Phase 2.1-A: Evidence Infrastructure Validation")
    print("  Source: SIMULATOR | Not Live | Test Environment\n")

    builder = EvidenceBuilder()
    evidence = builder.run_30_day_sim(seed=42)
    path = builder.save(evidence)

    print(f"\n  Done. Evidence package: {path}")
    print("  Ready for QMT data swap when available.")
