# AQFT Data Runtime Design V3.6.0


# AQF-T 数据运行系统详细设计


Version: V3.6.0
Status: Detailed Engineering Design
Classification: AQF-T 实时数据运行系统设计文件
Date: 2026-07-26


---

# 第一章 定位


Data Runtime 是 AQF-T 唯一的数据入口。对接 07_Data 的设计 Schema，负责数据从外部来源到各消费模块的完整管道。

```
外部数据源 → Collector → Stream → Processor → Cache → Feature Engine → Data Service → AI/Strategy/Risk
```

**核心指标: 行情延迟 < 1秒, 涨停数据延迟 < 10秒, Pipeline可用率 > 99%**

---

# 第二章 数据采集管道


## 2.1 Collector 配置

| 数据类型 | 采集器 | 频率 | 超时 |
|---------|------|:---:|:---:|
| 实时行情 | QMT/akshare | 3秒 | 5秒 |
| 涨停数据 | 东方财富爬虫 | 10秒 | 15秒 |
| 日K线 | akshare | 盘后 | 60秒 |
| 龙虎榜 | akshare | 盘后(16:00) | 120秒 |
| 北向资金 | 东方财富 | 30秒 | 30秒 |
| 新闻舆情 | API/爬虫 | 60秒 | 30秒 |

## 2.2 采集异常处理

```
采集失败:
  1次失败 → 记录DEBUG日志
  连续3次 → WARNING日志
  连续10次 → ERROR日志 + 切换备用数据源
  所有数据源失败 → 告警 + 使用最近缓存

备用数据源链:
  QMT → akshare → 东方财富爬虫 → 本地缓存(最后手段)
```

---

# 第三章 数据流处理


## 3.1 Stream Pipeline

```
Raw Data → Queue → Normalizer → Validator → Standard Layer → Feature Engine → Cache → Service
```

## 3.2 Normalizer 标准化规则

```
股票代码: 统一为 SH.600519 / SZ.000858 / BJ.8xxxxx
时间: 统一 UTC timestamp (毫秒)
价格: 人民币元, 保留2位小数
成交量: 股(不是手)
涨跌幅: 小数 (0.10 = 10%)
复权: 默认前复权

A股特殊:
  - 新股首日无涨跌幅, 标记 is_new_stock=true
  - ST标记从代码名提取
  - 科创板代码 688xxx, 涨跌幅±20%  
```

## 3.3 Validator 校验规则

```
必检:
  ✅ price > 0
  ✅ volume ≥ 0
  ✅ high ≥ low
  ✅ high ≥ open, high ≥ close
  ✅ low ≤ open, low ≤ close
  ✅ 涨跌幅在合理范围 (考虑涨跌停)
  ✅ 非停牌日数据不为空

异常值:
  - price跳空 > 20% (非除权日) → 标记 + 人工审核
  - volume > 历史均值10倍 → 标记 + 不自动过滤(可能是真实放量)
```

---

# 第四章 缓存策略


## 4.1 三级缓存

```
L1 内存缓存 (最快):
  内容: 最新Tick/最新K线/当前持仓/当前风险状态
  TTL: 实时数据 5秒 / 日线数据 1小时
  容量: 1000条

L2 本地文件缓存:
  内容: 近7天分钟数据 / 近30天日线数据
  格式: Parquet
  TTL: 按时间

L3 数据库:
  内容: 全部历史数据
  格式: SQLite/PostgreSQL
  TTL: 永久
```

## 4.2 缓存命中流程

```
请求 → L1(内存) → 命中 → 返回
                 → 未命中 → L2(文件) → 命中 → 回写L1 → 返回
                                      → 未命中 → L3(DB) → 回写L2+L1 → 返回
```

---

# 第五章 Feature Engine Runtime


## 5.1 实时特征计算

```
输入: 行情Tick/分钟K线
输出: 特征向量 → AI Brain 输入

计算管线 (每次Tick):
  1. 技术特征: MA/MACD/RSI/ATR/布林带 (增量更新)
  2. 量价特征: 量比/换手率/振幅/涨速
  3. 情绪特征: 情绪值/题材热度/封板强度 (聚合计算)
  4. 资金特征: 北向流入/主力净买入 (读取外部数据)
  5. 涨停特征: 连板天数/封单强度/炸板标记

输出: FeatureVector (768-dim)
延迟目标: < 50ms
```

## 5.2 特征版本管理

```
每个特征记录:
  feature_name: str
  formula_version: str
  input_data_version: str
  computed_at: datetime

特征变更时: 新旧版本并行计算1周 → 验证通过 → 切换
```

---

# 第六章 数据服务 API


## 6.1 实时数据

| 端点 | 功能 | 延迟 |
|------|------|:---:|
| GET /data/realtime/{symbol} | 实时行情 | < 100ms |
| GET /data/kline/{symbol}?period=1m | K线数据 | < 200ms |
| GET /data/limit_up/today | 今日涨停 | < 500ms |
| GET /data/limit_up/ladder | 涨停梯队 | < 500ms |
| GET /data/longhu/today | 今日龙虎榜 | < 1s |
| GET /data/auction/{symbol} | 集合竞价 | < 200ms |

## 6.2 特征数据

| 端点 | 功能 | 延迟 |
|------|------|:---:|
| GET /data/feature/{symbol} | 完整特征向量 | < 100ms |
| GET /data/sentiment/overview | 情绪全景 | < 500ms |
| GET /data/feature/regime | 当前Regime | < 200ms |

## 6.3 历史数据

| 端点 | 功能 |
|------|------|
| GET /data/history/{symbol}?start=&end=&period= | 历史K线 |
| GET /data/history/trades | 历史交易记录 |
| GET /data/history/signals | 历史信号记录 |

---

# 第七章 数据质量监控


## 7.1 实时监控指标

| 指标 | 告警阈值 | 说明 |
|------|:---:|------|
| 行情延迟 | > 5秒 | 数据源可能异常 |
| 数据缺失率 | > 1% | 某股票无数据 |
| 异常值比例 | > 0.1% | 价格跳空过多 |
| 涨停数据延迟 | > 30秒 | 影响打板决策 |
| Pipeline吞吐 | < 100条/秒 | 性能下降 |

## 7.2 盘后质量检查

```
每日盘后:
  ✅ 全量股票日线数据完整性
  ✅ 涨停数据与实际公告一致性
  ✅ 龙虎榜数据与交易所公告一致性
  ✅ 复权因子正确性
```

---

# 第八章 数据安全


```
权限:
  - 生产数据仅生产环境可访问
  - 测试环境使用脱敏数据

备份:
  - 日线数据: 每日备份
  - 交易记录: 实时备份
  - 全量数据库: 每周全量备份

加密:
  - 账户/资金数据: 加密存储
  - API密钥: 环境变量(不入库)
```

---

# 第九章 设计冻结声明


本文件定义 AQF-T Data Runtime V3.6.0 详细设计。

6通道实时采集、三级缓存、Feature Engine 实时计算(768-dim, <50ms)、16个数据服务端点、5项实时质量监控。

Data Runtime 是 AQF-T 所有智能模块的"眼睛"。

Version: V3.6.0
Status: Detailed Engineering Design
END OF AQFT DATA RUNTIME DESIGN
