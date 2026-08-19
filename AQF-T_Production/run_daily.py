"""
AQF-T 每日自动运行 Wrapper
==========================
供 Windows Task Scheduler 调用。
无论 Pipeline 是否产生交易，都写入状态文件。

用法:
  python run_daily.py [--source real|sim]

输出:
  reports/status/YYYYMMDD_status.json  ← 每日状态（无交易日也生成）
  reports/daily/YYYYMMDD_report.json   ← Pipeline 自带（有交易时）
  reports/errors/YYYYMMDD_error.json   ← 异常证据
"""

import sys
import json
import traceback
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

STATUS_DIR = ROOT / "reports" / "status"
ERROR_DIR = ROOT / "reports" / "errors"
STATUS_DIR.mkdir(parents=True, exist_ok=True)
ERROR_DIR.mkdir(parents=True, exist_ok=True)

# P1.1: 统一交易日历 (D3 — AQF-T 不持有本地日历逻辑)
sys.path.insert(0, str(Path(r"D:\quant_framework\src")))
from quant_framework.execution.trading_calendar import get_trading_calendar


def _build_reason(result: dict) -> str:
    """根据执行结果生成人类可读状态说明（Health Protocol v1.0）"""
    if not result.get("success"):
        return "Pipeline执行异常"
    regime = result.get("regime") or {}
    mode = regime.get("mode", "")
    if mode == "stop":
        return f"AQF-T判断市场{regime.get('phase', '退潮')}，今日不交易"
    if result.get("signals", 0) == 0:
        return "今日无符合条件的信号"
    return "正常运行"


def run_daily(source: str = "real") -> dict:
    """
    执行每日 Pipeline，返回执行摘要。
    任何异常都被捕获并写入 error evidence。
    """
    today = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().isoformat()

    result = {
        "date": today,
        "timestamp": timestamp,
        "source": source,
        "success": False,
        "data_source": "UNKNOWN",
        "regime": None,
        "candidates": 0,
        "signals": 0,
        "fills": 0,
        "rejected": 0,
        "errors": [],
        "warnings": [],
        "account": {},
    }

    try:
        from pipeline import ProductionPipeline
        from paper_runner import run_single_day, REAL_DATA_AVAILABLE

        pipeline = ProductionPipeline()
        use_real = (source == "real")

        print(f"\n[run_daily] {timestamp}  source={source}")
        state = run_single_day(pipeline, use_real_data=use_real)

        # ── P1-DI: 实际数据源 (B-4: 读自 paper_runner 注入的 _data_source, 不凭空推断) ──
        actual_source = (state.market_stats or {}).get("_data_source")
        if actual_source:
            result["data_source"] = actual_source
        elif use_real and REAL_DATA_AVAILABLE:
            result["data_source"] = "AKSHARE_EOD"
        elif use_real:
            result["data_source"] = "SIMULATOR"  # akshare 未安装, 回退到模拟
        else:
            result["data_source"] = "SIMULATOR"

        # 提取摘要
        result["success"] = True
        result["regime"] = {
            "phase": state.regime.sentiment_phase if state.regime else "UNKNOWN",
            "score": state.regime.sentiment_score if state.regime else 0,
            "mode": state.regime.operation_mode if state.regime else "UNKNOWN",
            "path_a": state.regime.path_a_allowed if state.regime else False,
            "path_b": state.regime.path_b_allowed if state.regime else False,
            "max_position_pct": state.regime.max_position_pct if state.regime else 0,
        }
        result["candidates"] = state.total_candidates
        result["signals"] = state.total_signals
        result["fills"] = state.total_fills
        result["rejected"] = state.total_rejected
        result["errors"] = state.errors
        result["warnings"] = state.warnings
        result["account"] = pipeline.broker.summary()

        # P1.1: pipeline 请求的市场数据日期
        # 注意: 此为 akshare 请求日期, 非 akshare 实际返回数据日期。
        # 盘前运行时 akshare 可能返回前日数据但此字段仍为今日。
        # P2 增加 observed_data_date。
        data_date = (
            state.market_stats.get("_meta", {}).get("date")
            or result.get("date", "")
        )

        # 打印摘要
        print(f"\n{'='*60}")
        print(f"  AQF-T Daily Run  {today}")
        print(f"  Source:   {source}")
        print(f"  Regime:   {result['regime']['phase']} ({result['regime']['mode']})")
        print(f"  Signals:  {result['signals']}")
        print(f"  Fills:    {result['fills']}")
        print(f"  Errors:   {len(result['errors'])}")
        print(f"  Warnings: {len(result['warnings'])}")
        print(f"  Account:  {result['account']}")
        print(f"{'='*60}")

        if state.errors:
            print(f"\n  [ERROR] 异常:")
            for e in state.errors:
                print(f"    - {e}")
        if state.warnings:
            print(f"\n  [WARN] 提示:")
            for w in state.warnings:
                print(f"    - {w}")

    except Exception as e:
        result["success"] = False
        result["errors"].append({
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc(),
        })
        print(f"\n[run_daily] FATAL ERROR: {e}")
        traceback.print_exc()

        # 写入错误证据
        error_file = ERROR_DIR / f"{today}_error.json"
        error_evidence = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "partial_result": result,
        }
        error_file.write_text(
            json.dumps(error_evidence, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[run_daily] Error evidence saved: {error_file}")

    finally:
        # 无论如何都写入状态文件
        status_file = STATUS_DIR / f"{today}_status.json"
        status_file.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[run_daily] Status saved: {status_file}")

        # -- AQF-T Health Protocol v1.0: 写入 latest_status.json --
        latest_status = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pipeline_status": "completed" if result["success"] else "error",
            "regime": result.get("regime", {}).get("phase", "UNKNOWN") if result.get("regime") else "UNKNOWN",
            "mode": result.get("regime", {}).get("mode", "UNKNOWN") if result.get("regime") else "UNKNOWN",
            "trade_allowed": result.get("regime", {}).get("mode") not in ("stop", None) if result.get("regime") else False,
            "reason": _build_reason(result),
            "data_source": result.get("data_source", "UNKNOWN"),
            "errors": len(result.get("errors", [])),
            "warnings": len(result.get("warnings", [])),
            # ── P1.1 Regime Snapshot Contract ──
            "data_date": data_date,
            "effective_from": get_trading_calendar().next_session_open().strftime("%Y-%m-%d %H:%M:%S"),
            "regime_version": "v1.0",
        }
        latest_file = STATUS_DIR / "latest_status.json"
        latest_file.write_text(
            json.dumps(latest_status, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[run_daily] Health protocol saved: {latest_file}")

        # -- Market Sensor Shadow v1.0: 采集资金环境数据 (只读, 不决策) --
        try:
            from market_sensor import MarketSensorEngine
            sensor = MarketSensorEngine()
            sensor.run()
        except Exception as sensor_err:
            print(f"[run_daily] Market Sensor skipped: {sensor_err}")

        # -- AVP Evidence Table v1.1: 每日证据追行 + T+N 回填 --
        try:
            from evidence_table import run as evidence_run, backfill_results
            evidence_run()
            # Outcome 回填: 扫描所有待补的过往行 (使用 akshare 沪深300 数据)
            n_backfilled = backfill_results()
            if n_backfilled:
                print(f"[run_daily] Evidence Outcome backfilled: {n_backfilled} row(s)")
        except Exception as ev_err:
            print(f"[run_daily] Evidence Table skipped: {ev_err}")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AQF-T Daily Runner")
    parser.add_argument(
        "--source", choices=["real", "sim"], default="real",
        help="数据源: real(akshare EOD) | sim(模拟器)"
    )
    args = parser.parse_args()
    run_daily(args.source)
