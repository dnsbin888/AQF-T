# AQF-T Architecture Reconciliation Plan V3.6.0


# AQF-T 架构归并计划 — 从双轨回到单轨


Version: V3.6.0
Type: Architecture Governance
Date: 2026-07-26


---

## 一、问题诊断

AQF-T 当前存在两套平行体系：

**世界A — 设计体系 (V2.8.6)**
- 03_AI_Brain → 04_Strategy → 05_Risk → 06_Execution → 07_Data
- 7份设计文档，架构完整
- **0行Python代码**

**世界B — 运行体系 (V3.x)**
- 28_Runtime → 29_Intelligence → 30_Execution → 31_Learning → 32_AShare
- 21个Python文件，17个可运行服务
- **无对应P1设计文档**

根因：V3.x是为了快速验证运行闭环产生的"实验分支"，但没有回归主架构。

---

## 二、归并策略

不删除V3.x代码。将V3.x代码迁移回V2.8.6设计体系，建立追溯链。

## 三、架构映射表 (Code → Design)

| V3.x 代码位置 | 迁移目标 (P1设计) | 当前状态 | 归并动作 |
|--------------|------------------|:---:|------|
| 28/agent_service | 23_Agent_Intelligence_System | 硬编码 | 迁移+保留 |
| 28/world_model_service | 24_World_Model_System | 硬编码 | 迁移+替换 |
| 28/decision_service | 25_Decision_Intelligence_System | 硬编码 | 迁移+替换 |
| 28/risk_service | 05_Risk + 18_Risk_Runtime | Kill Switch正确 | 迁移+增强 |
| 28/memory_service | 31_Learning_Intelligence | 内存存储 | 迁移+持久化 |
| 29/event_bus | 28_Distributed_Runtime | ✅ 保留 | 提升为基础设施 |
| 29/intelligence_pipeline | 25_Decision_Intelligence | ✅ 保留 | 映射回P5-03 |
| 29/data_pipeline | 07_Data + 32_AShare | 模拟数据 | 替换为真实 |
| 30/execution_engine | 06_Execution + 19_Execution_Runtime | 模拟成交 | 迁移+A股规则 |
| 30/simulation_engine | 20_Simulation_System | 随机成交 | 升级为事件驱动 |
| 30/portfolio_manager | 08_Parameter | ✅ 保留 | 映射回P1-08 |
| 31/experience_engine | 22_Evolution_System | ✅ 保留 | 映射回P4 |
| 31/evaluation_engine | 22_Evolution_System | ✅ 保留 | 映射回P4 |
| 31/reinforcement_runtime | 22_Evolution_System | Q-table | 映射回P4 |
| 31/strategy_memory | 22_Evolution_System | JSON持久化 | 映射回P4 |
| 31/pattern_mining | 22_Evolution_System | 规则发现 | 映射回P4 |
| 31/knowledge_graph | 22_Evolution_System | 因果图 | 映射回P4 |
| 31/model_evolution | 22_Evolution_System | 策略进化 | 映射回P4 |
| 31/experiment_engine | 22_Evolution_System | 实验沙盒 | 映射回P4 |
| 32/qmt_adapter | 07_Data | akshare fallback | 保留+增强 |
| 32/ashare_rules | 20_Simulation_System | T+1/涨跌停/费率 | 保留 |

---

## 四、归并后的目录结构

```
AQF-T/
├── 02_Constitution/                    (不变)
├── 01_Architecture/                    (不变)
│
├── 03_AI_Brain/                        ← 从V3.0.x迁移
│   ├── AQFT_AI_Brain_Design_V3.6.0.md  ← 升级到15KB+详细设计
│   └── prediction/                     ← 真实模型代码
│
├── 04_Strategy/                        ← 恢复
├── 05_Risk/                            ← 从28/risk_service迁移
│   └── risk_engine.py
│
├── 06_Execution/                       ← 从30/execution_engine迁移
│   └── execution_engine.py
│
├── 07_Data/                            ← 从29/data_pipeline迁移
│   └── data_pipeline.py
│
├── 14_Runtime/                         ← Runtime Foundation
├── 22_Evolution_System/                ← 从31/迁移全部8个服务
├── 23_Agent_System/                    ← 从28/agent_service迁移
├── 24_World_Model/                     ← 从28/world_model迁移
├── 25_Decision_Intelligence/           ← 从28/decision迁移
├── 28_Infrastructure/                  ← EventBus + Registry保留
├── 32_AShare_Runtime/                  ← 保留
│
└── 99_Archive/
    └── V3.0_Deprecated_Dirs/           ← 28/29/30/31旧目录归档
```

---

## 五、执行步骤

| Phase | 内容 | 工作量 |
|:---:|------|:---:|
| 1 | 核心设计文档深度升级 (03/05/07 → 15KB+) | 2天 |
| 2 | V3.x代码迁移到P1模块目录 (不改代码逻辑) | 1天 |
| 3 | 验证迁移后服务仍可启动 | 0.5天 |
| 4 | V3.x旧空目录归档到99_Archive | 0.5天 |

---

## 六、归并完成标准

- [ ] 每个V3.x代码文件有对应的P1设计模块
- [ ] 03_AI_Brain/05_Risk/06_Execution至少各有一个.py
- [ ] 核心设计文档从3KB升级到15KB+
- [ ] 旧V3.x目录归档，根目录恢复V2.8.6结构
- [ ] 服务仍可启动

---

*V3.6.0不是功能版本，是架构归并版本。从这里开始，设计和代码回到同一棵树上。*
