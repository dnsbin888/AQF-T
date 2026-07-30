# AQF-T Runtime Architecture Note

## QMT is an Execution Adapter

QMT is not AQF-T's core system. QMT is AQF-T's execution terminal.

```
                 AQF-T Intelligence Core
                         |
        ---------------------------------
        |               |               |
   Perception      Decision Core       Risk
   (eyes/brain)    (judgment)        (immune)
        |               |               |
        ---------------------------------
                         |
                  Execution Layer
                         |
                         v
                      QMT
                  (hands/feet)
```

### What AQF-T Owns
- Perception (what is happening)
- Pattern Recognition (what pattern is this)
- Decision (what to do)
- Risk (should we do it)
- Evidence (why we did it)
- Learning (how to improve)

### What QMT Owns
- Order routing
- Trade execution
- Account interface
- Market data delivery (raw)

### Principles
1. No strategy logic shall reside in QMT
2. No decision logic shall depend on QMT UI
3. QMT is replaceable: swap adapter, AQF-T core unchanged
4. AQF-T tells QMT WHAT to do, never asks QMT WHY

### Future
```
AQF-T
  |
Execution Adapter
  |-- QMT (current)
  |-- IBKR (possible)
  |-- Broker API (possible)
  |-- Paper Simulator (test)
```
