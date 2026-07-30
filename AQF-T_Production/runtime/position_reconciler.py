"""
PositionReconciler — V1.2 P0-3
Daily position reconciliation: AQF-T vs Broker. Detects drift before it becomes disaster.
"""
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class ReconcileResult:
    matched: bool = True
    drift_items: list = field(default_factory=list)
    report_path: str = ""
    timestamp: str = ""

class PositionReconciler:
    """持仓对齐器 — 盘前/盘后对账"""

    def __init__(self, output_dir: str = "runtime"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def reconcile(self, aqft_positions: dict, broker_positions: dict) -> ReconcileResult:
        """
        Compare AQF-T internal positions vs broker positions.

        aqft_positions: {symbol: {shares, avg_cost}}
        broker_positions: {symbol: {shares, avg_cost, market_value}}
        """
        result = ReconcileResult(timestamp=datetime.now().isoformat())
        all_symbols = set(aqft_positions.keys()) | set(broker_positions.keys())

        for sym in sorted(all_symbols):
            aqft = aqft_positions.get(sym, {})
            broker = broker_positions.get(sym, {})

            aqft_shares = aqft.get("shares", 0)
            broker_shares = broker.get("shares", 0)

            if aqft_shares != broker_shares:
                result.matched = False
                result.drift_items.append({
                    "symbol": sym,
                    "type": "MISMATCH",
                    "aqft_shares": aqft_shares,
                    "broker_shares": broker_shares,
                    "delta": broker_shares - aqft_shares,
                })

        # Save report
        date_str = datetime.now().strftime("%Y%m%d")
        report_file = self.output_dir / f"POSITION_RECONCILE_{date_str}.json"
        report = {
            "timestamp": result.timestamp,
            "matched": result.matched,
            "drift_count": len(result.drift_items),
            "drift_items": result.drift_items,
            "aqft_positions": {k: {"shares": v.get("shares", 0)} for k, v in aqft_positions.items()},
            "broker_positions": {k: {"shares": v.get("shares", 0)} for k, v in broker_positions.items()},
        }
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        result.report_path = str(report_file)

        return result

    def pre_market_check(self, aqft_positions, broker_positions) -> bool:
        """盘前检查: 一致则允许交易"""
        result = self.reconcile(aqft_positions, broker_positions)
        if not result.matched:
            print(f"[Reconciler] WARNING: {len(result.drift_items)} position drifts detected!")
            for d in result.drift_items:
                print(f"  {d['symbol']}: AQFT={d['aqft_shares']} vs Broker={d['broker_shares']} (delta={d['delta']})")
        return result.matched
