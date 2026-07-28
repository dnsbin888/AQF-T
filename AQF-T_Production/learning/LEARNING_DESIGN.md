# 06 Learning — AI插件 (纯建议)

## 定位

```
✅ 提供: 评分 / 概率 / 建议 / 经验
❌ 禁止: 直接下单 / 绕过Risk / 修改风控参数
```

## 三引擎

```
本地主力:
  LightGBM/CatBoost  趋势预测 (训练快/可解释/因子重要性)

云端辅助:
  Qwen API           因子挖掘 (IC 2.95%, 2026验证)
  DeepSeek API       选股建议 (实盘首周+7.23%)

L2模式:
  大单拆细识别 / DDX/DDY/DDZ监控 / 封单系数 / 盘口失衡
```

## 输出规范

```
每个预测必须附带:
  confidence: 置信度
  reasoning:  推理链 (可审计)
  factors:    主要贡献因子
```
