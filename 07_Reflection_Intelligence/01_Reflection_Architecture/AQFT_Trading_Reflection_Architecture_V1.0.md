# AQF-T Trading Reflection Architecture

Version: V1.0.0 | Status: ENGINEERING DRAFT — Awaiting Architect Review
Phase: V3.0 Phase 1 | Module: 07_Reflection_Intelligence
Created: 2026-07-28

---

## 1. Purpose

Reflection Intelligence 是 AQF-T 的 **交易后认知反馈层**。

P1-001 记录事实。P1-002 保存经历。P1-003 理解原因。

```
P1-001: "What happened?"       → ExecutionReport
P1-002: "What was the experience?" → TradingEpisode  
P1-003: "Why? What to learn?"  → Reflection → Knowledge
```

## 2. Pipeline

```
ExecutionReport → TradingEpisode → Outcome Analyzer → Reflection Engine → LearningProposal → Memory
```

## 3. Core Principle: Decision Quality ≠ Trading Result

专业交易系统区分：Good Decision/Bad Outcome vs Bad Decision/Good Outcome。不被单次盈亏误导。

## 4. Constitution

C-001/C-002 respected. Reflection proposes. Human governs. C-009 candidate.

## 5. Deliverables

```
07_Reflection_Intelligence/
├── 01_Reflection_Architecture/  ← This document
├── 02_Decision_Outcome_Model/
├── 03_Error_Attribution_Engine/
├── 04_Counterfactual_Review/
└── 05_Knowledge_Update_Interface/
```
