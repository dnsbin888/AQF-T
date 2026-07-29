"""
M3 Decision Trace — 决策审计链
Candidate → Decision → Risk → Execution → Result
每笔交易完整轨迹, 可回答: 为什么买? 为什么没买? 哪个环节失效?
"""
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from data_quality.replay.replay_decision import ReplayDecision, ReplayCandidate


@dataclass
class TraceStep:
    """决策链中的每一步"""
    stage: str                # CANDIDATE / DECISION / RISK / EXECUTION / RESULT
    timestamp: datetime
    detail: dict
    passed: bool
    reason: str = ""

    def hash(self) -> str:
        return hashlib.md5(
            f"{self.stage}{self.timestamp.isoformat()}{self.passed}".encode()
        ).hexdigest()


@dataclass
class DecisionTrace:
    """完整决策轨迹"""
    trace_id: str
    symbol: str
    steps: list[TraceStep] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""

    def add_step(self, stage: str, detail: dict, passed: bool, reason: str = ""):
        self.steps.append(TraceStep(stage, datetime.now(), detail, passed, reason))

    def is_complete(self) -> bool:
        stages = {s.stage for s in self.steps}
        return {"CANDIDATE", "DECISION", "RISK", "EXECUTION"}.issubset(stages)

    def can_answer(self, question: str) -> bool:
        """能否回答关键问题?"""
        if "为什么买" in question:
            return any(s.stage == "DECISION" and s.passed for s in self.steps)
        if "为什么没买" in question:
            return any(s.stage == "CANDIDATE" and not s.passed for s in self.steps) or \
                   any(s.stage == "RISK" and not s.passed for s in self.steps)
        if "为什么拒绝" in question:
            return any(s.stage == "RISK" and not s.passed for s in self.steps)
        if "为什么失败" in question:
            return any(s.stage == "EXECUTION" and not s.passed for s in self.steps)
        return False

    def to_report(self) -> str:
        steps_str = "\n".join(
            f"  [{s.stage}] {'PASS' if s.passed else 'FAIL'} — {s.reason}"
            for s in self.steps
        )
        return f"""
Decision Trace: {self.trace_id}
Symbol: {self.symbol}
Started: {self.started_at}
Steps:
{steps_str}
Complete: {self.is_complete()}
"""


class DecisionTracer:
    """决策追踪器 — 贯穿Candidate→Decision→Risk→Execution"""

    def __init__(self):
        self.traces: list[DecisionTrace] = []

    def trace_decision(self, symbol: str, decision: ReplayDecision,
                       risk_passed: bool = True, execution_passed: bool = True) -> DecisionTrace:
        trace = DecisionTrace(
            trace_id=f"TRACE-{len(self.traces)+1:04d}",
            symbol=symbol,
            started_at=datetime.now().isoformat(),
        )

        # Step 1: Candidate
        for c in decision.candidates:
            trace.add_step("CANDIDATE",
                           {"symbol": c.symbol, "strategy": c.strategy,
                            "score": c.score, "confidence": c.confidence},
                           True, f"Candidate: {c.symbol} score={c.score:.2f}")

        # Step 2: Decision
        trace.add_step("DECISION",
                       {"selected": decision.selected,
                        "position_pct": decision.position_pct,
                        "confidence": decision.confidence},
                       decision.confidence > 0.5,
                       f"Selected: {decision.selected}, "
                       f"position={decision.position_pct:.0%}")

        # Step 3: Risk
        trace.add_step("RISK",
                       {"risk_passed": risk_passed,
                        "max_position": 0.15, "max_daily_loss": -0.03},
                       risk_passed,
                       "Risk PASS" if risk_passed else "Risk REJECT: 超仓/退潮期/熔断")

        # Step 4: Execution
        trace.add_step("EXECUTION",
                       {"filled": execution_passed,
                        "slippage_bps": 15, "fill_rate": 1.0},
                       execution_passed,
                       "Execution FILLED" if execution_passed else "Execution FAILED")

        trace.completed_at = datetime.now().isoformat()
        self.traces.append(trace)
        return trace

    def coverage_report(self) -> dict:
        """追踪覆盖率统计"""
        total = len(self.traces)
        if total == 0:
            return {"total": 0}
        complete = sum(1 for t in self.traces if t.is_complete())
        can_why_buy = sum(1 for t in self.traces if t.can_answer("为什么买"))
        can_why_reject = sum(1 for t in self.traces if t.can_answer("为什么拒绝"))
        return {
            "total": total,
            "complete": complete,
            "complete_rate": f"{complete/total:.0%}",
            "why_buy": can_why_buy,
            "why_reject": can_why_reject,
        }
