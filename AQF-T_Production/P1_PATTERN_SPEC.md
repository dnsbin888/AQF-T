# P1 Pattern补全 — 实现规范


## 原则
- 全部规则, 零AI, 零新模块
- 输出统一Candidate字段 (score/confidence/evidence/regime_fit)
- 接入已有Pattern Library + Evidence Builder


## 任务1: SectorFlow (板块资金流向)

### 定位
回答: "今天哪个板块最强? 资金是否开始切换?"

### 输入
```
akshare板块数据:
  - 板块涨跌幅
  - 板块涨停家数
  - 板块资金净流入
  - 板块成交量变化
```

### 输出
```
sector_flow_score: 0-1

= 涨停家数变化 × 0.30
+ 资金净流入强度 × 0.30
+ 板块涨跌幅 × 0.20
+ 成交量变化 × 0.20
```

### 文件
`strategy/patterns/sector_flow.py`

### 验收
- 接入akshare获取板块数据
- 输出sector_flow_score
- Pipeline中接入
- 60天回放验证


## 任务2: RelativeStrength (相对强度)

### 定位
回答: "个股vs大盘/板块/龙头, 谁更强?"

### 输入
```
akshare数据:
  - 个股涨跌幅
  - 大盘(上证/深证)涨跌幅
  - 板块涨跌幅
  - 龙头涨跌幅
```

### 输出
```
RS_market:  个股5日涨幅 / 大盘5日涨幅
RS_sector:  个股5日涨幅 / 板块5日涨幅
RS_leader:  个股5日涨幅 / 龙头5日涨幅

综合: RS_score = (RS_market + RS_sector + RS_leader) / 3
```

### 文件
`strategy/patterns/relative_strength.py`

### 验收
- 接入akshare获取个股+大盘+板块数据
- 输出RS_market/RS_sector/RS_leader
- Pipeline中接入(影响候选排序)
- 60天回放验证


## 任务3 (小): Evidence Builder接入

### 定位
两个新Pattern完成后, 注册到Evidence Builder

### 验收
- Pattern Card生成
- 60天回放生成证据JSON
- Pattern Library更新为6个(从4个)


## 不改动清单

```
❌ 不修改Pipeline主链
❌ 不修改Risk/Decision/Execution
❌ 不修改Constitution
❌ 不新增AI模型
❌ 不新增外部依赖 (仅akshare)
```

## 新文件清单

```
strategy/patterns/__init__.py        (新建)
strategy/patterns/sector_flow.py     (新建, ~100行)
strategy/patterns/relative_strength.py (新建, ~100行)
```

## 交付物

```
1. sector_flow.py + relative_strength.py
2. Pipeline接入 (候选列表增加两个Pattern的评分)
3. 60天回放验证通过
4. Pattern Library更新 (4→6)
5. Evidence Package更新
```
