# AQF-T Experience Intelligence Architecture

Version: V1.0.0 | Status: ARCHITECT REVIEW PASSED — Phase 1 Experience Loop Enabled
Phase: V3.0 Phase 1 — Experience Layer | Module: 06_Experience_Intelligence
Created: 2026-07-28

---

## 1. Purpose

Upgrades Observation Intelligence to **Experience Intelligence** — transforming raw execution facts into structured trading experience.

```
Observation (P1-001):  "What happened?"
Experience (P1-002):   "What does this experience mean?"
```

## 2. Architecture

```
Observation Intelligence → EXPERIENCE INTELLIGENCE → Memory System → Evolution
         (facts)                (meaning)              (store)       (improve)
```

## 3. Four Sub-Modules

| Module | Question | Output |
|--------|----------|--------|
| Episode Model | What is a complete trading experience? | TradingEpisode |
| Pattern Extractor | What patterns emerge from episodes? | ExperiencePattern |
| Knowledge Router | Which patterns become knowledge? | KnowledgeCandidate |
| Memory Integration | How to store and retrieve? | Memory → Evolution feed |

## 4. Episode Definition

A TradingEpisode is NOT just "buy → profit". It is the complete lifecycle:

`MarketContext + DecisionContext + ExecutionContext + OutcomeContext + ReflectionContext`

## 5. Principle

Experience describes patterns. It does NOT auto-modify strategies. C-002: Immutable Core respected.

## 6. Deliverables

```
06_Experience_Intelligence/
├── 01_Experience_Architecture/    ← This document
├── 02_Episode_Model/
├── 03_Pattern_Extractor/
├── 04_Knowledge_Router/
└── 05_Memory_Integration/
```
