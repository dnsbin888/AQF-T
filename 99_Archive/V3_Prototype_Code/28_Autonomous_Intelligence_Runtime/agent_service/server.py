"""
AQF-T Agent Service — Multi-Agent 协调中心
端口: 8101
"""
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AQF-T Agent Council", version="3.1.1")

agents = {
    "market_agent":    {"status": "active", "role": "市场感知"},
    "strategy_agent":  {"status": "active", "role": "策略生成"},
    "risk_agent":      {"status": "active", "role": "风险审批"},
    "execution_agent": {"status": "standby", "role": "交易执行"},
    "analyst_agent":   {"status": "active", "role": "绩效分析"},
    "supervisor_agent":{"status": "active", "role": "协调仲裁"},
}

@app.get("/")
def root():
    return {"service": "agent_council", "agents": len(agents), "status": "ONLINE"}

@app.get("/agents")
def list_agents():
    return {"agents": agents, "timestamp": datetime.now().isoformat()}

@app.post("/agents/coordinate")
def coordinate(request: dict):
    """Agent 协调 — Supervisor 仲裁"""
    return {
        "decision": "CONSENSUS",
        "voting": {
            "market_agent": "BULL",
            "strategy_agent": "HOLD",
            "risk_agent": "APPROVE",
        },
        "supervisor_decision": "HOLD",
        "confidence": 0.82,
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/health")
def health():
    return {"service": "agent_council", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8101)
