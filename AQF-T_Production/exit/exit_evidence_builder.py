"""
Exit Evidence Builder — E4 (DEC-027 Final)
============================================
生成每笔卖出的完整证据包: 为什么买 → 为什么持有 → 为什么退出

只读已有数据, 不修改 Pipeline/Risk/Strategy
"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from exit.exit_evidence import ExitEvidence
from exit.exit_reason import ExitReason

ROOT = Path(__file__).parent.parent
EVIDENCE_DIR = ROOT / "evidence" / "exit"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


class ExitEvidenceBuilder:
    """
    退出证据构建器 — 从 Pipeline 运行结果中采集

    输入: PipelineState + ExitResult
    输出: exit_evidence.json (完整生命周期证据)
    """

    def __init__(self):
        self.evidence_log: list[ExitEvidence] = []

    def record_exit(self,
                    symbol: str,
                    exit_reason: str,
                    position_before: dict,
                    entry_evidence: dict,
                    trigger: dict,
                    execution: dict,
                    market_context: dict,
                    position_after: dict) -> ExitEvidence:
        """记录单笔退出"""
        ev = ExitEvidence(
            symbol=symbol,
            exit_reason=exit_reason,
            position_before=position_before,
            trigger=trigger,
            decision={"action": "SELL", "quantity": execution.get("quantity", 0)},
            execution=execution,
            position_after=position_after,
        )
        # 扩展字段
        ev.entry_evidence = entry_evidence
        ev.market_context = market_context
        self.evidence_log.append(ev)
        return ev

    def build_summary(self) -> dict:
        """汇总所有退出证据"""
        if not self.evidence_log:
            return {"total_exits": 0}

        by_reason = defaultdict(int)
        by_trigger_type = defaultdict(int)
        total_holding_days = 0
        total_pnl = 0.0
        wins = 0
        losses = 0

        for ev in self.evidence_log:
            by_reason[ev.exit_reason] += 1
            by_trigger_type[ev.trigger.get("type", "unknown")] += 1
            total_holding_days += ev.position_before.get("holding_days", 0)
            # P&L from execution
            sell_price = ev.execution.get("fill_price", 0)
            sell_qty = ev.execution.get("quantity", 0)
            avg_cost = ev.position_before.get("avg_cost", 0)
            if avg_cost > 0 and sell_qty > 0:
                pnl = (sell_price - avg_cost) * sell_qty
                total_pnl += pnl
                if pnl > 0:
                    wins += 1
                elif pnl < 0:
                    losses += 1

        total = len(self.evidence_log)
        return {
            "total_exits": total,
            "by_reason": dict(by_reason),
            "by_trigger_type": dict(by_trigger_type),
            "avg_holding_days": round(total_holding_days / total, 1) if total > 0 else 0,
            "total_pnl": round(total_pnl, 2),
            "win_count": wins,
            "loss_count": losses,
            "win_rate": round(wins / total * 100, 1) if total > 0 else 0,
            "evidence_log": [ev.to_dict() for ev in self.evidence_log],
        }

    def save(self, filename: str = None) -> str:
        """保存证据包"""
        if filename is None:
            filename = f"{datetime.now().strftime('%Y%m%d')}_exit_evidence.json"
        filepath = EVIDENCE_DIR / filename

        summary = self.build_summary()
        summary["generated_at"] = datetime.now().isoformat()
        summary["source"] = "SIMULATOR"
        summary["not_live"] = True

        filepath.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return str(filepath)


def build_exit_evidence_from_state(pipeline_state, exit_result=None) -> dict:
    """
    从 Pipeline State 中提取退出证据 (供 Pipeline 调用)

    每笔 REJECTED/FILLED 的 SELL 都生成证据。
    """
    builder = ExitEvidenceBuilder()

    for fill in (pipeline_state.fills or []):
        if fill.action != "SELL":
            continue

        # 找到对应的 signal
        signal = next(
            (s for s in (pipeline_state.signals or [])
             if s.symbol == fill.symbol and s.action == "SELL"),
            None
        )

        builder.record_exit(
            symbol=fill.symbol,
            exit_reason=fill.reason or "unknown",
            position_before={
                "shares": fill.fill_quantity,
                "avg_cost": fill.requested_price,
                "holding_days": 0,
            },
            entry_evidence=signal.reasoning if signal else "",
            trigger={
                "type": "strategy_exit" if signal else "risk_stop",
                "priority": signal.confidence * 100 if signal else 80,
                "reason": fill.reason,
            },
            execution={
                "action": "SELL",
                "quantity": fill.fill_quantity,
                "fill_price": fill.fill_price,
                "fee": fill.fee,
                "status": fill.status,
            },
            market_context={
                "regime": pipeline_state.regime.sentiment_phase if pipeline_state.regime else "N/A",
            },
            position_after={"shares": 0},
        )

    summary = builder.build_summary()
    if summary["total_exits"] > 0:
        path = builder.save()
        return {"path": path, "summary": summary}
    return {"summary": summary}
