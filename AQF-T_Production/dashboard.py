"""
AQF-T Web Dashboard — 大脑状态监控台
======================================
零依赖, 只读JSON, http://127.0.0.1:8080
启动: python dashboard.py
"""
import json
import os
import psutil
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

ROOT = Path(__file__).parent
REPORTS_DAILY = ROOT / "reports" / "daily"
REPORTS_EXEC = ROOT / "reports" / "execution"
EVIDENCE_FILE = ROOT / "evidence" / "PHASE2_DATA_EVIDENCE_SIM.json"
PORT = 8080

# ── Data readers (只读, 永不修改) ──

def _latest_json(directory: Path) -> dict | None:
    """读取目录下最新的JSON文件"""
    if not directory.exists():
        return None
    files = sorted(directory.glob("*.json"), reverse=True)
    for f in files:
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
    return None

def get_daily_report() -> dict | None:
    """今日报告, 找不到用最近一份"""
    today = datetime.now().strftime("%Y%m%d")
    today_file = REPORTS_DAILY / f"{today}_report.json"
    if today_file.exists():
        try:
            return json.loads(today_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return _latest_json(REPORTS_DAILY)

def get_execution_report() -> dict | None:
    return _latest_json(REPORTS_EXEC)

def get_evidence_meta() -> dict:
    if EVIDENCE_FILE.exists():
        try:
            return json.loads(EVIDENCE_FILE.read_text(encoding="utf-8")).get("meta", {})
        except (json.JSONDecodeError, OSError):
            pass
    return {}

def get_qmt_status() -> str:
    try:
        from xtquant import xtdata
        return "CONNECTED"
    except ImportError:
        return "UNAVAILABLE"

def get_db_status() -> str:
    import sqlite3
    db_path = ROOT / "data" / "aqft.db"
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute("SELECT 1")
            conn.close()
            return "OK"
        except Exception:
            return "ERROR"
    return "NO DB"

# ── HTML renderer ──

def render() -> str:
    daily = get_daily_report()
    exec_rpt = get_execution_report()
    evidence_meta = get_evidence_meta()

    # ── 环境标识 ──
    not_live = evidence_meta.get("not_live", True)
    source = evidence_meta.get("source", "SIMULATOR")
    if not_live:
        env_badge = f'[SIMULATION] Source: {source} | Not Live'
        env_color = "#e8a838"
    else:
        env_badge = f'[LIVE] Source: {source}'
        env_color = "#38a838"

    # ── 系统状态 ──
    regime = daily.get("regime", {}) if daily else {}
    health = daily.get("health", {}) if daily else {}
    pipeline = daily.get("pipeline", {}) if daily else {}
    account = daily.get("account", {}) if daily else {}
    signals = daily.get("signals", []) if daily else []
    fills = daily.get("fills", []) if daily else []
    exposure = daily.get("exposure", {}) if daily else {}
    errors = pipeline.get("errors", []) if daily else []

    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    qmt = get_qmt_status()
    db = get_db_status()

    phase = regime.get("phase", "N/A")
    mode = regime.get("operation_mode", "N/A")
    confidence = regime.get("regime_confidence", 0)

    total_candidates = pipeline.get("total_candidates", 0)
    total_signals = pipeline.get("total_signals", 0)
    total_fills = pipeline.get("total_fills", 0)
    total_rejected = pipeline.get("total_rejected", 0)

    total_value = account.get("total_value", 0)
    cash = account.get("cash", 0)
    positions_count = account.get("positions", 0)

    # ── KillSwitch ──
    ks_file = ROOT / "runtime" / "killswitch_state.json"
    ks_active = False
    ks_reason = ""
    if ks_file.exists():
        try:
            ks = json.loads(ks_file.read_text(encoding="utf-8"))
            ks_active = ks.get("active", False)
            ks_reason = ks.get("reason", "")
        except Exception:
            pass

    # ── 拒绝原因 (P0-1: 归类聚合) ──
    import re
    reject_reasons: dict[str, int] = {}
    for f in fills:
        if f.get("status") != "FILLED":
            raw = f.get("reason", "unknown")
            # 去掉百分比数字, 归类: "总仓位超40%: 49.1%" -> "总仓位超40%"
            reason = re.sub(r':\s*[\d.]+%?$', '', raw).strip()
            reject_reasons[reason] = reject_reasons.get(reason, 0) + 1

    # ── Strategy 展示映射 (P0-2) ──
    STRATEGY_LABELS = {
        "reseal": "Path A 回封板",
        "trend": "Path B1 趋势",
        "theme": "Path B2 题材",
        "intraday": "Path B3 日内",
        "ladder": "LadderScore",
        "leader": "LeaderLifeCycle",
        "emotion": "EmotionCycle",
    }

    # ── Sector 空值处理 (P0-3) ──
    sector_exposure = exposure.get("sector_exposure", {})
    sector_display = {}
    for k, v in sector_exposure.items():
        label = k if k.strip() else "未分类"
        sector_display[label] = v

    # ── Pattern Evidence (P0-4) ──
    evidence_data = {}
    if EVIDENCE_FILE.exists():
        try:
            evidence_data = json.loads(EVIDENCE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    pattern_evidence = evidence_data.get("pattern_evidence", {}).get("patterns", {})
    evidence_version = evidence_data.get("meta", {}).get("evidence_version", "")

    # ── 成交明细 ──
    fill_rows = ""
    for f in fills[:10]:
        sym = f.get("symbol", "")
        act = f.get("action", "")
        qty = f.get("fill_quantity", 0)
        price = f.get("fill_price", 0)
        status = f.get("status", "")
        reason = f.get("reason", "")
        color = "#4caf50" if status == "FILLED" else "#f44336"
        fill_rows += f"""
        <tr>
          <td>{sym}</td><td>{act}</td><td>{qty}</td>
          <td>{price:.2f}</td>
          <td style="color:{color}">{status}</td>
          <td style="font-size:12px;color:#888">{reason}</td>
        </tr>"""

    # ── 信号明细 ──
    signal_rows = ""
    for s in signals[:5]:
        strat_raw = s.get('strategy', '')
        strat_label = STRATEGY_LABELS.get(strat_raw, strat_raw)
        signal_rows += f"""
        <tr>
          <td>{s.get('symbol','')}</td><td>{s.get('action','')}</td>
          <td>{strat_label}</td><td>{s.get('position_pct',0):.0%}</td>
          <td>{s.get('confidence',0):.2f}</td>
          <td style="font-size:12px;color:#888">{s.get('reasoning','')}</td>
        </tr>"""

    # ── 风险拒绝 ──
    reject_rows = ""
    for reason, count in sorted(reject_reasons.items(), key=lambda x: -x[1])[:10]:
        reject_rows += f"<tr><td>{reason}</td><td>{count}</td></tr>"

    # ── KillSwitch warning ──
    ks_html = ""
    if ks_active:
        ks_html = f"""
        <div style="background:#c62828;color:#fff;padding:12px 20px;margin-bottom:16px;border-radius:4px;font-weight:bold">
          [WARN] KILLSWITCH ACTIVE — {ks_reason}
        </div>"""

    # ── Errors ──
    error_html = ""
    if errors:
        error_html = "<div style='background:#fff3e0;padding:12px;margin-top:8px;border-radius:4px'><b>Errors:</b><ul>" + \
                     "".join(f"<li style='font-size:12px'>{e}</li>" for e in errors[:5]) + "</ul></div>"

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="30">
<title>AQF-T Dashboard</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}}
h1{{font-size:22px;margin-bottom:4px}}
h2{{font-size:15px;color:#8b949e;margin-bottom:16px;font-weight:normal}}
.badge{{display:inline-block;padding:4px 12px;border-radius:3px;font-size:12px;font-weight:bold;color:#fff;background:{env_color};margin-bottom:12px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:16px;margin-bottom:12px}}
.row{{display:flex;gap:12px;flex-wrap:wrap}}
.col{{flex:1;min-width:200px}}
.stat{{font-size:28px;font-weight:bold}}
.stat-label{{font-size:11px;color:#8b949e;text-transform:uppercase}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;padding:6px 8px;border-bottom:1px solid #30363d;color:#8b949e;font-weight:normal;font-size:11px}}
td{{padding:6px 8px;border-bottom:1px solid #21262d}}
.green{{color:#3fb950}}
.red{{color:#f85149}}
.yellow{{color:#d2991d}}
</style>
</head>
<body>

<h1>AQF-T Dashboard</h1>
<h2>Personal Quant Trading OS — V1.2</h2>
<div class="badge">{env_badge}</div>
{ks_html}

<!-- 系统状态 -->
<div class="card">
  <div class="row">
    <div class="col">
      <div class="stat-label">Market Regime</div>
      <div class="stat" style="font-size:20px">{phase} <span style="font-size:13px;color:#8b949e">({mode}, conf={confidence:.2f})</span></div>
    </div>
    <div class="col">
      <div class="stat-label">QMT</div>
      <div class="stat" style="font-size:16px;color:{'#3fb950' if qmt == 'CONNECTED' else '#f85149'}">{qmt}</div>
    </div>
    <div class="col">
      <div class="stat-label">DB</div>
      <div class="stat" style="font-size:16px;color:{'#3fb950' if db == 'OK' else '#f85149'}">{db}</div>
    </div>
    <div class="col">
      <div class="stat-label">CPU</div>
      <div class="stat" style="font-size:16px">{cpu:.0f}%</div>
    </div>
    <div class="col">
      <div class="stat-label">MEM</div>
      <div class="stat" style="font-size:16px">{mem:.0f}%</div>
    </div>
    <div class="col">
      <div class="stat-label">KillSwitch</div>
      <div class="stat" style="font-size:16px;color:{'#f85149' if ks_active else '#3fb950'}">{'ACTIVE' if ks_active else 'SAFE'}</div>
    </div>
  </div>
</div>

<!-- 今日交易 -->
<div class="card">
  <div class="row">
    <div class="col">
      <div class="stat-label">Candidates</div>
      <div class="stat">{total_candidates}</div>
    </div>
    <div class="col">
      <div class="stat-label">Signals</div>
      <div class="stat">{total_signals}</div>
    </div>
    <div class="col">
      <div class="stat-label">Fills</div>
      <div class="stat green">{total_fills}</div>
    </div>
    <div class="col">
      <div class="stat-label">Rejected</div>
      <div class="stat red">{total_rejected}</div>
    </div>
    <div class="col">
      <div class="stat-label">Positions</div>
      <div class="stat">{positions_count}</div>
    </div>
    <div class="col">
      <div class="stat-label">Account Value</div>
      <div class="stat" style="font-size:18px">RMB {total_value:,.0f}</div>
    </div>
    <div class="col">
      <div class="stat-label">Cash</div>
      <div class="stat" style="font-size:18px">RMB {cash:,.0f}</div>
    </div>
  </div>
  <!-- Exposure -->
  <div style="margin-top:12px;font-size:12px;color:#8b949e">
    Total Exposure: {exposure.get('total_exposure_pct',0)}% |
    Daily New: {exposure.get('daily_new_exposure_pct',0)}% |
    Sector: {sector_display}
  </div>
  <!-- Pattern Evidence -->
  <div style="margin-top:8px;font-size:12px;color:#8b949e">
    Evidence v{evidence_version} |
    {" | ".join(f"{name}: {p.get('status','?')}" for name, p in pattern_evidence.items()) if pattern_evidence else 'No pattern evidence yet'}
  </div>
  {error_html}
</div>

<!-- 交易明细 -->
<div class="row">
  <div class="col" style="flex:2">
    <div class="card">
      <h2 style="margin-bottom:8px">Fills (Recent 10)</h2>
      <table>
        <tr><th>Symbol</th><th>Action</th><th>Qty</th><th>Price</th><th>Status</th><th>Reason</th></tr>
        {fill_rows if fill_rows else '<tr><td colspan="6" style="color:#8b949e">No fills yet</td></tr>'}
      </table>
    </div>
  </div>
  <div class="col">
    <div class="card">
      <h2 style="margin-bottom:8px">Risk Rejects</h2>
      <table>
        <tr><th>Reason</th><th>Count</th></tr>
        {reject_rows if reject_rows else '<tr><td colspan="2" style="color:#8b949e">None</td></tr>'}
      </table>
    </div>
  </div>
</div>

<!-- 信号明细 -->
<div class="card">
  <h2 style="margin-bottom:8px">Decision Signals (Recent 5)</h2>
  <table>
    <tr><th>Symbol</th><th>Action</th><th>Strategy</th><th>Position</th><th>Confidence</th><th>Reasoning</th></tr>
    {signal_rows if signal_rows else '<tr><td colspan="6" style="color:#8b949e">No signals yet</td></tr>'}
  </table>
</div>

<!-- Footer -->
<div style="text-align:center;font-size:11px;color:#484f58;margin-top:16px">
  AQF-T V1.2 | Auto-refresh 30s | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>

</body>
</html>"""
    return html


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html = render()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # silent


def main():
    print(f"\n  AQF-T Dashboard")
    print(f"  http://127.0.0.1:{PORT}")
    print(f"  Ctrl+C to stop\n")
    server = HTTPServer(("127.0.0.1", PORT), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dashboard stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
