# AQFT Cross-Market Intelligence Design V3.6.0


# AQF-T 跨市场智能系统详细设计


Version: V3.6.0 | Status: Detailed Engineering Design
Date: 2026-07-26

> 参考: 2025前沿研究(分位数关联/地缘政治风险传导/新兴市场传染) + A股特有传导链


---

# 第一章 定位


Cross-Market Intelligence 回答"外部世界如何影响A股"。A股游资必须理解的三条传导链：

```
传导链1 (美股→A股):
  NASDAQ暴跌 → 全球Risk-Off → 北向资金流出 → A股成长股承压 → 题材退潮

传导链2 (汇率→A股):
  美联储加息 → 美元走强 → 人民币贬值 → 外资流出 → A股权重股承压

传导链3 (商品→A股):
  原油暴涨 → 通胀预期 → 周期股上涨 → 成长股资金被抽 → 题材切换
```

---

# 第二章 A股关键外部信号


借鉴 2025 年学术研究发现的A股传导规律:

| 外部信号 | A股影响 | 传导时滞 | 监测指标 |
|---------|--------|:---:|------|
| 美联储利率决议 | 北向资金方向 | T+1 | 联邦基金利率/CEM FedWatch |
| 美元指数(DXY) | 人民币汇率→外资 | 实时 | USD/CNY |
| VIX恐慌指数 | 市场风险偏好 | 实时 | VIX > 25 → Risk-Off |
| 美债10Y收益率 | 成长股估值 | T+1 | US10Y |
| 原油价格 | 周期股/通胀预期 | T+2 | WTI/Brent |
| 美股期货(盘前) | A股开盘方向 | 9:00前 | ES/NQ |
| 港股/A50期货 | A股日内方向 | 盘中 | HSI/富时A50 |
| 地缘政治事件 | 全市场Risk-Off | 即时 | 新闻+社交情绪 |

---

# 第三章 冲击传播模型


借鉴 2025 年 QQ(分位数-on-分位数)关联研究:

```
外部冲击 → Risk Assessment:

正常市场 (分位数 50%):
  美联储+25bp → A股影响: -0.5%   (线性, 可预测)

极端市场 (分位数 5%/95%):
  美联储+25bp → A股影响: -3~5%   (非线性, 恐慌放大)
  
关键发现: 极端分位数下敏感度是中位数的 5-10倍
→ AQF-T 必须在Vix>25或北向单日流出>50亿时切换到高警戒模式
```

---

# 第四章 游资特化信号


```
游资决策需要的跨市场信号:

盘前(8:00-9:15):
  ✅ 美股收盘: 纳指/标普涨跌 + 中概股表现
  ✅ A50期货: 预示A股开盘方向
  ✅ 美元/人民币: 北向资金方向预判
  ✅ 全球Risk: VIX是否异常

盘中:
  ✅ 北向资金实时: 每30秒更新
  ✅ 港股联动: 同题材港股表现
  ✅ A50期货日内: 外资态度

触发规则:
  北向单日净流出 > 50亿 → 降仓至50%
  VIX > 30 → 暂停Dragon Strategy
  中概股隔夜暴跌 > 3% → A股开盘谨慎
```

---

# 第五章 API


| 端点 | 方法 | 功能 |
|------|:---:|------|
| GET /cross_market/overview | GET | 全球市场全景 |
| GET /cross_market/north_bound | GET | 北向资金实时 |
| GET /cross_market/alert | GET | 跨市场预警 |
| POST /cross_market/impact | POST | 外部事件影响评估 |

---

# 第六章 设计冻结声明


本文件定义 AQF-T Cross-Market Intelligence V3.6.0。

借鉴 2025 年QQ分位数关联研究 + A股三大传导链 + 游资跨市场决策信号。

核心: 极端市场状态下风险传导是非线性的(5-10倍放大)。

Version: V3.6.0 | Status: Detailed Engineering Design
END OF AQFT CROSS-MARKET INTELLIGENCE DESIGN
