# AQF-T 行业对标框架 V1.0


**定位:** 系统化差距分析方法论
**原则:** 对标行业, 不泛泛而谈。找到真正差距, 指导V1.x升级。
**更新:** 每季度重新Benchmark一次


---

## 一、研究对象

```
游资交易体系:
  龙头战法 / 回封板 / 情绪周期 / 打板策略
  QMT实战 / 个人量化 / 自动交易

中小私募量化:
  因子体系 / 风控框架 / 执行系统 / 回测引擎

主流AI Quant:
  LightGBM/XGBoost/CatBoost / Transformer / 多模态

开源框架:
  Qlib / Backtrader / vnpy / NautilusTrader / QuantMind
```

## 二、对标方法

```
不是看有没有模块。
逐项比较: 能力 → 行业标准 → AQF-T现状 → 差距 → 优先级

评级:
  ✅ 对齐 or 领先
  ⚠️ 部分具备, 可加强
  ❌ 缺失, 需补齐
  ➕ AQF-T独有 (行业少见但有效)
```

## 三、对标维度

### 3.1 交易执行链

```
自动交易        ✅   QMT直连
风控体系        ✅   44公式+KillSwitch+7检查
回测引擎        ✅   事件驱动+Walk-Forward
模拟盘          ✅   Paper Broker+A股规则
实盘监控        ⚠️   System Monitor有, 待实盘验证
异常恢复        ⚠️   设计了重连/重试, 待验证
```

### 3.2 数据体系

```
行情接入        ✅   QMT L2 + akshare + 三级冗余
数据质量        ⚠️   Data Health Score框架有, 待自动化
数据存储        ✅   SQLite 14张表
Feature Store   ❌   因子目前是文件计算, 无专用存储
数据版本        ⚠️   设计了版本管理, 未实现
```

### 3.3 策略体系

```
回封板          ✅   Perception规则, 2026数据验证
半路/接力       ✅   LGBM+XGBoost, B1/B2/B3拆分
情绪周期        ✅   四阶段+Regime引擎
Dragon龙头      ✅   V2.8.6 Dragon战法
策略生命周期    ✅   Knowledge Hub管理
策略A/B Test    ❌   未设计 (未来两条路绩效对比)
```

### 3.4 AI/模型体系

```
模型训练        ✅   LGBM+XGBoost, 三目标标签
Model Registry  ✅   版本管理+上线/回滚
模型评估        ✅   IC/ICIR/Sharpe/AUC
在线监控        ❌   无漂移检测/在线评估
自动重训练      ⚠️   触发条件有, 未自动化
模型融合        ✅   Stacking方案 (Stage 2验证)
可解释性        ✅   SHAP + Plugin Interface
```

### 3.5 工程体系

```
Event Bus       ✅   发布/订阅解耦
系统监控        ✅   QMT/L2/DB/CPU/内存
日志与审计      ✅   所有决策可追溯
配置管理        ✅   system.yaml
插件化          ✅   Learning Plugin Interface
CI/CD           ❌   未设计
灾备            ❌   未设计 (单机运行)
```

### 3.6 AQF-T独有 (行业少见)

```
Market Regime   ➕   总开关, 所有策略读取 (行业少见)
Perception      ➕   8层感知, 游资专属 (行业无)
Decision Core   ➕   统一Candidate, 路径分叉 (行业少见)
Knowledge Hub   ➕   归因+经验+训练+生命周期 (行业少见)
Constitution    ➕   14边界宪法 (行业罕见)
```

## 四、差距优先级

### P0 — 实盘前必须补齐

```
数据质量自动化      Data Health Score自动计算+告警
在线监控            模型漂移检测/数据漂移检测
异常恢复验证        QMT断线/DB异常/重复订单 场景测试
```

### P1 — V1.1 升级

```
Feature Store        因子统一存储+版本+血缘
策略A/B Test         路径A vs B 绩效统计对比
自动重训练           模型性能下降→自动触发重训
```

### P2 — V1.2+ 研究

```
多模态融合           结构化行情 + LLM文本
Transformer因子      时序特征提取 (仅Research Lab)
CI/CD                自动化测试+部署
灾备                 双机热备 or 云端备份
```

## 五、Benchmark 频率

```
首次:    2026-Q3 (V1.0冻结后)
更新:    每季度一次
触发:    行业重大变化时 (新框架/新论文/监管变化)

每次Benchmark输出:
  差距分析报告
  优先级调整建议
  V1.x升级路线更新
```

---

**本文件是AQF-T的行业对标方法论。指导V1.x升级, 防止闭门造车。**
