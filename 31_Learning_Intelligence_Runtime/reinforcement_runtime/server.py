"""
AQF-T Reinforcement Runtime — 强化学习环境
端口: 8122

AQF-T Arena: State→Action→Reward→Policy Update
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from datetime import datetime
from collections import defaultdict

app = FastAPI(title="AQF-T Reinforcement Runtime", version="3.4.0")

# Q-Table: (regime, volatility_level, action) -> expected_value
q_table: dict[tuple, float] = defaultdict(float)
learning_rate = 0.1
discount_factor = 0.9
episode_count = [0]


def _state_key(world: dict) -> tuple:
    regime = world.get("regime", "Unknown")
    vol = world.get("volatility", 0.15)
    vol_level = "Low" if vol < 0.1 else "Medium" if vol < 0.3 else "High"
    return (regime, vol_level)


def _calc_reward(outcome: dict) -> float:
    """AQF-T 奖励函数: 收益 - 风险惩罚 - 回撤惩罚 + 稳定性奖励"""
    ret = outcome.get("return", 0)
    drawdown = outcome.get("drawdown", 0)
    risk = outcome.get("risk_score", 30)
    return ret * 100 - drawdown * 50 - risk * 0.5 + 1.0


@app.get("/")
def root():
    return {
        "service": "reinforcement_runtime",
        "episodes": episode_count[0],
        "q_table_size": len(q_table),
    }

@app.post("/reinforcement/learn")
def learn(request: dict):
    """单次学习: State→Action→Reward→Update Q"""
    world = request.get("world_state", {})
    action = request.get("action", "HOLD")
    outcome = request.get("outcome", {})

    state = _state_key(world)
    reward = _calc_reward(outcome)
    episode_count[0] += 1

    # Q-Learning update
    old_q = q_table.get((*state, action), 0)
    best_next = max([q_table.get((*state, a), 0) for a in ["BUY","SELL","HOLD","REDUCE","INCREASE"]], default=0)
    new_q = old_q + learning_rate * (reward + discount_factor * best_next - old_q)
    q_table[(*state, action)] = new_q

    return {
        "state": state,
        "action": action,
        "reward": round(reward, 2),
        "q_value": round(new_q, 2),
        "episode": episode_count[0],
    }

@app.get("/reinforcement/policy")
def policy():
    """当前学到的策略: 每个状态下最优Action"""
    actions = ["BUY", "SELL", "HOLD", "REDUCE", "INCREASE"]
    policy_rules = {}
    states = set(k[:2] for k in q_table.keys())
    for s in states:
        best_action = max(actions, key=lambda a: q_table.get((*s, a), 0))
        best_value = q_table.get((*s, best_action), 0)
        policy_rules[f"{s[0]}_{s[1]}"] = {"action": best_action, "value": round(best_value, 2)}
    return {"policy": policy_rules, "episodes": episode_count[0]}

@app.get("/health")
def health():
    return {"service": "reinforcement_runtime", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8122)
