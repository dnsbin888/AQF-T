"""
AQF-T 核心数据结构定义
统一数据模型 — 所有模块共享
"""
from dataclasses import dataclass, field
from typing import Optional, Literal
from datetime import datetime


@dataclass
class MarketState:
    """市场状态"""
    timestamp: datetime
    symbol: str = ""
    price: float = 0.0
    volume: float = 0.0
    trend: Literal["UP", "DOWN", "NEUTRAL"] = "NEUTRAL"
    volatility: float = 0.0
    liquidity: float = 0.0


@dataclass
class Prediction:
    """AI 预测结果"""
    model: str = ""
    trend: Literal["UP", "DOWN", "NEUTRAL"] = "NEUTRAL"
    probability: float = 0.0
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TradingSignal:
    """交易信号"""
    strategy: str = ""
    symbol: str = ""
    action: Literal["BUY", "SELL", "HOLD"] = "HOLD"
    confidence: float = 0.0
    score: float = 0.0
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RiskDecision:
    """风险决策"""
    status: Literal["APPROVE", "ADJUST", "REJECT"] = "APPROVE"
    risk_score: float = 0.0
    reason: str = ""
    limit_checks: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Order:
    """订单"""
    order_id: str = ""
    symbol: str = ""
    side: Literal["BUY", "SELL"] = "BUY"
    quantity: float = 0.0
    price: float = 0.0
    type: Literal["MARKET", "LIMIT", "STOP"] = "MARKET"
    status: Literal["CREATED", "SUBMITTED", "FILLED", "CANCELLED", "REJECTED"] = "CREATED"
    risk_approval_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
