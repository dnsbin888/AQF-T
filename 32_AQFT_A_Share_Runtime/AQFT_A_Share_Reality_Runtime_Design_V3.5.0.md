# AQFT A-Share Reality Runtime V3.5.0
# AQF-T A股现实世界接入层设计

Version: V3.5.0 | Status: Runtime Engineering | Date: 2026-07-26

## 定位

V3.4.0: AQF-T 会学习进化（但学的是模拟数据）
V3.5.0: AQF-T 看见真实的A股市场

## 核心原则

不推翻现有架构。在 V3.1-V3.4 智能链基础上，将 Market Data Feed 从模拟替换为真实A股数据。

## 架构

QMT/xtquant → Market Gateway → Event Bus → World Model → Agent → Decision → Risk → Simulation (A-share rules) → Execution

## 新增能力

- A股实时行情 (tick/分钟/日线)
- T+1 买卖限制
- 涨跌停 (±10% / ±20% / ±5%)
- 真实手续费 (印花税0.1% + 佣金0.025% + 过户费0.001%)
- 最小交易单位 100股
- A股交易日历
