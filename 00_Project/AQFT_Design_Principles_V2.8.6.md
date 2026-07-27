# AQF-T Design Principles

Version: V2.8.6
Date: 2026-07-27
Status: ✅ FINAL — Architecture Rebaseline
Applies to: All V2.9+ module designs

---

## Core Principle

**Optimize for intelligence depth, not document quantity.**

---

## Six Review Gates

Every module design must pass all six gates before Freeze.

### Gate 1: Architecture Review

| Check | Question |
|-------|----------|
| Consistency | Does this module align with the system architecture? |
| Non-duplication | Does any existing module already cover this? |
| Constitution compliance | Does it violate any constitutional principle? |
| Placement | Is it in the correct phase / layer? |

### Gate 2: Dependency Review

| Check | Question |
|-------|----------|
| Upstream | Are all dependencies declared? |
| Downstream | Which modules depend on this one? |
| Circular | Any circular dependencies introduced? |
| Runtime | Does the runtime dependency chain hold? |

### Gate 3: Interface Review

| Check | Question |
|-------|----------|
| Input contract | Input format / schema defined? |
| Output contract | Output format / schema defined? |
| Compatibility | Compatible with existing interfaces? |
| Versioning | Interface versioned? |

### Gate 4: Engineering Specification Review

| Check | Question |
|-------|----------|
| Concreteness | Specific enough to implement? |
| Completeness | All edge cases addressed? |
| Data structures | Key data structures defined? |
| Algorithms | Core algorithms specified? |

### Gate 5: Implementation Readiness Review

| Check | Question |
|-------|----------|
| Prerequisites | All prerequisite modules frozen? |
| Dependencies | All dependency modules available? |
| Testability | Can this be tested independently? |
| Deployability | Can this be deployed incrementally? |

### Gate 6: Freeze Review

| Check | Question |
|-------|----------|
| Version | Version number assigned? |
| Documentation | FINAL document complete? |
| Index | Document Index updated? |
| Baseline | Git tag created? |

---

## Freeze Rules

1. **Frozen = Immutable.** Never overwrite a frozen document.
2. **Change requires Review.** Any post-freeze change → Architecture Review → Revision → new version.
3. **One source of truth.** ChatGPT is the sole design authority.
4. **Claude executes only.** Engineering Executor does not design, modify, or optimize.

---

## Design Workflow

```
Requirement
    │
    ▼
Gate 1: Architecture Review ──→ Pass/Fail
    │
    ▼
Gate 2: Dependency Review ────→ Pass/Fail
    │
    ▼
Gate 3: Interface Review ─────→ Pass/Fail
    │
    ▼
Gate 4: Engineering Spec ─────→ Pass/Fail
    │
    ▼
Gate 5: Implementation Readiness → Pass/Fail
    │
    ▼
FINAL Design
    │
    ▼
Claude Save + Index + Freeze
    │
    ▼
Gate 6: Freeze Review ────────→ FROZEN
```

---

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|------|
| Design and code in parallel | Design first, code after Freeze |
| Modify frozen docs silently | Review → Revision → New version |
| Two AIs designing same module | ChatGPT only — single source of truth |
| Skip review for "small" changes | All changes go through gates |
| Add modules without dependency check | Full dependency review every time |
| Optimize for document count | Optimize for intelligence depth |

---

*AQF-T Design Principles — V2.8.6 Architecture Rebaseline*
