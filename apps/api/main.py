"""
AQF-T API Gateway — FastAPI 入口
启动: python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8080 --reload
"""
import sys
from pathlib import Path

# 确保项目根目录在 Python path 中
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="AQF-T Intelligence API",
    version="3.1.0",
    description="Autonomous Quantitative Fusion Trading System",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── 系统状态 ──
@app.get("/")
def root():
    return {
        "system": "AQF-T",
        "version": "3.1.0",
        "status": "ONLINE",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/api/v1/status")
def system_status():
    return {
        "name": "AQF-T",
        "version": "3.1.0",
        "mode": "development",
        "modules": {
            "ai_brain": "initialized",
            "strategy": "initialized",
            "risk": "initialized (kill_switch ACTIVE)",
            "execution": "standby",
            "world_model": "initialized",
            "decision": "initialized",
            "agent": "initialized",
        },
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/api/v1/health")
def health_check():
    return {"health": "OK", "timestamp": datetime.now().isoformat()}

# ── Risk API ──
@app.post("/api/v1/risk/check")
def risk_check(signal: dict):
    """风险检查 — AQF-T 最高优先级"""
    risk_score = 25  # 示例: 0-100
    if risk_score < 30:      decision = "APPROVE"
    elif risk_score < 70:    decision = "ADJUST"
    else:                    decision = "REJECT"
    return {
        "decision": decision,
        "risk_score": risk_score,
        "reason": "All limits within bounds",
        "timestamp": datetime.now().isoformat(),
    }

# ── AI API ──
@app.post("/api/v1/ai/predict")
def ai_predict(data: dict):
    return {
        "model": "AQF-T-Prediction-v1",
        "prediction": {"trend": "UP", "probability": 0.68, "confidence": 0.82},
        "timestamp": datetime.now().isoformat(),
    }

# ── Decision API ──
@app.post("/api/v1/decision/evaluate")
def decision_evaluate(context: dict):
    return {
        "action": "HOLD",
        "confidence": 0.78,
        "risk_level": "medium",
        "reasoning": [
            "Liquidity environment: supportive",
            "Valuation: acceptable",
            "Market regime: Bull Expansion",
        ],
        "timestamp": datetime.now().isoformat(),
    }
