"""
AQF-T Execution Engine — 决策转订单
端口: 8110
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from datetime import datetime
from execution_events.events import bus, EventType

app = FastAPI(title="AQF-T Execution Engine", version="3.3.0")

orders: list[dict] = []
order_counter = [0]

@app.get("/")
def root():
    return {"service": "execution_engine", "version": "3.3.0", "orders_total": len(orders)}

@app.post("/execution/execute")
def execute(request: dict):
    """接收 Decision + Risk Approval → 生成订单"""
    risk_decision = request.get("risk_decision", "")
    if risk_decision == "REJECT":
        return {"status": "REJECTED", "reason": "Risk Engine rejected"}

    order_counter[0] += 1
    order = {
        "order_id": f"AQFT-ORD-{order_counter[0]:05d}",
        "symbol": request.get("symbol", "000300"),
        "action": request.get("action", "HOLD"),
        "quantity": request.get("quantity", 100),
        "price": request.get("price", 0),
        "risk_decision": risk_decision,
        "status": "CREATED",
        "timestamp": datetime.now().isoformat(),
    }
    orders.append(order)

    bus.publish(EventType.ORDER_CREATED, order, "execution_engine")
    return {"order": order, "status": "CREATED"}

@app.get("/execution/orders")
def list_orders(limit: int = 20):
    return {"orders": orders[-limit:], "total": len(orders)}

@app.get("/health")
def health():
    return {"service": "execution_engine", "health": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8110)
