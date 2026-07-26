"""
AQF-T Service Registry — 服务发现与健康检查
端口: 8100
"""
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AQF-T Service Registry", version="3.1.1")

services = {
    "gateway":         {"port": 8080, "status": "active"},
    "agent_service":   {"port": 8101, "status": "active"},
    "world_model":     {"port": 8102, "status": "active"},
    "decision_engine": {"port": 8103, "status": "active"},
    "risk_engine":     {"port": 8104, "status": "active"},
    "memory_service":  {"port": 8105, "status": "active"},
    "market_data":     {"port": 8106, "status": "active"},
    "message_bus":     {"port": 8200, "status": "active"},
}

@app.get("/")
def registry_root():
    return {"registry": "AQF-T Service Registry", "services": len(services)}

@app.get("/services")
def list_services():
    return {"services": services, "timestamp": datetime.now().isoformat()}

@app.get("/health")
def health():
    return {"health": "OK"}

@app.post("/register")
def register(name: str, port: int):
    services[name] = {"port": port, "status": "active"}
    return {"registered": name, "port": port}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8100)
