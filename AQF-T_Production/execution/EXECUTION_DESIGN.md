# 05 Execution — 执行引擎

## 国金miniQMT

```python
from xtquant import XtQuantTrader
trader = XtQuantTrader(path, session_id)
trader.start()
trader.connect()

# 下单
trader.order_stock(account, stock_code, order_type, price, volume)
# 撤单
trader.cancel_order_stock(account, order_id)
# 查询
trader.query_stock_asset(account)       # 资金
trader.query_stock_positions(account)   # 持仓
trader.query_stock_orders(account)      # 当日委托
trader.query_stock_trades(account)      # 当日成交
```

## A股规则

```
T+1:   当日买入 → 次日才可卖 (available/locked 追踪)
涨跌停: 主板±10% | 科创/创业±20% | 北交±30% | ST±5%
费率:   买入: 佣金0.025%(min5)+过户费0.001%
        卖出: +印花税0.1%
手数:   100股整数倍
```

## 双模式

```
研发: QMT完整版 (策略编写+回测优化)
实盘: miniQMT (500MB内存, 7×24静默挂机, 不弹窗)
```
