# Dashboard Backlog — Post-AVP Enhancements

> 2026-08-09 创建 | 2026-08-09 更新 (v1.2 完成 + 潜龙融合方案)
> AVP 期间不实现，8/19 后评估优先级。

---

## ✅ 已完成 (v1.2)

| 项目 | 说明 | 完成日 |
|------|------|:--:|
| Sensor 摘要行 | 资金环境/环境置信/市场信号/情绪 → 融入四列卡片 | 08-09 |
| `/api/sensor` + `/api/sensor/summary` | 两个只读端点 | 08-09 |
| Dashboard 布局重构 | 状态条 + 四列卡片 + 卡片去重 | 08-09 |

---

## 📋 Pending — AQF-T 自身

### P2: 五 Sensor 健康灯

```
✅ Margin | ✅ Institution | ✅ ETF | ✅ Southbound | ✅ Sentiment
```

每个 Sensor 的 error 状态映射为红绿灯。当前只在 latest_sensor.json 中有原始数据，前端未展示。

### P2: 情绪状态指示器增强

当前已有情绪 extreme + velocity 显示，可增加可视化（温度计/仪表盘）。

### P3: Evidence Table 页面

独立 Tab 或 `/evidence` 路由，表格式展示 evidence_table.csv，支持简单筛选。当前 CSV 可直接用 Excel 打开。

### P3: REST API 扩展

| 端点 | 功能 | 数据源 |
|------|------|--------|
| `GET /api/evidence/latest` | 最新 Evidence 行 | evidence_table.csv |
| `GET /api/evidence/range?from=&to=` | 日期范围查询 | evidence_table.csv |

---

## 🔗 潜龙 ↔ AQF-T 前端融合方案

> 2026-08-09 方案设计，Post-AVP (8/19后) 实施。

### 背景

潜龙和 AQF-T 各有独立前端，功能互补不重叠：

| | 潜龙 | AQF-T |
|---|---|---|
| 框架 | Flask + Jinja2 SSR | Python http.server |
| 端口 | 5002 | 8080 |
| 规模 | 200+ 路由, 30+ 模板 | 3 端点, 单页 |
| 功能 | 选股/回测/因子/信号/风控/交易 | 健康监控/regime/sensor/持仓 |
| 定位 | 研究→信号→执行 | 运行时监控台 |

两者加起来才是完整闭环：**潜龙管战斗，AQF-T 管战场**。

### 方案: API 驱动融合 (推荐)

```
潜龙 (Flask, :5002)
  └── templates/aqft_monitor.html   ← 新增页面
       ├── fetch(:8080/api/sensor/summary)
       ├── fetch(:8080/health)
       └── 用潜龙 unified.css 渲染
       
AQF-T (http.server, :8080)
  └── dashboard.py                  ← 一行不改，纯 API 数据源
```

### 实施步骤

1. **`D:\quant_web\templates\aqft_monitor.html`** — 新建页面
   - 用 Fetch API 读 AQF-T 三个端点
   - 渲染状态条 + 四列卡片 + 持仓/信号/成交表格
   - 复用潜龙暗色 CSS（`unified.css`），保持视觉一致
   - 30 秒自动刷新

2. **`D:\quant_web\app.py`** — 加一个路由
   ```python
   @app.route("/aqft")
   def aqft_monitor():
       return render_template("aqft_monitor.html")
   ```

3. **`D:\quant_web\templates\_topbar.html`** — 导航栏加入口
   ```html
   <a href="/aqft">AQF-T 监控</a>
   ```

### 设计原则

- **独立进程，互不依赖** — AQF-T 挂了潜龙不受影响，反之亦然
- **AQF-T 不改一行** — 纯作为数据源，现有 dashboard.py 保持原样
- **API 优先** — 页面只消费 API，不直接读文件
- **视觉统一** — 复用潜龙 CSS，但保留 AQF-T 的信息架构（状态条 + 四列）

### 风险评估

| 风险 | 缓解 |
|------|------|
| AQF-T 未启动时 API 不可达 | 页面显示 "AQF-T 离线"，不影响潜龙其他功能 |
| CORS (跨端口 fetch) | Flask 端加 `Access-Control-Allow-Origin` header |
| 数据格式变更 | API 版本化或前端做兼容处理 |

### 时间估算

| 步骤 | 工作量 |
|------|:--:|
| aqft_monitor.html 页面 | 1 天 |
| Flask 路由 + CORS | 0.5 天 |
| 导航栏入口 | 0.5 天 |
| 测试 + 样式打磨 | 1 天 |
| **合计** | **3 天** |

---

## 优先级总表 (Post-AVP)

| 优先级 | 项目 | 理由 |
|:--:|------|------|
| P1 | 🔗 潜龙融合 | 最大体验提升，统一入口 |
| P2 | 五 Sensor 健康灯 | Dashboard 完整性 |
| P2 | 情绪指示器增强 | 可视化提升 |
| P3 | Evidence Table 页面 | 当前 CSV 可代替 |
| P3 | 扩展 REST API | 按需添加 |

---

## AVP 期间规则

- ❌ 不实现任何上述功能
- ✅ 此文件仅作为记录 + 方案设计，防止丢失
