"""
AVP Evidence Table v1.1 (2026-08-09)
====================================
30天证据积累 — AVP 核心交付物。

v1.0: 50列 T+0 快照 (系统看到什么)
v1.1: 55列 + T+N Outcome 回填 (系统判断对不对)

每天从已有报告中提取一行，追加到 evidence_table.csv。
不调外部API (除 akshare 用于回填市场数据)，不产生交易信号，不改任何模型。

用法:
  python evidence_table.py                    # 处理今天
  python evidence_table.py --date 20260809    # 指定日期
  python evidence_table.py --backfill         # 回填所有待补 Outcome 行

输出:
  reports/evidence/evidence_table.csv         ← 累计证据表
"""

import json, csv, sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

ROOT = Path(__file__).parent
SENSOR_DIR = ROOT / "reports" / "sensor"
STATUS_DIR = ROOT / "reports" / "status"
DAILY_DIR = ROOT / "reports" / "daily"
EVIDENCE_DIR = ROOT / "reports" / "evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "evidence_table.csv"

# ── 列定义 ─────────────────────────────────────────
COLUMNS = [
    # 日期
    "date",
    # AQF-T Decision
    "regime_phase", "regime_score", "regime_mode",
    "path_a", "path_b", "max_position_pct",
    # Pipeline
    "candidates", "signals", "fills", "rejected",
    "data_source",
    # Market Sensor — Margin
    "margin_trend", "margin_strength", "margin_bal_5d_pct", "margin_bal_20d_pct",
    # Market Sensor — Institution
    "inst_flow", "inst_net", "inst_participation_pct",
    # Market Sensor — ETF
    "etf_appetite", "etf_risk_spread", "etf_large_chg", "etf_small_chg",
    # Market Sensor — Southbound
    "southbound_trend",
    # Market Sensor — Sentiment (market)
    "sent_mkt_score", "sent_mkt_label", "sent_advance_pct", "sent_breadth_pct",
    "sent_limit_up", "sent_limit_down",
    # Market Sensor — Sentiment (cycle)
    "sent_cycle_stage", "sent_cycle_scale", "sent_cycle_advice",
    # Market Sensor — Sentiment (aggregated)
    "sent_confidence", "sent_confidence_status",
    "sent_extreme_state", "sent_vel_1d", "sent_vel_5d",
    # Market Sensor — LLM (observe only)
    "llm_score", "llm_label",
    # Market Sensor — Summary
    "sensor_risk_appetite", "sensor_confidence",
    # Health
    "health_overall", "lgbm_loaded", "xgb_loaded",
    # Account
    "account_cash", "account_positions", "account_total_value",
    # Signals detail
    "signal_symbols", "signal_strategies",
    # Outcome (T+N backfill) — v1.1: 证据闭环
    "T1_return", "T3_return", "T5_return",
    "max_dd_5d", "benchmark_5d",
]

# ── 数据提取 ───────────────────────────────────────

def _load_json(path: Path) -> dict:
    """加载 JSON，文件不存在或损坏返回 {}"""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _safe_get(d: dict, *keys, default=None):
    """安全嵌套取值"""
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, {})
        else:
            return default
    return d if d != {} else default


def extract_row(date_str: str) -> dict:
    """从已有报告中提取一天的所有证据字段"""
    date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    sensor = _load_json(SENSOR_DIR / f"{date_str}_sensor.json")
    status = _load_json(STATUS_DIR / f"{date_str}_status.json")
    daily = _load_json(DAILY_DIR / f"{date_str}_report.json")

    row = {"date": date_fmt}

    # ── AQF-T Decision ──
    regime = status.get("regime", {}) or daily.get("regime", {})
    row["regime_phase"] = regime.get("phase", regime.get("operation_mode", ""))
    row["regime_score"] = regime.get("score", regime.get("sentiment_score"))
    row["regime_mode"] = regime.get("mode", regime.get("operation_mode", ""))
    row["path_a"] = regime.get("path_a", regime.get("path_a_allowed"))
    row["path_b"] = regime.get("path_b", regime.get("path_b_allowed"))
    row["max_position_pct"] = regime.get("max_position_pct")

    # ── Pipeline ──
    row["candidates"] = status.get("candidates", daily.get("pipeline", {}).get("total_candidates"))
    row["signals"] = status.get("signals", daily.get("pipeline", {}).get("total_signals"))
    row["fills"] = status.get("fills", daily.get("pipeline", {}).get("total_fills"))
    row["rejected"] = status.get("rejected", daily.get("pipeline", {}).get("total_rejected"))
    row["data_source"] = status.get("data_source", "")

    # ── Market Sensor: Margin ──
    margin = _safe_get(sensor, "sensors", "margin") or {}
    row["margin_trend"] = margin.get("trend", "")
    row["margin_strength"] = margin.get("strength_score")
    row["margin_bal_5d_pct"] = margin.get("balance_change_5d_pct")
    row["margin_bal_20d_pct"] = margin.get("balance_change_20d_pct")

    # ── Market Sensor: Institution ──
    lhb = _safe_get(sensor, "sensors", "lhb") or {}
    row["inst_flow"] = lhb.get("institution_flow", "")
    row["inst_net"] = lhb.get("institution_net")
    row["inst_participation_pct"] = lhb.get("institution_participation_pct")

    # ── Market Sensor: ETF ──
    etf = _safe_get(sensor, "sensors", "etf") or {}
    row["etf_appetite"] = etf.get("risk_appetite", "")
    row["etf_risk_spread"] = etf.get("risk_spread")
    row["etf_large_chg"] = etf.get("avg_large_cap_chg")
    row["etf_small_chg"] = etf.get("avg_small_cap_chg")

    # ── Market Sensor: Southbound ──
    sb = _safe_get(sensor, "sensors", "southbound") or {}
    row["southbound_trend"] = sb.get("trend", "")

    # ── Market Sensor: Sentiment (market) ──
    sent = _safe_get(sensor, "sensors", "sentiment") or {}
    mkt = sent.get("market_sentiment", {}) or {}
    row["sent_mkt_score"] = mkt.get("score")
    row["sent_mkt_label"] = mkt.get("label", "")
    row["sent_advance_pct"] = mkt.get("advance_ratio_pct")
    row["sent_breadth_pct"] = mkt.get("breadth_pct")
    row["sent_limit_up"] = mkt.get("limit_up")
    row["sent_limit_down"] = mkt.get("limit_down")

    # ── Market Sensor: Sentiment (cycle) ──
    cycle = sent.get("cycle", {}) or {}
    row["sent_cycle_stage"] = cycle.get("stage", "")
    row["sent_cycle_scale"] = cycle.get("position_scale")
    row["sent_cycle_advice"] = cycle.get("advice", "")

    # ── Market Sensor: Sentiment (aggregated) ──
    row["sent_confidence"] = sent.get("sentiment_confidence", {}).get("value")
    row["sent_confidence_status"] = sent.get("sentiment_confidence", {}).get("status", "")
    row["sent_extreme_state"] = sent.get("sentiment_extreme", {}).get("state", "")
    vel = sent.get("sentiment_velocity", {}) or {}
    row["sent_vel_1d"] = vel.get("change_1d")
    row["sent_vel_5d"] = vel.get("change_5d")

    # ── Market Sensor: LLM ──
    llm = sent.get("llm_sentiment", {}) or {}
    row["llm_score"] = llm.get("score")
    row["llm_label"] = llm.get("label", "")

    # ── Market Sensor: Summary ──
    summary = sensor.get("summary", {}) or {}
    row["sensor_risk_appetite"] = summary.get("risk_appetite", "")
    row["sensor_confidence"] = summary.get("confidence")

    # ── Health ──
    health = daily.get("health", {}) or {}
    row["health_overall"] = health.get("overall", "")
    models = health.get("models", {}) or {}
    row["lgbm_loaded"] = models.get("lgbm_trend")
    row["xgb_loaded"] = models.get("xgb_timing")

    # ── Account ──
    acct = status.get("account", {}) or daily.get("account", {}) or {}
    row["account_cash"] = acct.get("cash")
    row["account_positions"] = acct.get("positions")
    row["account_total_value"] = acct.get("total_value")

    # ── Signals ──
    signals_list = daily.get("signals", []) or []
    row["signal_symbols"] = ",".join(s.get("symbol", "") for s in signals_list)
    row["signal_strategies"] = ",".join(s.get("strategy", "") for s in signals_list)

    return row


def append_row(row: dict):
    """追加一行到 evidence_table.csv，首次自动创建带表头"""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = EVIDENCE_FILE.exists()

    with open(EVIDENCE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def run(date_str: Optional[str] = None):
    """主入口: 提取并追加"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")

    print(f"[EvidenceTable] Extracting row for {date_str}...")

    try:
        row = extract_row(date_str)
    except Exception as e:
        print(f"[EvidenceTable] ERROR extracting row: {e}")
        return None

    # 检查是否已有数据 (避免重复追加)
    if EVIDENCE_FILE.exists():
        try:
            with open(EVIDENCE_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                existing_dates = {r.get("date", "") for r in reader}
            if row["date"] in existing_dates:
                print(f"[EvidenceTable] {row['date']} already in table, skipping")
                return row
        except Exception:
            pass

    append_row(row)

    # 打印摘要
    filled = sum(1 for v in row.values() if v not in (None, "", False))
    total = len(COLUMNS)
    print(f"[EvidenceTable] Row appended: {filled}/{total} fields populated")
    print(f"[EvidenceTable]   regime={row['regime_phase']} | "
          f"signals={row['signals']} | fills={row['fills']} | "
          f"sensor_conf={row['sensor_confidence']} | "
          f"sent_extreme={row['sent_extreme_state']}")

    return row


# ── Outcome Backfill (v1.1) ────────────────────────

def _fetch_hs300_data() -> dict:
    """获取沪深300日线数据，返回 {date_str: close_price} 字典。

    使用 akshare 下载全部历史，缓存在内存中。
    只在 backfill 时调用，不影响日常 pipeline。
    """
    try:
        import akshare as ak
    except ImportError:
        print("[EvidenceTable] akshare not available, cannot backfill outcomes")
        return {}

    try:
        df = ak.stock_zh_index_daily(symbol="sh000300")
        # df columns: date, open, close, high, low, volume
        prices = {}
        for _, row in df.iterrows():
            try:
                d = str(row["date"]).replace("-", "")
                prices[d] = float(row["close"])
            except (ValueError, KeyError):
                continue
        print(f"[EvidenceTable] Loaded {len(prices)} days of HS300 data")
        return prices
    except Exception as e:
        print(f"[EvidenceTable] Failed to fetch HS300 data: {e}")
        return {}


def _get_trading_days_after(prices: dict, date_str: str, n: int) -> list:
    """获取 date_str 之后的 n 个交易日日期列表 (不含 date_str 当日)。

    需要在 prices 中存在对应日期的数据。
    Returns list of date strings in YYYYMMDD format.
    """
    # Sort all dates
    all_dates = sorted(prices.keys())
    try:
        idx = all_dates.index(date_str)
    except ValueError:
        return []
    # Return the next n trading days
    return all_dates[idx + 1 : idx + 1 + n]


def _compute_outcomes(prices: dict, date_str: str) -> dict:
    """计算一个日期的 T+N Outcome 字段。

    Args:
        prices: {YYYYMMDD: close_price} 字典
        date_str: YYYY-MM-DD 格式的日期

    Returns:
        {T1_return, T3_return, T5_return, max_dd_5d, benchmark_5d} 或空字典
    """
    date_compact = date_str.replace("-", "")
    base_close = prices.get(date_compact)
    if base_close is None or base_close == 0:
        return {}

    trading_days = _get_trading_days_after(prices, date_compact, 5)

    def _compute_return(n: int) -> float | None:
        """Compute return over n trading days."""
        if len(trading_days) >= n:
            target = prices.get(trading_days[n - 1])
            if target and base_close:
                return round((target - base_close) / base_close * 100, 2)
        return None

    def _compute_max_dd() -> float | None:
        """Compute max drawdown over available trading days in the 5-day window."""
        closes = [base_close]
        for d in trading_days:
            c = prices.get(d)
            if c:
                closes.append(c)
        if len(closes) < 2:
            return None
        peak = closes[0]
        max_dd = 0.0
        for c in closes[1:]:
            if c > peak:
                peak = c
            dd = (peak - c) / peak * 100
            if dd > max_dd:
                max_dd = dd
        return round(max_dd, 2)

    t1 = _compute_return(1)
    t3 = _compute_return(3)
    t5 = _compute_return(5)
    max_dd = _compute_max_dd()

    # Only return if we have at least T1 (minimum for any outcome)
    if t1 is None:
        return {}

    return {
        "T1_return": t1,
        "T3_return": t3,
        "T5_return": t5,
        "max_dd_5d": max_dd,
        "benchmark_5d": t5,  # 沪深300 即为基准
    }


def backfill_results(date_str: Optional[str] = None):
    """回填 Evidence Table 中 Outcome 字段。

    扫描 evidence_table.csv，找到 Outcome 字段为空且已过 T+5 的行，
    使用 akshare 获取沪深300 数据计算 T+N 收益并更新。

    Args:
        date_str: 指定日期 (YYYYMMDD)，None 则扫描所有待补行
    """
    if not EVIDENCE_FILE.exists():
        print("[EvidenceTable] No evidence file, nothing to backfill")
        return 0

    # 读取全部行
    rows = []
    with open(EVIDENCE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not rows:
        print("[EvidenceTable] Empty evidence file")
        return 0

    # 检查是否有 Outcome 列
    has_outcome = "T1_return" in (fieldnames or [])
    if not has_outcome:
        print("[EvidenceTable] Outcome columns not present, adding them")
        fieldnames = fieldnames + ["T1_return", "T3_return", "T5_return", "max_dd_5d", "benchmark_5d"]
        for row in rows:
            for col in ["T1_return", "T3_return", "T5_return", "max_dd_5d", "benchmark_5d"]:
                row[col] = ""

    # 确定需要回填的行
    today_compact = datetime.now().strftime("%Y%m%d")

    if date_str:
        targets = [r for r in rows if r.get("date", "") == f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"]
    else:
        targets = []
        for r in rows:
            row_date = r.get("date", "")
            # 检查 Outcome 是否为空
            if r.get("T1_return", "") not in ("", None):
                continue
            # 检查是否已过至少 T+1 (至少需要下一个交易日数据)
            row_compact = row_date.replace("-", "")
            if row_compact >= today_compact:
                continue  # 今天或未来日期，无法回填
            targets.append(r)

    if not targets:
        print("[EvidenceTable] No rows need backfill (all up to date)")
        return 0

    # 获取市场数据
    prices = _fetch_hs300_data()
    if not prices:
        print("[EvidenceTable] Cannot backfill without market data")
        return 0

    # 回填每一行
    updated = 0
    for row in targets:
        row_date = row.get("date", "")
        outcomes = _compute_outcomes(prices, row_date)
        if outcomes:
            for k, v in outcomes.items():
                row[k] = v if v is not None else ""
            updated += 1
            print(f"[EvidenceTable] Backfilled {row_date}: "
                  f"T1={outcomes.get('T1_return')}%, T5={outcomes.get('T5_return')}%, "
                  f"maxDD={outcomes.get('max_dd_5d')}%")
        else:
            print(f"[EvidenceTable] No market data for {row_date}, skipped")

    # 写回文件
    if updated > 0:
        with open(EVIDENCE_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        print(f"[EvidenceTable] {updated} row(s) backfilled, file updated")

    return updated

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AVP Evidence Table v1.1 — daily extraction + T+N backfill")
    parser.add_argument("--date", type=str, default=None, help="Date in YYYYMMDD format")
    parser.add_argument("--backfill", action="store_true", help="Backfill Outcome fields for all pending rows")
    parser.add_argument("--backfill-date", type=str, default=None, help="Backfill a specific date (YYYYMMDD)")
    args = parser.parse_args()

    if args.backfill:
        backfill_results()
    elif args.backfill_date:
        backfill_results(args.backfill_date)
    else:
        run(args.date)
