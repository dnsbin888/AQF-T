# Web Dashboard 设计规范 (给新窗口)

## 定位
AQF-T 大脑状态监控台。QMT显示"手做了什么"，Dashboard显示"为什么这么做"。

## 技术约束
- 单文件 `dashboard.py`
- 零第三方框架 (只用Python stdlib)
- 只读 reports/*.json (永不修改)
- 启动: `python dashboard.py` → http://127.0.0.1:8080

## 展示内容

### 顶部: 系统状态
- Mode (paper/live)
- Regime (冰点/回暖/高潮/退潮)
- QMT状态 / DB状态 / CPU% / 内存%
- KillSwitch状态

### 中部: 今日交易
- 候选数 / 信号数 / 成交数 / 拒绝数
- 仓位% / 日盈亏 / 总回撤

### 底部: 交易明细
- 最近10条: 标的/方向/数量/价格/状态/原因
- 风控拒绝原因列表

## JSON数据来源 (稳定接口)

```python
# dashboard.py 只读这三个路径:
reports/daily/{date}_report.json    # 每日交易汇总
reports/execution/{date}_execution.json  # 执行指标
*_evidence.json                     # Pattern证据 (根目录)
```

## 自动刷新
- 每30秒读取最新JSON
- HTML meta refresh 或 JS setInterval

## GPT Review 补充 (DEC-024)

### 1. 兼容无数据状态
```
首次启动 reports/ 为空时:
  Regime: N/A (no data)
  今日交易: 0/0/0/0
  不能因缺JSON崩溃
```

### 2. 环境标识
```
顶部显示运行模式:
  [SIMULATION] Source: Simulator | Not Live
  [PAPER]     Source: Paper Broker
  [LIVE]      Source: QMT xtdata
从 PHASE2_DATA_EVIDENCE_SIM.json 的 meta.not_live 读取
```

### 3. 数据路径兼容
```
自动匹配当天文件 YYYYMMDD_report.json
找不到 → 用最近一份
都没有 → 显示空状态
```

## 不需要做的
- ❌ Flask/FastAPI/Django
- ❌ WebSocket实时推送
- ❌ 数据库直连
- ❌ 修改任何JSON文件
