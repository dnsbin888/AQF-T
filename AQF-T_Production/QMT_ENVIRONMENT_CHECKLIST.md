# QMT Environment Checklist


## A1. 软件环境

```
□ 国金QMT客户端已安装
  路径: D:\国金证券\QMT (config/system.yaml已配置)

□ xtquant可import
  验证: python -c "from xtquant import xtdata; print('OK')"

□ miniQMT权限已开通
  国金证券 → QMT设置 → miniQMT模式

□ 交易账户已登录
  验证: 打开QMT → 登录交易账户 → 正常显示持仓/资金
```

## A2. 行情数据权限

```
□ 基础行情 (L1)
  验证: xtdata.get_market_data() 返回数据

□ Level-2行情 (L2)
  验证: xtdata.subscribe_quote() 返回10档盘口

□ 逐笔成交 (Tick)
  验证: xtdata.get_l2_transaction() 返回数据

□ 历史数据
  验证: xtdata.get_local_data() 任意股票近1个月日线
```

## A3. 交易权限

```
□ 模拟交易权限
  验证: QMT → 模拟交易 → 可下单/可撤单

□ 委托权限
  验证: xttrader.order_stock() 模拟下单返回委托编号

□ 查询权限
  验证: xttrader.query_stock_asset() 返回账户信息
        xttrader.query_stock_positions() 返回持仓信息
```

## A4. AQF-T接入前验证

```
□ Provider接口已定义 (MarketDataProvider抽象类)
  位置: data/market_data_provider.py

□ SimulatorProvider已实现 ✅

□ QMTProvider骨架已创建
  位置: data/qmt_provider.py
  方法: connect/get_tick/get_position/get_account (空实现)

□ Pipeline模式切换
  config/system.yaml → mode: paper → live
  或命令行: python main.py --mode live

□ Evidence接口不变
  Simulator和QMT输出格式完全一致
```

## A5. 接入后验证

```
□ 模拟盘先跑 (mode=paper, provider=QMT)
  验证: 真实行情进入 → Pipeline正常运行 → Dashboard显示数据

□ Evidence对比
  SIM Evidence (60天基准) vs QMT Evidence (新生成)
  重点: Decision Consistency / Risk Fingerprint / Pattern Funnel

□ 如果漂移 < 预期
  → 进入小资金实盘 (≤10万)

□ 如果漂移 > 预期
  → 排查数据源/延迟/执行差异 → 不急于实盘
```

---

**当前状态: A1-A3 需在QMT电脑上逐项验证。**
**A4 接口已就绪。A5 等QMT环境后执行。**
