# 02 Data — 数据设计

## 数据源 (三级, 均已可用)

```
L2 国金QMT (主力):
  xtdata.getl2transaction()      → 逐笔成交 (每笔明细/方向/大小)
  xtdata.getl2order()            → 逐笔委托 (挂/撤/成交)
  xtdata.subscribe_quote()       → 十档盘口 (bid1-10/ask1-10)
  xtdata.getl2orderqueue()       → 委托队列 (买一/卖一挂单明细)
  xtdata.getl2transactioncount() → 大单统计 (特大单/大单/中单/小单)

L1 QMT基础:
  xtdata.get_market_data()       → 分钟K线 / 日K线

Free akshare (兜底):
  涨停列表 / 龙虎榜(T+1) / 财务数据 / 北向资金
```

## 数据库 (SQLite 14张表)

```
基础10张 (引用 V2.8.6 10_Engineering):
  stock_basic / stock_daily / stock_minute
  limit_up_record / longhu_record
  factor_value
  orders / positions / signals / risk_log

L2新增4张:
  l2_transaction    (逐笔成交: symbol/time/price/volume/direction/type)
  l2_order          (逐笔委托: symbol/time/price/volume/direction/status)
  l2_orderbook      (盘口快照: symbol/time/bid1-10/ask1-10 每3秒)
  l2_block_stats    (大单统计: big_buy/big_sell/net_flow)
```

## 因子 (100个)

```
技术30: MA/MACD/RSI/KDJ/BOLL/ATR/OBV/WR/CCI/ADX + 衍生
Alpha30: momentum/reversal/vol/skew/drawdown/sharpe/beta/corr
情绪20: 涨停家数/连板高度/炸板率/封单强度/北向/题材热度/龙虎榜
资金20: 主力净流入/大单占比/DDX/DDY/DDZ/融资余额/大宗
```
