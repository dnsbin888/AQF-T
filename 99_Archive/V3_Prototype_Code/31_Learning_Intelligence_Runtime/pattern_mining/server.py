"""
AQF-T Pattern Mining — 规律发现引擎 (端口: 8124)
从交易经验中自动发现市场规律
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi import FastAPI
from datetime import datetime
from collections import Counter

app = FastAPI(title="AQF-T Pattern Mining", version="3.4.5")
discovered_rules: list[dict] = []


@app.get("/")
def root():
    return {"service": "pattern_mining", "rules_discovered": len(discovered_rules)}

@app.post("/pattern_mining/discover")
def discover(experiences: list[dict]):
    """从一批经验中自动发现规律"""
    global discovered_rules
    rules = []

    # Rule 1: Regime-Action 关联
    regime_actions = Counter()
    regime_results = {}
    for e in experiences:
        regime = e.get("world_state", {}).get("regime", "")
        action = e.get("decision", {}).get("action", "")
        pnl = e.get("outcome", {}).get("return", 0)
        key = f"{regime}|{action}"
        regime_actions[key] += 1
        if key not in regime_results:
            regime_results[key] = []
        regime_results[key].append(pnl)

    for key, pnls in regime_results.items():
        avg = sum(pnls) / len(pnls) if pnls else 0
        regime, action = key.split("|")
        if avg > 0.015 and len(pnls) >= 2:
            rules.append({
                "type": "regime_action",
                "condition": f"IF regime='{regime}' THEN action='{action}'",
                "avg_return": round(avg, 4),
                "confidence": round(min(len(pnls)/5, 1.0), 2),
                "samples": len(pnls),
            })

    # Rule 2: Volatility-Risk 关联
    for e in experiences:
        vol = e.get("world_state", {}).get("volatility", 0.15)
        risk_d = e.get("risk", {}).get("decision", "")
        pnl = e.get("outcome", {}).get("return", 0)
        if vol > 0.25 and risk_d == "ADJUST" and pnl > -0.02:
            rules.append({
                "type": "volatility_risk",
                "condition": "IF volatility>25% THEN risk=ADJUST reduces loss",
                "avg_return": round(pnl, 4),
                "confidence": 0.75,
                "samples": 1,
            })

    # Rule 3: Trend-Confidence 关联
    high_conf_wins = [e for e in experiences
                      if e.get("decision", {}).get("confidence", 0) > 0.8
                      and e.get("outcome", {}).get("return", 0) > 0]
    if len(high_conf_wins) >= 2:
        rules.append({
            "type": "confidence_quality",
            "condition": "IF confidence>80% THEN win_rate increases",
            "avg_return": round(sum(e["outcome"]["return"] for e in high_conf_wins)/len(high_conf_wins), 4),
            "confidence": 0.82,
            "samples": len(high_conf_wins),
        })

    discovered_rules = rules[-50:]  # keep top 50
    return {"rules": rules, "total_discovered": len(discovered_rules)}

@app.get("/pattern_mining/rules")
def get_rules():
    return {"rules": discovered_rules, "timestamp": datetime.now().isoformat()}

@app.get("/health")
def health():
    return {"service": "pattern_mining", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8124)
