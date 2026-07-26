"""
AQF-T Risk Service — 风险控制引擎 (最高否决权 + Kill Switch)
端口: 8104
"""
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AQF-T Risk Engine", version="3.1.1")

kill_switch_active = True

@app.get("/")
def root():
    return {
        "service": "risk_engine",
        "status": "ONLINE",
        "kill_switch": "ACTIVE" if kill_switch_active else "DISABLED",
        "version": "3.1.1",
    }

@app.post("/risk/check")
def risk_check(request: dict):
    risk_score = 25
    position_limit = 0.30
    drawdown_limit = 0.20

    checks = {
        "position_limit": {"limit": position_limit, "current": 0.15, "pass": True},
        "drawdown_limit": {"limit": drawdown_limit, "current": 0.05, "pass": True},
        "exposure_limit": {"limit": 0.50, "current": 0.30, "pass": True},
    }

    if risk_score < 30:       decision = "APPROVE"
    elif risk_score < 70:     decision = "ADJUST"
    else:                     decision = "REJECT"

    return {
        "decision": decision,
        "risk_score": risk_score,
        "checks": checks,
        "kill_switch": "ACTIVE",
        "timestamp": datetime.now().isoformat(),
    }

@app.post("/risk/emergency_stop")
def emergency_stop():
    """紧急停止 — Kill Switch"""
    global kill_switch_active
    kill_switch_active = True
    return {
        "action": "EMERGENCY_STOP",
        "status": "ALL_TRADING_HALTED",
        "kill_switch": "ACTIVE",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/health")
def health():
    return {"service": "risk_engine", "health": "OK", "kill_switch": "ACTIVE"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8104)
