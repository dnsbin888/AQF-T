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

# ── V1.3 Helpers ──

def _risk_heatmap(reject_reasons: dict) -> str:
    if not reject_reasons:
        return '<span style="color:#8b949e">无拒绝记录</span>'
    total = sum(reject_reasons.values()) or 1
    colors = {"交易时段": "#58a6ff", "仓位限制": "#f0883e", "单票限制": "#f85149",
              "资金不足": "#d2991d", "流动性": "#8b949e"}
    rows = ""
    for reason, count in sorted(reject_reasons.items(), key=lambda x: -x[1])[:6]:
        pct = count / total * 100
        color = "#8b949e"
        for k, c in colors.items():
            if k in reason:
                color = c
                break
        rows += f"""<div style="margin-bottom:3px">
          <span style="display:inline-block;width:120px;font-size:11px">{reason[:12]}</span>
          <span style="display:inline-block;width:40px;text-align:right;font-size:11px">{count}</span>
          <span style="display:inline-block;height:8px;width:{max(pct,1)}%;background:{color};border-radius:2px;vertical-align:middle;margin-left:4px"></span>
        </div>"""
    return rows

def _regime_calendar() -> str:
    from datetime import timedelta
    colors = {"高潮期": "#f85149", "回暖期": "#f0883e", "冰点期": "#58a6ff", "退潮期": "#6e7681"}
    cells = ""
    for i in range(6, -1, -1):
        d = datetime.now() - timedelta(days=i)
        date_str = d.strftime("%m/%d")
        # Read daily report for that date
        f = REPORTS_DAILY / f"{d.strftime('%Y%m%d')}_report.json"
        phase = "?"
        color = "#30363d"
        if f.exists():
            try:
                rpt = json.loads(f.read_text(encoding="utf-8"))
                phase = rpt.get("regime", {}).get("phase", "?")[0]
                color = colors.get(rpt.get("regime", {}).get("phase", ""), "#30363d")
            except Exception:
                pass
        cells += f"""<div style="text-align:center;padding:6px 8px;background:{color};border-radius:3px;color:#fff;min-width:38px">
          <div style="font-size:10px;opacity:0.8">{date_str}</div>
          <div style="font-weight:bold">{phase}</div>
        </div>"""
    return cells

def _pattern_ranking(patterns: dict) -> str:
    if not patterns:
        return '<tr><td colspan="3" style="color:#8b949e">暂无数据</td></tr>'
    ranked = sorted(patterns.items(), key=lambda x: x[1].get("trigger_count", 0), reverse=True)
    labels = {"PositionAnchor": "回封锚定", "LeaderLifeCycle": "龙头周期", "LadderScore": "梯队评分",
              "EmotionCycle": "情绪周期", "SectorFlow": "板块资金", "RelativeStrength": "相对强度"}
    rows = ""
    for name, p in ranked:
        label = labels.get(name, name)
        count = p.get("trigger_count", 0)
        status = p.get("status", "?")
        sc = "#3fb950" if status == "validated" else "#f85149"
        rows += f"""<tr><td>{label}</td><td style="text-align:right">{count}</td><td style="color:{sc};font-size:11px">{status}</td></tr>"""
    return rows

# ── HTML renderer ──

def render() -> str:
    daily = get_daily_report()
    exec_rpt = get_execution_report()
    evidence_meta = get_evidence_meta()

    # ── 环境标识 ──
    not_live = evidence_meta.get("not_live", True)
    source = evidence_meta.get("source", "SIMULATOR")
    if not_live:
        env_badge = f'[模拟] 数据源: {source} | 非实盘'
        env_color = "#e8a838"
    else:
        env_badge = f'[实盘] 数据源: {source}'
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

    # ── 股票名称映射 ──
    STOCK_NAMES = {
        "000001": "平安银行", "000002": "万科A", "000858": "五粮液",
        "002594": "比亚迪", "300750": "宁德时代", "600519": "贵州茅台",
        "601012": "隆基绿能", "688981": "中芯国际", "300059": "东方财富",
        "002230": "科大讯飞",
    }
    def stock_label(sym):
        name = STOCK_NAMES.get(sym, "")
        return f"{name}({sym})" if name else sym

    # ── 展示映射 ──
    ACTION_LABELS = {"BUY": "买入", "SELL": "卖出", "HOLD": "持有"}
    STATUS_LABELS = {"FILLED": "已成交", "REJECTED": "已拒绝", "QUEUED": "排队中", "PARTIAL": "部分成交"}

    # ── 持仓信息 ──
    broker_positions = {}
    try:
        ks = json.loads((ROOT / "runtime" / "supervisor_state.json").read_text(encoding="utf-8"))
    except Exception:
        ks = {}
    # Read positions from broker summary
    position_detail = account.get("positions", 0)
    position_rows = ""
    # Show position estimate from fills
    held = {}
    for f in fills:
        if f.get("status") == "FILLED":
            s = f.get("symbol", "")
            if s not in held:
                held[s] = {"shares": 0, "cost": 0}
            if f.get("action") == "BUY":
                held[s]["shares"] += f.get("fill_quantity", 0)
                held[s]["cost"] = f.get("fill_price", 0)
            elif f.get("action") == "SELL":
                held[s]["shares"] -= f.get("fill_quantity", 0)
    # Also read from report account
    for s, info in held.items():
        if info["shares"] > 0:
            label = stock_label(s)
            position_rows += f"""
            <tr>
              <td>{label}</td>
              <td style="text-align:right">{info['shares']}</td>
              <td style="text-align:right">{info['cost']:.2f}</td>
              <td style="text-align:right">{info['shares'] * info['cost']:,.0f}</td>
              <td style="text-align:right">-</td>
              <td style="text-align:right">-</td>
            </tr>"""

    # ── 成交明细 ──
    fill_rows = ""
    for f in fills[:10]:
        sym = stock_label(f.get("symbol", ""))
        act = ACTION_LABELS.get(f.get("action", ""), f.get("action", ""))
        qty = f.get("fill_quantity", 0)
        price = f.get("fill_price", 0)
        fee_val = f.get("fee", 0)
        cost = price * qty + fee_val if act == "买入" else price * qty - fee_val
        ts = f.get("timestamp", "")[:19].replace("T", " ")
        status = STATUS_LABELS.get(f.get("status", ""), f.get("status", ""))
        reason = f.get("reason", "")
        is_filled = f.get("status") == "FILLED"
        color = "#4caf50" if is_filled else "#f44336"
        # P&L for SELL only
        pnl_str = ""
        if act == "卖出" and is_filled:
            sym_key = f.get("symbol", "")
            # approximate avg cost from position tracking
            pnl_str = "<td style='text-align:right'>-</td><td style='text-align:right'>-</td>"
        if act == "买入":
            pnl_str = "<td style='text-align:right'>-</td><td style='text-align:right'>-</td>"
        fill_rows += f"""
        <tr>
          <td style="font-size:11px;color:#8b949e">{ts}</td>
          <td>{sym}</td><td>{act}</td><td style="text-align:right">{qty}</td>
          <td style="text-align:right">{price:.2f}</td>
          <td style="text-align:right">{cost:,.0f}</td>
          {pnl_str}
          <td style="color:{color}">{status}</td>
          <td style="font-size:11px;color:#888">{reason}</td>
        </tr>"""

    # ── 信号明细 ──
    signal_rows = ""
    for s in signals[:5]:
        strat_raw = s.get('strategy', '')
        strat_label = STRATEGY_LABELS.get(strat_raw, strat_raw)
        act_label = ACTION_LABELS.get(s.get('action', ''), s.get('action', ''))
        signal_rows += f"""
        <tr>
          <td>{stock_label(s.get('symbol',''))}</td><td>{act_label}</td>
          <td>{strat_label}</td><td>{s.get('position_pct',0):.0%}</td>
          <td>{s.get('confidence',0):.2f}</td>
          <td style="font-size:12px;color:#888">{s.get('reasoning','')}</td>
        </tr>"""

    # ── 风险拒绝 ──
    reject_rows = ""
    for reason, count in sorted(reject_reasons.items(), key=lambda x: -x[1])[:10]:
        reject_rows += f"<tr><td>{reason}</td><td>{count}</td></tr>"

    # ── KillSwitch warning ──
    qmt_label = "已连接" if qmt == "CONNECTED" else "未连接"
    db_label = "正常" if db == "OK" else "异常"

    ks_html = ""
    if ks_active:
        ks_html = f"""
        <div style="background:#c62828;color:#fff;padding:12px 20px;margin-bottom:16px;border-radius:4px;font-weight:bold">
          [警告] 熔断已触发 — {ks_reason}
        </div>"""

    # ── Errors ──
    error_html = ""
    if errors:
        error_html = "<div style='background:#fff3e0;padding:12px;margin-top:8px;border-radius:4px'><b>异常:</b><ul>" + \
                     "".join(f"<li style='font-size:12px'>{e}</li>" for e in errors[:5]) + "</ul></div>"

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="30">
<title>AQF-T 监控台</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Microsoft YaHei','Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}}
h1{{font-size:22px;margin-bottom:4px}}
h2{{font-size:15px;color:#8b949e;margin-bottom:16px;font-weight:normal}}
.badge{{display:inline-block;padding:4px 12px;border-radius:3px;font-size:12px;font-weight:bold;color:#fff;background:{env_color};margin-bottom:12px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:16px;margin-bottom:12px}}
.row{{display:flex;gap:12px;flex-wrap:wrap}}
.col{{flex:1;min-width:200px}}
.stat{{font-size:28px;font-weight:bold}}
.stat-label{{font-size:11px;color:#8b949e}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;padding:6px 8px;border-bottom:1px solid #30363d;color:#8b949e;font-weight:normal;font-size:11px}}
td{{padding:6px 8px;border-bottom:1px solid #21262d}}
.green{{color:#3fb950}}
.red{{color:#f85149}}
.yellow{{color:#d2991d}}
</style>
</head>
<body>

<h1>AQF-T 监控台</h1>
<h2>V1.2</h2>
<div class="badge">{env_badge}</div>
{ks_html}

<!-- 系统状态 -->
<div class="card">
  <div class="row">
    <div class="col">
      <div class="stat-label">市场状态</div>
      <div class="stat" style="font-size:20px">{phase} <span style="font-size:13px;color:#8b949e">({mode}, 置信度={confidence:.2f})</span></div>
    </div>
    <div class="col">
      <div class="stat-label">QMT</div>
      <div class="stat" style="font-size:16px;color:{'#3fb950' if qmt == 'CONNECTED' else '#f85149'}">{qmt_label}</div>
    </div>
    <div class="col">
      <div class="stat-label">数据库</div>
      <div class="stat" style="font-size:16px;color:{'#3fb950' if db == 'OK' else '#f85149'}">{db_label}</div>
    </div>
    <div class="col">
      <div class="stat-label">CPU</div>
      <div class="stat" style="font-size:16px">{cpu:.0f}%</div>
    </div>
    <div class="col">
      <div class="stat-label">内存</div>
      <div class="stat" style="font-size:16px">{mem:.0f}%</div>
    </div>
    <div class="col">
      <div class="stat-label">熔断</div>
      <div class="stat" style="font-size:16px;color:{'#f85149' if ks_active else '#3fb950'}">{'已触发' if ks_active else '安全'}</div>
    </div>
  </div>
</div>

<!-- 今日交易 -->
<div class="card">
  <div class="row">
    <div class="col">
      <div class="stat-label">候选</div>
      <div class="stat">{total_candidates}</div>
    </div>
    <div class="col">
      <div class="stat-label">信号</div>
      <div class="stat">{total_signals}</div>
    </div>
    <div class="col">
      <div class="stat-label">成交</div>
      <div class="stat green">{total_fills}</div>
    </div>
    <div class="col">
      <div class="stat-label">拒绝</div>
      <div class="stat red">{total_rejected}</div>
    </div>
    <div class="col">
      <div class="stat-label">持仓</div>
      <div class="stat">{positions_count}</div>
    </div>
    <div class="col">
      <div class="stat-label">账户总值</div>
      <div class="stat" style="font-size:18px">{total_value:,.0f}</div>
    </div>
    <div class="col">
      <div class="stat-label">现金</div>
      <div class="stat" style="font-size:18px">{cash:,.0f}</div>
    </div>
  </div>
  <!-- 敞口 -->
  <div style="margin-top:12px;font-size:12px;color:#8b949e">
    总敞口: {exposure.get('total_exposure_pct',0)}% |
    当日新增: {exposure.get('daily_new_exposure_pct',0)}% |
    板块: {sector_display}
  </div>
  <!-- Pattern 证据 -->
  <div style="margin-top:8px;font-size:12px;color:#8b949e">
    证据版本 v{evidence_version} |
    {" | ".join(f"{name}: {p.get('status','?')}" for name, p in pattern_evidence.items()) if pattern_evidence else '暂无证据'}
  </div>
  {error_html}
</div>

<!-- 持仓明细 -->
<div class="card">
  <h2 style="margin-bottom:8px">当前持仓</h2>
  <table>
    <tr><th>标的</th><th style="text-align:right">数量</th><th style="text-align:right">成本</th><th style="text-align:right">市值</th><th style="text-align:right">盈亏</th><th style="text-align:right">盈亏率</th></tr>
    {position_rows if position_rows else '<tr><td colspan="6" style="color:#8b949e">空仓</td></tr>'}
  </table>
</div>

<!-- 交易明细 -->
<div class="row">
  <div class="col" style="flex:2">
    <div class="card">
      <h2 style="margin-bottom:8px">成交明细 (最近10条)</h2>
      <table>
        <tr><th>时间</th><th>标的</th><th>方向</th><th style="text-align:right">数量</th><th style="text-align:right">价格</th><th style="text-align:right">成本</th><th style="text-align:right">盈亏</th><th style="text-align:right">盈亏率</th><th>状态</th><th>原因</th></tr>
        {fill_rows if fill_rows else '<tr><td colspan="10" style="color:#8b949e">暂无成交</td></tr>'}
      </table>
    </div>
  </div>
  <div class="col">
    <div class="card">
      <h2 style="margin-bottom:8px">风控拒绝</h2>
      <table>
        <tr><th>原因</th><th>次数</th></tr>
        {reject_rows if reject_rows else '<tr><td colspan="2" style="color:#8b949e">无</td></tr>'}
      </table>
    </div>
  </div>
</div>

<!-- 信号明细 -->
<div class="card">
  <h2 style="margin-bottom:8px">决策信号 (最近5条)</h2>
  <table>
    <tr><th>标的</th><th>方向</th><th>策略</th><th>仓位</th><th>置信度</th><th>依据</th></tr>
    {signal_rows if signal_rows else '<tr><td colspan="6" style="color:#8b949e">暂无信号</td></tr>'}
  </table>
</div>

<!-- V1.3: 收益摘要 + 风控热力 -->
<div class="row">
  <div class="col">
    <div class="card">
      <h2 style="margin-bottom:8px">收益摘要</h2>
      <div style="font-size:13px">
        <div style="margin-bottom:4px">账户总值: <b>{total_value:,.0f}</b></div>
        <div style="margin-bottom:4px">可用现金: <b>{cash:,.0f}</b></div>
        <div style="margin-bottom:4px">持仓市值: <b>{total_value - cash:,.0f}</b></div>
        <div style="color:#8b949e;font-size:11px">总成交 {account.get('total_trades',0)} 笔 | 当前持仓 {positions_count} 只</div>
      </div>
    </div>
  </div>
  <div class="col" style="flex:2">
    <div class="card">
      <h2 style="margin-bottom:8px">风控热力</h2>
      <div style="font-size:12px">
        {_risk_heatmap(reject_reasons)}
      </div>
    </div>
  </div>
</div>

<!-- V1.3: 7日Regime日历 + Pattern排序 -->
<div class="row">
  <div class="col" style="flex:2">
    <div class="card">
      <h2 style="margin-bottom:8px">7日市场状态</h2>
      <div style="display:flex;gap:6px;font-size:12px">
        {_regime_calendar()}
      </div>
    </div>
  </div>
  <div class="col">
    <div class="card">
      <h2 style="margin-bottom:8px">Pattern 排序</h2>
      <table style="font-size:12px">
        <tr><th>Pattern</th><th style="text-align:right">触发</th><th>状态</th></tr>
        {_pattern_ranking(pattern_evidence)}
      </table>
    </div>
  </div>
</div>

<!-- Footer -->
<div style="text-align:center;font-size:11px;color:#484f58;margin-top:16px">
  AQF-T V1.2 | 每30秒自动刷新 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
