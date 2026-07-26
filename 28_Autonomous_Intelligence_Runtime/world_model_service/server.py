"""
AQF-T World Model Service — 五层认知引擎
端口: 8102
"""
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AQF-T World Model", version="3.1.1")

@app.get("/")
def root():
    return {"service": "world_model", "status": "ONLINE", "version": "3.1.1"}

@app.get("/world/state")
def world_state():
    return {
        "market": "China A-Share",
        "regime": "Bull Expansion",
        "liquidity": "Expansion",
        "volatility": "Medium",
        "sentiment": "Greed (65/100)",
        "risk_level": 35,
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/world/regime")
def regime():
    return {
        "current": "World-001 (Bull Expansion)",
        "confidence": 0.87,
        "phase": "Mid",
        "next_regime_probability": {
            "Bull_Continue": 0.62,
            "Sideways": 0.25,
            "Reversal": 0.13,
        },
    }

@app.get("/health")
def health():
    return {"service": "world_model", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8102)
