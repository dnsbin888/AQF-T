# AQF-T Feature Engineering Specification V3.6.0


# AQF-T 因子工程规范


Version: V3.6.0 | Status: Engineering Specification | Date: 2026-07-26

> 参考: WorldQuant 101 Alpha + QMT 8类因子 + 游资实战因子


---

# 第一章 因子清单 (100个)


## 1.1 技术因子 (30个)

| # | 因子名 | 公式 | 周期 |
|:--:|--------|------|:---:|
| 1 | MA_5 | 5日均线 | 5d |
| 2 | MA_20 | 20日均线 | 20d |
| 3 | MA_60 | 60日均线 | 60d |
| 4 | MA偏离_5 | (close-MA5)/MA5 | 5d |
| 5 | MA偏离_20 | (close-MA20)/MA20 | 20d |
| 6 | MACD_DIF | EMA12-EMA26 | — |
| 7 | MACD_DEA | DIF的9日EMA | — |
| 8 | MACD_BAR | (DIF-DEA)×2 | — |
| 9 | MACD金叉 | DIF上穿DEA | 1d |
| 10 | RSI_6 | 6日RSI | 6d |
| 11 | RSI_14 | 14日RSI | 14d |
| 12 | RSI_超买 | RSI14>70 | 1d |
| 13 | RSI_超卖 | RSI14<30 | 1d |
| 14 | KDJ_K | 随机指标K | 9d |
| 15 | KDJ_D | 随机指标D | 9d |
| 16 | KDJ_金叉 | K上穿D | 1d |
| 17 | BOLL_UP | 布林上轨 | 20d |
| 18 | BOLL_MID | 布林中轨(MA20) | 20d |
| 19 | BOLL_DN | 布林下轨 | 20d |
| 20 | BOLL_WIDTH | (UP-DN)/MID | 20d |
| 21 | ATR_14 | 14日平均真实波幅 | 14d |
| 22 | ATR_比率 | ATR14/close | 14d |
| 23 | 量比 | V/V5_avg | 1d |
| 24 | 换手率 | V/流通股 | 1d |
| 25 | 振幅 | (high-low)/pre_close | 1d |
| 26 | 涨速 | (close-pre_close)/pre_close | 1d |
| 27 | OBV | 累积能量潮 | — |
| 28 | WR | 威廉指标 | 14d |
| 29 | CCI | 商品通道指数 | 14d |
| 30 | ADX | 平均趋向指数 | 14d |

## 1.2 Alpha因子 (30个)

| # | 因子名 | 公式 | 类型 |
|:--:|--------|------|:---:|
| 31 | momentum_5d | close/close_5d-1 | 动量 |
| 32 | momentum_20d | close/close_20d-1 | 动量 |
| 33 | momentum_60d | close/close_60d-1 | 动量 |
| 34 | reversal_5d | -momentum_5d | 反转 |
| 35 | volatility_20d | std(ret,20) | 波动 |
| 36 | volatility_60d | std(ret,60) | 波动 |
| 37 | vol_ratio | vol_20d/vol_60d | 波动变化 |
| 38 | skewness_20d | 偏度(ret,20) | 分布 |
| 39 | kurtosis_20d | 峰度(ret,20) | 分布 |
| 40 | max_drawdown_60d | 60日最大回撤 | 风险 |
| 41 | upside_vol | 正收益波动率 | 上行 |
| 42 | downside_vol | 负收益波动率 | 下行 |
| 43 | sharpe_60d | ret_avg/std×√252 | 效率 |
| 44 | sortino_60d | ret_avg/downside_std | 效率 |
| 45 | corr_market_20d | corr(ret,index_ret,20) | Beta |
| 46 | beta_60d | cov(ret,index)/var(index) | Beta |
| 47 | alpha_60d | ret-beta×index_ret | Alpha |
| 48 | turnover_5d_avg | avg(turnover,5) | 流动性 |
| 49 | turnover_20d_avg | avg(turnover,20) | 流动性 |
| 50 | amount_5d_avg | avg(amount,5) | 成交额 |
| 51 | amount_ratio | amount/amount_20d_avg | 放量 |
| 52 | volume_ratio | volume/volume_20d_avg | 量比 |
| 53 | price_position_60d | (close-low60)/(high60-low60) | 位置 |
| 54 | gap_ratio | (open-pre_close)/pre_close | 跳空 |
| 55 | intraday_amplitude | (high-low)/open | 日内振幅 |
| 56 | upper_shadow | (high-max(open,close))/high | 上影线 |
| 57 | lower_shadow | (min(open,close)-low)/low | 下影线 |
| 58 | volume_price_corr_20d | corr(volume,close,20) | 量价相关 |
| 59 | high_low_ratio_20d | avg(high/low,20) | 波动范围 |
| 60 | consecutive_up_days | 连续上涨天数 | 趋势强度 |

## 1.3 情绪因子 ⭐ (20个)

| # | 因子名 | 公式 | 来源 |
|:--:|--------|------|------|
| 61 | sentiment_score | 涨停×2-跌停×3+连板×5+北向×10 | 03_AI_Brain |
| 62 | limit_up_count | 全市场涨停家数 | 实时 |
| 63 | limit_down_count | 全市场跌停家数 | 实时 |
| 64 | board_height_max | 最高连板高度 | 实时 |
| 65 |炸板率 | 炸板/摸板 | 实时 |
| 66 | first_board_promotion | 昨日首板今连板比例 | 日 |
| 67 | seal_strength | 封单额/成交额 | 实时 |
| 68 | north_bound_net | 北向净流入(亿) | 实时 |
| 69 | north_bound_direction | 连续3日净流入方向 | 日 |
| 70 | margin_balance_change | 融资余额变化率 | 日 |
| 71 | theme_heat_score | 题材热度公式 | 03_AI_Brain |
| 72 | dragon_board_count | 题材龙头连板数 | 实时 |
| 73 | sector_limit_up_count | 同题材涨停家数 | 实时 |
| 74 | institutional_net | 龙虎榜机构净买入 | 日 |
| 75 | retail_sentiment_idx | 散户情绪(社交媒体) | 日 |
| 76 | news_sentiment_score | 新闻舆情评分 | 实时 |
| 77 | policy_sentiment | 政策级别×影响方向 | 不定期 |
| 78 | up_down_ratio | 上涨/下跌家数 | 实时 |
| 79 | index_trend | 大盘趋势方向 | 日 |
| 80 | vix_proxy | 波动率/均值(恐慌代理) | 日 |

## 1.4 资金因子 (20个)

| # | 因子名 | 公式 | 来源 |
|:--:|--------|------|------|
| 81 | main_net_inflow | 主力净流入 | 实时 |
| 82 | main_inflow_ratio | 主力净流入/成交额 | 实时 |
| 83 | big_order_ratio | 大单成交占比 | 实时 |
| 84 | institution_flow_5d | 机构资金5日累计 | 日 |
| 85 | retail_flow_5d | 散户资金5日累计 | 日 |
| 86 | margin_balance | 融资余额 | 日 |
| 87 | short_interest_ratio | 融券余量/流通股 | 日 |
| 88 | block_trade_premium | 大宗交易溢价率 | 不定期 |
| 89 | insider_buy | 高管增持金额 | 不定期 |
| 90 | insider_sell | 高管减持金额 | 不定期 |
| 91 | fund_holding_pct | 基金持仓占比 | 季 |
| 92 | fund_holding_change | 基金持仓变化 | 季 |
| 93 | north_holding_pct | 北向持仓占比 | 日 |
| 94 | north_holding_change | 北向持仓变化 | 日 |
| 95 | ipo_lock_expire | 解禁日期临近 | 不定期 |
| 96 | pledge_ratio | 股权质押比例 | 不定期 |
| 97 | dividend_yield | 股息率 | 年 |
| 98 | buyback_amount | 回购金额 | 不定期 |
| 99 | capital_flow_score | 综合资金流向评分 | 日 |
| 100| flow_momentum | 资金流向趋势 | 5d |

---

# 第二章 因子处理流程

```
Raw Data → 缺失值填充(前向fill) → 标准化(Z-Score) → 去极值(3σ截尾) → 中性化(行业+市值) → Factor Store
```

# 第三章 因子评价

| 指标 | 阈值 | 说明 |
|------|:---:|------|
| IC (Rank) | > 0.05 | 信息系数 |
| IR | > 0.5 | 信息比率 |
| 分层回测 | Top-Bottom > 5% | 多空收益差 |
| 换手率 | < 80% | 因子稳定性 |
| 最大回撤 | < 30% | 因子风险 |

---

Version: V3.6.0 | Status: Engineering Specification
END OF AQFT FEATURE ENGINEERING SPECIFICATION
