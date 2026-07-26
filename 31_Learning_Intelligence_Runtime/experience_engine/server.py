"""
AQF-T Experience Engine — 原始日志→结构化经验
端口: 8120

核心跃迁: Memory≠Log. Experience=Context+Action+Outcome+Lesson
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AQF-T Experience Engine", version="3.4.0")

experiences: list[dict] = []
patterns: dict[str, list[dict]] = {}


def extract_lesson(exp: dict) -> str:
    """从交易结果中提取经验教训"""
    outcome = exp.get("outcome", {})
    decision = exp.get("decision", {})
    world = exp.get("world_state", {})

    pnl = outcome.get("return", 0)
    regime = world.get("regime", "")
    confidence = decision.get("confidence", 0)

    if pnl > 0.03 and confidence > 0.7:
        return f"High confidence decisions in {regime} tend to succeed"
    elif pnl < -0.02:
        return f"Low confidence (<{confidence}) in {regime} = higher risk"
    elif world.get("volatility", 0) > 0.3:
        return f"High volatility ({world.get('volatility')}) → reduce exposure recommended"
    else:
        return f"Normal market: follow standard strategy"


@app.get("/")
def root():
    return {"service": "experience_engine", "experiences": len(experiences), "patterns": len(patterns)}

@app.post("/experience/extract")
def extract(request: dict):
    """将原始交易事件转换为结构化经验"""
    exp = {
        "id": f"EXP-{len(experiences)+1:05d}",
        "world_state": request.get("world_state", {}),
        "decision": request.get("decision", {}),
        "risk": request.get("risk", {}),
        "execution": request.get("execution", {}),
        "outcome": request.get("outcome", {}),
        "lesson": extract_lesson(request),
        "importance": _calc_importance(request),
        "timestamp": datetime.now().isoformat(),
    }
    experiences.append(exp)

    # 按Regime聚合
    regime = exp["world_state"].get("regime", "Unknown")
    if regime not in patterns:
        patterns[regime] = []
    patterns[regime].append(exp)

    return {"experience": exp, "patterns_discovered": len(patterns)}


def _calc_importance(exp: dict) -> int:
    """经验重要性评分"""
    score = 30
    pnl = abs(exp.get("outcome", {}).get("return", 0))
    if pnl > 0.05:   score += 30
    if pnl > 0.02:   score += 15
    if exp.get("risk", {}).get("decision") == "ADJUST": score += 20
    if exp.get("risk", {}).get("decision") == "REJECT": score += 40
    return min(score, 100)


@app.get("/experience/patterns")
def get_patterns():
    """返回按Regime聚合的经验模式"""
    return {
        "regimes": list(patterns.keys()),
        "pattern_count": {k: len(v) for k, v in patterns.items()},
        "top_lessons": [e["lesson"] for e in experiences[-5:]],
    }

@app.get("/health")
def health():
    return {"service": "experience_engine", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8120)
