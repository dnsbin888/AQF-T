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
from socketserver import ThreadingMixIn

ROOT = Path(__file__).parent
REPORTS_DAILY = ROOT / "reports" / "daily"
REPORTS_EXEC = ROOT / "reports" / "execution"
REPORTS_STATUS = ROOT / "reports" / "status"
REPORTS_SENSOR = ROOT / "reports" / "sensor"
EVIDENCE_FILE = ROOT / "evidence" / "PHASE2_DATA_EVIDENCE_SIM.json"
PORT = 8081

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

def get_today_data() -> dict | None:
    """
    Phase 1 数据读取优先级 (禁止旧数据 fallback):
      1. reports/status/YYYYMMDD_status.json  ← Phase 1 真实数据
      2. reports/daily/YYYYMMDD_report.json   ← 当日报告 (如果有)
      3. 都没有 → None, 前端显示"今日数据未生成"

    绝不回退到旧日期的 reports/daily/ 数据。
    """
    today = datetime.now().strftime("%Y%m%d")

    # Priority 1: Phase 1 status file (真实数据链)
    status_file = REPORTS_STATUS / f"{today}_status.json"
    if status_file.exists():
        try:
            return json.loads(status_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # Priority 2: Today's daily report (仅当日)
    daily_file = REPORTS_DAILY / f"{today}_report.json"
    if daily_file.exists():
        try:
            return json.loads(daily_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # Priority 3: Nothing — explicitly None
    return None

def get_latest_status() -> dict | None:
    """读取 AQF-T Health Protocol v1.0 — 系统最后已知状态"""
    latest_file = REPORTS_STATUS / "latest_status.json"
    if latest_file.exists():
        try:
            return json.loads(latest_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return None

def get_latest_sensor() -> dict | None:
    """读取 Market Sensor 最新快照 — 只读，不参与交易决策"""
    latest_file = REPORTS_SENSOR / "latest_sensor.json"
    if latest_file.exists():
        try:
            return json.loads(latest_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return None

def get_qmt_status() -> str:
    """
    QMT 状态检测 (三级, 避免假连接):
      - CONNECTED:    xtquant 可导入且服务可达
      - DEGRADED:     xtquant 可导入但无法验证服务
      - UNAVAILABLE:  xtquant 未安装

    import xtquant 成功 ≠ API 可用 — 不依赖 import 副作用判断连接。
    用快速探测验证: 尝试获取板块信息 (轻量, 非阻塞)。
    """
    try:
        from xtquant import xtdata
        # 快速连通性探测: 获取板块列表 (无需参数, 轻量调用)
        try:
            sectors = xtdata.get_sector_list()
            if sectors:
                return "CONNECTED"
        except Exception:
            pass
        return "DEGRADED"
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
        date_key = d.strftime("%Y%m%d")
        phase_full = ""

        # P1-DI: 优先读 status/ (Phase 1), 再读 daily/ (旧格式)
        sf = REPORTS_STATUS / f"{date_key}_status.json"
        df = REPORTS_DAILY / f"{date_key}_report.json"
        if sf.exists():
            try:
                rpt = json.loads(sf.read_text(encoding="utf-8"))
                phase_full = (rpt.get("regime") or {}).get("phase", "")
            except Exception:
                pass
        if not phase_full and df.exists():
            try:
                rpt = json.loads(df.read_text(encoding="utf-8"))
                phase_full = rpt.get("regime", {}).get("phase", "")
            except Exception:
                pass

        phase = phase_full[0] if phase_full else "-"
        color = colors.get(phase_full, "#30363d")
        cells += f"""<div style="text-align:center;padding:6px 8px;background:{color};border-radius:3px;color:#fff;min-width:38px">
          <div style="font-size:10px;opacity:0.8">{date_str}</div>
          <div style="font-weight:bold">{phase}</div>
        </div>"""
    return cells

# ── EA Task 2: 数据源 & 新鲜度标注 ──
def _source_badge(source: str, freshness: str = "") -> str:
    """生成数据源 + 新鲜度标注 HTML"""
    source_map = {
        "AKSHARE_EOD": ("akshare", "#8b949e"),
        "V2-realtime": ("V2 eastmoney", "#3fb950"),
        "eastmoney-realtime": ("eastmoney 实时", "#3fb950"),
        "pytdx": ("TDX(pytdx)", "#58a6ff"),
        "parquet-eod": ("Parquet EOD", "#d2991d"),
        "qmt": ("QMT", "#3fb950"),
        "sina": ("新浪", "#8b949e"),
        "fallback": ("⚠️ 保底", "#f0883e"),
    }
    label, color = source_map.get(source, (source or "未知", "#8b949e"))
    badge = f'<span style="font-size:10px;color:{color};border:1px solid {color};border-radius:3px;padding:0 4px;margin-left:2px">{label}</span>'
    if freshness:
        badge += f'<span style="font-size:10px;color:#8b949e;margin-left:2px">· {freshness}</span>'
    return badge

def _freshness_label(date_str: str) -> str:
    """计算数据年龄 (T+0 / T+1 / T+N)"""
    from datetime import date as dt_date
    if not date_str:
        return ""
    try:
        d = dt_date.fromisoformat(date_str)
        age = (dt_date.today() - d).days
        if age == 0:
            return "今日"
        elif age == 1:
            return "T+1 昨日"
        else:
            return f"T+{age} · {date_str}"
    except Exception:
        return date_str

# ── EA Task 1: Decision Context 展示层 ──
def _build_context_reconciliation(latest: dict | None, sensor: dict | None) -> dict:
    """构建决策上下文解释层 — 只解释, 不决策

    Returns: {conflicts: [...], explanation: str, recommendation: str, severity: str}
    """
    conflicts = []
    explanations = []
    severity = "info"  # info / warning / critical

    # 1. Gate闭合 vs 情绪乐观
    gate_open = latest.get("trade_allowed", False) if latest else False
    regime = latest.get("regime", "未知") if latest else "未知"
    mode = latest.get("mode", "") if latest else ""

    if sensor:
        sent = (sensor.get("sensors", {}) or {}).get("sentiment", {}) or {}
        mkt = sent.get("market_sentiment", {}) or {}
        cycle = sent.get("cycle", {}) or {}
        sent_conf = sent.get("sentiment_confidence", {}) or {}

        mkt_score = mkt.get("score", 50)
        mkt_label = mkt.get("label", "")
        cycle_stage = cycle.get("stage", "")
        cycle_label = cycle.get("label", "")
        conf_val = sent_conf.get("value", 50)
        conf_status = sent_conf.get("status", "")

        # ── P1: Gate OPEN + 实时风险恶化 (STRUCTURAL_BULL ≠ BROAD_BULL) ──
        # 这是 EA+FA 2026-08-12 确认的架构现象：
        # AQF-T 回答"是否允许Entry"，Sensor 回答"实时情绪是否恶化"——两者不矛盾。
        # 但当 Gate OPEN 且实时情绪显著恶化时，Dashboard 必须显式标注。
        sent_vel_1d = (sent.get("sentiment_velocity", {}) or {}).get("change_1d")
        sent_ext_state = (sent.get("sentiment_extreme", {}) or {}).get("state", "")
        llm = sent.get("llm_sentiment", {}) or {}
        llm_score = llm.get("score", 0)

        if gate_open and (mkt_score < 35 or (sent_vel_1d is not None and sent_vel_1d < -10)):
            deterioration_type = "sharp_drop" if (sent_vel_1d is not None and sent_vel_1d < -15) else "moderate"
            conflicts.append({
                "signal_a": f"Gate 开放 ({regime} · {mode})",
                "signal_b": f"实时情绪恶化 (score={mkt_score}, Δ1d={sent_vel_1d})",
                "type": "gate_open_vs_sentiment_deterioration",
            })
            if deterioration_type == "sharp_drop":
                explanations.append(
                    f"<b>🔴 实时风险骤降 vs Gate 开放</b>: "
                    f"AQF-T Engine 基于 EOD 数据判定 {regime}（STRUCTURAL_BULL），Gate 正确开放。"
                    f"但实时情绪 {mkt_score} 分（{mkt_label}），1日变化 {sent_vel_1d:+.0f}——"
                    f"市场 breadth 正在恶化。这不是 Gate 错误，而是 <b>STRUCTURAL_BULL ≠ BROAD_BULL</b> "
                    f"的经典场景：涨停梯队完整但涨跌比/情绪面短期恶化。"
                    f"当前不改变 Production Gate，但建议关注 Entry 质量。"
                )
            else:
                explanations.append(
                    f"<b>🟡 实时风险偏弱 vs Gate 开放</b>: "
                    f"AQF-T Gate 基于 EOD 数据正确开放（{regime}），"
                    f"但实时情绪 {mkt_score} 分（{mkt_label}）。"
                    f"这属于正常的 <b>时间尺度错位</b>——Engine 是 T+1 EOD，Sensor 是实时。"
                    f"当前不改变 Production Gate。"
                )
            severity = "critical" if deterioration_type == "sharp_drop" else "warning"

        # ── LLM 情绪显著偏空 (不参与 Gate，仅观察) ──
        if gate_open and llm_score < -30:
            conflicts.append({
                "signal_a": f"Gate 开放 ({regime})",
                "signal_b": f"LLM 情绪 {llm_score} ({llm.get('label', '')})",
                "type": "gate_open_vs_llm",
            })
            explanations.append(
                f"<b>🟡 LLM 情绪偏空 vs Gate 开放</b>: "
                f"DeepSeek 分析东财头条得出 {llm.get('label', '偏空')}（{llm_score}）。"
                f"LLM 是高层语义信号，非校准风险变量——<b>不参与 Gate 决策</b>。"
                f"仅作为信息面观察记录。"
            )
            if severity == "info":
                severity = "warning"

        # Conflict: Gate stop but sentiment optimistic
        if not gate_open and mkt_score >= 60 and regime != "高潮期":
            conflicts.append({
                "signal_a": f"Gate 关闭 ({regime} · {mode})",
                "signal_b": f"市场情绪 {mkt_label} ({mkt_score})",
                "type": "gate_vs_sentiment",
            })
            explanations.append(
                f"<b>🟡 Gate 关闭 vs 情绪{mkt_label}</b>: "
                f"AQF-T Gate 基于前一交易日判定退潮期（{regime}），禁止交易。"
                f"但今日实时市场情绪{mkt_label}（{mkt_score}分），"
                f"LU={mkt.get('limit_up', '?')} LD={mkt.get('limit_down', '?')}。"
                f"这可能是Gate滞后（T+1 EOD更新）与盘中情绪变化之间的自然时间差。"
            )
            severity = "warning"

        # Conflict: Cycle = ferment/startup but Gate closed
        if not gate_open and cycle_stage in ("ferment", "startup"):
            conflicts.append({
                "signal_a": f"Gate 关闭 ({regime})",
                "signal_b": f"情绪周期 {cycle_label}",
                "type": "gate_vs_cycle",
            })
            explanations.append(
                f"<b>🟡 Gate 关闭 vs 周期{cycle_label}</b>: "
                f"情绪周期判断当前处于{cycle_label}，通常对应积极仓位。"
                f"但AQF-T Gate未开放，说明交易环境尚未确认。"
                f"这可能是情绪领先于交易环境恢复的正常现象。"
                f"等待Gate重新开放后再执行仓位决策。"
            )
            severity = "warning"

        # Conflict: Sentiment consensus high + regime stop
        if not gate_open and conf_status == "favorable" and conf_val >= 65:
            if not conflicts:
                conflicts.append({
                    "signal_a": f"Gate 关闭 ({regime})",
                    "signal_b": f"情绪信心 favorable ({conf_val})",
                    "type": "gate_vs_consensus",
                })
                explanations.append(
                    f"<b>🟡 多Sensor乐观 vs Gate关闭</b>: "
                    f"市场Sensor汇总信心{conf_val}（favorable），但Gate仍在保护状态。"
                    f"多空信号分歧是正常现象，Gate以风控为优先。"
                )
                severity = "warning"

        # All consistent
        if not conflicts:
            if not gate_open:
                explanations.append(
                    f"<b>✅ 信号一致</b>: Gate 关闭与{regime}一致。"
                    f"情绪{mkt_label}（{mkt_score}）未达到足以改变判定的水平。"
                    f"当前空仓观望是合理决策。"
                )
            else:
                explanations.append(
                    f"<b>✅ 信号一致</b>: Gate 开放，情绪{mkt_label}（{mkt_score}），"
                    f"周期{cycle_label}。交易环境正常。"
                )
    else:
        explanations.append("<b>等待数据</b>: Sensor 数据暂不可用，无法生成上下文解释。")

    # 构建综合解释
    explanation_html = "<br>".join(explanations)
    conflicts_html = " / ".join(f"{c['signal_a']} ⇄ {c['signal_b']}" for c in conflicts) if conflicts else "无冲突"

    sev_map = {
        "info": ("#30363d", "📋 决策上下文"),
        "warning": ("#6b4c00", "⚠️ 决策上下文 · 信号分歧"),
        "critical": ("#7d1a1a", "🔴 决策上下文 · 严重冲突"),
    }
    bg_color, title = sev_map.get(severity, sev_map["info"])

    return {
        "conflicts": conflicts,
        "explanation": explanation_html,
        "conflicts_summary": conflicts_html,
        "severity": severity,
        "bg_color": bg_color,
        "title": title,
    }

def _pattern_ranking(patterns: dict) -> str:
    if not patterns:
        return '<tr><td colspan="3" style="color:#8b949e">暂无数据</td></tr>'
    ranked = sorted(patterns.items(), key=lambda x: x[1].get("trigger_count", 0), reverse=True)
    labels = {"PositionAnchor": "卡位博弈", "LeaderLifeCycle": "龙头8维", "LadderScore": "梯队完整性",
              "EmotionCycle": "情绪周期", "SectorFlow": "板块轮动", "RelativeStrength": "相对强度"}
    rows = ""
    for name, p in ranked:
        label = labels.get(name, name)
        count = p.get("trigger_count", 0)
        status = p.get("status", "?")
        sc = "#3fb950" if status == "validated" else "#f85149"
        rows += f"""<tr><td>{label}</td><td style="text-align:right">{count}</td><td style="color:{sc};font-size:11px">{status}</td></tr>"""
    return rows

def _exit_summary() -> str:
    """E4: 退出统计 — 从 evidence/exit/ 读取最新"""
    exit_dir = ROOT / "evidence" / "exit"
    if not exit_dir.exists():
        return '<span style="color:#8b949e">暂无退出证据</span>'
    files = sorted(exit_dir.glob("*_exit_evidence.json"), reverse=True)
    if not files:
        return '<span style="color:#8b949e">暂无退出证据</span>'
    try:
        data = json.loads(files[0].read_text(encoding="utf-8"))
    except Exception:
        return '<span style="color:#8b949e">退出证据读取失败</span>'

    total = data.get("total_exits", 0)
    if total == 0:
        return '<span style="color:#8b949e">暂无退出事件</span>'

    by_reason = data.get("by_reason", {})
    labels = {"hard_stop": "硬止损", "drawdown_limit": "回撤限制", "regime_break": "退潮清仓",
              "killswitch": "熔断", "break_exit": "炸板退出", "leader_end": "龙头结束",
              "pattern_invalid": "依据失效"}

    rows = ""
    for reason, count in sorted(by_reason.items(), key=lambda x: -x[1]):
        label = labels.get(reason, reason)
        rows += f"<tr><td>{label}</td><td style=\"text-align:right\">{count}</td><td style=\"font-size:11px;color:#8b949e\">{reason}</td></tr>"

    win_rate = data.get("win_rate", 0)
    avg_hold = data.get("avg_holding_days", 0)
    total_pnl = data.get("total_pnl", 0)
    pnl_color = "#3fb950" if total_pnl > 0 else ("#f85149" if total_pnl < 0 else "#8b949e")

    return f"""
    <div class="row" style="font-size:13px;margin-bottom:8px">
      <div class="col"><b>{total}</b> 次退出</div>
      <div class="col">胜率 <b>{win_rate}%</b></div>
      <div class="col">均持 <b>{avg_hold}</b>天</div>
      <div class="col">盈亏 <b style="color:{pnl_color}">{total_pnl:+,.0f}</b></div>
    </div>
    <table style="font-size:12px">
      <tr><th>退出类型</th><th style="text-align:right">次数</th><th>标识</th></tr>
      {rows}
    </table>
    """

# ── HTML renderer ──

def render() -> str:
    today_data = get_today_data()        # Phase 1: status/ 优先, 禁旧 fallback
    daily = get_daily_report()           # 保留: 仅用于补充数据 (pattern/exit)
    exec_rpt = get_execution_report()
    evidence_meta = get_evidence_meta()

    # ── 今日数据状态标记 ──
    is_status_format = False  # True: Phase 1 status 文件, False: 旧 daily 格式
    data_available_today = today_data is not None

    # -- AQF-T Health Protocol v1.0: 读取系统最后已知状态 --
    latest = get_latest_status()
    # -- Market Sensor: 读取最新环境数据 --
    latest_sensor = get_latest_sensor()
    data_age_hours = 0
    data_stale = False
    latest_timestamp = ""
    if latest and latest.get("timestamp"):
        latest_timestamp = latest["timestamp"]
        try:
            ts = datetime.strptime(latest["timestamp"], "%Y-%m-%d %H:%M:%S")
            data_age_hours = (datetime.now() - ts).total_seconds() / 3600
            data_stale = data_age_hours > 6
        except ValueError:
            pass

    if data_available_today:
        # 检测数据格式: status 文件有 "source" 字段, daily 文件有 "pipeline" 字段
        is_status_format = "source" in today_data and "pipeline" not in today_data

    # ── 环境标识 (P1-DI: 利用 status 文件的 source/timestamp) ──
    status_timestamp = ""
    if is_status_format:
        data_source = today_data.get("data_source", "UNKNOWN")
        status_timestamp = today_data.get("timestamp", "")
        if data_source in ("AKSHARE_EOD", "akshare"):
            env_badge = f'[真实] AKSHARE_EOD | 今日已运行'
            env_color = "#38a838"
        elif today_data.get("source") == "real":
            env_badge = f'[真实] AKSHARE_EOD | 今日已运行'
            env_color = "#38a838"
        else:
            env_badge = f'[模拟] SIMULATOR | 今日已运行'
            env_color = "#e8a838"
    elif data_available_today:
        # 旧 daily 格式 (仅当日)
        env_badge = f'[报告] DAILY_REPORT | 今日已生成'
        env_color = "#38a838"
    else:
        not_live = evidence_meta.get("not_live", True)
        source = evidence_meta.get("source", "SIMULATOR")
        if not_live:
            env_badge = f'[模拟] 数据源: {source} | 非实盘'
            env_color = "#e8a838"
        else:
            env_badge = f'[实盘] 数据源: {source}'
            env_color = "#38a838"

    # ── 系统状态 (P1-DI: 从 status 文件读取真实数据) ──
    if is_status_format:
        # Phase 1 status 格式归一化
        regime_raw = today_data.get("regime", {}) or {}
        regime = {
            "phase": regime_raw.get("phase", "N/A"),
            "operation_mode": regime_raw.get("mode", "N/A"),
            "regime_confidence": regime_raw.get("score", 0) / 200,  # score 归一化
        }
        health = {}
        pipeline = {
            "total_candidates": today_data.get("candidates", 0),
            "total_signals": today_data.get("signals", 0),
            "total_fills": today_data.get("fills", 0),
            "total_rejected": today_data.get("rejected", 0),
            "errors": today_data.get("errors", []),
        }
        account = today_data.get("account", {})
        signals = today_data.get("signals", []) if isinstance(today_data.get("signals"), list) else []
        fills = today_data.get("fills", []) if isinstance(today_data.get("fills"), list) else []
        exposure = {}
        errors = today_data.get("errors", [])
        if isinstance(errors, list) and errors and isinstance(errors[0], dict):
            errors = [e.get("message", str(e)) for e in errors]
        warnings = today_data.get("warnings", [])
        if isinstance(warnings, list) and warnings and isinstance(warnings[0], dict):
            warnings = [w.get("message", str(w)) for w in warnings]
    else:
        # 无今日数据 — 全部空值, 不禁旧 daily fallback
        regime = {"phase": "N/A", "operation_mode": "N/A", "regime_confidence": 0}
        health = {}
        pipeline = {"total_candidates": 0, "total_signals": 0, "total_fills": 0,
                     "total_rejected": 0, "errors": []}
        account = {"cash": 0, "positions": 0, "total_value": 0, "total_trades": 0}
        signals = []
        fills = []
        exposure = {}
        errors = [f"EOD 模式 · 上次更新: {latest_timestamp or '无记录'} · 等待今日 15:30 Pipeline"]
        warnings = []
    # ── 旧 daily 仅用于补充数据 (pattern/exit/calendar) ──
    # P1-DI: 仅使用今日 daily, 不禁用旧 fallback
    daily_today = None
    today_daily_file = REPORTS_DAILY / f"{datetime.now().strftime('%Y%m%d')}_report.json"
    if today_daily_file.exists():
        try:
            daily_today = json.loads(today_daily_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    daily_fallback = daily_today if daily_today else {}

    cpu = psutil.cpu_percent(interval=0.1)  # P1-DI: 首次采样间隔, 避免 0%
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
        "ladder": "梯队完整性",
        "leader": "龙头8维",
        "emotion": "情绪周期",
    }

    # ── Sector 空值处理 (P0-3) — 从 daily 补充, status 没有此字段 ──
    sector_exposure = daily_fallback.get("exposure", {}).get("sector_exposure", {}) if daily_fallback else {}
    sector_display = {}
    for k, v in sector_exposure.items():
        label = k if k.strip() else "未分类"
        sector_display[label] = v

    # ── Pattern Evidence (P0-4) — 仅从 evidence 文件读取, 不影响今日交易数据 ──
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

    # ── EA Task 3: Signal type badges ──
    def _signal_badge(sig_type: str) -> str:
        """ML / Rule / Shadow 信号身份区分"""
        badges = {
            "ml": '<span style="font-size:10px;background:#1a3a5c;color:#58a6ff;border-radius:3px;padding:1px 5px">🤖 ML</span>',
            "rule": '<span style="font-size:10px;background:#3d2e00;color:#d2991d;border-radius:3px;padding:1px 5px">📏 Rule</span>',
            "shadow": '<span style="font-size:10px;background:#2e1a3d;color:#bc8cff;border-radius:3px;padding:1px 5px">👁️ Shadow</span>',
        }
        return badges.get(sig_type, "")

    # ── 信号明细 ──
    signal_rows = ""
    for s in signals[:5]:
        strat_raw = s.get('strategy', '')
        strat_label = STRATEGY_LABELS.get(strat_raw, strat_raw)
        act_label = ACTION_LABELS.get(s.get('action', ''), s.get('action', ''))
        # EA Task 3: 信号身份分类 (基于 strategy 字段)
        strat_raw = s.get('strategy', '')
        if strat_raw in ('lgbm', 'xgboost', 'ridge', 'ensemble'):
            sig_type = "ml"
        elif strat_raw in ('catboost',):
            sig_type = "shadow"
        else:
            sig_type = "rule"
        badge = _signal_badge(sig_type)
        signal_rows += f"""
        <tr>
          <td>{stock_label(s.get('symbol',''))}{badge}</td><td>{act_label}</td>
          <td>{strat_label}</td><td>{s.get('position_pct',0):.0%}</td>
          <td>{s.get('confidence',0):.2f}</td>
          <td style="font-size:12px;color:#888">{s.get('reasoning','')}</td>
        </tr>"""

    # ── 风险拒绝 ──
    reject_rows = ""
    for reason, count in sorted(reject_reasons.items(), key=lambda x: -x[1])[:10]:
        reject_rows += f"<tr><td>{reason}</td><td>{count}</td></tr>"

    # ── KillSwitch warning ──
    qmt_labels = {"CONNECTED": "已连接", "DEGRADED": "降级", "UNAVAILABLE": "未安装"}
    qmt_colors = {"CONNECTED": "#3fb950", "DEGRADED": "#d2991d", "UNAVAILABLE": "#f85149"}
    qmt_label = qmt_labels.get(qmt, qmt)
    qmt_color = qmt_colors.get(qmt, "#f85149")
    db_label = "正常" if db == "OK" else "异常"

    # -- AQF-T Health Protocol v1.0: 三态 banner --
    if not data_available_today:
        if latest and latest.get("pipeline_status") == "completed":
            last_ts = latest.get("timestamp", "")
            is_today_run = datetime.now().strftime("%Y-%m-%d") in str(last_ts)
            if is_today_run:
                health_banner = f"<div style='background:#e8a838;color:#000;padding:12px 20px;margin-bottom:16px;border-radius:4px;font-weight:bold'>[通知] AQF-T 今日已运行 — 判定 {latest.get('regime', 'N/A')}，不交易 — {latest.get('reason', '')}</div>"
            else:
                health_banner = f"<div style='background:#e8a838;color:#000;padding:12px 20px;margin-bottom:16px;border-radius:4px;font-weight:bold'>[EOD] AQF-T 上次运行: {last_ts} | 判定 {latest.get('regime', 'N/A')}，不交易 | 等待今日 15:30 Pipeline</div>"
        elif latest and latest.get("pipeline_status") == "error":
            health_banner = f"<div style='background:#c62828;color:#fff;padding:12px 20px;margin-bottom:16px;border-radius:4px;font-weight:bold'>[异常] AQF-T 上次运行出错 — {latest.get('errors', 0)} 个错误, {latest.get('warnings', 0)} 个提示</div>"
        else:
            if latest and latest.get("timestamp"):
                health_banner = f"<div style='background:#e8a838;color:#000;padding:12px 20px;margin-bottom:16px;border-radius:4px;font-weight:bold'>[EOD] AQF-T 数据模式: 日终批处理 | 上次: {latest.get('timestamp', 'N/A')} | 今日 15:30 自动更新 | 当前非故障</div>"
            else:
                health_banner = "<div style='background:#e8a838;color:#000;padding:12px 20px;margin-bottom:16px;border-radius:4px;font-weight:bold'>[EOD] AQF-T 数据模式: 日终批处理 | 等待首次运行 | 今日 15:30 自动更新</div>"
    else:
        health_banner = ""

    # -- AQF-T Health Protocol v1.0: Pipeline 健康状态计算 --
    if latest:
        if latest.get("pipeline_status") == "completed":
            pipeline_status_color = "#3fb950"
            pipeline_status_label = "正常"
        elif latest.get("pipeline_status") == "error":
            pipeline_status_color = "#f85149"
            pipeline_status_label = "异常"
        else:
            pipeline_status_color = "#8b949e"
            pipeline_status_label = "未知"

        if latest.get("trade_allowed"):
            trade_allowed_color = "#3fb950"
            trade_allowed_label = "允许交易"
        else:
            trade_allowed_color = "#f0883e"
            trade_allowed_label = "禁止交易"
        trade_reason = latest.get("reason", "")

        if data_age_hours < 3:
            freshness_color = "#3fb950"
            freshness_label = f"新鲜 ({data_age_hours:.1f}h前)"
        elif data_age_hours < 6:
            freshness_color = "#d2991d"
            freshness_label = f"稍旧 ({data_age_hours:.0f}h前)"
        else:
            freshness_color = "#f85149"
            freshness_label = f"&#9888; stale ({data_age_hours:.0f}h前)"

        last_update_display = latest_timestamp
    else:
        pipeline_status_color = "#8b949e"
        pipeline_status_label = "未运行"
        trade_allowed_color = "#8b949e"
        trade_allowed_label = "未知"
        trade_reason = "等待首次运行"
        freshness_color = "#8b949e"
        freshness_label = "未知"
        last_update_display = "-"

    # -- Market Sensor 摘要变量 --
    sensor_risk = ""
    sensor_conf = ""
    sensor_signals = ""
    sensor_sent = ""
    sensor_data_available = False
    if latest_sensor:
        summary = latest_sensor.get("summary", {}) or {}
        sensor_risk = summary.get("risk_appetite", "")
        sensor_conf = summary.get("confidence", "")
        sensor_signals_list = summary.get("signals", []) or []
        sensor_signals = ", ".join(sensor_signals_list) if sensor_signals_list else "无"
        # 情绪摘要
        sent = (latest_sensor.get("sensors", {}) or {}).get("sentiment", {}) or {}
        sent_conf = sent.get("sentiment_confidence", {}) or {}
        sent_ext = sent.get("sentiment_extreme", {}) or {}
        sent_vel = sent.get("sentiment_velocity", {}) or {}
        sent_conf_val = sent_conf.get("value", "")
        sent_ext_state = sent_ext.get("state", "")
        sent_vel_1d = sent_vel.get("change_1d", "")
        if sent_conf_val:
            sensor_sent = f"情绪: {sent_conf_val}"
            if sent_ext_state:
                sensor_sent += f" | {sent_ext_state}"
            if sent_vel_1d is not None:
                sensor_sent += f" | Δ1d: {sent_vel_1d:+.0f}" if isinstance(sent_vel_1d, (int, float)) else ""
        sensor_data_available = True

    # Sensor 信号颜色
    if sensor_risk == "expanding":
        sensor_risk_color = "#3fb950"
        sensor_risk_label = "扩张"
    elif sensor_risk == "contracting":
        sensor_risk_color = "#f85149"
        sensor_risk_label = "收缩"
    elif sensor_risk == "mixed":
        sensor_risk_color = "#d2991d"
        sensor_risk_label = "分化"
    else:
        sensor_risk_color = "#8b949e"
        sensor_risk_label = sensor_risk or "-"

    if isinstance(sensor_conf, (int, float)):
        if sensor_conf >= 60:
            sensor_conf_color = "#3fb950"
        elif sensor_conf >= 40:
            sensor_conf_color = "#d2991d"
        else:
            sensor_conf_color = "#f85149"
        sensor_conf_label = f"{sensor_conf:.0f}"
    else:
        sensor_conf_color = "#8b949e"
        sensor_conf_label = "-"

    # ── Dashboard v1.2: 状态条颜色计算 (Health Protocol 三态映射) ──
    if not data_available_today:
        status_bar_color = "#30363d"  # 灰 — EOD 等待中
        status_bar_system = "EOD · 等待 15:30"
        status_bar_regime = "日终批处理模式"
    elif ks_active:
        status_bar_color = "#7d1a1a"  # 红 — 熔断
        status_bar_system = "⚠️ 熔断已触发"
        status_bar_regime = f"{phase} · Gate 关闭 · {ks_reason}"
    elif latest:
        ps = latest.get("pipeline_status", "")
        if ps == "error" or ps == "WARNING" or ps == "CRITICAL":
            status_bar_color = "#7d1a1a"  # 红 — 异常
            status_bar_system = "🔴 AQF-T 异常"
            status_bar_regime = f"{phase} · {ps}"
        elif latest.get("trade_allowed") and phase in ("高潮期", "回暖期", "发酵期"):
            status_bar_color = "#1a5c2e"  # 绿 — 正常交易
            status_bar_system = "🟢 AQF-T 正常运行"
            status_bar_regime = f"{phase} · Gate 开放"
        else:
            status_bar_color = "#6b4c00"  # 黄 — stop/保护
            status_bar_system = "🟡 AQF-T 保护中"
            gate_label = "Gate 开放" if latest.get("trade_allowed") else "Gate 关闭"
            status_bar_regime = f"{phase} · {gate_label}"
    else:
        status_bar_color = "#1a5c2e"
        status_bar_system = "🟢 AQF-T 正常运行"
        status_bar_regime = f"{phase} · {mode}"
    status_bar_actions = f"今日 {total_signals} 信号 / {total_fills} 成交 / {total_rejected} 拒绝"

    ks_html = ""
    # 熔断信息已整合到状态条中，不再单独显示 banner（但保留变量兼容）

    # ── Errors & Warnings ──
    error_html = ""
    warning_html = ""
    if errors:
        error_html = "<div style='background:#fff3e0;padding:12px;margin-top:8px;border-radius:4px'><b>🔴 错误:</b><ul>" + \
                     "".join(f"<li style='font-size:12px'>{e}</li>" for e in errors[:5]) + "</ul></div>"
    if warnings:
        warning_html = "<div style='background:#1a2e1a;padding:12px;margin-top:4px;border-radius:4px'><b>🟡 提示:</b><ul>" + \
                       "".join(f"<li style='font-size:12px'>{w}</li>" for w in warnings[:5]) + "</ul></div>"

    # ── Dashboard v1.2 布局 ──
    # 7日趋势小点
    from datetime import timedelta
    _regime_colors = {"高潮期": "#f85149", "回暖期": "#f0883e", "冰点期": "#58a6ff", "退潮期": "#6e7681", "发酵期": "#3fb950"}
    _trend_dots = ""
    for i in range(6, -1, -1):
        d = datetime.now() - timedelta(days=i)
        dk = d.strftime("%Y%m%d")
        phase_full = ""
        sf = REPORTS_STATUS / f"{dk}_status.json"
        df = REPORTS_DAILY / f"{dk}_report.json"
        if sf.exists():
            try:
                phase_full = (json.loads(sf.read_text(encoding="utf-8")).get("regime") or {}).get("phase", "")
            except Exception:
                pass
        if not phase_full and df.exists():
            try:
                phase_full = json.loads(df.read_text(encoding="utf-8")).get("regime", {}).get("phase", "")
            except Exception:
                pass
        clr = _regime_colors.get(phase_full, "#30363d")
        _trend_dots += f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{clr};margin:0 2px" title="{phase_full or "无数据"}"></span>'

    # 情绪1日变化
    sent_vel_str = "-"
    if latest_sensor:
        sent = (latest_sensor.get("sensors", {}) or {}).get("sentiment", {}) or {}
        sv = sent.get("sentiment_velocity", {}) or {}
        sv_1d = sv.get("change_1d")
        if sv_1d is not None and isinstance(sv_1d, (int, float)):
            arrow = "↗" if sv_1d > 0 else ("↘" if sv_1d < 0 else "→")
            sent_vel_str = f"{arrow} {sv_1d:+.0f}"

    # 情绪极端
    sent_ext_str = "-"
    if latest_sensor:
        sent2 = (latest_sensor.get("sensors", {}) or {}).get("sentiment", {}) or {}
        se = sent2.get("sentiment_extreme", {}) or {}
        if se.get("state"):
            sent_ext_str = se["state"]

    sent_conf_display = sensor_conf_label  # from existing computation

    # 板块信号列表
    market_signals_list = sensor_signals.split(", ") if sensor_signals else []
    market_signals_html = "<br>".join(market_signals_list[:3]) if market_signals_list else "无"

    # ── EA Task 1: Decision Context 展示层 ──
    ctx = _build_context_reconciliation(latest, latest_sensor)

    # ── EA Task 2: 数据源标注 ──
    # 行情源映射
    actual_sources = []
    if latest_sensor:
        # ETF 源
        etf_src = (latest_sensor.get("sensors", {}) or {}).get("etf", {}).get("data_source", "")
        if etf_src:
            actual_sources.append(f"ETF行情: {etf_src}")
        # 情绪源
        sent_src = ((latest_sensor.get("sensors", {}) or {}).get("sentiment", {}) or {}).get("market_sentiment", {}).get("_source", "")
        if sent_src:
            actual_sources.append(f"市场情绪: {sent_src}")
        # 融资源
        margin_date = (latest_sensor.get("sensors", {}) or {}).get("margin", {}).get("latest_date", "")
        if margin_date:
            actual_sources.append(f"融资: akshare")
    if not actual_sources:
        actual_sources.append("等待首次运行")
    sources_display = " / ".join(actual_sources)

    # 融资新鲜度
    margin_date = (latest_sensor.get("sensors", {}) or {}).get("margin", {}).get("latest_date", "") if latest_sensor else ""
    margin_freshness = _freshness_label(margin_date) if margin_date else ""

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="30">
<title>AQF-T 监控台</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Microsoft YaHei','Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:16px;margin-bottom:12px}}
.row{{display:flex;gap:12px;flex-wrap:wrap}}
.col{{flex:1;min-width:140px}}
.col-card{{flex:1;min-width:140px;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:14px}}
.col-card h3{{font-size:13px;color:#c9d1d9;border-bottom:1px solid #30363d;padding-bottom:8px;margin-bottom:10px;font-weight:bold}}
.stat-row{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;font-size:13px}}
.stat-label{{font-size:11px;color:#8b949e}}
.stat-val{{font-size:14px;font-weight:bold;text-align:right}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;padding:6px 8px;border-bottom:1px solid #30363d;color:#8b949e;font-weight:normal;font-size:11px}}
td{{padding:6px 8px;border-bottom:1px solid #21262d}}
.green{{color:#3fb950}}
.red{{color:#f85149}}
.yellow{{color:#d2991d}}
</style>
</head>
<body>

<!-- Dashboard v1.2: 状态条 -->
<div style="background:{status_bar_color};color:#fff;padding:14px 24px;border-radius:6px;margin-bottom:16px;font-size:15px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
  <span style="font-weight:bold">{status_bar_system}</span>
  <span style="opacity:0.6">│</span>
  <span>{status_bar_regime}</span>
  <span style="opacity:0.6">│</span>
  <span>{status_bar_actions}</span>
</div>
{health_banner if not data_available_today else ""}
{ks_html}

<!-- EA Task 1: Decision Context 展示层 -->
<div style="background:{ctx['bg_color']};color:#c9d1d9;padding:12px 20px;border-radius:6px;margin-bottom:12px;font-size:13px">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
    <span style="font-weight:bold;font-size:14px">{ctx['title']}</span>
    {f'<span style="font-size:11px;color:#8b949e">冲突: {ctx["conflicts_summary"]}</span>' if ctx['conflicts'] else '<span style="font-size:11px;color:#3fb950">✅ 一致</span>'}
  </div>
  <div style="line-height:1.7">{ctx['explanation']}</div>
</div>

<!-- Dashboard v1.3: 决策层 + 实时风险观察层 (EA+FA 2026-08-12) -->
	<div style="color:#8b949e;font-size:11px;margin-bottom:4px;padding-left:4px;border-left:3px solid #3fb950">🔒 <b>决策层</b> — AQF-T Engine 唯一权威 · Gate 控制交易权限</div>
	<div class="row">
	  <!-- 列1: AQF-T Regime + Gate -->
	  <div class="col-card" style="border-left:3px solid #3fb950">
	    <h3>&#128202; AQF-T Regime</h3>
	    <div class="stat-row"><span class="stat-label">市场状态</span><span class="stat-val" style="font-size:16px;font-weight:bold">{phase}</span></div>
	    <div class="stat-row"><span class="stat-label">Gate</span><span class="stat-val" style="color:{trade_allowed_color};font-size:15px">{'🟢 开放' if latest and latest.get('trade_allowed') else '🔒 关闭'}</span></div>
	    <div class="stat-row"><span class="stat-label">置信度</span><span class="stat-val">{confidence:.2f}</span></div>
	    <div class="stat-row"><span class="stat-label">模式</span><span class="stat-val" style="font-size:12px">{mode}</span></div>
	    <div class="stat-row"><span class="stat-label">数据源</span><span class="stat-val" style="font-size:11px">{sources_display}</span></div>
	    <div style="font-size:10px;color:#8b949e;margin-top:4px">数据日期: {latest.get("data_date", "?") if latest else "?"} · 生效: {latest.get("effective_from", "?") if latest else "?"}</div>
	    <div style="margin-top:8px"><span class="stat-label">7日趋势</span> <span style="margin-left:4px">{_trend_dots}</span></div>
	  </div>

	  <!-- 列2: 账户概览 (决策层) -->
	  <div class="col-card" style="border-left:3px solid #3fb950">
	    <h3>&#128176; 账户概览</h3>
	    <div class="stat-row"><span class="stat-label">账户总值</span><span class="stat-val">¥{total_value:,.0f}</span></div>
	    <div class="stat-row"><span class="stat-label">可用现金</span><span class="stat-val">¥{cash:,.0f}</span></div>
	    <div class="stat-row"><span class="stat-label">持仓市值</span><span class="stat-val">¥{total_value - cash:,.0f}</span></div>
	    <div style="border-top:1px solid #21262d;padding-top:6px;margin-top:6px">
	      <div class="stat-row"><span class="stat-label">今日候选</span><span class="stat-val">{total_candidates}</span></div>
	      <div class="stat-row">
	        <span class="stat-label">信号 <span class="green">{total_signals}</span></span>
	        <span class="stat-label">成交 <span class="green">{total_fills}</span></span>
	        <span class="stat-label">拒绝 <span class="red">{total_rejected}</span></span>
	      </div>
	    </div>
	    <div style="font-size:11px;color:#8b949e;margin-top:4px">总成交 {account.get('total_trades',0)} 笔 | 持仓 {positions_count} 只</div>
	  </div>
	</div>

	<!-- 实时风险观察层 (Shadow — 不参与交易决策) -->
	<div style="color:#8b949e;font-size:11px;margin-bottom:4px;margin-top:16px;padding-left:4px;border-left:3px solid #d2991d">&#128065;&#65039; <b>实时风险观察层</b> — Shadow 模式 · 采集/展示但不改变 Production Gate</div>
	<div class="row">
	  <!-- 列3: 实时市场 Sensor -->
	  <div class="col-card" style="border-left:3px solid #d2991d">
	    <h3>&#127754; 实时市场 Sensor</h3>
	    <div class="stat-row"><span class="stat-label">资金环境</span><span class="stat-val" style="color:{sensor_risk_color};font-size:13px">{sensor_risk_label}{_source_badge('pytdx' if sensor_risk_label not in ('-', '') else '')}</span></div>
	    <div class="stat-row"><span class="stat-label">环境置信</span><span class="stat-val" style="color:{sensor_conf_color}">{sent_conf_display}{_source_badge('sensor', 'aggregate')}</span></div>
	    <div class="stat-row"><span class="stat-label">情绪极端</span><span class="stat-val" style="font-size:13px">{sent_ext_str}{_source_badge('V2-realtime')}</span></div>
	    <div class="stat-row"><span class="stat-label">情绪 1日</span><span class="stat-val" style="font-size:13px">{sent_vel_str}</span></div>
	    <div style="margin-top:6px"><span class="stat-label">市场信号</span><div style="font-size:12px;color:#8b949e;margin-top:2px">{market_signals_html}</div></div>
	    {f'<div style="font-size:10px;color:#d2991d;margin-top:6px">⚠️ 融资数据: {margin_freshness}</div>' if margin_freshness and 'T+' in margin_freshness else ''}
	    <div style="font-size:10px;color:#6e7681;margin-top:8px;padding-top:6px;border-top:1px solid #21262d">👁️ Shadow · 不参与 Gate · 仅作风险观察</div>
	  </div>

	  <!-- 列4: 系统健康 (观察层) -->
	  <div class="col-card" style="border-left:3px solid #d2991d">
	    <h3>&#9881;&#65039; 系统健康</h3>
	    <div class="stat-row"><span class="stat-label">Pipeline</span><span class="stat-val" style="color:{pipeline_status_color};font-size:13px">{pipeline_status_label}</span></div>
	    <div class="stat-row"><span class="stat-label">交易许可</span><span class="stat-val" style="color:{trade_allowed_color};font-size:13px">{'允许' if latest and latest.get('trade_allowed') else '禁止'}</span></div>
	    <div style="font-size:11px;color:#8b949e;margin:-2px 0 4px 0">{trade_reason}</div>
	    <div class="stat-row"><span class="stat-label">QMT</span><span class="stat-val" style="color:{qmt_color};font-size:13px">{qmt_label}</span></div>
	    <div class="stat-row"><span class="stat-label">数据库</span><span class="stat-val" style="color:{'#3fb950' if db == 'OK' else '#f85149'};font-size:13px">{db_label}</span></div>
	    <div class="stat-row"><span class="stat-label">CPU / 内存</span><span class="stat-val" style="font-size:13px">{cpu:.0f}% / {mem:.0f}%</span></div>
	    <div class="stat-row"><span class="stat-label">数据新鲜度</span><span class="stat-val" style="color:{freshness_color};font-size:12px">{freshness_label}</span></div>
	    <div style="font-size:11px;color:#8b949e;margin-top:2px">{last_update_display}</div>
	    {f'<div style="font-size:10px;color:#d2991d;margin-top:4px">⚠️ 融资: {margin_freshness}</div>' if margin_freshness and 'T+' in margin_freshness else ''}
	  </div>
	</div>

{error_html}
{warning_html}

<!-- 持仓明细 -->
<div class="card" style="margin-top:12px">
  <h2 style="margin-bottom:8px;font-size:15px;color:#8b949e;font-weight:normal">📌 当前持仓 ({positions_count} 只)</h2>
  <table>
    <tr><th>标的</th><th style="text-align:right">数量</th><th style="text-align:right">成本</th><th style="text-align:right">市值</th><th style="text-align:right">盈亏</th><th style="text-align:right">盈亏率</th></tr>
    {position_rows if position_rows else '<tr><td colspan="6" style="color:#8b949e">空仓</td></tr>'}
  </table>
</div>

<!-- 成交明细 + 决策信号 -->
<div class="row">
  <div class="col" style="flex:2;min-width:280px">
    <div class="card">
      <h2 style="margin-bottom:8px;font-size:15px;color:#8b949e;font-weight:normal">📋 成交明细 (最近10条)</h2>
      <table>
        <tr><th>时间</th><th>标的</th><th>方向</th><th style="text-align:right">数量</th><th style="text-align:right">价格</th><th style="text-align:right">成本</th><th style="text-align:right">盈亏</th><th style="text-align:right">盈亏率</th><th>状态</th><th>原因</th></tr>
        {fill_rows if fill_rows else '<tr><td colspan="10" style="color:#8b949e">暂无成交</td></tr>'}
      </table>
    </div>
  </div>
  <div class="col" style="min-width:220px">
    <div class="card">
      <h2 style="margin-bottom:8px;font-size:15px;color:#8b949e;font-weight:normal">📡 决策信号 (最近5条)</h2>
      <table>
        <tr><th>标的</th><th>方向</th><th>策略</th><th>仓位</th><th>置信度</th><th>依据</th></tr>
        {signal_rows if signal_rows else '<tr><td colspan="6" style="color:#8b949e">暂无信号</td></tr>'}
      </table>
    </div>
  </div>
</div>

<!-- 风控拒绝 -->
<div class="card">
  <h2 style="margin-bottom:8px;font-size:15px;color:#8b949e;font-weight:normal">📛 风控拒绝</h2>
  <table>
    <tr><th>原因</th><th style="text-align:right">次数</th></tr>
    {reject_rows if reject_rows else '<tr><td colspan="2" style="color:#8b949e">无</td></tr>'}
  </table>
</div>

<!-- 7日日历 + Pattern + 退出统计 -->
<div class="row">
  <div class="col" style="min-width:220px">
    <div class="card">
      <h2 style="margin-bottom:8px;font-size:15px;color:#8b949e;font-weight:normal">📅 7日市场状态</h2>
      <div style="display:flex;gap:6px;font-size:12px">
        {_regime_calendar()}
      </div>
    </div>
  </div>
  <div class="col" style="min-width:160px">
    <div class="card">
      <h2 style="margin-bottom:8px;font-size:15px;color:#8b949e;font-weight:normal">📊 Pattern 排序</h2>
      <table style="font-size:12px">
        <tr><th>Pattern</th><th style="text-align:right">触发</th><th>状态</th></tr>
        {_pattern_ranking(pattern_evidence)}
      </table>
    </div>
  </div>
  <div class="col" style="min-width:180px">
    <div class="card">
      <h2 style="margin-bottom:8px;font-size:15px;color:#8b949e;font-weight:normal">📈 退出统计</h2>
      {_exit_summary()}
    </div>
  </div>
</div>

<!-- Footer -->
<div style="text-align:center;font-size:11px;color:#484f58;margin-top:16px;line-height:1.6">
  AQF-T v1.3 | Dashboard · 每30秒自动刷新 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
  <span style="color:#6e7681">
  数据源: TDX(pytdx) 实时行情 · akshare 融资/龙虎榜 · DeepSeek LLM情绪 · V2 eastmoney 市场情绪 · signal_table.json ML信号<br>
  👁️ Shadow: XGB v2 · CatBoost · Ridge | ML: LGBM | Rule: daban · oversold_bounce<br>
  🔒 AVP冻结中 · 8/19 Evidence Review · 只展示不决策
  </span>
</div>

</body>
</html>"""
    return html


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """多线程 HTTP 服务器 — 避免单请求阻塞整个 Dashboard"""
    daemon_threads = True


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
            # P1-DI: 返回结构化健康数据, 不只是 "OK"
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                today = get_today_data()
                health_data = {
                    "status": "ok",
                    "timestamp": datetime.now().isoformat(),
                    "data_available": today is not None,
                    "data_mode": "EOD",
                    "data_mode_desc": "日终批处理 · 每日 15:30 自动运行",
                    "qmt": get_qmt_status(),
                    "db": get_db_status(),
                    "cpu_pct": psutil.cpu_percent(interval=0.1),
                    "mem_pct": psutil.virtual_memory().percent,
                }
                if today:
                    health_data["regime"] = (today.get("regime") or {}).get("phase", "N/A")
                    health_data["data_source"] = today.get("data_source", "UNKNOWN")
                # AQF-T Health Protocol v1.0
                latest_status = get_latest_status()
                if latest_status:
                    health_data["pipeline_status"] = latest_status.get("pipeline_status", "unknown")
                    health_data["trade_allowed"] = latest_status.get("trade_allowed", False)
                    health_data["last_run"] = latest_status.get("timestamp", "")
                self.wfile.write(json.dumps(health_data, ensure_ascii=False).encode("utf-8"))
            except Exception:
                self.wfile.write(b'{"status":"error"}')
        elif self.path == "/api/sensor":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            sensor_data = get_latest_sensor()
            if sensor_data:
                self.wfile.write(json.dumps(sensor_data, ensure_ascii=False).encode("utf-8"))
            else:
                self.wfile.write(b'{"error":"no sensor data available"}')
        elif self.path == "/api/sensor/summary":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            sensor_data = get_latest_sensor()
            if sensor_data:
                summary = sensor_data.get("summary", {})
                sentiment = (sensor_data.get("sensors", {}) or {}).get("sentiment", {}) or {}
                light = {
                    "date": sensor_data.get("date", ""),
                    "risk_appetite": summary.get("risk_appetite", ""),
                    "confidence": summary.get("confidence", ""),
                    "signals": summary.get("signals", []),
                    "sentiment_confidence": sentiment.get("sentiment_confidence", {}).get("value"),
                    "sentiment_extreme": sentiment.get("sentiment_extreme", {}).get("state"),
                    "sentiment_velocity_1d": sentiment.get("sentiment_velocity", {}).get("change_1d"),
                }
                self.wfile.write(json.dumps(light, ensure_ascii=False).encode("utf-8"))
            else:
                self.wfile.write(b'{"error":"no sensor data available"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # silent


def main():
    print(f"\n  AQF-T Dashboard")
    print(f"  http://127.0.0.1:{PORT}")
    print(f"  Ctrl+C to stop\n")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dashboard stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
