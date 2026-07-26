"""
AQF-T Knowledge Graph — 金融市场因果知识图谱 (端口: 8125)
事件→原因→结果→规律
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AQF-T Knowledge Graph", version="3.4.5")

# 预建金融因果知识
graph = {
    "nodes": {
        "rate_cut": {"type": "policy", "label": "降息"},
        "rate_hike": {"type": "policy", "label": "加息"},
        "liquidity_expand": {"type": "market", "label": "流动性扩张"},
        "liquidity_tighten": {"type": "market", "label": "流动性收缩"},
        "growth_up": {"type": "sector", "label": "成长股上涨"},
        "growth_down": {"type": "sector", "label": "成长股下跌"},
        "value_up": {"type": "sector", "label": "价值股上涨"},
        "risk_on": {"type": "sentiment", "label": "Risk On"},
        "risk_off": {"type": "sentiment", "label": "Risk Off"},
        "bull_regime": {"type": "regime", "label": "牛市环境"},
        "bear_regime": {"type": "regime", "label": "熊市环境"},
    },
    "edges": [
        {"from": "rate_cut", "to": "liquidity_expand", "weight": 0.85, "lag": "3d"},
        {"from": "rate_hike", "to": "liquidity_tighten", "weight": 0.80, "lag": "5d"},
        {"from": "liquidity_expand", "to": "growth_up", "weight": 0.72, "lag": "1w"},
        {"from": "liquidity_expand", "to": "risk_on", "weight": 0.68, "lag": "3d"},
        {"from": "liquidity_tighten", "to": "growth_down", "weight": 0.75, "lag": "1w"},
        {"from": "liquidity_tighten", "to": "risk_off", "weight": 0.70, "lag": "2d"},
        {"from": "risk_on", "to": "bull_regime", "weight": 0.65, "lag": "1w"},
        {"from": "risk_off", "to": "bear_regime", "weight": 0.62, "lag": "1w"},
        {"from": "rate_cut", "to": "value_up", "weight": 0.55, "lag": "2w"},
    ],
}


@app.get("/")
def root():
    return {"service": "knowledge_graph", "nodes": len(graph["nodes"]), "edges": len(graph["edges"])}

@app.get("/knowledge_graph/traverse")
def traverse(from_node: str = "rate_cut"):
    """从某个节点出发遍历因果链"""
    path = [from_node]
    visited = {from_node}
    current = from_node

    for _ in range(5):
        next_edges = [e for e in graph["edges"] if e["from"] == current and e["to"] not in visited]
        if not next_edges:
            break
        best = max(next_edges, key=lambda e: e["weight"])
        current = best["to"]
        visited.add(current)
        path.append(f"{current} (w={best['weight']}, lag={best['lag']})")

    return {"from": from_node, "causal_chain": " → ".join(path), "depth": len(path)}

@app.get("/knowledge_graph/impact")
def impact(event: str):
    """查询某个事件的影响范围"""
    affected = [e["to"] for e in graph["edges"] if e["from"] == event]
    return {"event": event, "label": graph["nodes"].get(event, {}).get("label", ""),
            "affects": affected, "timestamp": datetime.now().isoformat()}

@app.get("/health")
def health():
    return {"service": "knowledge_graph", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8125)
