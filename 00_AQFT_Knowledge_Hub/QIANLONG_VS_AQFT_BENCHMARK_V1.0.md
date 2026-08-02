# 潜龙 vs AQF-T：全维度深度比对报告 V1.0

Version: V1.0.0
Date: 2026-08-02
Type: 战略分析 — 系统融合可行性评估
Author: CC (Claude Code) — 二次审计

---

## 一、系统概览

| | 潜龙 (Qianlong) | AQF-T |
|---|---|---|
| **全称** | 潜龙量化交易系统 | Adaptive Quantitative Fusion Trading System |
| **定位** | 个人量化 × 游资纪律 × 小型私募流程 | 自适应量化融合交易系统 |
| **代码规模** | 363+ Python文件 (quant_framework) + web | 80 Python文件 (Production) |
| **设计母库** | 无独立母库（代码即文档） | V2.8.6 FROZEN (59份FINAL文档) |
| **开发模式** | 自下而上，实战迭代 6个月 | 自上而下，设计先行，GPT设计→人工批复→CC执行 |
| **测试** | 51/51 全链路测试 | 34/34 (25 M1 + 9 Pipeline E2E) |
| **QMT** | ✅ 真实连接，交易过 | ❌ 仅Simulator，未接入 |
| **设计质量** | 实用主义 | 架构治理 |

---

## 二、九维逐项比对

### 维度 1：架构设计

| 子项 | 潜龙 | AQF-T | 评分 |
|------|------|-------|:--:|
| **架构清晰度** | 函数式+模块混合，随时间积累 | 分层管线：Regime→Perception→Path→Decision→Risk→Execution | 🟡 AQF-T优 |
| **模块边界** | 边界模糊，模块间有交叉引用 | Constitution 14条边界，Frozen模块不可侵入 | 🟡 AQF-T优 |
| **可维护性** | 依赖开发者记忆 | 59份设计文档+Decision Log可追溯 | 🟡 AQF-T优 |
| **灵活性** | 极其灵活，快速迭代 | Frozen后改动需Review→新版本号 | 🔴 潜龙优 |
| **文档完整性** | 记忆文件为主，非正式 | 完整设计文档+工程规范+冻结声明 | 🟡 AQF-T优 |

**小结**：AQF-T 架构清晰但僵化，潜龙灵活但散乱。互补。

---

### 维度 2：信号生成

| 子项 | 潜龙 | AQF-T | 评分 |
|------|------|-------|:--:|
| **因子体系** | 因子注册表 + 自动化管线 + IC跟踪 | 100因子设计文档，生产未完全落地 | 🔴 潜龙优 |
| **ML模型** | ✅ LGBM IC=0.30 + XGBoost AUC + CatBoost Spearman=0.90，Optuna调优 | LGBM+XGBoost框架，缺训练数据和Optuna | 🔴 潜龙优 |
| **投票机制** | Triple Vote (2/3同意，min_models=1) | 无独立投票，DecisionCore做冲突消解 | 🔴 潜龙优 |
| **信号分级** | Lv1(2%)→Lv5(12%)，5级信号+仓位映射 | Path A(规则)/Path B(ML)→综合评分→Decision | 🟡 各有特色 |
| **回封板感知** | 弱转强压测+ConnorsRSI | ✅ Path A完整感知管线(炸板分类+回封确认+龙头判定) | 🟡 AQF-T优 |
| **TDX公式信号** | ✅ 30秒轮询，端到端<30秒 | 无 | 🔴 潜龙特有 |

**小结**：潜龙信号体系实战成熟；AQF-T Path A感知管线设计精良但未验证。**潜龙的ML+AQF-T的感知=最强组合**。

---

### 维度 3：风控体系

| 子项 | 潜龙 | AQF-T | 评分 |
|------|------|-------|:--:|
| **事前风控** | 8项检查：信号去重/乌龙指/涨跌停/日笔数/信号等级/仓位总数/资金/集中度 | PreTradeChecker 44公式 APPROVE/ADJUST/REJECT | 🟡 相近 |
| **仓位管理** | 信号等级×市场系数，板块≤30%，单票≤20% | Regime自适应：高潮70%/回暖50%/冰点10%/退潮0% | 🟡 各有特色 |
| **熔断机制** | 日亏损-5%，撤单率>50% | KillSwitch 独立模块 | 🟡 相近 |
| **止损体系** | ✅ ATR动态止损 + 三级移动止盈(5%/7%/10%) | ExitPipeline: 硬止损+Regime Break+龙头结束 | 🟡 各有特色 |
| **T+1/涨跌停** | ✅ 完整实现 | ✅ PaperBroker已实现 | 🟢 平 |
| **风控审批链** | 4元组返回(APPROVE/REJECT/REDUCE/QUEUE) | 标准3元组(APPROVE/ADJUST/REJECT) | 🟡 潜龙多QUEUE状态 |

**小结**：两者风控都很完善。潜龙的ATR动态止损+移动止盈更贴近实战；AQF-T的ExitPipeline架构更完整（Risk Exit→Strategy Exit→Evidence）。

---

### 维度 4：执行层

| 子项 | 潜龙 | AQF-T | 评分 |
|------|------|-------|:--:|
| **QMT通道** | ✅ passorder(<5ms) + Flask审核双通道 | ❌ 仅PaperBroker模拟 | 🔴 潜龙优 |
| **键盘交易** | ✅ F1-F8快捷键+联动精灵 | 无 | 🔴 潜龙特有 |
| **同花顺联动** | ✅ 持仓读取+弹窗杀手 | 无 | 🔴 潜龙特有 |
| **执行Agent** | 无独立Agent层 | DEC-024定义三层架构(Strategic→ExecutionAgent→QMT) | 🟡 AQF-T有设计 |
| **Paper Trading** | paper_engine.py (基础) | PaperBroker (T+1/费率/涨跌停/流动性) | 🟡 AQF-T优 |

**小结**：潜龙执行层实战可用的，AQF-T还在设计阶段。**这是最大的差距**。

---

### 维度 5：数据体系

| 子项 | 潜龙 | AQF-T | 评分 |
|------|------|-------|:--:|
| **数据源** | ✅ TDX公式+akshare+baostock+QMT xtdata+Sina实时(5路径) | MarketDataProvider ABC，仅Simulator | 🔴 潜龙优 |
| **实时行情** | ✅ Sina批量+TDX+QMT，多路径降级 | 无 | 🔴 潜龙优 |
| **Level-2** | QMT L2（已开通，未全量接入） | data/sources/qmt_l2_loader.py 骨架 | 🟡 相近 |
| **龙虎榜** | ✅ lhb_fetcher.py 每日增量 | 无 | 🔴 潜龙特有 |
| **北向资金** | ✅ northbound_factor.py | 无 | 🔴 潜龙特有 |
| **数据治理** | 12项审计/备份/校验/Git | 无独立治理层 | 🔴 潜龙优 |
| **数据质量** | 基础 | M1 Data Quality完整框架(Validator/Detector/Recovery/Health) | 🟡 AQF-T优 |

**小结**：潜龙的数据管道丰富且实战验证；AQF-T的数据质量框架设计完善但未接入真实数据。

---

### 维度 6：监控与告警

| 子项 | 潜龙 | AQF-T | 评分 |
|------|------|-------|:--:|
| **钉钉推送** | ✅ Webhook+指令解析+SSE推送 | 无 | 🔴 潜龙特有 |
| **Web Dashboard** | Flask多页面+Streamlit+Plotly图表 | 单页HTTP :8080 | 🔴 潜龙优 |
| **系统监控** | 基础(bat重启脚本) | SystemMonitor+Watchdog+Supervisor独立模块 | 🟡 AQF-T优 |
| **运行时治理** | 无 | 7模块：Supervisor/Recovery/PositionReconciler/KillSwitch/Idempotency/ConfigValidator/Logger | 🟡 AQF-T优 |

**小结**：潜龙的钉钉+Web前端生态远胜AQF-T；AQF-T的Runtime监控体系更工程化。

---

### 维度 7：退出/生命周期

| 子项 | 潜龙 | AQF-T | 评分 |
|------|------|-------|:--:|
| **止盈** | ✅ 三级移动止盈 (5%/7%/10% + 回落卖) | 无独立止盈模块 | 🔴 潜龙优 |
| **止损** | ✅ ATR动态止损+固定%止损 | ExitPipeline E2 (Risk Exit) 硬止损 | 🟡 各有特色 |
| **策略退出** | 弱（依赖人工判断） | ✅ E3: 炸板退出/龙头结束/题材死亡 | 🟡 AQF-T优 |
| **退出证据** | 无 | ✅ E4 Exit Evidence完整记录 | 🟡 AQF-T优 |
| **Exit Pipeline** | 无独立管线 | ✅ 完整ExitPipeline(E1骨架→E4证据) | 🟡 AQF-T优 |

**小结**：潜龙的止盈止损实战优化；AQF-T的策略退出+证据体系设计精良。**结合=完整**。

---

### 维度 8：治理与决策追溯

| 子项 | 潜龙 | AQF-T | 评分 |
|------|------|-------|:--:|
| **系统宪法** | AI工作宪法 v1.0 | Constitution V2.8.6 (14边界+C004-C016) | 🟡 AQF-T优 |
| **参数治理** | 三级体系(唯一真相源+禁止硬编码+铁律) | 参数版本化(config/system.yaml) | 🔴 潜龙优 |
| **决策追溯** | 审计日志(audit_log.jsonl) | Decision Log结构化(背景+选项+结论+影响) | 🟡 各有特色 |
| **冻结机制** | 执行层锁定+代码只可调参 | Frozen模块+CC约束+GPT Review Gate | 🟡 AQF-T优 |
| **防重机制** | ✅ 三层防重(信号ID/日期/集合) | Idempotency模块 | 🟡 相近 |

**小结**：治理都很强。潜龙的参数治理更实操；AQF-T的冻结+审阅机制更正式。

---

### 维度 9：AI与研究能力

| 子项 | 潜龙 | AQF-T | 评分 |
|------|------|-------|:--:|
| **ML模型** | ✅ 3模型Optuna优化，实战IC跟踪 | 模型框架(Alpha/Timing)，缺训练 | 🔴 潜龙优 |
| **因子IC** | ✅ full_market_ic自动化+IC历史 | 因子IC设计文档，未工程化 | 🔴 潜龙优 |
| **进化系统** | 手工迭代 | 22_Evolution完整设计(已审计为需归档) | 🟡 各有特色 |
| **LLM** | 评估过TradingAgents(结论：不适合) | deepseek_enabled=false | 🟢 平 |
| **World Model** | 无 | 24_World_Model完整设计(已审计为长期研究) | 🟢 均不实用 |
| **Agent** | 无 | 23_Agent设计(已审计为归档) | 🟢 均不实用 |

**小结**：潜龙ML实战强；AQF-T的未来概念多但不可落地。

---

## 三、综合评分

| 维度 | 潜龙 | AQF-T | 优胜 |
|------|:--:|:--:|------|
| 1. 架构设计 | 6/10 | **9/10** | AQF-T |
| 2. 信号生成 | **8/10** | 5/10 | 潜龙 |
| 3. 风控体系 | **8/10** | 7/10 | 潜龙 |
| 4. 执行层 | **9/10** | 3/10 | 潜龙 |
| 5. 数据体系 | **9/10** | 3/10 | 潜龙 |
| 6. 监控告警 | **8/10** | 5/10 | 潜龙 |
| 7. 退出/生命周期 | 5/10 | **8/10** | AQF-T |
| 8. 治理追溯 | 7/10 | **8/10** | AQF-T |
| 9. AI/研究 | **7/10** | 3/10 | 潜龙 |
| **综合** | **7.4/10** | **5.7/10** | 潜龙 |

> 潜龙胜在执行和数据；AQF-T胜在架构和治理。

---

## 四、差距矩阵

### 潜龙有、AQF-T缺（🔴 致命差距）

| 项目 | 影响 | 优先级 |
|------|------|:--:|
| QMT真实连接+交易 | AQF-T无法实盘 | P0 |
| 实时行情（5路径） | AQF-T看不到真实市场 | P0 |
| ML模型训练+Optuna优化 | AQF-T信号无统计基础 | P0 |
| 钉钉推送 | 无移动端告警 | P1 |
| 龙虎榜+北向资金 | 缺游资核心数据 | P1 |
| 通达信公式信号 | 缺技术面信号源 | P1 |
| ATR动态止损+移动止盈 | 退出不够精细 | P1 |
| Flask多页面Web | Dashboard太简陋 | P2 |
| 三级参数治理 | 参数管理需加强 | P2 |

### AQF-T有、潜龙缺（🟡 架构差距）

| 项目 | 影响 | 优先级 |
|------|------|:--:|
| Constitution冻结治理 | 架构变动无强制约束 | P1 |
| ExitPipeline (策略退出+证据) | 卖出缺乏系统化归因 | P0 |
| Decision Log 结构化 | 决策追溯不够完整 | P1 |
| Runtime 7模块 (Supervisor/KillSwitch/Recovery) | 运行时保障不足 | P1 |
| Path A 回封板感知管线 | 打板决策缺乏系统化 | P1 |
| Evidence Package | 缺少完整证据体系 | P1 |
| MarketDataProvider 统一接口 | 数据源切换不够优雅 | P2 |
| 四阶段情绪周期 | 市场判断粒度不够 | P2 |

---

## 五、改进方案

### 短期 (本周可做，不改代码)

| 行动 | 说明 |
|------|------|
| 1. 互读对方设计 | 潜龙团队读 AQF-T ExitPipeline/Constitution；AQF-T 团队读 潜龙参数治理/风控 |
| 2. 定义桥接协议 | 统一信号JSON格式（symbol/action/confidence/position_pct/reasoning） |
| 3. 差距优先级排序 | 按致命→重要→改善排列 |

### 中期 (需要GPT设计+老板批复)

| 行动 | AQF-T侧 | 潜龙侧 |
|------|---------|--------|
| P0: QMT数据桥接 | 实现QMTProvider→MarketDataProvider | 暴露QMT行情接口 |
| P0: 退出增强 | ExitPipeline吸收ATR止损+移动止盈 | 接入ExitPipeline的策略退出信号 |
| P1: 信号互传 | Decision信号→潜龙QMT执行 | ML信号→AQF-T Path B候选池 |
| P1: 证据互通 | Evidence→潜龙Dashboard展示 | 交易记录→AQF-T Decision Memory |
| P2: Web统一 | Dashboard增强 | 潜龙Flask嵌入AQF-T状态卡片 |

### 长期 (等QMT环境+真实交易数据)

| 行动 | 说明 |
|------|------|
| 市场状态统一 | 潜龙4因子市场状态 vs AQF-T 4阶段情绪周期 → 双引擎交叉验证 |
| 参数治理融合 | 潜龙三级体系 + AQF-T Frozen机制 |
| 完整证据闭环 | 入口→持仓→退出→归因 全链路 |

---

## 六、核心结论

### 不合一，但互操作

**代码层面不合并。** 两个系统的基因不同（363 vs 80文件，实战 vs 设计），强行合并会两败俱伤。

**功能层面桥接。** 通过统一信号格式 + 桥接层，实现：
- AQF-T 给潜龙：Regime判断、Path A信号、ExitPipeline卖出、Evidence证据
- 潜龙 给 AQF-T：QMT行情、ML评分、钉钉推送、实时执行、龙虎榜数据

### 最优先的三件事

1. **QMT数据接入AQF-T** — 让AQF-T看到真实市场
2. **ExitPipeline接入潜龙** — 让潜龙拥有系统化的策略退出+证据
3. **统一信号格式** — 两个系统的信号可以互通

### 一句话

> **AQF-T 是大脑，潜龙是身体。不合一，但互联。**

---

*潜龙 vs AQF-T 深度比对报告 V1.0 — 2026-08-02*
*作者：CC (Claude Code) — 执行+审计*
*状态：待老板审核，关键结论可传递给GPT做桥接架构设计*

---

# 附录：给 GPT 的完整设计简报

> 以下内容可直接复制给 ChatGPT，让它充分理解两个系统的全貌和你的设计需求。

---

## 一、我是谁、我要什么

**身份**：个人量化交易者，风格偏向游资（打板/回封板）但有系统化思维。不是机构，不是高频。

**目标系统定位**：个人量化 × 游资纪律 × 小型私募流程。对标三层：①个人量化(vnpy/QMT/聚宽) ②游资(情绪周期/止损纪律) ③小型私募(风控/归因/流程)。

**核心需求**：我手上有两套独立的量化系统。一套是自己实战迭代了 6 个月的"潜龙"，一套是从 GitHub 拉下来的 AQF-T（GPT 设计的）。我不想合并代码，但想让它们互补——潜龙有执行能力和数据，AQF-T 有更好的决策框架。

**我需要你设计**：一个轻量的"决策增强层"，让 AQF-T 作为潜龙的副驾，不替代任何模块，只在决策链路的三个关键点增强。

---

## 二、我已有两个系统

### 系统A：潜龙 (D:\quant_framework)

**我日常用的主系统。QMT 连接过，真实交易过。**

#### 架构
```
数据层(5路径) → 因子管线 → ML三模型(LGBM/XGBoost/CatBoost) → 5级信号 → 仓位计算 → 风控 → QMT执行
                                                                                   ↓
TDX通达信公式信号 ─────────────────────────────────────────────────────────→ QMT快速通道(<5ms)
                                                                                   ↓
                                                                         Flask审核通道 ← 键盘F1-F8
```

#### 关键模块详情

**信号生成**：
- 因子注册表 + 自动化发现管线（Generator→Simulator→Checker→Register）
- ML 三模型已训练：LGBM IC=0.30 / XGBoost AUC优化 / CatBoost Spearman=0.90（都用 Optuna 调过参）
- Triple Vote：2/3 模型同意才出信号（当前 min_models=1，即任一模型有信号就通过）
- 5 级信号→仓位映射：Lv1=2% Lv2=4% Lv3=6% Lv4=8% Lv5=12%
- TDX 通达信公式信号：30 秒轮询解析 .txt，端到端 <30 秒

**市场状态**：
- 四因子打分：趋势(40%)+量价(20%)+宽度(20%)+波动(20%)
- 输出三档：牛市/震荡/熊市 → 牛市×1.0 / 震荡×0.7 / 熊市×0.4
- 统一 API：`/api/market-regime`

**风控（事前 8 项检查）**：
1. 信号 ID 去重（同一天同一信号不重复执行）
2. 乌龙指防护（单笔金额上限）
3. 日交易笔数限制
4. 涨跌停检查（涨停排队/QUEUE，跌停拒绝）
5. 信号等级最低阈值
6. 持仓总数上限
7. 资金检查
8. 单票集中度（超限→REDUCE）
- 板块 ≤30%，单票 ≤20%
- 日亏损熔断 -5%，撤单率 >50% 熔断
- 返回四元组：APPROVE / REJECT / REDUCE / QUEUE

**止盈止损**：
- ATR 动态止损（ATR×2，波动大放宽/波动小收紧）
- 三级移动止盈：盈利 ≥5% 触发→回落 1% 卖 1/3 → 盈利 ≥7%→回落 2% 再卖 1/3 → 盈利 ≥10%→回落 3% 清仓
- 涨停持仓不卖（除非回落 >3%）
- 硬止损：龙头票 10%，普通票 8%

**执行通道**：
- QMT passorder 快速通道（<5ms）
- Flask POST 审核通道（双道并行：快速执行 + 审核记录）
- 键盘快捷键 F1-F8：买/卖/撤单/涨停买/跌停卖/半仓/全仓
- 同花顺联动精灵（持仓读取 + 弹窗杀手）
- 🔒 实盘双锁：必须手动设 `real_confirmed=true` 才执行实盘交易

**数据管道**：
- 5 路径实时行情：Sina 批量 → TDX → QMT xtdata → akshare → baostock（多路径自动降级）
- 龙虎榜每日增量（lhb_fetcher.py）
- 北向资金因子（northbound_factor.py）
- SQLite 存储 + 定时备份 + 12 项数据治理

**前端与通知**：
- Flask 多页面 Web：仪表盘 / 复盘 / 情绪 / 配置
- Streamlit + Plotly 交互图表（app.py :8501）
- SSE 实时推送（信号→浏览器）
- 钉钉机器人：Webhook 推送 + Outgoing 指令解析（可远程控制）
- 统一 Dark Theme + nav_bar.js

**治理**：
- AI 工作宪法 v1.0
- 参数治理三级体系（唯一真相源 + 禁止硬编码 + 铁律）
- 防重机制三层（信号 ID / 日期 / 集合）
- 执行层交付清单 + 代码锁定（只可调参，不可改核心逻辑）
- 审计日志 audit_log.jsonl

#### 潜龙的短板（需要你的 AQF-T 来补）

1. **市场状态太粗**：只有牛市/震荡/熊市三档，看不出情绪。价格可能还在涨但市场情绪已经在退潮——我的系统捕捉不到这个。
2. **卖出缺乏策略驱动**：有 ATR 止损和移动止盈，但都是价格驱动的。如果"买入理由消失了"（比如炸板了、龙头结束了、题材死亡了），系统不会主动提醒卖出。
3. **决策不透明**：ML 模型输出一个分数，但不知道为什么打这个分。没有推理链。
4. **信号来源单一**：主要是 ML 打分 + TDX 公式。缺 AQF-T 那种回封板感知（炸板分类→回封确认→龙头判定）。
5. **没有证据体系**：今天为什么买 A？为什么没买 B？为什么卖 C？没有系统化的记录和归因。
6. **没有退出证据**：卖了就卖了，不做归因分析。

---

### 系统B：AQF-T (D:\AQF-T)

**GPT 设计、CC (Claude Code) 执行的系统。设计精良但缺真实数据。34/34 测试通过，纯模拟环境。**

#### 架构
```
Constitution(交易制度)
      ↓
Market Regime(总开关: 今天能不能做?)
      ↓
Data(QMT L2 + akshare)
      ↓
Perception(8层感知: 炸板/回封/对手/足迹...)
      ↓
Path A(回封板·规则)  Path B(半路/接力·ML)
      ↓                    ↓
      └────────┬────────────┘
               ↓
        Decision Core(融合/冲突消解/仓位分配)
               ↓
           Risk(合法?超仓?熔断?)
               ↓
        Execution(PaperBroker/未来QMT)
               ↓
        Knowledge Hub(归因+经验+Evidence)
               ↓
        ExitPipeline(策略退出: 炸板退出/龙头结束/题材死亡)
```

#### 关键资产

**市场状态**：
- 四阶段情绪周期：冰点期 / 回暖期 / 高潮期 / 退潮期
- 每阶段 → 自动映射操作模式：退潮=stop(禁止交易) / 冰点=defensive(10%仓位) / 回暖=cautious(50%) / 高潮=aggressive(70%)
- 双引擎交叉验证（RegimeEngine + SentimentEngine），矛盾时保守优先

**Path A — 回封板感知（潜龙没有的）**
- 板块地位评估（主线/次线/杂线）
- 炸板分类（洗盘 vs 诱多）
- 回封确认（缩量/快速/联动，≥2 个条件才进场）
- 龙头判定（Dragon 8 维打分）

**ExitPipeline（潜龙最大缺口）**
- E1 骨架：trigger→validate→priority→ExitOrder
- E2 Risk Exit：硬止损 / 回撤限制 / 退潮全清 / 熔断
- E3 Strategy Exit：炸板退出 / 龙头结束 / 题材死亡 / 依据失效
- E4 Exit Evidence：每笔退出记录完整证据

**Evidence 证据体系**
- Decision Record：上下文 + 证据 + 替代方案 + 条件
- Reasoning Trace：5 层推理链（为什么/为什么不/什么会改变）
- Outcome Evaluation：A-F 评级，t+n 天后回溯

**治理**
- Constitution V2.8.6 FROZEN（14 条边界宪法）
- Decision Log 结构化（背景 + 选项 + 结论 + 影响）
- Frozen 模块（不可修改，改动需 Review→新版本号）

**Runtime 保障**
- 7 模块：Supervisor / Recovery / PositionReconciler / KillSwitch / Idempotency / ConfigValidator / Logger

#### AQF-T 的短板
- 没有 QMT 连接，只有 PaperBroker 模拟
- 没有真实行情，只有 SimulatorProvider
- ML 模型只有框架，没训练过
- Dashboard 是单页 HTTP，非常简陋
- 没有钉钉、没有 Flask、没有移动端

---

## 三、硬约束（两个系统共同遵守）

**技术边界**：
- 单机 Windows + CPU only（无 GPU）
- SQLite（不引入 PostgreSQL/Redis）
- pip install（无 Docker）
- 无 LLM 本地推理（deepseek_enabled=false）
- ≤5 笔日交易，≤8 持仓

**设计红线**：
- AI 永远不直接下单（人工审批不可绕过）
- Risk 拥有最高否决权
- 不改 AQF-T Frozen 模块
- 不改潜龙执行通道

**协作模式**：
```
GPT(你) 设计 → 老板批复 → CC(Claude Code) 写代码落盘
CC 二次审计把关：蓝图对齐/安全可靠/进步验证/定位适配
```

---

## 四、我需要你设计什么

### 总体方案：决策增强层（Decision Augmentation Layer）

**核心理念**：AQF-T 是潜龙的副驾。不是替代，是增强。AQF-T 挂了，潜龙照常运行。

**三个增强点**：

```
潜龙现有链路：
  TDX信号 → ML评分 → 信号等级 → 仓位计算 → 风控 → QMT执行

增强后链路：
  TDX信号 → ML评分 → ⬆️ 增强点1 → 信号等级 → ⬆️ 增强点2 → 风控 → QMT执行 → ⬆️ 增强点3
                     市场状态增强              决策仲裁              退出管理增强
```

### 增强点 1：市场状态增强

AQF-T 四阶段情绪周期作为潜龙四因子模型的补充或替代。
输出：今日市场状态 + 置信度 + 操作建议（满仓/谨慎/轻仓/空仓）。

### 增强点 2：决策仲裁

融合潜龙 ML 评分 + AQF-T Path A/B 信号，输出最终决策。
规则：双共振=满仓 / 单方信号=半仓 / 任一否决=不交易 / Regime 退潮=覆盖一切。

### 增强点 3：退出管理增强

AQF-T ExitPipeline 的策略退出信号（炸板/龙头结束/题材死亡）与潜龙止盈止损并存。
谁先触发谁执行，互补不冲突。

---

### 需要你输出的具体设计

| # | 设计产出 | 说明 |
|---|----------|------|
| 1 | **统一信号 JSON Schema** | 两个系统都能输出的标准格式：symbol/action/confidence/position_pct/reasoning/source |
| 2 | **融合仲裁规则** | 潜龙信号 + AQF-T 信号 → 最终决策的完整规则表（不是投票，是证据加权） |
| 3 | **API 契约** | 潜龙调用 AQF-T 的端点设计：GET /regime, POST /decision/evaluate, GET /exit/check, GET /evidence |
| 4 | **降级策略** | AQF-T 不可用时，潜龙如何平滑回退（每个增强点的 fallback 逻辑） |
| 5 | **潜龙前端新增页面** | AQF-T 决策视图嵌入潜龙 Flask 的 UI 方案（页面布局/数据展示/交互设计） |
| 6 | **增强层目录结构** | 建议代码放哪里（D:\quant_framework\augmentation\ 或独立桥接目录） |

---

## 五、你可以参考的 AQF-T 设计文档

这些文档在 `D:\AQF-T\` 仓库中：

| 文档 | 路径 | 用途 |
|------|------|------|
| 系统宪法 | `02_Constitution/` | 理解边界和红线 |
| 市场状态设计 | `03_AI_Brain/Decision_Intelligence/AQFT_Decision_Intelligence_Architecture_V2.9.1.md` | 四阶段+行动映射 |
| 融合引擎 | `03_AI_Brain/Decision_Intelligence/AQFT_Decision_Fusion_Engine_Design_V1.0.md` | 多源证据融合 |
| 行动选择 | `03_AI_Brain/Decision_Intelligence/AQFT_Action_Selection_Engine_Design_V1.0.md` | 7级行动空间 |
| 退出管线 | `AQF-T_Production/exit/exit_pipeline.py` | ExitPipeline 完整代码 |
| 生产架构 | `AQF-T_Production/AQFT_PRODUCTION_FINAL.md` | 生产系统全貌 |
| 比对报告 | `00_AQFT_Knowledge_Hub/QIANLONG_VS_AQFT_BENCHMARK_V1.0.md` | 本文档 |
| CC 角色 | `00_AQFT_Knowledge_Hub/CC_ROLE_V2.md` | 理解执行约束 |

---

---

## 附录B：潜龙日常运行流程（GPT补全请求）

> 前面讲了潜龙"有什么模块"。这里讲潜龙"每天怎么工作"——对融合方案至关重要。

### 一天的完整时间线

```
08:30  启动系统
         ├── 潜龙一键启动.bat
         ├── Step 1: 杀掉旧进程（Flask 5002 / Streamlit 8501）
         ├── Step 2: 清理 Python 缓存（__pycache__/*.pyc）
         ├── Step 3: 校验 app.py 语法（validate_app.py，如有错自动修复）
         ├── Step 4: 启动 Flask（端口 5002，min 窗口）
         ├── Step 5: 等待 Flask 就绪（轮询 curl /screener，最多 60 秒）
         └── Step 6: 可选启动 Streamlit 仪表盘（--full 参数）

09:00  盘前检查
         ├── morning_checklist.py（09:20 执行）
         │   ├── Flask 服务是否响应
         │   ├── QMT 是否可连接
         │   ├── 数据文件是否存在（信号表/trade_plan/行情parquet）
         │   ├── 信号表是否今天生成的
         │   ├── 交易计划标的数是否正常
         │   └── 打印 PASS/FAIL/WARN 三色结果
         │
         └── pre_market_check.py（09:25 执行，10项检查）
             ├── QMT xtquant 是否可用 → 不可用则降级到 TDX
             ├── SQLite 数据库完整性（PRAGMA integrity_check）
             ├── 磁盘空间 >1GB
             ├── 行情数据新鲜度 <300秒
             ├── Flask 进程是否存活
             ├── 信号中心是否有数据
             ├── PaperAutoLoop 是否运行中
             ├── RuleEngine 规则是否加载
             ├── 昨日对账结果
             └── 备份状态

09:25  数据准备
         ├── 5路径实时行情启动：
         │   Sina API 批量获取（主路径）
         │   → 失败则 TDX 本地数据
         │   → 失败则 QMT xtdata
         │   → 失败则 akshare
         │   → 失败则 baostock
         │
         ├── TDX 公式扫描（tdx_signal_watcher.py）
         │   ├── 30秒轮询 custom_pools\*.txt
         │   ├── 解析通达信公式导出的选股结果
         │   ├── 写入 tdx_pool_stocks.json
         │   └── QMT 读取 → 查 auto_trade_plan 候选池
         │
         └── 龙虎榜增量更新（lhb_fetcher.py）
             └── 北向资金因子更新（northbound_factor.py）

09:30  盘中交易
         ├── 统一交易循环（trading_loop.py，10秒间隔）
         │   ├── 检查是否交易时段（9:25-11:30, 13:00-15:05）
         │   ├── 获取市场状态（market_state_classifier）
         │   ├── 运行 ML 模型：
         │   │   LGBM → 生成信号（min_score=30）
         │   │   XGBoost → 生成信号
         │   │   CatBoost → 如果模型文件存在则参与
         │   ├── Triple Vote：≥min_models(1) 同意 → 进入信号池
         │   ├── 5级信号映射仓位（Lv1=2% → Lv5=12%）
         │   ├── 仓位系数 × 市场系数（牛市1.0/震荡0.7/熊市0.4）
         │   ├── 风控检查（8项：信号ID去重/乌龙指/涨跌停/日笔数/…）
         │   ├── 返回 APPROVE/REJECT/REDUCE/QUEUE
         │   ├── APPROVE → QMT passorder 执行（<5ms）
         │   └── 写入 auto_trade_plan.json
         │
         ├── 盘中实时信号扫描（scan_live.py）
         │   ├── 盘前预筛：2000只 → 200只候选（价格/量/因子）
         │   ├── 订阅实时行情（只盯候选池）
         │   ├── 每3秒刷新报价
         │   └── 价格触及支撑位 → 告警
         │
         ├── 出场监控（auto_exit_monitor.py，5秒间隔）
         │   ├── 遍历持仓
         │   ├── 硬止损 ≤ -5.5% → 全卖
         │   ├── 软止损 ≤ -3% → 卖一半
         │   ├── 移动止盈：盈利≥5%触发回落1%卖1/3
         │   ├── 移动止盈：盈利≥7%触发回落2%再卖1/3
         │   ├── 移动止盈：盈利≥10%触发回落3%清仓
         │   └── 涨停持仓不卖（除非回落>3%）
         │
         ├── 实时推送（SSE，/api/stream）
         │   └── 信号/成交/拒绝 → 浏览器实时更新
         │
         └── 钉钉推送（dingtalk_alerts.py）
             ├── 成交通知（标的/价格/数量/时间）
             ├── 止损/止盈触发通知
             ├── 错误/异常告警
             └── 支持 Outgoing 指令解析（远程控制）

11:30  午休
         └── 交易循环自动暂停（非交易时段检查）

13:00  下午盘
         └── 交易循环自动恢复

15:00  收盘
         ├── 交易循环自动停止
         ├── 日终对账（daily_reconciliation.py）
         │   ├── 比较 3 个持仓源：
         │   │   SQLite trades.db
         │   │   paper_account.json
         │   │   live_positions_track.json
         │   └── 输出差异报告 + 漂移告警
         │
         ├── 日终报告（daily_report.py）
         │   └── 今日成交/拒绝/收益/持仓/归因
         │
         ├── IC 自动更新（ic_auto_update.bat）
         │   └── full_market_ic.py → full_market_ic_report.json
         │
         ├── 因子健康检查（factor_health.py）
         │   └── 因子 IC 衰减检测 → factor_health_log.jsonl
         │
         ├── 备份（backup_now.py / 一键备份.bat）
         │   ├── 关键 JSON 状态文件
         │   ├── trade_log.csv
         │   ├── factor_registry.json
         │   ├── paper_account.json
         │   └── 备份到 D:\backups\ + 百度云同步盘
         │
         └── Evidence/审计日志
             ├── audit_log.jsonl（每笔审批记录）
             ├── alerts.jsonl（告警历史）
             └── 百度云同步盘自动同步到云端
```

### 关键交互点（AQF-T 可以插入的地方）

```
时间点     潜龙当前动作              AQF-T 增强点
─────────────────────────────────────────────────────
09:00      morning_checklist         + AQF-T Regime 判断加入检查清单
09:25      四因子市场状态             ⬆️ 增强点1：替换为四阶段情绪周期
09:30      ML信号→5级→仓位           ⬆️ 增强点2：AQF-T Path A/B 参与仲裁
09:30-15:00 自动止盈止损              ⬆️ 增强点3：AQF-T ExitPipeline 策略退出
15:00      日终报告                   + AQF-T Evidence 证据归因
15:30      备份                       + AQF-T Decision Log 追加
```

### 潜龙的"启动方式"特性

- **手动启动**：双击 `.bat` 文件（不是 systemd/服务）
- **前台窗口**：Flask 和 Streamlit 开在独立的 min 窗口
- **关闭方式**：直接关掉 bat 窗口 → 所有进程被杀
- **重启方式**：`潜龙重启.bat` = 杀进程 + 清缓存 + 重新启动
- **外网访问**：`启动外网映射.bat` → localtunnel（qianlong.loca.lt）
- **强制重启**：`强制重启Flask.bat`（不清理缓存，直接杀+启）

### 潜龙的"容错"特性

- **QMT 不可用** → 自动降级到 TDX 数据
- **Flask 挂了** → `watchdog.py` 监控 + 钉钉告警 + 自动重启
- **数据源挂了** → 5 路径自动降级（Sina→TDX→QMT→akshare→baostock）
- **实盘双锁**：`real_confirmed=true` 才真正下单（防止误操作）
- **熔断机制**：KillSwitch 可手动/自动触发，触发后所有交易停止

---

*附录B：潜龙日常运行流程 — 2026-08-02 补充*
*此节专门回应 GPT 的"我还不知道潜龙真正每天是怎么工作的"请求*

---

## 附录C：信号→决策→风控→执行 完整调用链

> 回应 GPT 问题②③⑤：ML在哪里起作用、谁最终决定、真正的执行线程

### 调用链全景图

```
信号来源（并行运行）
├── TDX 公式信号
│   └── tdx_signal_watcher.py (30s轮询)
│       └── 解析 custom_pools\*.txt
│           └── 写入 tdx_pool_stocks.json
│               └── QMT 读取 → 匹配 auto_trade_plan
│
├── ML 三模型投票
│   └── triple_vote.py
│       ├── LGBM (lgbm_strategy.py, 模型: lgbm_model.pkl, IC=0.30)
│       ├── XGBoost (xgb_factor_weight.py, 模型: xgb_model.json)
│       └── CatBoost (train_catboost.py, 已退役, 自动跳过)
│           └── ≥min_models(1) 同意 → 进入信号池
│
├── V1-5 因子信号
│   └── factor_registry.py → get_active_factors()
│       └── realtime_quotes.py → 实时价格缓存
│           └── RuleEngine.check_buy_signal() → 因子评分
│
└── 信号中心聚合
    └── app.py /api/signal-center
        ├── FACTOR_CACHE (TDX + 因子信号)
        ├── signal_table.json (ML信号, 由 ml_daily_report.py 盘后生成)
        └── 统一输出: [{symbol, strategy, power_score, buy_signal, ...}]

                    ↓ 所有信号汇入

            统一交易循环 (trading_loop.py, 10s间隔)
                    ↓
        Step 1: 获取信号
            ├── 读 FACTOR_CACHE (内存, app.py 维护)
            ├── HTTP 兜底: curl /api/signal-center
            └── V1-5 因子注入 (_inject_v15_signals)
                    ↓
        Step 2: 决策适配 (decision_adapter.py)
            ├── B6: 市场状态检测 → 动态参数(仓位系数)
            ├── B5: HRP 风险平价仓位分配
            ├── B3: 行业敞口检查(超限丢弃)
            ├── B2: ATR 滑点调整买入价
            └── 输出: [{symbol, shares, price, position_pct, stop_loss}]
                    ↓
        Step 3: 风控检查 (paper_engine.auto_trade_check)
            └── 调用 live_trader.py 的 8 项检查:
                ├── 信号ID去重 (同一天不重复)
                ├── 乌龙指(单笔金额上限)
                ├── 涨跌停(涨停QUEUE, 跌停REJECT)
                ├── 日交易笔数
                ├── 信号等级最低阈值
                ├── 持仓上限
                ├── 资金检查
                └── 单票集中度
                    ↓
                返回: APPROVE / REJECT / REDUCE / QUEUE
                    ↓
        Step 4: 执行
            APPROVE → 写入 auto_trade_plan.json
                    → 根据 channel 配置:
                       ├── "qmt" → qmt_quick_trade.py → passorder()
                       └── "ths" → 联动精灵 → 同花顺
                    → 写入 trade_log.csv
                    → 写入 audit_log.jsonl
                    ↓
        Step 5: 推送
            ├── SSE → /api/stream → 浏览器实时更新
            ├── 钉钉 → dingtalk_alerts.py → Webhook 推送
            └── EventBus → 订阅者(如有)
```

### 谁最终决定买？

```
权重链（从高到低）：

1. 风控否决权(最高)
   └── PreTradeChecker 说 REJECT → 无条件不买
   └── KillSwitch 激活 → 全部停止
   └── 实盘双锁 real_confirmed=false → 全部 REJECT

2. 信号等级(Lv1-5)
   └── Lv5(12%) > Lv4(8%) > Lv3(6%) > Lv2(4%) > Lv1(2%)
   └── Lv1-2 在熊市可能被市场系数压到实际仓位=0

3. ML 和 TDX 的关系
   └── 不是"ML先选→TDX确认"也不是"TDX先选→ML过滤"
   └── 是"平行运行、各自出分、信号中心聚合、按power_score排序"
   └── 两个来源的信号可以同时在候选池中
   └── 最终谁买由 power_score 排序 + 仓位上限决定(前N只)
```

---

## 附录D：Position 生命周期

> 回应 GPT 问题④：买入后持仓如何管理

### 持仓的一天

```
T日 09:30  买入成交
    ├── paper_account.json 新增 position
    ├── trade_log.csv 记录买入
    └── position_tracker.json 更新

T日 盘中  持续监控 (auto_exit_monitor.py, 5s间隔)
    ├── 硬止损 -5.5% → 全卖
    ├── 软止损 -3% → 卖一半
    ├── 移动止盈 T1: 盈≥5% + 回落≥1% → 卖1/3
    ├── 移动止盈 T2: 盈≥7% + 回落≥2% → 再卖1/3
    ├── 移动止盈 T3: 盈≥10% + 回落≥3% → 清仓
    └── 涨停持仓不卖(除非回落>3%)

T日 15:00 收盘
    └── 持仓不变, 等次日

T+1日 09:25 集合竞价
    ├── 今开卖半: 如果开盘即跌(T+1卖半策略)
    └── 策略止盈: 如果达到止盈条件

T+1-T+6 盘中
    ├── RuleEngine 持续检查出场规则
    ├── 每日重新评分? → 否, 不重新评分
    ├── 每日重新排序? → 否, 不重新排序
    └── 动态仓位? → 否, 固定仓位, 只在卖出时调整

T+7日 持仓到期
    └── max_hold_days=7 → 强制清仓("持仓到期(7天≥7天)")

持仓结束
    └── paper_account.json 移除 position
    └── trade_log.csv 记录卖出+盈亏
```

### 关键差异 vs AQF-T

| | 潜龙 | AQF-T |
|---|---|---|
| 持仓重评 | ❌ 不重新评分 | ✅ 设计中有(但未实现) |
| 策略退出 | ❌ 只有价格驱动 | ✅ ExitPipeline 策略驱动 |
| 退出证据 | ❌ 只记日志 | ✅ E4 Exit Evidence |
| 生命周期 | 买入→持有→到期/止损 | Entry→Holding→Exit→Evidence |

**最大缺口**：潜龙没有"买入理由消失了所以应该卖"。只靠价格和天数管退出。

---

## 附录E：Flask 前端页面与数据来源

> 回应 GPT 补充请求④

### 页面清单

| 路由 | 页面名 | 数据来源 API |
|------|--------|-------------|
| `/` | 首页 | /api/summary |
| `/screener` | 选股器 | /api/screener/top_stocks, /api/screener/watchlist |
| `/dashboard` | 仪表盘 | /api/paper-trade/v2, /api/market-state, /api/risk-dashboard |
| `/live-trade` | 实盘交易 | /api/live-trade/status, /api/live-trade/positions, /api/live-trade/rules |
| `/risk-console` | 风控台 | /api/kill-switch/status, /api/risk/exposure, /api/emergency/status |
| `/trade-journal` | 交易日志 | /api/trade-journal, /api/trade-logs |
| `/review` | 复盘 | /api/attribution/daily, /api/strategy-replay |
| `/strategy-config` | 策略配置 | /api/strategies/available, /api/strategy-combo |
| `/strategy-market` | 策略市场 | /api/strategy-market |
| `/formula-manager` | 公式管理 | /api/formulas, /api/tdx-pools |
| `/factor-lab` | 因子实验室 | /api/factor-all, /api/factor/ic-analysis, /api/factor/registry |
| `/ml-signals` | ML信号 | /api/ml/signals-v3, /api/ml/stats |
| `/terminal` | 终端 | /api/signal-center, /api/signals/aggregate |
| `/command-center` | 指挥中心 | /api/unified-state, /api/system/overview |
| `/control-panel` | 控制面板 | /api/system/health, /api/paper-trade/auto-loop |
| `/data-manager` | 数据管理 | /api/data-manager |
| `/user-customizations` | 用户定制 | /api/user-customizations |
| `/quant-backtest` | 量化回测 | /api/quant-backtest |
| `/factor-dashboard` | 因子仪表盘 | /api/factor-importance, /api/factor/ic-trend |
| `/trading-dashboard` | 交易仪表盘 | /api/paper/status, /api/summary/today |

### 实时推送通道

| 通道 | 端点 | 用途 |
|------|------|------|
| SSE | `/api/stream` | 实时信号推送浏览器 |
| SSE | `/api/paper-trade/sse` | 模拟交易事件推送 |
| SSE | `/api/events` | 通用事件流 |
| SSE | `/api/link/stream` | 联动精灵事件 |

---

## 附录F：QMT 执行模块架构（职责划分）

> 回应 GPT 补充请求⑤：不是代码细节，是职责划分

### QMT 三件套

```
┌─────────────────────────────────────────────┐
│  qmt_broker.py (D:\quant_web)               │
│  角色: QMT 交易接口封装                       │
│  职责:                                       │
│    - XtQuant 连接管理 (connect/disconnect)    │
│    - 账户信息查询                             │
│    - 下单 (passorder via xttrader)           │
│    - 撤单 (cancel_order)                     │
│    - 持仓查询 (query_positions)              │
│    - 委托/成交回调处理                         │
│  不负责: 信号产生、风控决策、仓位计算            │
└─────────────────────────────────────────────┘
                      ↑
                      │ 调用
┌─────────────────────────────────────────────┐
│  qmt_quick_trade.py (D:\quant_framework)     │
│  角色: QMT 快速下单封装                        │
│  职责:                                       │
│    - 价格类型选择 (限价/市价)                   │
│    - 订单参数组装                             │
│    - 快速通道执行 (<5ms passorder)             │
│    - 返回成交确认                              │
│  不负责: 该不该买、买多少                        │
└─────────────────────────────────────────────┘
                      ↑
                      │ 调用
┌─────────────────────────────────────────────┐
│  live_trader.py (D:\quant_framework)         │
│  角色: 实盘交易总控                            │
│  职责:                                       │
│    - 合并三个执行通道:                          │
│      QMT(程序化) + Flask(审核) + 键盘(手动)     │
│    - 自动交易开关 (auto_trade_enabled)          │
│    - 实盘双锁 (real_confirmed)                 │
│    - 键盘快捷键绑定 (F1-F8)                    │
│    - 同花顺联动精灵管理                         │
│  不负责: 信号产生 (只消费信号)                   │
└─────────────────────────────────────────────┘
```

### QMT 数据读取（与执行分离）

```
qmt_data_provider.py (D:\quant_framework)
  角色: QMT 行情/数据读取
  职责:
    - xtdata.get_market_data() 行情获取
    - Level-2 数据 (逐笔/十档)
    - 板块/指数数据
    - 财务数据
  不负责: 交易执行
```

---

## 附录G：对 GPT "Decision Interface" 概念的回应

GPT 提出：

```
潜龙 (Execution Platform)
        ▲
        │
  Decision Interface (信号标准化/决策请求/Evidence返回/降级)
        ▲
        │
  AQF-T (Decision OS)
```

**CC 评价**：✅ 这个方向比原来的"桥接层"更好。

**原因**：

1. **解耦更彻底** — 不是 AQF-T ↔ 潜龙 的点对点桥接，而是"决策接口"标准化后，任何决策引擎(未来第三个也行)都可以接
2. **降级更安全** — Decision Interface 自带降级逻辑（AQF-T不可用→潜龙自决），而不是让调用方自己处理
3. **证据回流** — Decision Interface 不只是"请求→回复"，还负责把执行结果(成交/退出/盈亏)回传给 AQF-T，形成 Evidence 闭环
4. **符合冻结策略** — 两边代码都不改，只加一个独立层

**建议设计要点**：

| 接口方法 | 方向 | 职责 |
|----------|:--:|------|
| `GET /decision/regime` | 潜龙→AQF-T | 获取今日市场状态+操作模式 |
| `POST /decision/evaluate` | 潜龙→AQF-T | 传入候选信号，返回增强决策 |
| `POST /decision/exit-check` | 潜龙→AQF-T | 传入持仓，返回策略退出建议 |
| `POST /evidence/record` | AQF-T→潜龙 | AQF-T 无法直接写盘时，通过潜龙记录证据 |
| `POST /execution/feedback` | 潜龙→AQF-T | 成交/退出结果回传，供 AQF-T 学习 |
| `GET /health` | 双向 | 健康检查，决定是否降级 |

---

*附录C-G：潜龙深度补充 — 2026-08-02*
*覆盖 GPT 五项请求：①运行流程图 ②调用链 ③Position生命周期 ④前端页面 ⑤QMT架构*
*增加 GPT Decision Interface 概念确认*
