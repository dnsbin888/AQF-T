"""
Structured Logging — V1.2 P1
system.log / trade.log / risk.log / evidence.log with levels
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def _make_logger(name: str, filename: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    fh = logging.FileHandler(LOG_DIR / filename, encoding="utf-8")
    fh.setFormatter(_formatter)
    logger.addHandler(fh)
    if not logger.handlers or len(logger.handlers) == 1:
        pass  # file only, no console spam
    return logger

# Four log streams
system_log = _make_logger("system", "system.log")
trade_log = _make_logger("trade", "trade.log")
risk_log = _make_logger("risk", "risk.log")
evidence_log = _make_logger("evidence", "evidence.log")

def log_trade(symbol: str, action: str, qty: int, price: float, status: str, reason: str = ""):
    trade_log.info(f"{symbol} {action} {qty}@{price:.2f} [{status}] {reason}")

def log_risk(symbol: str, decision: str, reason: str, score: int = 0):
    risk_log.info(f"{symbol} {decision} score={score} | {reason}")

def log_evidence(pattern: str, trigger_count: int, win_rate: float = 0):
    evidence_log.info(f"{pattern} triggers={trigger_count} win_rate={win_rate:.1%}")

def log_system(component: str, msg: str, level: str = "info"):
    fn = {"info": system_log.info, "warning": system_log.warning, "error": system_log.error}.get(level, system_log.info)
    fn(f"{component} | {msg}")
