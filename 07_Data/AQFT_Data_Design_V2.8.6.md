# AQFT Data Design V3.6.0


# AQF-T 数据体系详细设计


Version: V3.6.0
Status: Detailed Engineering Design
Classification: AQF-T 数据基础设施核心设计文件
Date: 2026-07-26


---

# 第一章 数据体系定位


Data 模块是 AQF-T 所有智能模块的数据基础。为 AI Brain、Strategy、Risk、Execution 提供统一数据服务。

```
External Data Source → Data Acquisition → Raw Layer → Standard Layer → Feature Layer → Model Service → Feedback
```

---

# 第二章 A股数据源全景


## 2.1 数据源清单

### 行情数据（实时 + 历史）

| 数据项 | 粒度 | 来源 | 更新频率 | 用途 |
|--------|:---:|------|:---:|------|
| Tick 行情 | 3秒/笔 | QMT/xtquant | 实时 | 打板监控、盘口分析 |
| 分钟K线 | 1/5/15/30/60分钟 | akshare/QMT | 实时 | 分时承接、日内策略 |
| 日K线 | 日 | akshare/tushare | 盘后 | 趋势分析、回测 |
| 周/月K线 | 周/月 | akshare | 盘后 | 中长期趋势 |
| 实时盘口 | 10档 | QMT Level-2 | 实时 | 封单监控、盘口深度 |
| 集合竞价 | 9:15-9:25 | QMT/akshare | 竞价时段 | 竞价分析、龙头锁定 |

### 涨停数据 ⭐ 游资核心

| 数据项 | 说明 | 来源 | 更新频率 |
|--------|------|------|:---:|
| 涨停列表 | 当日涨停股、涨停时间、封单量 | akshare/东方财富 | 实时 |
| 连续涨停 | 连板高度、连板天数 | akshare | 实时 |
| 炸板列表 | 摸板未封、封板后打开 | akshare/东方财富 | 实时 |
| 封板强度 | 封单额/流通市值、封单额/成交额 | 自计算 | 实时 |
| 涨停梯队 | 首板/二板/三板/四板/五板+ 数量 | 自聚合 | 实时 |
| 首板晋级率 | 昨日首板今日连板比例 | 自计算 | 盘中 |

### 龙虎榜数据 ⭐ 游资核心

| 数据项 | 说明 | 来源 | 更新频率 |
|--------|------|------|:---:|
| 龙虎榜明细 | 上榜股票、买入/卖出席位、金额 | akshare/东方财富 | 盘后 |
| 游资席位库 | 知名游资席位映射 | 自维护 | 定期 |
| 机构专用席位 | 机构买入/卖出 | akshare | 盘后 |
| 北向资金 | 沪深股通净买入 | akshare/东方财富 | 实时 |
| 主力净流入 | 大单资金流向 | akshare | 实时 |

### 资金面数据

| 数据项 | 说明 | 来源 | 更新频率 |
|--------|------|------|:---:|
| 融资融券余额 | 两融余额及变化 | akshare | 日 |
| 大宗交易 | 大宗交易明细 | akshare | 日 |
| 股东增减持 | 重要股东增减持 | akshare | 不定期 |
| IPO/定增 | 新股发行、增发信息 | akshare | 不定期 |

### 基本面数据

| 数据项 | 说明 | 来源 | 更新频率 |
|--------|------|------|:---:|
| 财务数据 | 年报/季报（营收/利润/ROE/PE/PB） | akshare/tushare | 季/年 |
| 板块分类 | 申万/中信行业分类 | akshare | 定期 |
| 指数成分 | 沪深300/中证500/科创50等 | akshare | 定期 |
| ST/退市 | ST标记、退市风险 | akshare | 实时 |

### 情绪数据

| 数据项 | 说明 | 来源 | 更新频率 |
|--------|------|------|:---:|
| 涨停家数 | 全市场 | akshare | 实时 |
| 跌停家数 | 全市场 | akshare | 实时 |
| 炸板率 | 炸板数/摸板数 | 自计算 | 盘中 |
| 涨跌比 | 上涨/下跌家数 | akshare | 实时 |
| 新闻舆情 | 政策/行业/个股新闻 | 自爬/API | 实时 |
| 社交媒体热度 | 雪球/东方财富讨论热度 | 自爬 | 实时 |

---

# 第三章 数据分层架构


## 3.1 Raw Data Layer（原始数据层）

```
存储位置: data/raw/
格式: Parquet (日线) / JSON (实时)
保留策略: 原始数据永久保留，不修改

内容:
  - QMT tick数据
  - akshare日线数据
  - 龙虎榜原始数据
  - 新闻原文
```

## 3.2 Standard Data Layer（标准数据层）

```
存储位置: data/standard/
格式: Parquet (统一Schema)
处理: 清洗 + 标准化 + 去重 + 复权

标准化内容:
  - 股票代码统一: SH.600519 / SZ.000858
  - 时间格式: UTC timestamp
  - 价格单位: 元（人民币）
  - 复权方式: 前复权
```

## 3.3 Feature Data Layer（特征数据层）

```
存储位置: data/features/
格式: Parquet (按日期分区)
来源: Standard Layer → Feature Pipeline

特征类型:
  - 技术特征: MA/MACD/RSI/ATR/布林带
  - 量价特征: 量比/换手率/振幅/涨速
  - 情绪特征: 情绪值/题材热度/封板强度
  - 资金特征: 北向流入/融资变化/主力净买入
  - 涨停特征: 连板天数/封单强度/炸板标记
```

## 3.4 Result Data Layer（结果数据层）

```
存储位置: data/results/
格式: Parquet

内容:
  - 交易记录: 每笔成交
  - 信号记录: 策略信号及结果
  - 模型预测: AI预测及实际对比
  - 风险事件: Kill Switch/熔断记录
```

---

# 第四章 核心数据 Schema


## 4.1 日K线

```
DailyKLine:
  symbol: str              # SH.600519
  trade_date: date
  open: float
  high: float
  low: float
  close: float
  volume: int              # 成交量(股)
  amount: float            # 成交额(元)
  turnover: float          # 换手率
  amplitude: float         # 振幅
  pct_change: float        # 涨跌幅
  is_limit_up: bool        # 是否涨停
  is_limit_down: bool      # 是否跌停
  adj_factor: float        # 复权因子
```

## 4.2 涨停数据

```
LimitUpRecord:
  symbol: str
  trade_date: date
  board_count: int         # 连板数(首板=1)
  limit_up_time: datetime  # 首次涨停时间
  open_count: int          # 炸板次数
  seal_amount: float       # 封单额(元)
  seal_ratio: float        # 封单/流通市值
  turnover_at_limit: float # 涨停时换手率
  is_dragon: bool          # 是否为题材龙头
  sector: str              # 所属题材
```

## 4.3 龙虎榜

```
LongHuRecord:
  symbol: str
  trade_date: date
  reason: str              # 上榜原因
  total_buy: float         # 总买入
  total_sell: float        # 总卖出
  net_buy: float           # 净买入
  seats: [
    {
      name: str            # 席位名称
      type: 游资 | 机构 | 量化 | 散户
      buy: float
      sell: float
      net: float
    }
  ]
  top_seats: [str]         # 买入前5席位
  is_institution_heavy: bool
```

## 4.4 集合竞价

```
AuctionData:
  symbol: str
  trade_date: date
  phase: str               # 9:15-9:20 | 9:20-9:25
  current_price: float     # 当前撮合价
  volume: int              # 虚拟成交量
  amount: float
  price_change_pct: float  # 相对昨收涨跌幅
  order_imbalance: float   # 买卖盘不平衡度
```

---

# 第五章 数据更新频率


| 数据类型 | 更新频率 | 延迟要求 | 优先数据源 |
|---------|:---:|:---:|------|
| Tick行情 | 实时(3秒) | < 1秒 | QMT |
| 分钟K线 | 每分钟 | < 5秒 | QMT |
| 日K线 | 盘后 | < 1小时 | akshare |
| 涨停板 | 实时 | < 10秒 | 东方财富 |
| 龙虎榜 | 盘后(16:00后) | < 1小时 | akshare |
| 北向资金 | 实时 | < 30秒 | 东方财富 |
| 融资融券 | 盘后 | < 2小时 | akshare |
| 财务数据 | 季报发布后 | < 1天 | tushare |
| 新闻舆情 | 实时 | < 1分钟 | API/爬虫 |
| 情绪指标 | 每分钟 | < 5秒 | 自计算 |

---

# 第六章 数据质量


## 6.1 质量检查规则

```
必检项目:
  ✅ 完整性: 当日应有多少只股票有数据
  ✅ 准确性: 价格/成交量非负，涨跌幅在合理范围
  ✅ 一致性: 前复权价格连续，不复权价格与公告一致
  ✅ 时效性: 数据延迟不超过阈值

异常检测:
  - 价格跳空 > 20% (除除权日)
  - 成交量 > 历史均值10倍
  - 停牌股票仍有成交数据
  - 涨停价计算与实际不符
```

## 6.2 异常处理流程

```
Detection → Log → Attempt Correction → If Failed → Skip + Alert
```

---

# 第七章 数据服务接口


| 端点 | 方法 | 功能 |
|------|:---:|------|
| /data/market/realtime | GET | 实时行情 |
| /data/market/history | GET | 历史K线 |
| /data/limit_up/today | GET | 今日涨停 |
| /data/limit_up/ladder | GET | 涨停梯队 |
| /data/longhu/today | GET | 今日龙虎榜 |
| /data/longhu/seat/{name} | GET | 席位历史 |
| /data/auction/{symbol} | GET | 集合竞价 |
| /data/capital/north_bound | GET | 北向资金 |
| /data/capital/margin | GET | 融资融券 |
| /data/sentiment/overview | GET | 情绪全景 |
| /data/financial/{symbol} | GET | 财务数据 |
| /data/news/{symbol_or_sector} | GET | 相关新闻 |

---

# 第八章 存储方案


| 层级 | 存储 | 格式 | 保留 |
|------|------|------|:---:|
| Raw | 本地文件 + SQLite索引 | Parquet/JSON | 永久 |
| Standard | SQLite/PostgreSQL | 结构化表 | 5年+ |
| Feature | Parquet | 列式 | 3年 |
| Result | SQLite | 结构化表 | 永久 |

```
初期: SQLite (个人/小团队完全够用)
数据量 > 10GB: 迁移 PostgreSQL
数据量 > 100GB: 引入 ClickHouse/DolphinDB
```

---

# 第九章 设计冻结声明


本文件定义 AQF-T Data V3.6.0 详细设计。

覆盖六大类A股数据源（行情/涨停/龙虎榜/资金/基本面/情绪），四层数据架构，20+ 数据Schema，12 个数据服务接口。

数据是 AQF-T 所有智能模块的基础。没有数据，AI 只是空壳。

Version: V3.6.0
Status: Detailed Engineering Design
END OF AQFT DATA DESIGN
