# DEC-032D: Fusion Policy

Version: V1.0.0
Status: DESIGN — 初稿
Date: 2026-08-03
Part of: DEC-032 Evidence Intelligence Design (M2)
Based on: DEC-032A/B/C + DEC-029 Evidence First

---

## 一、Fusion 是什么

**Fusion 不是投票。不是仲裁。是 Evidence 的自然聚合。**

多个 Producer 各自输出 Evidence。Fusion 将它们聚合为一个 Decision。Fusion 本身也是 Evidence 的消费者——它只读 Evidence，不修改 Evidence。

## 二、核心原则

1. **Evidence Weight, not Model Weight** — 权重基于 Evidence 的历史可信度，不是模型偏好
2. **Regime Gates, not Always On** — 不同市场阶段使用不同的 Evidence 组合
3. **Confidence Gates, not Binary** — 融合结果带置信度，低置信度→保守
4. **Risk Override, always** — 风险 Evidence 永远拥有否决权

## 三、Fusion 框架

```
Evidence Input
│
├── Trend Evidence     {direction: LONG,  strength: 0.82, confidence: 0.81}
├── Momentum Evidence  {direction: LONG,  strength: 0.77, confidence: 0.73}
├── Board Evidence     {direction: LONG,  strength: 0.91, confidence: 0.88}
├── Regime Evidence    {phase: 高潮期,    confidence: 0.94}
├── Risk Evidence      {level: LOW,       confidence: 0.90}
└── Flow Evidence      {direction: INFLOW, strength: 0.65, confidence: 0.70}
        │
        ▼
   Weight Assignment (per Evidence, per Regime)
        │
        ▼
   Weighted Fusion
        │
        ▼
   Confidence Gate
        │
        ▼
   Risk Override Check
        │
        ▼
   Decision Output
   {action: BUY, position: 12%, confidence: 0.83, reasoning: [...]}
```

## 四、权重模型

### 4.1 基础权重

每个 Evidence 的基础权重由 Evaluation 决定：

```
Weight(Evidence) = f(Evaluation.hit_rate, Health.drift_level)

默认映射:
  hit_rate ≥ 0.70 + drift=LOW     → weight = 0.30
  hit_rate ≥ 0.60 + drift=LOW     → weight = 0.25
  hit_rate ≥ 0.50 + drift≤MEDIUM  → weight = 0.20
  hit_rate < 0.50 or drift=HIGH   → weight = 0.10
  lifecycle = ARCHIVED             → weight = 0.00
```

### 4.2 Regime 自适应

同一 Evidence 在不同 Regime 下权重不同：

| Evidence | 高潮期 | 回暖期 | 冰点期 | 退潮期 |
|----------|:-----:|:-----:|:-----:|:-----:|
| Trend | 0.25 | 0.30 | 0.15 | 0.00 |
| Momentum | 0.25 | 0.20 | 0.10 | 0.00 |
| Board | 0.20 | 0.25 | 0.15 | 0.00 |
| Regime | 0.10 | 0.10 | 0.30 | 0.50 |
| Risk | 0.10 | 0.10 | 0.20 | 0.50 |
| Flow | 0.10 | 0.05 | 0.10 | 0.00 |

**退潮期**: Regime + Risk 占 100% → 自动禁止买入。

### 4.3 Confidence Gate

融合后的置信度决定操作范围：

| 融合置信度 | 允许操作 |
|:--------:|----------|
| > 0.80 | 满仓执行（Regime 上限内） |
| 0.60-0.80 | 半仓执行 |
| 0.40-0.60 | 仅 Hold（不新增仓位） |
| < 0.40 | 观望（不操作） |

## 五、Fusion 公式（参考）

```
Fused_Score = Σ (Evidence_i.strength × Evidence_i.confidence × Weight_i × Regime_Factor_i)

Decision = {
  action:      Fused_Score > 0.6 → BUY, < -0.6 → SELL, else HOLD
  position:    Regime.max_position × Confidence_Factor
  confidence:  Weighted_Avg(Evidence_i.confidence × Weight_i)
  reasoning:   [各 Evidence 的贡献度排序]
}
```

## 六、Fusion 不做的事

```
❌ 不做模型投票（那是 Triple Vote 的事）
❌ 不做信号仲裁（那是 HypothesisArbitrator 的事）
❌ 不直接输出订单（那是 Decision → Risk → Execution 的事）
❌ 不修改 Evidence（Evidence 永远 Immutable）
❌ 不对单一 Evidence 做判断（Fusion 的输入必须 ≥2 个 Evidence）
```

## 七、实现阶段

| 阶段 | 内容 | 前置条件 |
|------|------|----------|
| Phase 2.1 | 静态权重 Fusion（手动配置权重表） | DEC-032A/B/C 冻结 |
| Phase 2.2 | Regime 自适应权重 | P0-3 Evaluation 积累 ≥ 60天 |
| Phase 2.3 | 历史 Evidence 权重学习 | P0-4 Health 稳定运行 |
| Phase 3 | 自动化权重调整（Evolution System 接管） | 需 DEC-030 Evidence Governance |

---

*DEC-032D Fusion Policy V1.0 — 待老板评审*
