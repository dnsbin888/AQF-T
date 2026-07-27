# AQF-T Trading Episode Model V1.0

Version: V1.0.0 | Status: ENGINEERING DRAFT — Phase 1
Module: 06_Experience_Intelligence / 02_Episode_Model

---

## 1. Definition

A TradingEpisode captures the **complete lifecycle** of one trading decision from context through outcome.

## 2. Episode Structure

```json
{
  "episode_id": "EP_20260728_001",
  "market_context": {
    "regime": "Expansion", "emotion_phase": "Warming",
    "emotion_score": 65, "theme": "AI", "leader_status": "2-board confirmed"
  },
  "decision_context": {
    "decision_id": "DEC_20260728_093500", "action": "ENTER",
    "confidence": 0.82, "reason": ["AI theme confirmed", "Leader 2-board", "Capital inflow"]
  },
  "execution_context": {
    "plan_id": "EP_20260728_100000", "strategy_type": "LeaderMomentum",
    "entry_mode": "staged_3", "quality_score": 0.87
  },
  "outcome_context": {
    "exit_date": null, "unrealized_pnl_pct": 2.75,
    "holding_days": 0, "health_score": 78, "status": "ACTIVE"
  },
  "reflection": { "what_worked": null, "what_didnt": null, "key_lesson": null }
}
```

## 3. Episode Lifecycle

ACTIVE → CLOSED → EVALUATED → REFLECTED → ARCHIVED

## 4. vs Traditional Trade Log

Traditional: `symbol, buy_price, sell_price, pnl`

AQF-T Episode: **Why we traded + What we knew + How we executed + What we learned**
