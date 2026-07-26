"""
AQF-T Portfolio Manager — 资产组合状态管理
端口: 8112
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from datetime import datetime
from execution_events.events import bus, EventType

app = FastAPI(title="AQF-T Portfolio Manager", version="3.3.0")

portfolio = {
    "cash": 1_000_000.0,
    "initial_capital": 1_000_000.0,
    "positions": {},
    "total_trades": 0,
    "realized_pnl": 0.0,
    "max_drawdown": 0.0,
    "peak_value": 1_000_000.0,
}

@app.get("/")
def root():
    total_value = portfolio["cash"]
    for pos in portfolio["positions"].values():
        total_value += pos.get("market_value", 0)
    pnl = total_value - portfolio["initial_capital"]
    return {
        "service": "portfolio_manager",
        "total_value": round(total_value, 2),
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl / portfolio["initial_capital"] * 100, 2),
        "positions": len(portfolio["positions"]),
    }

@app.post("/portfolio/update")
def update_portfolio(event: dict):
    """接收 Execution Event → 更新组合状态"""
    global portfolio
    action = event.get("action", "")
    symbol = event.get("symbol", "")
    fill_price = event.get("fill_price", 0)
    quantity = event.get("quantity", 0)

    if action == "BUY":
        cost = fill_price * quantity
        portfolio["cash"] -= cost
        if symbol not in portfolio["positions"]:
            portfolio["positions"][symbol] = {"shares": 0, "avg_cost": 0}
        pos = portfolio["positions"][symbol]
        total_shares = pos["shares"] + quantity
        pos["avg_cost"] = (pos["avg_cost"] * pos["shares"] + fill_price * quantity) / total_shares if total_shares > 0 else 0
        pos["shares"] = total_shares
        pos["market_value"] = pos["shares"] * fill_price
    elif action == "SELL":
        pos = portfolio["positions"].get(symbol, {"shares": 0})
        sell_shares = min(quantity, pos["shares"])
        revenue = fill_price * sell_shares
        portfolio["cash"] += revenue
        pos["shares"] -= sell_shares
        pos["market_value"] = pos["shares"] * fill_price

    portfolio["total_trades"] += 1

    # Max drawdown tracking
    total_value = portfolio["cash"] + sum(p.get("market_value", 0) for p in portfolio["positions"].values())
    if total_value > portfolio["peak_value"]:
        portfolio["peak_value"] = total_value
    current_drawdown = (portfolio["peak_value"] - total_value) / portfolio["peak_value"] if portfolio["peak_value"] > 0 else 0
    portfolio["max_drawdown"] = max(portfolio["max_drawdown"], current_drawdown)

    bus.publish(EventType.PORTFOLIO_UPDATED, {
        "total_value": round(total_value, 2),
        "drawdown": round(current_drawdown * 100, 2),
        "max_drawdown": round(portfolio["max_drawdown"] * 100, 2),
    }, "portfolio_manager")

    return {"status": "updated", "total_value": round(total_value, 2)}

@app.get("/portfolio/status")
def status():
    total_value = portfolio["cash"]
    for pos in portfolio["positions"].values():
        total_value += pos.get("market_value", 0)
    return {
        "cash": round(portfolio["cash"], 2),
        "positions": portfolio["positions"],
        "total_value": round(total_value, 2),
        "pnl": round(total_value - portfolio["initial_capital"], 2),
        "pnl_pct": round((total_value - portfolio["initial_capital"]) / portfolio["initial_capital"] * 100, 2),
        "max_drawdown": round(portfolio["max_drawdown"] * 100, 2),
        "total_trades": portfolio["total_trades"],
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/health")
def health():
    return {"service": "portfolio_manager", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8112)
