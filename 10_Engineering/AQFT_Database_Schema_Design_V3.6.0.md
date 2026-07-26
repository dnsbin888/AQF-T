# AQF-T Database Schema Design V3.6.0


# AQF-T 数据库设计详细规范


Version: V3.6.0 | Status: Engineering Specification
Date: 2026-07-26

> 参考: 行业PostgreSQL/SQLite双轨制 + SQLAlchemy ORM + 时序数据最佳实践


---

# 第一章 数据库选型


```
开发/单机: SQLite (零配置, 便携, <10GB完全够用)
生产/团队: PostgreSQL (ACID, 并发, 扩展)
高频Tick: TDengine/TimescaleDB (时序优化, 高压缩) — 后期引入
```

# 第二章 ER核心表 (10张)


## 2.1 基础信息

```sql
stock_basic (
  ts_code VARCHAR(20) PRIMARY KEY,    -- SH.600519
  name VARCHAR(50),
  exchange VARCHAR(10),               -- SH/SZ/BJ
  industry VARCHAR(50),               -- 申万行业
  sector VARCHAR(50),                 -- 题材板块
  list_date DATE,
  total_shares NUMERIC(20,4),
  float_shares NUMERIC(20,4),
  is_st BOOLEAN DEFAULT FALSE,
  status VARCHAR(10) DEFAULT 'L'      -- L上市/D退市/S停牌
);
```

## 2.2 日线行情

```sql
stock_daily (
  id SERIAL PRIMARY KEY,
  ts_code VARCHAR(20) NOT NULL,
  trade_date DATE NOT NULL,
  open NUMERIC(12,4), high NUMERIC(12,4),
  low NUMERIC(12,4), close NUMERIC(12,4),
  pre_close NUMERIC(12,4),
  volume BIGINT,                       -- 股
  amount NUMERIC(20,2),                -- 元
  turnover NUMERIC(8,4),               -- 换手率
  pct_chg NUMERIC(8,4),                -- 涨跌幅
  is_limit_up BOOLEAN,                 -- 涨停
  is_limit_down BOOLEAN,               -- 跌停
  UNIQUE(ts_code, trade_date)
);
CREATE INDEX idx_daily_code ON stock_daily(ts_code);
CREATE INDEX idx_daily_date ON stock_daily(trade_date);
```

## 2.3 分钟K线

```sql
stock_minute (
  symbol VARCHAR(20) NOT NULL,
  period VARCHAR(10) NOT NULL,          -- 1m/5m/15m/30m/60m
  ts TIMESTAMP NOT NULL,
  open NUMERIC(12,4), high NUMERIC(12,4),
  low NUMERIC(12,4), close NUMERIC(12,4),
  volume BIGINT, amount NUMERIC(20,2),
  UNIQUE(symbol, period, ts)
);
```

## 2.4 涨停数据 ⭐

```sql
limit_up_record (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(20) NOT NULL,
  trade_date DATE NOT NULL,
  board_count INT DEFAULT 1,            -- 连板数
  limit_up_time TIME,                   -- 首次涨停时间
  open_count INT DEFAULT 0,             -- 炸板次数
  seal_amount NUMERIC(20,2),            -- 封单额
  seal_ratio NUMERIC(8,4),              -- 封单/流通市值
  turnover_at_limit NUMERIC(8,4),       -- 涨停时换手率
  is_dragon BOOLEAN,                    -- 是否题材龙头
  sector VARCHAR(50),                   -- 所属题材
  UNIQUE(symbol, trade_date)
);
```

## 2.5 龙虎榜 ⭐

```sql
longhu_record (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(20) NOT NULL,
  trade_date DATE NOT NULL,
  reason VARCHAR(200),
  total_buy NUMERIC(20,2),
  total_sell NUMERIC(20,2),
  net_buy NUMERIC(20,2),
  seat_details JSONB,                   -- [{name,type,buy,sell,net}]
  top_seats TEXT[],
  is_institution_heavy BOOLEAN,
  UNIQUE(symbol, trade_date)
);
```

## 2.6 因子库

```sql
factor_value (
  factor_id VARCHAR(64) NOT NULL,       -- 'momentum_20d'/'PE'/'sentiment_score'
  stock_code VARCHAR(16) NOT NULL,
  trade_date DATE NOT NULL,
  factor_value DOUBLE PRECISION,
  update_time TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (factor_id, stock_code, trade_date)
);
```

## 2.7 订单

```sql
orders (
  id SERIAL PRIMARY KEY,
  order_id VARCHAR(50) UNIQUE NOT NULL,  -- AQFT-ORD-00001
  symbol VARCHAR(20) NOT NULL,
  side VARCHAR(10) NOT NULL,             -- BUY/SELL
  quantity INT NOT NULL,
  price NUMERIC(12,4),
  type VARCHAR(10) DEFAULT 'MARKET',     -- MARKET/LIMIT
  status VARCHAR(20) DEFAULT 'CREATED',
  filled_qty INT DEFAULT 0,
  filled_avg_price NUMERIC(12,4),
  fee NUMERIC(12,4),
  slippage_bps NUMERIC(8,2),
  risk_decision VARCHAR(20),             -- APPROVE/ADJUST/REJECT
  strategy_signal_id VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 2.8 持仓

```sql
positions (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(20) NOT NULL,
  shares INT NOT NULL,
  available_shares INT NOT NULL,         -- T+1可用
  locked_shares INT DEFAULT 0,           -- T+1锁定
  avg_cost NUMERIC(12,4),
  market_value NUMERIC(20,2),
  unrealized_pnl NUMERIC(20,2),
  snapshot_time TIMESTAMP DEFAULT NOW()
);
```

## 2.9 信号日志

```sql
signals (
  id SERIAL PRIMARY KEY,
  signal_id VARCHAR(50) UNIQUE,
  symbol VARCHAR(20) NOT NULL,
  action VARCHAR(10) NOT NULL,           -- BUY/SELL/HOLD
  strategy VARCHAR(50),                  -- Dragon/Trend/VolumePrice
  confidence NUMERIC(3,2),
  ai_fusion_score NUMERIC(3,2),
  risk_score INT,
  reasoning TEXT,                        -- AI推理链
  generated_at TIMESTAMP DEFAULT NOW()
);
```

## 2.10 风控日志

```sql
risk_log (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(20),
  risk_score INT NOT NULL,
  decision VARCHAR(20) NOT NULL,         -- APPROVE/ADJUST/REJECT/KILL_SWITCH
  reason TEXT,
  position_before JSONB,
  position_after JSONB,
  triggered_at TIMESTAMP DEFAULT NOW()
);
```

---

# 第三章 SQLite 性能优化

```sql
PRAGMA journal_mode = WAL;           -- 支持并发读写
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;          -- 64MB
PRAGMA temp_store = MEMORY;
```

---

# 第四章 Python 接入 (SQLAlchemy)

```python
# 开发: SQLite
engine = create_engine('sqlite:///data/aqft.db')
# 生产: PostgreSQL
# engine = create_engine('postgresql://user:pass@localhost/aqft')

# 批量写入行情
df.to_sql('stock_daily', engine, if_exists='append', index=False)

# 因子写入
df.to_sql('factor_value', engine, if_exists='append', index=False)
```

---

# 第五章 设计冻结

本文件定义 AQF-T Database Schema V3.6.0。10张核心表覆盖行情/涨停/龙虎榜/因子/订单/持仓/信号/风控。SQLite开发→PostgreSQL生产双轨制。

Version: V3.6.0 | Status: Engineering Specification
END OF AQFT DATABASE SCHEMA DESIGN
