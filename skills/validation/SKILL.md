---
name: validation
description: Unified validation orchestration for code quality, consistency, and project health. Auto-triggers on code changes, PR creation, or explicit validation requests. Coordinates refining, housekeeping, and custom validators into cohesive pipelines. Use for "validate", "check", "verify", "验证", "检查", or when quality assurance is needed.
---

# Validation

Unified validation orchestration that coordinates all quality checks into cohesive pipelines.

## Philosophy

**Validation is not a gate—it's a continuous feedback loop.**

Traditional validation: Code → Gate → Pass/Fail
This validation: Code → Insight → Learn → Improve → Code

### The Iron Law

> **NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.**

Before asserting work is done, fixed, or passing—verify with fresh evidence. No exceptions.

See [reference/verification-gate.md](reference/verification-gate.md) for the 5-step protocol.

### Defense-in-Depth

Four validation layers, each catching what others miss:

| Layer | Purpose | Example |
|-------|---------|---------|
| 1. Entry Point | Reject invalid input | Missing fields, wrong format |
| 2. Business Logic | Enforce domain rules | Cohesion, size, breaking changes |
| 3. Environment | Prevent unsafe operations | Force push, missing tools |
| 4. Instrumentation | Capture evidence | Metrics, logs, patterns |

See [reference/defense-in-depth.md](reference/defense-in-depth.md) for details.

## Core Concepts

### Validation Pipeline

A pipeline is an ordered sequence of validators that run together:

```
┌─────────────────────────────────────────────────────────┐
│                    VALIDATION PIPELINE                  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐ │
│  │ Syntax  │ → │ Quality │ → │ Security│ → │ Custom  │ │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘ │
│       ↓             ↓             ↓             ↓       │
│  ┌─────────────────────────────────────────────────────┐│
│  │              VALIDATION REPORT                      ││
│  │  • Issues found (with severity)                     ││
│  │  • Suggestions for improvement                      ││
│  │  • Patterns detected                                ││
│  └─────────────────────────────────────────────────────┘│
│       ↓                                                 │
│  ┌─────────────────────────────────────────────────────┐│
│  │              MEMORY PERSISTENCE                     ││
│  │  .memory/validations/YYYY-MM-DD-context.md          ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Validation Levels

| Level | When | Validators | Time |
|-------|------|------------|------|
| **Quick** | Every save, small changes | Syntax, basic quality | <10s |
| **Standard** | Before commit, medium changes | + Security, consistency | <1min |
| **Comprehensive** | Before PR, major changes | + Impact, architecture | <5min |

### Built-in Validators

| Validator | Checks | Source |
|-----------|--------|--------|
| **reviewability** | Cohesion, size, noise | refining |
| **impact** | Blast radius, breaking changes | refining |
| **consistency** | Index alignment, doc freshness | housekeeping |
| **security** | OWASP top 10, secrets, injection | refining |
| **architecture** | Patterns, boundaries, coupling | engineering |

## Auto-Trigger Rules

Validation auto-triggers based on context:

| Context | Pipeline | Rationale |
|---------|----------|-----------|
| `git add` (staged changes) | quick | Fast feedback before commit |
| "commit" / "提交" | standard | Ensure commit quality |
| "PR" / "MR" / "pull request" | comprehensive | Full validation for review |
| "validate" / "verify" / "检查" | standard | Explicit request |
| Session end | quick | Catch uncommitted issues |

## Workflow

### 1. Detect Context

Determine what to validate and which pipeline to use:

```
Context Detection
├── Explicit request? → Use requested level
├── PR/MR related? → comprehensive
├── Commit related? → standard
├── Code changed? → quick
└── Default → standard
```

### 2. Run Pipeline

Execute validators in order, collecting results:

```
For each validator in pipeline:
  1. Run validator
  2. Collect findings (issues, suggestions, patterns)
  3. If critical issue found → option to stop early
  4. Continue to next validator
```

### 3. Generate Report

Produce structured validation report:

```markdown
# Validation Report

**Context**: [what was validated]
**Pipeline**: [quick/standard/comprehensive]
**Time**: [execution time]

## Summary
- 🔴 Critical: N issues
- 🟡 Important: N issues
- 🔵 Suggestions: N items
- ✅ Passed: N checks

## Findings

### Critical (🔴)
[Must fix before proceeding]

### Important (🟡)
[Should address]

### Suggestions (🔵)
[Consider for improvement]

## Patterns Detected
[Recurring issues or positive patterns]

## Recommended Actions
[Prioritized next steps]
```

### 4. Persist Results

Record validation results for learning:

```
.memory/
└── validations/
    └── YYYY-MM-DD-context.md
```

See [reference/persistence.md](reference/persistence.md) for format.

## Collaboration with Other Skills

Validation orchestrates, doesn't replace:

| Skill | Validation Delegates To |
|-------|------------------------|
| refining | Reviewability gate, impact analysis |
| housekeeping | Consistency checks, doc health |
| engineering | Architecture validation |
| memory | Persist findings, track trends |

```
User Request
    │
    ▼
validation (orchestrate)
    │
    ├──► refining (reviewability, impact)
    ├──► housekeeping (consistency)
    ├──► engineering (architecture)
    │
    ▼
validation (aggregate results)
    │
    ▼
memory (persist findings)
```

## Quick Commands

| Command | Action |
|---------|--------|
| "validate" | Run standard pipeline on staged/changed files |
| "validate quick" | Run quick pipeline |
| "validate comprehensive" | Run full pipeline |
| "validate [file/dir]" | Validate specific target |
| "validation report" | Show recent validation results |
| "validation trends" | Analyze validation history |

## Pipeline Configuration

Customize pipelines per project in `.validation.yml`:

```yaml
# .validation.yml
pipelines:
  quick:
    validators: [syntax, lint]
    timeout: 10s

  standard:
    validators: [syntax, lint, security, reviewability]
    timeout: 60s

  comprehensive:
    validators: [syntax, lint, security, reviewability, impact, architecture]
    timeout: 300s

custom_validators:
  - name: domain-rules
    command: ./scripts/validate-domain.sh
    severity: important
```

## Validation Feedback Loop

The system learns from validation results:

```
┌────────────────────────────────────────────────────────┐
│                   FEEDBACK LOOP                        │
│                                                        │
│  Validate → Record → Analyze → Learn → Prevent        │
│      ↑                                    │            │
│      └────────────────────────────────────┘            │
│                                                        │
│  Example:                                              │
│  1. Detect "console.log left in code" 3x this week   │
│  2. Record pattern in .memory/validations/            │
│  3. Analyze: common before commits                    │
│  4. Learn: add to quick pipeline                      │
│  5. Prevent: catch earlier next time                  │
└────────────────────────────────────────────────────────┘
```

See [reference/feedback-loop.md](reference/feedback-loop.md) for details.

## Reference

**Core Concepts**:
- [reference/verification-gate.md](reference/verification-gate.md) - The Iron Law and 5-step protocol
- [reference/defense-in-depth.md](reference/defense-in-depth.md) - Four-layer validation strategy

**Configuration**:
- [reference/validators.md](reference/validators.md) - Built-in validator details
- [reference/pipelines.md](reference/pipelines.md) - Pipeline configuration
- [reference/custom-validators.md](reference/custom-validators.md) - Creating custom validators

**Learning**:
- [reference/persistence.md](reference/persistence.md) - Result persistence format
- [reference/feedback-loop.md](reference/feedback-loop.md) - Learning from validation

**Templates**:
- [templates/validation-report.md](templates/validation-report.md) - Report template

## Anti-Patterns

- ❌ **Gate mentality**: Treating validation as pass/fail instead of feedback
- ❌ **Over-validation**: Running comprehensive on every keystroke
- ❌ **Ignoring trends**: Not learning from recurring issues
- ❌ **Siloed validation**: Not coordinating with other skills
- ❌ **Premature claims**: Saying "Done!" without fresh verification
- ❌ **Single layer**: Relying on one check to catch everything

### Anti-Rationalization

Common excuses that bypass validation:

| Rationalization | Counter |
|-----------------|---------|
| "I just ran it" | Memory unreliable. Run again. |
| "It's obvious" | Obvious things fail. Verify. |
| "Too simple" | Simple compounds to complex. Check. |
| "User is waiting" | Wrong answers waste more time. |
| "Just this once" | Never 'just' once. No exceptions. |

See [reference/verification-gate.md](reference/verification-gate.md) for the full table.

## Notes

- Validation enhances, never blocks (unless critical security issue)
- Quick pipeline should feel instant
- Persist results for trend analysis
- Coordinate with refining for commits/PRs
