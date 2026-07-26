"""
AQF-T Memory Service — 模拟记忆与经验检索
端口: 8105
"""
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AQF-T Memory Service", version="3.1.1")

memory_store = [
    {"id": "M-001", "world": "Bull Expansion", "action": "HOLD", "outcome": "+35%", "importance": 85},
    {"id": "M-002", "world": "Liquidity Crisis", "action": "REDUCE", "outcome": "-8% (avoided -25%)", "importance": 95},
    {"id": "M-003", "world": "Policy Stimulus", "action": "INCREASE", "outcome": "+42%", "importance": 80},
]

@app.get("/")
def root():
    return {"service": "memory_service", "experiences": len(memory_store), "status": "ONLINE"}

@app.get("/memory/search")
def search(world: str = "", top_k: int = 5):
    results = [m for m in memory_store if world.lower() in m["world"].lower()]
    return {"query": world, "results": results[:top_k], "timestamp": datetime.now().isoformat()}

@app.post("/memory/store")
def store(experience: dict):
    memory_store.append(experience)
    return {"stored": experience.get("id"), "total": len(memory_store)}

@app.get("/health")
def health():
    return {"service": "memory_service", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8105)
