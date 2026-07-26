"""
AQF-T Evaluation Engine — AI模块绩效评分
端口: 8121

给每个智能模块打分: World Model / Agent / Decision / Risk / Execution
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AQF-T Evaluation Engine", version="3.4.0")

module_scores = {
    "world_model":    {"accuracy": 0.0, "count": 0, "total_score": 0},
    "agent_council":  {"accuracy": 0.0, "count": 0, "total_score": 0},
    "decision_engine":{"accuracy": 0.0, "count": 0, "total_score": 0},
    "risk_engine":    {"accuracy": 0.0, "count": 0, "total_score": 0},
    "execution":      {"accuracy": 0.0, "count": 0, "total_score": 0},
}


@app.get("/")
def root():
    return {"service": "evaluation_engine", "modules": len(module_scores)}

@app.post("/evaluation/score")
def score(request: dict):
    """给一次交易中的各模块打分"""
    results = {}
    for module in module_scores:
        score_val = _evaluate_module(module, request)
        ms = module_scores[module]
        ms["count"] += 1
        ms["total_score"] += score_val
        ms["accuracy"] = round(ms["total_score"] / ms["count"], 2)
        results[module] = {"score": score_val, "cumulative": ms["accuracy"]}
    return {"evaluation": results, "timestamp": datetime.now().isoformat()}


def _evaluate_module(module: str, ctx: dict) -> float:
    """单模块评价"""
    world = ctx.get("world_state", {})
    decision = ctx.get("decision", {})
    risk = ctx.get("risk", {})
    outcome = ctx.get("outcome", {})

    if module == "world_model":
        regime = world.get("regime", "")
        actual_trend = outcome.get("actual_trend", "NEUTRAL")
        if "Bull" in regime and actual_trend == "UP":   return 8.0
        if "Bear" in regime and actual_trend == "DOWN":  return 8.0
        return 5.0

    if module == "decision_engine":
        action = decision.get("action", "HOLD")
        pnl = outcome.get("return", 0)
        if action == "BUY"  and pnl > 0:   return 9.0
        if action == "SELL" and pnl < 0:   return 9.0
        if action == "HOLD" and abs(pnl) < 0.01: return 7.0
        return 4.0

    if module == "risk_engine":
        risk_decision = risk.get("decision", "")
        drawdown = outcome.get("drawdown", 0)
        if risk_decision == "REJECT" and drawdown > 0.03:  return 9.0
        if risk_decision == "APPROVE" and drawdown < 0.02: return 8.0
        return 6.0

    if module == "agent_council":
        consensus = ctx.get("agent_consensus", {})
        pnl = outcome.get("return", 0)
        sup = consensus.get("supervisor_decision", "")
        if sup == "BUY" and pnl > 0:   return 8.0
        if sup == "HOLD":              return 6.0
        return 5.0

    if module == "execution":
        execution = ctx.get("execution", {})
        slippage = abs(execution.get("slippage", 0))
        if slippage < 0.1:   return 9.0
        if slippage < 0.5:   return 7.0
        return 5.0

    return 5.0


@app.get("/evaluation/report")
def report():
    """模块绩效报告"""
    ranked = sorted(module_scores.items(), key=lambda x: x[1]["accuracy"], reverse=True)
    return {
        "modules": {name: data for name, data in ranked},
        "best": ranked[0][0] if ranked else "N/A",
        "worst": ranked[-1][0] if ranked else "N/A",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/health")
def health():
    return {"service": "evaluation_engine", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8121)
