"""
ETF Share Flow Shadow Sensor v1.0 (2026-08-11)
================================================
AVP 冻结期 — 只采集，不决策。

背景:
  - 北向资金 2024-08 起监管关停，全行业不可用
  - ETF 份额变化 = 替代"聪明钱"信号的关键维度
  - 当前 ETFSensor 只看价格涨跌，丢失了资金流核心信息

数据源:
  akshare fund_etf_spot_em() → 最新份额 列

覆盖 ETF:
  510050 (上证50)     — large
  510300 (沪深300)    — large
  510500 (中证500)    — mid
  512100 (中证1000)   — small
  588000 (科创50)     — small
  159915 (创业板)     — small

信号逻辑:
  - 下跌+份额增加 → 抄底资金进场 (bullish divergence)
  - 上涨+份额减少 → 获利了结       (bearish divergence)
  - 份额连续3日净增 → 机构配置型流入
  - 份额连续3日净减 → 机构撤退

输出:
  reports/sensor/etf_share_flow/YYYYMMDD_etf_share.json
  reports/sensor/etf_share_flow/latest_etf_share.json

用法:
  python sensors/etf_share_flow.py                  # 今天
  python sensors/etf_share_flow.py --date 20260810  # 指定日期

禁止事项:
  ❌ 不改 AQF-T regime / Gate / position_scale
  ❌ 不生成交易信号
  ✅ 每日采集 → Observation → 8/19 决定是否接入主 Sensor
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

ROOT = Path(__file__).parent.parent
OUTPUT_DIR = ROOT / "reports" / "sensor" / "etf_share_flow"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 目标 ETF ──────────────────────────────────────────
TARGET_ETFS = {
    "510050": {"name": "上证50ETF",   "category": "large"},
    "510300": {"name": "沪深300ETF",  "category": "large"},
    "510500": {"name": "中证500ETF",  "category": "mid"},
    "512100": {"name": "中证1000ETF", "category": "small"},
    "588000": {"name": "科创50ETF",   "category": "small"},
    "159915": {"name": "创业板ETF",   "category": "small"},
}


def _safe_float(v, default=0.0) -> float:
    try:
        return float(v) if v is not None else default
    except (ValueError, TypeError):
        return default


def collect(date_str: Optional[str] = None) -> dict:
    """采集 ETF 份额数据 — 纯读操作，不写任何生产文件"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        import akshare as ak
        df = ak.fund_etf_spot_em()
    except ImportError:
        return {
            "status": "error",
            "error": "akshare not available",
            "date": date_str,
            "timestamp": timestamp,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"fund_etf_spot_em failed: {e}",
            "date": date_str,
            "timestamp": timestamp,
        }

    # ── 提取目标 ETF 的份额 + 价格 ──
    etfs = {}
    total_share_change_pct = 0.0
    inflow_count = 0
    outflow_count = 0

    for code, meta in TARGET_ETFS.items():
        match = df[df["代码"] == code]
        if len(match) == 0:
            etfs[code] = {"name": meta["name"], "status": "not_found"}
            continue

        row = match.iloc[0]
        current_share = _safe_float(row.get("最新份额"), 0)
        current_price = _safe_float(row.get("最新价"), 0)
        change_pct = _safe_float(row.get("涨跌幅"), 0)
        volume = _safe_float(row.get("成交量"), 0)
        amount = _safe_float(row.get("成交额"), 0)

        # 读昨天份额做对比
        prev_share = _load_previous_share(code, date_str)
        share_change = current_share - prev_share if prev_share > 0 and current_share > 0 else 0
        share_change_pct = (share_change / prev_share * 100) if prev_share > 0 else 0

        est_flow = share_change * current_price if share_change != 0 else 0  # 估算资金流

        direction = "net_zero"
        if share_change_pct > 0.5:
            direction = "net_inflow"
            inflow_count += 1
        elif share_change_pct < -0.5:
            direction = "net_outflow"
            outflow_count += 1

        etfs[code] = {
            "name": meta["name"],
            "category": meta["category"],
            "close": current_price,
            "change_pct": round(change_pct, 2),
            "volume": int(volume),
            "amount": amount,
            "shares": current_share,                         # 最新份额
            "share_change": round(share_change, 2),          # 份额变化
            "share_change_pct": round(share_change_pct, 2),  # 份额变化%
            "est_flow": round(est_flow, 2),                  # 估算资金流
            "direction": direction,
        }

    # ── 汇总 ──
    large_etfs = [e for c, e in etfs.items() if TARGET_ETFS[c]["category"] == "large"]
    small_etfs = [e for c, e in etfs.items() if TARGET_ETFS[c]["category"] in ("small", "mid")]

    large_share_chg = sum(
        e.get("share_change_pct", 0) for e in large_etfs
        if e.get("status") != "not_found"
    )
    small_share_chg = sum(
        e.get("share_change_pct", 0) for e in small_etfs
        if e.get("status") != "not_found"
    )

    # 整体方向
    if inflow_count > outflow_count:
        overall_direction = "net_inflow"
    elif outflow_count > inflow_count:
        overall_direction = "net_outflow"
    else:
        overall_direction = "net_zero"

    # 背离检测: price vs share flow
    divergence_signals = []
    for code, e in etfs.items():
        if e.get("status") == "not_found":
            continue
        chg = e.get("change_pct", 0)
        share_chg = e.get("share_change_pct", 0)
        if chg < -1 and share_chg > 1:
            divergence_signals.append(f"{e['name']}: 跌{chg}%+份额增{share_chg}% → 抄底")
        elif chg > 1 and share_chg < -1:
            divergence_signals.append(f"{e['name']}: 涨{chg}%+份额减{share_chg}% → 获利了结")

    result = {
        "report_type": "etf_share_flow",
        "version": "1.0",
        "status": "shadow",
        "date": date_str,
        "timestamp": timestamp,
        "etfs": etfs,
        "summary": {
            "overall_direction": overall_direction,
            "inflow_count": inflow_count,
            "outflow_count": outflow_count,
            "large_cap_share_chg_pct": round(large_share_chg, 2),
            "small_cap_share_chg_pct": round(small_share_chg, 2),
            "divergence_signals": divergence_signals,
            "note": "AVP Shadow — 仅供参考，不参与交易决策",
        },
        "warnings": [],
    }

    return result


def _load_previous_share(code: str, current_date: str) -> float:
    """尝试读取前一交易日的份额数据"""
    # 尝试昨天
    try:
        dt = datetime.strptime(current_date, "%Y-%m-%d")
        prev_date = (dt - timedelta(days=1)).strftime("%Y-%m-%d")
    except ValueError:
        return 0

    prev_file = OUTPUT_DIR / f"{prev_date.replace('-', '')}_etf_share.json"
    if prev_file.exists():
        try:
            prev_data = json.loads(prev_file.read_text(encoding="utf-8"))
            prev_etf = prev_data.get("etfs", {}).get(code, {})
            return _safe_float(prev_etf.get("shares"), 0)
        except (json.JSONDecodeError, OSError):
            pass

    # 尝试更早的
    for offset in range(2, 6):
        try:
            dt = datetime.strptime(current_date, "%Y-%m-%d")
            earlier = (dt - timedelta(days=offset)).strftime("%Y-%m-%d")
            f = OUTPUT_DIR / f"{earlier.replace('-', '')}_etf_share.json"
            if f.exists():
                prev_data = json.loads(f.read_text(encoding="utf-8"))
                prev_etf = prev_data.get("etfs", {}).get(code, {})
                val = _safe_float(prev_etf.get("shares"), 0)
                if val > 0:
                    return val
        except Exception:
            continue

    return 0


def _write_report(result: dict, date_str: str):
    """写入每日报告和最新快照"""
    date_compact = date_str.replace("-", "")
    daily_file = OUTPUT_DIR / f"{date_compact}_etf_share.json"
    latest_file = OUTPUT_DIR / "latest_etf_share.json"

    daily_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ETFShareFlow] Written: {daily_file}")
    print(f"[ETFShareFlow] Latest:  {latest_file}")


def run(date_str: Optional[str] = None):
    """主入口"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    print(f"[ETFShareFlow] {date_str} — collecting ETF share flow...")

    result = collect(date_str)

    if result.get("status") == "error":
        print(f"[ETFShareFlow] ERROR: {result.get('error')}")
        return result

    _write_report(result, date_str)

    # 摘要
    s = result.get("summary", {})
    print(f"[ETFShareFlow] Direction:    {s.get('overall_direction')}")
    print(f"[ETFShareFlow] Inflow/Outflow: {s.get('inflow_count')}/{s.get('outflow_count')}")
    print(f"[ETFShareFlow] Large cap:     {s.get('large_cap_share_chg_pct')}%")
    print(f"[ETFShareFlow] Small cap:     {s.get('small_cap_share_chg_pct')}%")
    divs = s.get("divergence_signals", [])
    if divs:
        for d in divs:
            print(f"[ETFShareFlow] ⚠️ Divergence: {d}")
    else:
        print(f"[ETFShareFlow] No price/share divergence detected")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ETF Share Flow Shadow Sensor v1.0")
    parser.add_argument("--date", type=str, default=None, help="Date in YYYYMMDD or YYYY-MM-DD")
    args = parser.parse_args()

    date_str = args.date
    if date_str and len(date_str) == 8:
        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    run(date_str)
