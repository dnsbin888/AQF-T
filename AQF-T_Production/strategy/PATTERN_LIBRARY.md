# Pattern Library — 游资模式库


**定位:** 游资战法规则化, 统一输入输出, 可单独回测验证
**原则:** 全部规则, 零AI, 零新模块


---

## 已有模式 (直接可用)

```
情绪周期    ✅ 冰点/回暖/高潮/退潮 + 情绪值公式
龙头8维     ⚠️ 6/8 (缺领涨性+唯一性)
梯队模型    ✅ LadderScore (P0已补)
龙头生命周期 ✅ 8阶段 (P0已补)
回封/分歧转一致 ✅ Path A 核心
卡位博弈    ✅ PositionAnchor (P0已补)
龙头淘汰    ✅ LeaderInvalid (P0已补)
```

## 待补模式

```
P0 领涨性 ✅ 已补 (同板块最早封板→1.0)
P0 唯一性 ✅ 已补 (板块内最高连板→1.0)

P1 相对强度 (RelativeStrength):
  RS_market:  个股vs大盘 (大盘跌+个股抗跌→龙头确认)
  RS_sector:  个股vs板块 (板块弱+个股强→独立走势)
  RS_leader:  个股vs龙头 (跟风vs龙头→身位判断)
  全部规则, 不需要AI

P1 板块轮动 (SectorFlow):
  资金流入强度 / 涨停家数变化 / 高低切换检测

P1 接力强度 (RelayStrength):
  封板持续率 / 梯队完整率 / 接力成功率

P2 弱转强规则化:
  前日弱+竞价强+开盘承接+放量突破 → 信号
```

## 统一接口

```
每个Pattern输出标准Candidate字段:

  pattern:     模式名称
  score:       评分 0-1
  confidence:  置信度
  evidence:    证据链 (可审计)
  regime_fit:  适用情绪周期
```

---

**全部规则, 零AI, 可单独回测验证, 不修改主链。**
