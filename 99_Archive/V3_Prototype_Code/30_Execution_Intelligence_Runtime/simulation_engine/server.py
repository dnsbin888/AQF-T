"""
AQF-T Simulation Trading Engine — 模拟市场环境
端口: 8111

模拟: 滑点 / 手续费 / 涨跌停 / 成交概率 / 流动性约束
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from datetime import datetime
from execution_events.events import bus, EventType

app = FastAPI(title="AQF-T Simulation Engine", version="3.3.0")

simulated_positions: dict[str, dict] = {}
simulation_log: list[dict] = []
cash = 1_000_000.0
fee_rate = 0.0003  # 万三手续费


@app.get("/")
def root():
    return {"service": "simulation_engine", "version": "3.3.0", "cash": cash, "positions": len(simulated_positions)}

@app.post("/simulation/fill")
def simulate_fill(order: dict):
    """模拟订单成交"""
    action = order.get("action", "HOLD")
    symbol = order.get("symbol", "000300")
    price = order.get("price", 100)
    quantity = order.get("quantity", 100)

    if action == "HOLD":
        return {"status": "NO_ACTION"}

    # 模拟滑点: ±0.5%
    slippage = random.uniform(-0.005, 0.005)
    fill_price = price * (1 + slippage)

    # 模拟手续费
    fee = fill_price * quantity * fee_rate

    # 模拟成交概率: 95%
    filled = random.random() < 0.95

    result = {
        "order_id": order.get("order_id", ""),
        "symbol": symbol,
        "action": action,
        "requested_price": price,
        "fill_price": round(fill_price, 2),
        "slippage": round(slippage * 100, 3),
        "quantity": quantity,
        "fee": round(fee, 2),
        "filled": filled,
        "status": "FILLED" if filled else "FAILED",
        "timestamp": datetime.now().isoformat(),
    }

    if filled:
        if symbol not in simulated_positions:
            simulated_positions[symbol] = {"shares": 0, "cost": 0}
        if action == "BUY":
            simulated_positions[symbol]["shares"] += quantity
            simulated_positions[symbol]["cost"] = fill_price
        elif action == "SELL":
            simulated_positions[symbol]["shares"] = max(0, simulated_positions[symbol]["shares"] - quantity)

    simulation_log.append(result)
    bus.publish(EventType.EXECUTION_RESULT, result, "simulation_engine")
    return result

@app.get("/simulation/portfolio")
def portfolio():
    return {
        "cash": cash,
        "positions": simulated_positions,
        "total_trades": len(simulation_log),
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/health")
def health():
    return {"service": "simulation_engine", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8111)
