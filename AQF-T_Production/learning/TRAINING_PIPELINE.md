# Training Pipeline — 模型训练流程


## LGBM 趋势预测 (B1 Trend用)

### 三目标标签

```
不是预测单一收益率。是游资视角的三维评估:

Label 1: 短线爆发 (未来5日最高收益)
  回答: "有没有机会?"
  计算: max(close_t1..close_t5) / close_t0 - 1

Label 2: 最大回撤 (未来5日最大亏损)
  回答: "风险多大?"
  计算: min(close_t1..close_t5) / close_t0 - 1

Label 3: 资金认可 (是否进入涨停/连板状态)
  回答: "游资关注?"
  值: 1(涨停/连板) / 0.5(大涨>5%) / 0(其他)

最终: 机会评分 = 爆发概率×0.5 - 风险概率×0.3 + 资金认可度×0.2
```

### 数据准备

```
数据源: akshare 日K线 (3年+历史)
股票池: 沪深A股 (排除ST/新股<375天/停牌)
标签: 三目标 (爆发/回撤/资金认可)
```

特征 (100个):
  技术30: MA/MACD/RSI/KDJ/BOLL/ATR/OBV/...
  Alpha30: momentum/reversal/vol/skew/sharpe/beta/...
  情绪20: 涨停家数/连板高度/炸板率/北向/...
  资金20: 主力净流入/大单占比/DDX/DDY/...
```

### 训练

```
from lightgbm import LGBMClassifier, early_stopping

数据划分:
  Train: 2022-2024 (3年)
  Val:   2025 Q1-Q3
  Test:  2025 Q4-2026

训练:
  LGBMClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    num_leaves=31,
    min_child_samples=100,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=0.1,
  )
  model.fit(X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[early_stopping(50)])

预处理:
  - 整体Z-Score标准化 (不做截面标准化)
  - 不做行业/市值中性化 (广发验证: 反而降低效果)

损失函数: 多目标等权合成
  MSE + NDCG + Hinge Loss → 最终因子
```

### 评估

```
IC (Rank) > 0.05
ICIR > 0.3
分层回测 Top-Bottom > 5%
AUC > 0.65

不达标 → 检查特征/标签/过拟合 → 调整 → 重训
达标 → Model Registry → 月度滚动更新
```

---

## XGBoost L2 — 确认器 (非决策者)

```
定位: Confirmation Model, 不是 Trading Model

路径A: Perception发现回封 → XGBoost确认盘口质量
路径B3: Alpha发现强势 → XGBoost确认封板概率

融合公式: Final = Perception×0.7 + XGBoost×0.3

不输出: BUY/SELL
只输出: 盘口质量分 0-1
```

### 训练

### 数据准备

```
数据源: QMT L2 (3个月历史)
股票池: 仅涨停相关股票 (非全市场)
标签: 未来30分钟/60分钟收益率 二分类(NOW/WAIT)

特征:
  L2_1: 逐笔成交特征
    - 大单买入占比
    - 主动买入/卖出比
    - 成交密度 (笔/分钟)
  L2_2: 十档盘口特征
    - 买卖盘失衡率
    - 盘口深度变化率
    - 价差变化
  L2_3: 封单特征
    - 封单量变化率
    - 撤单率
    - 封单/流通市值比
```

### 训练

```
from xgboost import XGBClassifier

XGBClassifier(
    n_estimators=300,
    learning_rate=0.03,
    max_depth=5,
    subsample=0.7,
    colsample_bytree=0.7,
    reg_alpha=0.5,
    reg_lambda=1.0,
    scale_pos_weight=3,  # NOW样本稀少, 加权
)
```

### 评估

```
分类准确率 > 55% (NOW/WAIT)
NOW召回率 > 60% (不错过好机会)
WAIT精确率 > 60% (不浪费资金)
```

---

## 经验积累 (在线学习)

```
每笔交易后:
  ① 记录: 预测值 vs 实际结果
  ② 入库: Experience DB
  ③ 月结: 统计模型准确率变化
  ④ 触发: 准确率下降>10% → 自动重训

重训频率:
  LGBM: 月度滚动 (新增1个月数据, 重新训)
  XGBoost: 日度 (新增1天L2数据, 增量更新)
```
