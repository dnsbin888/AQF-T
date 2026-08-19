"""
Regime Feature Builder v1.0 (2026-08-11)
=========================================
基于 Regime Feature Schema v1.0，从已有 Evidence Table + Daily Reports
计算 41 特征（Snapshot + Delta + Persistence + Divergence），
输出标准化特征矩阵。

用法:
  python features/regime_features.py                    # 处理全部
  python features/regime_features.py --date 20260811    # 指定日期
  python features/regime_features.py --csv              # 仅输出CSV，不打印

输入:
  reports/evidence/evidence_table.csv   ← 55列原始证据
  reports/daily/*_report.json           ← zhatban_rate / promotion_rate

输出:
  reports/evidence/feature_matrix.csv   ← 41特征 + 数据质量标记

设计原则:
  - 纯读→算→写，不调任何外部API
  - 不修改 evidence_table.csv 或其他生产文件
  - 不产生交易信号，不碰 Gate / Pipeline
  - 符合 PA 2026-08-11 裁决: Evidence 标准化，不修改生产逻辑
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from collections import OrderedDict

ROOT = Path(__file__).parent.parent
DAILY_DIR = ROOT / "reports" / "daily"
EVIDENCE_DIR = ROOT / "reports" / "evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "evidence_table.csv"
FEATURE_FILE = EVIDENCE_DIR / "feature_matrix.csv"

# ═══════════════════════════════════════════════════════
# Column Definitions (per Schema v1.0)
# ═══════════════════════════════════════════════════════

# F1: Market Structure (5 features)
F1_COLS = [
    "F1.1_zhatban_rate",
    "F1.2_promotion_rate",
    "F1.3_regime_score",
    "F1.4_zhatban_x_promotion",
    "F1.5_score_acceleration",
]

# F2: Market Breadth (5 features)
F2_COLS = [
    "F2.1_advance_ratio",
    "F2.2_breadth_pct",
    "F2.3_limit_up",
    "F2.4_limit_down",
    "F2.5_limit_ratio",
]

# F3: Capital Flow (7 features)
F3_COLS = [
    "F3.1_margin_bal_5d",
    "F3.2_margin_bal_20d",
    "F3.3_inst_net",
    "F3.4_inst_participation",
    "F3.5_etf_risk_spread",
    "F3.6_margin_trend_enc",     # stable=0, expanding=1, contracting=-1
    "F3.7_inst_flow_enc",        # positive=1, neutral=0, negative=-1
]

# F4: Sentiment & Cycle (8 features)
F4_COLS = [
    "F4.1_sent_score",
    "F4.2_sent_confidence",
    "F4.3_sent_vel_1d",
    "F4.4_sent_vel_5d",
    "F4.5_sent_extreme_enc",     # normal=0, panic=-1, euphoria=1
    "F4.6_cycle_stage_enc",      # startup=0, ferment=1, climax=2, decline=-1
    "F4.7_cycle_scale",
    "F4.8_risk_appetite_enc",    # contracting=-1, neutral=0, expanding=1
]

# F5: Delta (8 features) — computed from F1-F4 day-over-day
F5_COLS = [
    "F5.1_d_zhatban_1d",
    "F5.2_d_zhatban_3d",
    "F5.3_d_promotion_1d",
    "F5.4_d_advance_1d",
    "F5.5_d_limit_up_1d",
    "F5.6_d_limit_down_1d",
    "F5.7_d_margin_5d",
    "F5.8_d_sent_vel_accel",
]

# F6: Persistence (6 features) — computed from history
F6_COLS = [
    "F6.1_consecutive_regime",
    "F6.2_consecutive_stop",
    "F6.3_days_since_normal",
    "F6.4_regime_switch_5d",
    "F6.5_score_trend_3d",
    "F6.6_score_trend_slope",
]

# F7: Divergence (2 features)
F7_COLS = [
    "F7.1_sent_regime_divergence",     # bull_divergence / bear_divergence / aligned
    "F7.2_breadth_zhatban_divergence",  # True / False
]

# Data Quality (5 fields)
Q_COLS = [
    "Q1_source_type",
    "Q2_data_quality",
    "Q3_is_simulator",
    "Q4_is_production_eod",
    "Q5_field_fill_rate",
]

# Outcome Labels (from existing CSV)
OUTCOME_COLS = [
    "L1_regime_phase",
    "L2_trade_allowed",
    "T1_return",
    "T3_return",
    "T5_return",
    "max_dd_5d",
    "benchmark_5d",
]

ALL_FEATURE_COLS = (
    ["date"]
    + F1_COLS + F2_COLS + F3_COLS + F4_COLS
    + F5_COLS + F6_COLS + F7_COLS
    + Q_COLS
    + OUTCOME_COLS
)


# ═══════════════════════════════════════════════════════
# Encoders
# ═══════════════════════════════════════════════════════

def _enc_margin_trend(v: str) -> float | None:
    if v == "stable": return 0
    if v == "expanding": return 1
    if v == "contracting": return -1
    return None

def _enc_inst_flow(v: str) -> float | None:
    if v == "positive": return 1
    if v == "neutral": return 0
    if v == "negative": return -1
    return None

def _enc_extreme(v: str) -> float | None:
    if v == "normal": return 0
    if v == "panic": return -1
    if v == "euphoria": return 1
    return None

def _enc_cycle_stage(v: str) -> float | None:
    if v == "startup": return 0
    if v == "ferment": return 1
    if v == "climax": return 2
    if v == "decline": return -1
    return None

def _enc_risk_appetite(v: str) -> float | None:
    if v == "contracting": return -1
    if v == "neutral": return 0
    if v == "expanding": return 1
    return None


# ═══════════════════════════════════════════════════════
# Data Loading
# ═══════════════════════════════════════════════════════

def _load_daily_report(date_str: str) -> dict:
    """Load daily report JSON for zhatban_rate / promotion_rate."""
    path = DAILY_DIR / f"{date_str}_report.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def load_evidence_rows() -> list[dict]:
    """Read all rows from evidence_table.csv."""
    if not EVIDENCE_FILE.exists():
        print(f"[Features] Evidence file not found: {EVIDENCE_FILE}")
        return []

    with open(EVIDENCE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ═══════════════════════════════════════════════════════
# Feature Computation
# ═══════════════════════════════════════════════════════

def _safe_float(v, default=None):
    """Convert value to float, returning default on failure."""
    if v is None or v == "":
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def _safe_int(v, default=None):
    """Convert value to int, returning default on failure."""
    if v is None or v == "":
        return default
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return default


def compute_snapshot(row: dict, daily_regime: dict) -> dict:
    """Compute F1-F4 snapshot features from one evidence row + daily report."""
    f = {}

    # ── F1: Market Structure ──
    f["F1.1_zhatban_rate"] = _safe_float(daily_regime.get("zhatban_rate"))
    f["F1.2_promotion_rate"] = _safe_float(daily_regime.get("promotion_rate"))
    f["F1.3_regime_score"] = _safe_float(row.get("regime_score"))
    zr = f["F1.1_zhatban_rate"] or 0
    pr = f["F1.2_promotion_rate"] or 0
    f["F1.4_zhatban_x_promotion"] = round(zr * (1 - pr), 4) if zr and pr is not None else None
    f["F1.5_score_acceleration"] = None  # needs T-1, filled in compute_delta

    # ── F2: Market Breadth ──
    f["F2.1_advance_ratio"] = _safe_float(row.get("sent_advance_pct"))
    f["F2.2_breadth_pct"] = _safe_float(row.get("sent_breadth_pct"))
    f["F2.3_limit_up"] = _safe_int(row.get("sent_limit_up"))
    f["F2.4_limit_down"] = _safe_int(row.get("sent_limit_down"))
    lu = f["F2.3_limit_up"] or 0
    ld = f["F2.4_limit_down"] or 1
    f["F2.5_limit_ratio"] = round(lu / max(ld, 1), 2) if lu else None

    # ── F3: Capital Flow ──
    f["F3.1_margin_bal_5d"] = _safe_float(row.get("margin_bal_5d_pct"))
    f["F3.2_margin_bal_20d"] = _safe_float(row.get("margin_bal_20d_pct"))
    f["F3.3_inst_net"] = _safe_float(row.get("inst_net"))
    f["F3.4_inst_participation"] = _safe_float(row.get("inst_participation_pct"))
    f["F3.5_etf_risk_spread"] = _safe_float(row.get("etf_risk_spread"))
    f["F3.6_margin_trend_enc"] = _enc_margin_trend(row.get("margin_trend", ""))
    f["F3.7_inst_flow_enc"] = _enc_inst_flow(row.get("inst_flow", ""))

    # ── F4: Sentiment & Cycle ──
    f["F4.1_sent_score"] = _safe_float(row.get("sent_mkt_score"))
    f["F4.2_sent_confidence"] = _safe_float(row.get("sent_confidence"))
    f["F4.3_sent_vel_1d"] = _safe_float(row.get("sent_vel_1d"))
    f["F4.4_sent_vel_5d"] = _safe_float(row.get("sent_vel_5d"))
    f["F4.5_sent_extreme_enc"] = _enc_extreme(row.get("sent_extreme_state", ""))
    f["F4.6_cycle_stage_enc"] = _enc_cycle_stage(row.get("sent_cycle_stage", ""))
    f["F4.7_cycle_scale"] = _safe_float(row.get("sent_cycle_scale"))
    f["F4.8_risk_appetite_enc"] = _enc_risk_appetite(row.get("sensor_risk_appetite", ""))

    return f


def _field_name_to_delta_key(field: str) -> str | None:
    """Map F5 delta field to the source column it references in T-1."""
    mapping = {
        "F5.1_d_zhatban_1d": "F1.1_zhatban_rate",
        "F5.2_d_zhatban_3d": "F1.1_zhatban_rate",
        "F5.3_d_promotion_1d": "F1.2_promotion_rate",
        "F5.4_d_advance_1d": "F2.1_advance_ratio",
        "F5.5_d_limit_up_1d": "F2.3_limit_up",
        "F5.6_d_limit_down_1d": "F2.4_limit_down",
        "F5.7_d_margin_5d": "F3.1_margin_bal_5d",
        "F5.8_d_sent_vel_accel": "F4.3_sent_vel_1d",
    }
    return mapping.get(field)


def compute_delta(all_rows: list[dict], idx: int) -> dict:
    """Compute F5 Delta features by comparing row idx with T-1, T-2, T-3."""
    f = {c: None for c in F5_COLS}
    row = all_rows[idx]
    row_date = row.get("date", "")

    if idx == 0:
        return f  # first row has no history

    # F5.1, F5.3-F5.8: simple T-1 delta
    for delta_col, source_col in [
        ("F5.1_d_zhatban_1d", "F1.1_zhatban_rate"),
        ("F5.3_d_promotion_1d", "F1.2_promotion_rate"),
        ("F5.4_d_advance_1d", "F2.1_advance_ratio"),
        ("F5.5_d_limit_up_1d", "F2.3_limit_up"),
        ("F5.6_d_limit_down_1d", "F2.4_limit_down"),
        ("F5.7_d_margin_5d", "F3.1_margin_bal_5d"),
        ("F5.8_d_sent_vel_accel", "F4.3_sent_vel_1d"),
    ]:
        cur = _safe_float(row.get(source_col))
        prev = _safe_float(all_rows[idx - 1].get(source_col))
        if cur is not None and prev is not None:
            f[delta_col] = round(cur - prev, 4)

    # F1.5: score_acceleration (fill in snapshot too)
    cur_score = _safe_float(row.get("F1.3_regime_score"))
    prev_score = _safe_float(all_rows[idx - 1].get("F1.3_regime_score"))
    if cur_score is not None and prev_score is not None:
        f["F1.5_score_acceleration"] = round(cur_score - prev_score, 4)
        row["F1.5_score_acceleration"] = f["F1.5_score_acceleration"]

    # F5.2: 3-day mean deviation
    cur_zr = _safe_float(row.get("F1.1_zhatban_rate"))
    prev_zrs = []
    for i in range(max(0, idx - 3), idx):
        z = _safe_float(all_rows[i].get("F1.1_zhatban_rate"))
        if z is not None:
            prev_zrs.append(z)
    if cur_zr is not None and len(prev_zrs) >= 1:
        mean_prev = sum(prev_zrs) / len(prev_zrs)
        f["F5.2_d_zhatban_3d"] = round(cur_zr - mean_prev, 4)

    return f


def compute_persistence(all_rows: list[dict], idx: int) -> dict:
    """Compute F6 Persistence features by scanning historical rows."""
    f = {c: None for c in F6_COLS}
    row = all_rows[idx]
    current_regime = row.get("regime_phase", "")

    # F6.1: consecutive same regime
    consecutive = 1
    for i in range(idx - 1, -1, -1):
        if all_rows[i].get("regime_phase") == current_regime:
            consecutive += 1
        else:
            break
    f["F6.1_consecutive_regime"] = consecutive

    # F6.2: consecutive stop (trade_allowed=false)
    consecutive_stop = 0
    # Check current row: stop = regime_mode is "stop" or max_position_pct is 0
    for i in range(idx, -1, -1):
        r = all_rows[i]
        mode = r.get("regime_mode", "")
        max_pos = _safe_float(r.get("max_position_pct"), 1.0)
        if mode == "stop" or (max_pos is not None and max_pos == 0):
            consecutive_stop += 1
        else:
            break
    f["F6.2_consecutive_stop"] = consecutive_stop

    # F6.3: days since last normal
    days_since = 0
    for i in range(idx - 1, -1, -1):
        if all_rows[i].get("regime_mode") == "normal":
            break
        days_since += 1
    else:
        days_since = None  # never had normal
    f["F6.3_days_since_normal"] = days_since

    # F6.4: regime switches in last 5 days
    regimes = [all_rows[i].get("regime_phase", "") for i in range(max(0, idx - 4), idx + 1)]
    switches = sum(1 for j in range(1, len(regimes)) if regimes[j] != regimes[j-1])
    f["F6.4_regime_switch_5d"] = switches if len(regimes) >= 2 else None

    # F6.5: score 3-day moving average
    scores = []
    for i in range(max(0, idx - 2), idx + 1):
        s = _safe_float(all_rows[i].get("regime_score"))
        if s is not None:
            scores.append(s)
    f["F6.5_score_trend_3d"] = round(sum(scores) / len(scores), 2) if scores else None

    # F6.6: score slope (linear regression over up to 5 days)
    ys = []
    for i in range(max(0, idx - 4), idx + 1):
        s = _safe_float(all_rows[i].get("regime_score"))
        if s is not None:
            ys.append(s)
    if len(ys) >= 2:
        n = len(ys)
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        num = sum((xs[j] - mean_x) * (ys[j] - mean_y) for j in range(n))
        den = sum((xs[j] - mean_x) ** 2 for j in range(n))
        f["F6.6_score_trend_slope"] = round(num / den, 4) if den != 0 else None
    else:
        f["F6.6_score_trend_slope"] = None

    return f


def compute_divergence(row: dict) -> dict:
    """Compute F7 Divergence features."""
    f = {}

    # F7.1: Sensor-Regime divergence
    sent_score = _safe_float(row.get("F4.1_sent_score"), 50)
    regime_phase = row.get("L1_regime_phase", row.get("regime_phase", ""))
    # Sensor bullish: sent_score >= 60
    # Sensor bearish: sent_score < 40
    # Regime bearish: 退潮期 or 冰点期
    # Regime bullish: 高潮期 or 回暖期
    sent_bullish = sent_score is not None and sent_score >= 60
    sent_bearish = sent_score is not None and sent_score < 40
    regime_bearish = regime_phase in ("退潮期", "冰点期")
    regime_bullish = regime_phase in ("高潮期", "回暖期")

    if sent_bullish and regime_bearish:
        f["F7.1_sent_regime_divergence"] = "bull_divergence"
    elif sent_bearish and regime_bullish:
        f["F7.1_sent_regime_divergence"] = "bear_divergence"
    else:
        f["F7.1_sent_regime_divergence"] = "aligned"

    # F7.2: Breadth-Zhatban divergence
    advance = _safe_float(row.get("F2.1_advance_ratio"), 50)
    zhatban = _safe_float(row.get("F1.1_zhatban_rate"), 0)
    f["F7.2_breadth_zhatban_divergence"] = (
        advance is not None and zhatban is not None
        and advance > 50 and zhatban > 0.40
    )

    return f


def compute_data_quality(row: dict, daily_regime: dict) -> dict:
    """Compute Q1-Q5 data quality markers."""
    q = {}

    # Q1: source_type
    source = row.get("data_source", "")
    q["Q1_source_type"] = source if source else "UNKNOWN"

    # Q3: is_simulator
    is_sim = source == "SIMULATOR"
    q["Q3_is_simulator"] = is_sim

    # Q2: data_quality
    if is_sim:
        q["Q2_data_quality"] = "excluded"
    elif source == "AKSHARE_EOD":
        q["Q2_data_quality"] = "production"
    elif source == "PRE_HEALTH_PROTOCOL":
        q["Q2_data_quality"] = "shadow"
    else:
        q["Q2_data_quality"] = "shadow"

    # Q4: is_production_eod
    q["Q4_is_production_eod"] = (source == "AKSHARE_EOD")

    # Q5: field_fill_rate
    # Count non-empty feature fields (F1-F4 only, since F5-F7 depend on history)
    f_fields = F1_COLS + F2_COLS + F3_COLS + F4_COLS
    filled = sum(1 for c in f_fields if row.get(c) not in (None, "", False))
    q["Q5_field_fill_rate"] = round(filled / len(f_fields), 3) if f_fields else 0

    return q


# ═══════════════════════════════════════════════════════
# Main Pipeline
# ═══════════════════════════════════════════════════════

def build_feature_matrix(rows: list[dict]) -> list[dict]:
    """Build full feature matrix from evidence rows."""
    feature_rows = []

    for idx, raw_row in enumerate(rows):
        date_str = raw_row.get("date", "").replace("-", "")
        print(f"  [{idx+1}/{len(rows)}] {date_str} ...", end=" ")

        # Load daily report for zhatban/promotion
        daily = _load_daily_report(date_str) if date_str else {}
        regime_data = daily.get("regime", {})

        # Base row starts with date
        feat_row = OrderedDict()
        feat_row["date"] = raw_row.get("date", "")

        # F1-F4: Snapshot
        snap = compute_snapshot(raw_row, regime_data)
        for col in F1_COLS + F2_COLS + F3_COLS + F4_COLS:
            feat_row[col] = snap.get(col)

        # Load snapshot into a temporary enriched row for delta/persistence
        # (merge raw + snapshot for cross-reference)
        enriched = {**raw_row, **snap}

        # F5: Delta (needs full history)
        delta = compute_delta([{**r, **_build_snapshot_for_row(r)} for r in rows], idx)
        # Use a simpler approach — build all snapshots first, then compute deltas

        # We'll do two-pass approach
        feature_rows.append((feat_row, raw_row, regime_data, snap))

    # Two-pass: first pass builds all snapshots, second pass computes delta/persistence
    final_rows = []
    all_snapshots = []

    for feat_row, raw_row, regime_data, snap in feature_rows:
        # Merge snapshot into feat_row
        for col in F1_COLS + F2_COLS + F3_COLS + F4_COLS:
            feat_row[col] = snap.get(col)
        # Attach data quality metadata early (needed by delta computation)
        source = raw_row.get("data_source", "")
        feat_row["Q1_source_type"] = source if source else "UNKNOWN"
        feat_row["Q2_data_quality"] = (
            "excluded" if source == "SIMULATOR"
            else "production" if source == "AKSHARE_EOD"
            else "shadow"
        )
        all_snapshots.append(feat_row)

    # Second pass: delta, persistence, divergence, quality
    for idx, (feat_row, raw_row, regime_data, snap) in enumerate(feature_rows):
        date_str = raw_row.get("date", "").replace("-", "")

        # F5: Delta
        delta = _compute_delta_from_snapshots(all_snapshots, idx)
        for col in F5_COLS:
            feat_row[col] = delta.get(col)
        # Also fill F1.5 from delta
        if delta.get("F1.5_score_acceleration") is not None:
            feat_row["F1.5_score_acceleration"] = delta["F1.5_score_acceleration"]

        # F6: Persistence
        pers = _compute_persistence_from_snapshots(all_snapshots, idx, rows)
        for col in F6_COLS:
            feat_row[col] = pers.get(col)

        # L: Labels — set BEFORE divergence (F7 needs L1_regime_phase)
        feat_row["L1_regime_phase"] = raw_row.get("regime_phase", "")
        feat_row["L2_trade_allowed"] = (
            raw_row.get("regime_mode") != "stop"
            and _safe_float(raw_row.get("max_position_pct"), 0) > 0
        )

        # F7: Divergence
        div = compute_divergence(feat_row)
        for col in F7_COLS:
            feat_row[col] = div.get(col)

        # Q: Data Quality
        qual = compute_data_quality({**raw_row, **feat_row}, regime_data)
        for col in Q_COLS:
            feat_row[col] = qual.get(col)

        # Outcome
        for oc in ["T1_return", "T3_return", "T5_return", "max_dd_5d", "benchmark_5d"]:
            feat_row[oc] = _safe_float(raw_row.get(oc))

        final_rows.append(feat_row)

        # Summary
        filled = sum(1 for v in feat_row.values() if v not in (None, "", False))
        total = len(ALL_FEATURE_COLS)
        print(f"  [{idx+1}/{len(rows)}] {date_str} → {filled}/{total} fields, "
              f"regime={feat_row['L1_regime_phase']}, "
              f"quality={feat_row['Q2_data_quality']}, "
              f"divergence={feat_row.get('F7.1_sent_regime_divergence', '?')}")

    return final_rows


def _build_snapshot_for_row(row: dict) -> dict:
    """Quick snapshot from raw evidence row (used in two-pass)."""
    f = {}
    zr = _safe_float(row.get("F1.1_zhatban_rate"))
    pr = _safe_float(row.get("F1.2_promotion_rate"))
    f["F1.1_zhatban_rate"] = zr
    f["F1.2_promotion_rate"] = pr
    f["F1.3_regime_score"] = _safe_float(row.get("regime_score"))
    f["F2.1_advance_ratio"] = _safe_float(row.get("sent_advance_pct"))
    f["F2.3_limit_up"] = _safe_int(row.get("sent_limit_up"))
    f["F2.4_limit_down"] = _safe_int(row.get("sent_limit_down"))
    f["F3.1_margin_bal_5d"] = _safe_float(row.get("margin_bal_5d_pct"))
    f["F4.3_sent_vel_1d"] = _safe_float(row.get("sent_vel_1d"))
    return f


def _compute_delta_from_snapshots(all_snapshots: list[dict], idx: int) -> dict:
    """Compute F5 Delta using pre-computed snapshots.

    Skips delta when previous row has insufficient data quality
    (PRE_HEALTH_PROTOCOL / SIMULATOR) to avoid false "data appeared" jumps.
    """
    f = {c: None for c in F5_COLS}
    row = all_snapshots[idx]

    if idx == 0:
        return f

    prev = all_snapshots[idx - 1]

    # Check if prev row has valid sensor data (not PRE_HEALTH_PROTOCOL or SIMULATOR)
    prev_quality = prev.get("Q2_data_quality", "")
    prev_has_valid_data = prev_quality == "production"

    # Simple T-1 deltas — only compute if prev has valid data
    pairs = [
        ("F5.1_d_zhatban_1d", "F1.1_zhatban_rate"),
        ("F5.3_d_promotion_1d", "F1.2_promotion_rate"),
        ("F5.4_d_advance_1d", "F2.1_advance_ratio"),
        ("F5.5_d_limit_up_1d", "F2.3_limit_up"),
        ("F5.6_d_limit_down_1d", "F2.4_limit_down"),
        ("F5.7_d_margin_5d", "F3.1_margin_bal_5d"),
        ("F5.8_d_sent_vel_accel", "F4.3_sent_vel_1d"),
    ]
    for dcol, scol in pairs:
        cur = _safe_float(row.get(scol))
        prv = _safe_float(prev.get(scol))
        if cur is not None and prv is not None and prev_has_valid_data:
            f[dcol] = round(cur - prv, 4)

    # F1.5 score acceleration
    cur_sc = _safe_float(row.get("F1.3_regime_score"))
    prev_sc = _safe_float(prev.get("F1.3_regime_score"))
    if cur_sc is not None and prev_sc is not None and prev_has_valid_data:
        f["F1.5_score_acceleration"] = round(cur_sc - prev_sc, 4)

    # F5.2: 3-day mean deviation — only use production-quality rows
    cur_zr = _safe_float(row.get("F1.1_zhatban_rate"))
    prev_zrs = []
    for i in range(max(0, idx - 3), idx):
        if all_snapshots[i].get("Q2_data_quality") == "production":
            z = _safe_float(all_snapshots[i].get("F1.1_zhatban_rate"))
            if z is not None:
                prev_zrs.append(z)
    if cur_zr is not None and len(prev_zrs) >= 1:
        mean_prev = sum(prev_zrs) / len(prev_zrs)
        f["F5.2_d_zhatban_3d"] = round(cur_zr - mean_prev, 4)

    return f


def _compute_persistence_from_snapshots(
    all_snapshots: list[dict], idx: int, raw_rows: list[dict]
) -> dict:
    """Compute F6 Persistence using pre-computed snapshots and raw rows."""
    f = {c: None for c in F6_COLS}
    row = raw_rows[idx]
    current_regime = row.get("regime_phase", "")

    # F6.1: consecutive same regime
    consecutive = 1
    for i in range(idx - 1, -1, -1):
        if raw_rows[i].get("regime_phase") == current_regime:
            consecutive += 1
        else:
            break
    f["F6.1_consecutive_regime"] = consecutive

    # F6.2: consecutive stop
    consecutive_stop = 0
    for i in range(idx, -1, -1):
        r = raw_rows[i]
        mode = r.get("regime_mode", "")
        max_pos = _safe_float(r.get("max_position_pct"), 1.0)
        if mode == "stop" or (max_pos is not None and max_pos == 0):
            consecutive_stop += 1
        else:
            break
    f["F6.2_consecutive_stop"] = consecutive_stop

    # F6.3: days since last normal
    days_since = 0
    found = False
    for i in range(idx - 1, -1, -1):
        if raw_rows[i].get("regime_mode") == "normal":
            found = True
            break
        days_since += 1
    f["F6.3_days_since_normal"] = days_since if found else max(days_since, 0)

    # F6.4: regime switches in last 5 days
    regimes = [
        raw_rows[i].get("regime_phase", "")
        for i in range(max(0, idx - 4), idx + 1)
    ]
    switches = sum(1 for j in range(1, len(regimes)) if regimes[j] != regimes[j-1])
    f["F6.4_regime_switch_5d"] = switches if len(regimes) >= 2 else None

    # F6.5: score 3-day MA
    scores = []
    for i in range(max(0, idx - 2), idx + 1):
        s = _safe_float(raw_rows[i].get("regime_score"))
        if s is not None:
            scores.append(s)
    f["F6.5_score_trend_3d"] = round(sum(scores) / len(scores), 2) if scores else None

    # F6.6: score slope (linear regression, up to 5 days)
    ys = []
    for i in range(max(0, idx - 4), idx + 1):
        s = _safe_float(raw_rows[i].get("regime_score"))
        if s is not None:
            ys.append(s)
    if len(ys) >= 2:
        n = len(ys)
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        num = sum((xs[j] - mean_x) * (ys[j] - mean_y) for j in range(n))
        den = sum((xs[j] - mean_x) ** 2 for j in range(n))
        f["F6.6_score_trend_slope"] = round(num / den, 4) if den != 0 else None
    else:
        f["F6.6_score_trend_slope"] = None

    return f


def write_feature_matrix(feature_rows: list[dict]):
    """Write feature matrix to CSV."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    with open(FEATURE_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ALL_FEATURE_COLS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(feature_rows)

    print(f"\n[Features] Written {len(feature_rows)} rows to {FEATURE_FILE}")


def print_summary(feature_rows: list[dict]):
    """Print a human-readable summary."""
    print("\n" + "=" * 70)
    print("  Regime Feature Matrix v1.0 — Summary")
    print("=" * 70)

    # Count quality distribution
    quality_counts = {}
    for r in feature_rows:
        q = r.get("Q2_data_quality", "unknown")
        quality_counts[q] = quality_counts.get(q, 0) + 1

    print(f"  Total rows:       {len(feature_rows)}")
    print(f"  Quality distribution: {quality_counts}")

    # Count divergence
    div_counts = {}
    for r in feature_rows:
        d = r.get("F7.1_sent_regime_divergence", "unknown")
        div_counts[d] = div_counts.get(d, 0) + 1

    print(f"  Divergence:       {div_counts}")

    # Latest row features with values
    if feature_rows:
        latest = feature_rows[-1]
        print(f"\n  Latest row: {latest.get('date')}")
        print(f"    Regime: {latest.get('L1_regime_phase')} | "
              f"Trade: {latest.get('L2_trade_allowed')} | "
              f"Quality: {latest.get('Q2_data_quality')}")
        print(f"    F1.1 zhatban: {latest.get('F1.1_zhatban_rate')} | "
              f"F1.2 promotion: {latest.get('F1.2_promotion_rate')} | "
              f"F1.3 score: {latest.get('F1.3_regime_score')}")
        print(f"    F2.1 advance: {latest.get('F2.1_advance_ratio')}% | "
              f"F2.3 limit_up: {latest.get('F2.3_limit_up')} | "
              f"F2.4 limit_down: {latest.get('F2.4_limit_down')}")
        print(f"    F4.1 sentiment: {latest.get('F4.1_sent_score')} | "
              f"F4.3 vel_1d: {latest.get('F4.3_sent_vel_1d')} | "
              f"F4.8 risk: {latest.get('F4.8_risk_appetite_enc')}")
        print(f"    F6.1 consec_regime: {latest.get('F6.1_consecutive_regime')}d | "
              f"F6.2 consec_stop: {latest.get('F6.2_consecutive_stop')}d | "
              f"F6.4 switches_5d: {latest.get('F6.4_regime_switch_5d')}")
        print(f"    F7.1 divergence: {latest.get('F7.1_sent_regime_divergence')} | "
              f"F7.2 breadth_zhatban: {latest.get('F7.2_breadth_zhatban_divergence')}")

        # Delta columns for latest
        deltas = {k: v for k, v in latest.items()
                  if k.startswith("F5.") and v is not None}
        if deltas:
            print(f"    F5 Delta: {deltas}")

    print("=" * 70)


# ═══════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════

def main(date_str: Optional[str] = None, csv_only: bool = False):
    """Main entry point."""
    if not EVIDENCE_FILE.exists():
        print(f"[Features] ERROR: Evidence file not found: {EVIDENCE_FILE}")
        return 1

    rows = load_evidence_rows()
    if not rows:
        print("[Features] No evidence rows loaded")
        return 1

    if date_str:
        rows = [r for r in rows if r.get("date", "") == f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"]
        if not rows:
            print(f"[Features] Date {date_str} not found in evidence table")
            return 1

    print(f"[Features] Processing {len(rows)} evidence row(s)...")

    feature_rows = build_feature_matrix(rows)
    write_feature_matrix(feature_rows)

    if not csv_only:
        print_summary(feature_rows)

    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Regime Feature Builder v1.0 — Evidence → Feature Matrix"
    )
    parser.add_argument("--date", type=str, default=None, help="Date in YYYYMMDD format")
    parser.add_argument("--csv", action="store_true", help="CSV output only, no summary")
    args = parser.parse_args()

    sys.exit(main(args.date, args.csv))
