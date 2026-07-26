"""
AQF-T Model Evolution — 策略进化引擎 (端口: 8126)
Old Strategy → Performance → Mutation → Backtest → Promotion
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AQF-T Model Evolution", version="3.4.5")

strategies = [
    {"id": "S-001", "name": "Trend Following", "weight": 0.35, "regime_fit": "Bull Expansion",
     "performance": 0.12, "status": "active", "generation": 1},
    {"id": "S-002", "name": "Mean Reversion", "weight": 0.25, "regime_fit": "Sideways",
     "performance": 0.05, "status": "active", "generation": 1},
    {"id": "S-003", "name": "Defensive", "weight": 0.20, "regime_fit": "Bear Decline",
     "performance": -0.02, "status": "active", "generation": 1},
    {"id": "S-004", "name": "AI Adaptive", "weight": 0.20, "regime_fit": "Any",
     "performance": 0.08, "status": "active", "generation": 1},
]
evolution_log: list[dict] = []
generation_counter = [1]


@app.get("/")
def root():
    active = [s for s in strategies if s["status"] == "active"]
    return {"service": "model_evolution", "strategies": len(strategies), "active": len(active),
            "generation": generation_counter[0]}

@app.post("/model_evolution/evolve")
def evolve(request: dict):
    """策略进化: 评估→变异→选择"""
    global strategies

    # 1. Evaluate: 根据最近表现调整权重
    for s in strategies:
        perf_delta = random.gauss(0, 0.02)
        s["performance"] = round(s["performance"] + perf_delta, 4)
        s["weight"] = round(max(0.05, min(0.50, s["weight"] + perf_delta * 0.5)), 2)

    # 归一化权重
    total_w = sum(s["weight"] for s in strategies)
    for s in strategies:
        s["weight"] = round(s["weight"] / total_w, 2)

    # 2. Mutation: 表现差的策略变异
    worst = min(strategies, key=lambda s: s["performance"])
    if worst["performance"] < -0.03:
        generation_counter[0] += 1
        new_strategy = {
            "id": f"S-{len(strategies)+1:03d}",
            "name": f"{worst['name']} v{generation_counter[0]}",
            "weight": 0.10,
            "regime_fit": random.choice(["Bull Expansion", "Bear Decline", "Sideways", "High Volatility"]),
            "performance": 0.0,
            "status": "candidate",
            "generation": generation_counter[0],
            "parent": worst["id"],
        }
        strategies.append(new_strategy)
        worst["status"] = "retired"

    evolution_log.append({
        "timestamp": datetime.now().isoformat(),
        "generation": generation_counter[0],
        "active_strategies": len([s for s in strategies if s["status"] == "active"]),
    })

    return {"strategies": strategies, "generation": generation_counter[0]}

@app.get("/model_evolution/portfolio")
def get_portfolio():
    """当前策略组合"""
    active = [s for s in strategies if s["status"] in ("active", "candidate")]
    return {
        "strategies": active,
        "generation": generation_counter[0],
        "best": max(active, key=lambda s: s["performance"])["name"] if active else "N/A",
    }

@app.get("/health")
def health():
    return {"service": "model_evolution", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8126)
