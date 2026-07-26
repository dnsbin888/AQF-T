"""
AQF-T Strategy Memory — 长期持久记忆 (端口: 8123)
重启不丢失。按类型索引。
"""
import json, sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi import FastAPI

app = FastAPI(title="AQF-T Strategy Memory", version="3.4.5")

DATA_DIR = Path(__file__).parent / "experience_store"
DATA_DIR.mkdir(exist_ok=True)

STORE_FILES = {
    "market_cases": DATA_DIR / "market_cases.json",
    "success_cases": DATA_DIR / "success_cases.json",
    "failed_cases": DATA_DIR / "failed_cases.json",
    "strategy_rules": DATA_DIR / "strategy_rules.json",
}


def _load(store: str) -> list:
    path = STORE_FILES.get(store)
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def _save(store: str, data: list):
    path = STORE_FILES.get(store)
    if path:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@app.get("/")
def root():
    return {"service": "strategy_memory", "version": "3.4.5",
            "stores": {k: len(_load(k)) for k in STORE_FILES}}

@app.post("/strategy_memory/store")
def store(experience: dict):
    """持久化存储经验，按类型分库"""
    outcome = experience.get("outcome", {})
    pnl = outcome.get("return", 0)

    # 所有案例
    cases = _load("market_cases")
    cases.append({**experience, "stored_at": datetime.now().isoformat()})
    if len(cases) > 1000:
        cases = cases[-500:]
    _save("market_cases", cases)

    # 成功/失败分库
    if pnl > 0.02:
        s = _load("success_cases")
        s.append(experience)
        _save("success_cases", s[-200:])
    elif pnl < -0.02:
        f = _load("failed_cases")
        f.append(experience)
        _save("failed_cases", f[-200:])

    return {"stored": True, "total_cases": len(cases),
            "successes": len(_load("success_cases")), "failures": len(_load("failed_cases"))}

@app.get("/strategy_memory/query")
def query(regime: str = "", min_pnl: float = 0):
    """按市场环境查询历史经验"""
    cases = _load("market_cases")
    results = [c for c in cases
               if (not regime or regime in c.get("world_state", {}).get("regime", ""))
               and c.get("outcome", {}).get("return", 0) >= min_pnl]
    summary = {}
    for c in results:
        regime_k = c.get("world_state", {}).get("regime", "?")
        if regime_k not in summary:
            summary[regime_k] = {"count": 0, "avg_return": 0, "best_action": ""}
        summary[regime_k]["count"] += 1
        summary[regime_k]["avg_return"] += c.get("outcome", {}).get("return", 0)
    for k in summary:
        summary[k]["avg_return"] = round(summary[k]["avg_return"] / summary[k]["count"], 4)
    return {"query": regime, "results": results[-20:], "summary": summary}

@app.get("/health")
def health():
    return {"service": "strategy_memory", "health": "OK", "persistent": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8123)
