# AQF-T System Map


# AQF-T 系统全景图


Version: V2.8.6 → V3.0.0 Bridge
Updated: 2026-07-26

---

## 完整架构层次

```
AQF-T Intelligence Trading System
│
├── 00_AQFT_Knowledge_Hub          ← 知识管理中心（本层）
│   ├── INDEX.md                   ← 总入口
│   ├── SYSTEM_MAP.md              ← 本文件
│   ├── MODULE_REGISTRY.md         ← 模块注册
│   ├── AI_CONTEXT.md              ← AI上下文
│   └── VERSION_CONTROL.md         ← 版本治理
│
├── 00_Project                     项目管理
│   ├── AQFT_Document_Index.md
│   ├── AQFT_Project_Roadmap_V2.8.6.md
│   ├── AQFT_Version_Control_V2.8.6.md
│   └── AQFT_Development_Plan_V2.8.6.md
│
├── 01_Architecture                系统架构层
│   ├── 01_System_Architecture     ✅
│   ├── 02_Data_Flow               ✅
│   ├── 03_Module_Architecture     ✅
│   └── 04_Deployment_Architecture ✅
│
├── 02_Constitution                系统宪法 ✅
│
├── 03_AI_Brain                    AI智能核心 ✅
├── 04_Strategy                    策略体系 ✅
├── 05_Risk                        风险控制 ✅
├── 06_Execution                   交易执行 ✅
├── 07_Data                        数据体系 ✅
├── 08_Parameter                   参数治理 ✅
├── 09_Test                        测试验证 ✅
├── 10_Engineering                 软件工程 ✅
├── 11_AI_Implementation           AI工程实现 ✅
├── 12_Data_Engineering            数据工程 ✅
├── 13_Code_Framework              代码框架 ✅
│
├── 14_Runtime                     P3 运行系统 ✅
├── 15_Data_Runtime                ✅
├── 16_AI_Runtime                  ✅
├── 17_Strategy_Runtime            ✅
├── 18_Risk_Runtime                ✅
├── 19_Execution_Runtime           ✅
├── 20_Simulation_System           ✅
├── 21_Production_Runtime          ✅
│
├── 22_Evolution_System            P4 自进化 ✅
│
├── 23_Agent_Intelligence_System   P5 多智能体 ✅
├── 24_World_Model_System          P5 世界模型 ✅
│
├── 99_Archive                     历史归档
│
├── ai_brain/                      代码骨架
├── strategy/                      代码骨架
├── risk/                          代码骨架
├── execution/                     代码骨架
├── data/                          代码骨架
├── parameter/                     代码骨架
├── test/                          代码骨架
├── config/                        配置中心
├── src/                           核心代码
├── scripts/                       工具脚本
└── logs/                          运行日志
```

## 数据流闭环

External Data → Data Runtime → AI Runtime → Strategy Runtime → Risk Runtime → Execution Runtime → Simulation → Production → Monitoring → Optimization → Learning → Decision → Knowledge → Governance → Evolution → (back to AI Runtime)

---

*维护规则：模块新增/删除/变更时，必须同步更新本文件。*
