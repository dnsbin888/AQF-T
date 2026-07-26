"""
AQF-T Intelligence Console — Web 控制台
启动: python apps/console/server.py
访问: http://127.0.0.1:8080
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI(title="AQF-T Console", version="3.1.0")

CONSOLE_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AQF-T Intelligence Console V3.1.0</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:#0a0e17; color:#c9d1d9; font-family:'Segoe UI',monospace; padding:20px; }
        .header { border-bottom:2px solid #1f6feb; padding-bottom:15px; margin-bottom:20px; }
        .header h1 { color:#58a6ff; font-size:28px; }
        .header .sub { color:#8b949e; font-size:14px; margin-top:5px; }
        .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(350px,1fr)); gap:15px; }
        .card { background:#161b22; border:1px solid #30363d; border-radius:8px; padding:18px; }
        .card h3 { color:#58a6ff; margin-bottom:12px; font-size:16px; border-bottom:1px solid #21262d; padding-bottom:8px; }
        .row { display:flex; justify-content:space-between; padding:5px 0; font-size:14px; }
        .label { color:#8b949e; }
        .value { color:#c9d1d9; font-weight:bold; }
        .green { color:#3fb950; }
        .yellow { color:#d2991d; }
        .red { color:#f85149; }
        .blue { color:#58a6ff; }
        .module-grid { display:flex; flex-wrap:wrap; gap:8px; }
        .module-tag { background:#1f6feb22; border:1px solid #1f6feb44; color:#58a6ff; padding:4px 12px; border-radius:4px; font-size:12px; }
        .module-tag.active { background:#3fb95022; border-color:#3fb95044; color:#3fb950; }
        .status-bar { background:#161b22; border:1px solid #30363d; border-radius:8px; padding:12px 18px; margin-top:15px; display:flex; justify-content:space-between; align-items:center; }
        .status-dot { width:10px; height:10px; border-radius:50%; background:#3fb950; display:inline-block; margin-right:8px; animation:pulse 2s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        .reasoning { background:#0d1117; border-radius:4px; padding:10px; margin-top:8px; font-size:13px; line-height:1.6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AQF-T Intelligence Console</h1>
        <div class="sub">Autonomous Quantitative Fusion Trading System | V3.1.0 | Architecture Freeze Complete</div>
    </div>

    <div class="grid">
        <div class="card">
            <h3>System Status</h3>
            <div class="row"><span class="label">Version</span><span class="value blue">V3.1.0</span></div>
            <div class="row"><span class="label">Mode</span><span class="value green">Development</span></div>
            <div class="row"><span class="label">Uptime</span><span class="value">--</span></div>
            <div class="row"><span class="label">Risk Kill Switch</span><span class="value green">ACTIVE</span></div>
        </div>

        <div class="card">
            <h3>World Status</h3>
            <div class="row"><span class="label">Market</span><span class="value">China A-Share</span></div>
            <div class="row"><span class="label">Environment</span><span class="value green">Liquidity Expansion</span></div>
            <div class="row"><span class="label">Regime</span><span class="value blue">Bull Expansion</span></div>
            <div class="row"><span class="label">Risk Level</span><span class="value yellow">Medium (35/100)</span></div>
        </div>

        <div class="card">
            <h3>Decision Engine</h3>
            <div class="row"><span class="label">Recommendation</span><span class="value blue">HOLD</span></div>
            <div class="row"><span class="label">Confidence</span><span class="value green">82%</span></div>
            <div class="row"><span class="label">Next Review</span><span class="value">5 min</span></div>
            <div class="reasoning">
                <strong>Reasoning:</strong><br>
                Fed Policy → USD → Capital Flow → Risk Adjustment<br>
                Liquidity: Supportive | Valuation: Acceptable
            </div>
        </div>

        <div class="card">
            <h3>Module Registry</h3>
            <div class="module-grid">
                <span class="module-tag active">ai_brain</span>
                <span class="module-tag active">strategy</span>
                <span class="module-tag active">risk</span>
                <span class="module-tag">execution</span>
                <span class="module-tag active">world_model</span>
                <span class="module-tag active">decision</span>
                <span class="module-tag active">agent</span>
                <span class="module-tag active">data</span>
            </div>
        </div>
    </div>

    <div class="status-bar">
        <span><span class="status-dot"></span> AQF-T Intelligence Console ONLINE</span>
        <span style="color:#8b949e;">P0-P5 Architecture Frozen | P6 Runtime Active</span>
        <span style="color:#8b949e;">""" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</span>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def console():
    return CONSOLE_HTML

@app.get("/api/v1/status")
def status():
    return {
        "system": "AQF-T",
        "version": "3.1.0",
        "status": "ONLINE",
        "mode": "development",
        "modules": {
            "ai_brain": "active", "strategy": "active",
            "risk": "active (kill_switch)", "execution": "standby",
            "world_model": "active", "decision": "active", "agent": "active"
        },
        "timestamp": datetime.now().isoformat(),
    }
