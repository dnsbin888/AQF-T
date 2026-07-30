"""
Report Writer — 日终报告持久化
==============================
GPT P0-3: 将 Pipeline 运行结果写入结构化 JSON 文件

输出目录:
  reports/
    daily/    20260730_report.json
    pattern/  PositionAnchor.json / LeaderLifeCycle.json / ...
    execution/ trade_report.json
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class ReportWriter:
    """
    报告持久化器

    每次 Pipeline 运行后调用:
      writer.write_daily_report(state, pipeline)
      writer.write_execution_report(fills)
      writer.write_pattern_evidence(evidence_list)
    """

    def __init__(self, base_dir: str = "reports"):
        self.base_dir = Path(base_dir)
        self.daily_dir = self.base_dir / "daily"
        self.pattern_dir = self.base_dir / "pattern"
        self.execution_dir = self.base_dir / "execution"

        for d in [self.daily_dir, self.pattern_dir, self.execution_dir]:
            d.mkdir(parents=True, exist_ok=True)

    # ═══════════════════════════════════════════════════════════
    # Daily Report
    # ═══════════════════════════════════════════════════════════

    def write_daily_report(self, state, pipeline) -> str:
        """
        写入日终报告

        Args:
            state: PipelineState
            pipeline: ProductionPipeline

        Returns:
            文件路径
        """
        date_str = state.date or datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str.replace('-', '')}_report.json"
        filepath = self.daily_dir / filename

        # 收集敞口数据
        exposure = {}
        if hasattr(pipeline, 'risk_checker'):
            exposure = pipeline.risk_checker.exposure_summary()

        report = {
            "report_type": "daily",
            "date": date_str,
            "generated_at": datetime.now().isoformat(),

            # Regime
            "regime": {
                "phase": state.regime.sentiment_phase if state.regime else "UNKNOWN",
                "operation_mode": state.regime.operation_mode if state.regime else "UNKNOWN",
                "sentiment_score": state.regime.sentiment_score if state.regime else 0,
                "regime_confidence": state.regime.regime_confidence if state.regime else 0,
                "zhatban_rate": state.regime.zhatban_rate if state.regime else 0,
                "promotion_rate": state.regime.promotion_rate if state.regime else 0,
                "path_a_allowed": state.regime.path_a_allowed if state.regime else False,
                "path_b_allowed": state.regime.path_b_allowed if state.regime else False,
                "max_position_pct": state.regime.max_position_pct if state.regime else 0,
            },

            # Candidates / Signals
            "pipeline": {
                "total_candidates": state.total_candidates,
                "total_signals": state.total_signals,
                "total_fills": state.total_fills,
                "total_rejected": state.total_rejected,
                "errors": [str(e) for e in state.errors],
            },

            # Signals detail
            "signals": [
                {
                    "symbol": s.symbol,
                    "action": s.action,
                    "strategy": s.strategy,
                    "position_pct": s.position_pct,
                    "confidence": s.confidence,
                    "reasoning": s.reasoning,
                }
                for s in (state.signals or [])
            ],

            # Fills detail
            "fills": [
                {
                    "symbol": f.symbol,
                    "action": f.action,
                    "status": f.status,
                    "fill_price": f.fill_price,
                    "fill_quantity": f.fill_quantity,
                    "fee": f.fee,
                    "reason": f.reason,
                    "timestamp": f.timestamp,
                }
                for f in (state.fills or [])
            ],

            # Risk & Exposure
            "exposure": exposure,

            # Account
            "account": pipeline.broker.summary() if hasattr(pipeline, 'broker') else {},

            # System health
            "health": pipeline.monitor.check().to_dict() if hasattr(pipeline, 'monitor') else {},
        }

        filepath.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return str(filepath)

    # ═══════════════════════════════════════════════════════════
    # Execution Report
    # ═══════════════════════════════════════════════════════════

    def write_execution_report(self, fills: list, date_str: str = None) -> str:
        """写入执行报告"""
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str.replace('-', '')}_execution.json"
        filepath = self.execution_dir / filename

        filled = [f for f in fills if f.status == "FILLED"]
        rejected = [f for f in fills if f.status != "FILLED"]

        report = {
            "report_type": "execution",
            "date": date_str,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_orders": len(fills),
                "filled": len(filled),
                "rejected": len(rejected),
                "fill_rate": round(len(filled) / max(len(fills), 1) * 100, 1),
                "total_commission": round(sum(f.fee for f in filled), 2),
                "avg_slippage_bps": round(
                    sum(f.slippage_bps for f in filled) / max(len(filled), 1), 1
                ),
            },
            "rejection_reasons": self._count_reasons(rejected),
            "fills": [
                {
                    "symbol": f.symbol,
                    "action": f.action,
                    "fill_price": f.fill_price,
                    "fill_quantity": f.fill_quantity,
                    "fee": f.fee,
                    "slippage_bps": f.slippage_bps,
                    "timestamp": f.timestamp,
                }
                for f in filled
            ],
        }

        filepath.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return str(filepath)

    # ═══════════════════════════════════════════════════════════
    # Pattern Evidence
    # ═══════════════════════════════════════════════════════════

    def write_pattern_evidence(self, pattern_name: str, evidence: dict) -> str:
        """
        写入 Pattern Evidence (GPT M5: Evidence Pipeline)

        Args:
            pattern_name: PositionAnchor / LeaderLifeCycle / LadderScore / EmotionCycle
            evidence: 证据数据
        """
        filename = f"{pattern_name}.json"
        filepath = self.pattern_dir / filename

        # 增量更新: 读取已有 → 追加 → 写入
        existing = {}
        if filepath.exists():
            try:
                existing = json.loads(filepath.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = {"pattern": pattern_name, "evidence_log": []}

        log = existing.get("evidence_log", [])
        log.append({
            "timestamp": datetime.now().isoformat(),
            **evidence,
        })

        # 保留最近100条
        if len(log) > 100:
            log = log[-100:]

        output = {
            "pattern": pattern_name,
            "last_updated": datetime.now().isoformat(),
            "total_entries": len(log),
            "evidence_log": log,
        }

        filepath.write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return str(filepath)

    # ═══════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════

    def _count_reasons(self, rejected: list) -> dict:
        """统计拒绝原因"""
        counts = {}
        for r in rejected:
            reason = r.reason or "未知"
            counts[reason] = counts.get(reason, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))

    def list_reports(self, report_type: str = "daily") -> list[str]:
        """列出已有报告"""
        dir_map = {
            "daily": self.daily_dir,
            "pattern": self.pattern_dir,
            "execution": self.execution_dir,
        }
        d = dir_map.get(report_type, self.daily_dir)
        return sorted([str(f) for f in d.glob("*.json")], reverse=True)

    def latest_daily_report(self) -> Optional[dict]:
        """读取最近一份日终报告"""
        files = self.list_reports("daily")
        if not files:
            return None
        return json.loads(Path(files[0]).read_text(encoding="utf-8"))
