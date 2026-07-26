"""
AQF-T Experiment Engine — 策略实验沙盒 (端口: 8127)
Hypothesis → Experiment → Result → Knowledge
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AQF-T Experiment Engine", version="3.4.5")
experiments: list[dict] = []


@app.get("/")
def root():
    return {"service": "experiment_engine", "experiments": len(experiments)}

@app.post("/experiment/run")
def run_experiment(hypothesis: dict):
    """运行一个策略假设实验"""
    exp_id = f"EXP-{len(experiments)+1:04d}"

    # Simulate experiment result
    import random
    result = {
        "id": exp_id,
        "hypothesis": hypothesis.get("description", ""),
        "strategy": hypothesis.get("strategy", ""),
        "regime": hypothesis.get("regime", ""),
        "result": {
            "return": round(random.gauss(0.02, 0.04), 4),
            "sharpe": round(random.gauss(1.2, 0.5), 2),
            "max_drawdown": round(random.uniform(0.02, 0.20), 3),
            "win_rate": round(random.uniform(0.40, 0.70), 2),
        },
        "verdict": "PROMOTE" if random.random() > 0.4 else "DISCARD",
        "timestamp": datetime.now().isoformat(),
    }
    experiments.append(result)
    return {"experiment": result}

@app.get("/experiment/list")
def list_experiments():
    promoted = [e for e in experiments if e["verdict"] == "PROMOTE"]
    return {"total": len(experiments), "promoted": len(promoted), "recent": experiments[-10:]}

@app.get("/health")
def health():
    return {"service": "experiment_engine", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8127)
