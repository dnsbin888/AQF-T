# AQFT AI Runtime Design V3.6.0


# AQF-T AI 运行系统详细设计


Version: V3.6.0
Status: Detailed Engineering Design
Classification: AQF-T AI 实时运行体系设计文件
Date: 2026-07-26


---

# 第一章 定位


AI Runtime 将 03_AI_Brain 的设计变为可运行的推理服务。管理四引擎 (Prediction/Sentiment/RiskIntelligence/Fusion) 的模型加载、在线推理、结果输出和持续学习。

```
Data Runtime (特征数据) → AI Runtime (推理) → Strategy (信号生成)
```

---

# 第二章 模型加载


## 2.1 加载流程

```
系统启动 → Model Registry 读取 → 下载模型文件 → 校验版本 → 加载到内存 → Warmup推理 → READY
```

## 2.2 模型清单

| 引擎 | 模型类型 | 文件 | 加载方式 | 内存估算 |
|------|---------|------|---------|:---:|
| Prediction | LightGBM | prediction_v1.lgb | joblib/pickle | 50MB |
| Sentiment | XGBoost | sentiment_v1.xgb | joblib/pickle | 30MB |
| Risk Intelligence | LightGBM | risk_ai_v1.lgb | joblib/pickle | 30MB |
| Fusion | 逻辑回归+规则 | — | 代码逻辑 | < 5MB |

> 模型文件统一存放: models/

## 2.3 加载验证

```
加载后立即验证:
  ✅ 模型文件完整性 (MD5校验)
  ✅ 版本号匹配
  ✅ 空推理测试 (随机输入 → 有效输出)
  → 通过: READY
  → 失败: 回退到上一版本 → 告警
```

---

# 第三章 在线推理


## 3.1 推理 Pipeline

```
Feature Vector (来自 Data Runtime)
       │
       ▼
  ┌─────────────┐
  │ Preprocessing│  特征标准化/缺失值填充/归一化
  └─────────────┘
       │
       ▼
  ┌─────────────┐
  │ Model Predict│  LightGBM/XGBoost predict()
  └─────────────┘
       │
       ▼
  ┌─────────────┐
  │ Postprocess  │  概率校准/阈值判断/格式转换
  └─────────────┘
       │
       ▼
  PredictionOutput (发送到 Strategy)
```

## 3.2 四引擎并发调用

```
Real-time Market Event
       │
       ├──→ Prediction Engine (并行)
       ├──→ Sentiment Engine (并行)
       └──→ Risk Intelligence (并行)
               │
               ▼
          Fusion Engine (汇总)
               │
               ▼
          FusionOutput
```

## 3.3 推理性能要求

```
单次推理延迟: < 50ms (P50), < 200ms (P99)
并发能力: 支持10路并发推理
批推理: 支持批量预测(用于回测, 1000条 < 5秒)
```

---

# 第四章 推理调度


## 4.1 盘中调度

```
Market Tick (每3秒)
  → Sentiment 更新 (每分钟一次, 减少计算)
  → Prediction 更新 (每5分钟一次)
  → Risk Intelligence (每10秒一次, 实时性要求高)
```

## 4.2 事件驱动推理

```
以下事件触发立即推理:
  - 涨停板事件 (需要立即评估 Dragon Strategy 可行性)
  - 炸板事件 (需要立即评估卖出)
  - Regime 切换事件 (需要立即更新策略配置)
  - 人工查询 (即时响应)
```

## 4.3 盘后批推理

```
盘后 (15:00后):
  - 全量股票 Prediction 更新 (批量)
  - Sentiment 日终评估
  - 模型漂移检测
  - 龙虎榜分析
```

---

# 第五章 模型热切换


## 5.1 切换流程

```
新模型就绪 → 加载到备用Slot → 影子模式运行(1天) → 对比结果 → 切换
```

## 5.2 影子模式

```
新模型加载后:
  - 旧模型继续提供线上推理
  - 新模型同步接收输入, 输出记录到日志(不影响线上)
  - 24小时后对比: 新模型输出 vs 旧模型输出 vs 实际结果
  - 通过对比 → 切换为主模型
  - 未通过 → 卸载新模型 + 记录原因
```

---

# 第六章 模型监控


## 6.1 运行指标

| 指标 | 告警阈值 | 说明 |
|------|:---:|------|
| 推理延迟 P99 | > 500ms | 性能下降 |
| 推理错误率 | > 1% | 模型异常 |
| Prediction Drift | 分布变化 > 0.15 | 数据漂移 |
| Sentiment 偏离 | 与实际情绪周期不一致 > 2天 | 情绪模型失效 |
| 内存使用 | > 80% | 资源不足 |

## 6.2 模型健康状态

```
HEALTHY → 指标正常
WARNING → 单项指标超阈值
DEGRADED → 多项指标异常 + 降低置信度
FAILED → 停止使用 + 回退到上一版本
```

---

# 第七章 持续学习接口


## 7.1 反馈数据流

```
Trading Result → Experience Engine → 错误分析 → 训练数据生成 → 重训练触发
```

## 7.2 重训练触发条件

```
自动触发:
  ✅ 模型漂移 > 阈值 (持续3天)
  ✅ 预测准确率下降 > 10%
  ✅ 新增训练数据 > 30天

手动触发:
  POST /ai/model/retrain
```

---

# 第八章 API


| 端点 | 方法 | 功能 |
|------|:---:|------|
| POST /ai/predict | POST | 趋势预测 |
| POST /ai/sentiment | POST | 情绪分析 |
| POST /ai/risk | POST | AI风险预测 |
| POST /ai/fusion | POST | 综合决策 |
| GET /ai/model/status | GET | 所有模型状态 |
| POST /ai/model/switch | POST | 模型热切换 |
| POST /ai/model/retrain | POST | 触发重训练 |
| GET /ai/health | GET | 服务健康 |

---

# 第九章 设计冻结声明


本文件定义 AQF-T AI Runtime V3.6.0 详细设计。

四引擎并发推理(50ms延迟) + 模型热切换(影子模式) + 实时模型监控 + 持续学习接口。AI Runtime 是 AQF-T 的"大脑皮层"。

Version: V3.6.0
Status: Detailed Engineering Design
END OF AQFT AI RUNTIME DESIGN
