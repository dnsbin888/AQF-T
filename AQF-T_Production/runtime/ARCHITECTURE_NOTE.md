# AQF-T Runtime Architecture Note

## Three-Layer Architecture (DEC-024 Frozen)

```
                 AQF-T Strategic Layer
                 (大脑 — 战略决策)

        | Perception | Pattern | Decision | Risk | Evidence |
        |  眼睛       | 模式    | 判断     | 免疫  | 记忆     |

                          |
                          | Decision Intent
                          v

               Execution Intelligence Layer
               (反射 — 执行智能)

        | Order Planning | Smart Routing | Cancel/Replace |
        | Slippage Control | Fill Quality | Execution State |

                          |
                          | Order
                          v

                  QMT Trading Channel
                  (手足 — 交易通道)

        | xtquant | Broker API | Account | Market Data |
```

## What AQF-T Strategic Layer Owns (不可下放)
- Market Regime — 今天能不能做
- Perception — 市场在发生什么
- Pattern Recognition — 什么模式
- Decision Core — 选什么/多少
- Portfolio Risk — 能不能做
- Evidence Framework — 为什么

## What Execution Agent Owns (局部智能)
- Order splitting (大单拆小)
- Spread/depth protection (盘口保护)
- Cancel/replace (超时撤改)
- VWAP/TWAP (成交优化)
- Limit-up queuing (涨停排队策略)
- Fill quality analysis

## What QMT Channel Owns
- Order routing / execution
- Market data delivery (raw)
- Account interface
- Position query

## Prohibited (红线)
- Execution Agent MUST NOT discover trading opportunities
- Execution Agent MUST NOT modify risk parameters
- Execution Agent MUST NOT bypass AQF-T decisions
- No strategy logic in QMT channel
- No decision dependency on QMT UI

## Data Flow
```
AQF-T Intent (Decision)
        |
        v
Execution Agent (HOW to execute)
        |
        v
QMT Order (WHAT to send)
        |
        v
Market
```
NOT:
```
QMT Data -> Find opportunity -> Auto trade  (FORBIDDEN)
```

## Version Alignment
- V1.0: Pipeline Integration ✅
- V1.1: Runtime Hardening ✅
- V1.2: Production Runtime Layer ✅ (runtime/ 7 modules)
- V1.3: Execution Intelligence Layer (direction frozen)
- DEC-024: QMT Role Redefinition ✅
