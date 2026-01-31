---
type: decision
status: active
tags: [validation, architecture, quality, automation]
created: 2026-01-31
updated: 2026-01-31
---

# Decision: Unified Validation Skill

## Context

The existing validation logic was scattered across multiple skills:
- `refining`: reviewability gate, impact analysis
- `housekeeping`: consistency checks, doc health
- `orientation`: health diagnosis
- `engineering`: architecture validation

This created several issues:
1. No unified entry point for validation
2. No validation result persistence
3. No learning from validation patterns
4. No coordinated pipeline execution

## Decision

Create a new **validation** skill that serves as the unified orchestration layer for all quality checks.

### Key Design Decisions

1. **Orchestration, not replacement**: validation coordinates existing validators in refining, housekeeping, etc. rather than reimplementing them

2. **Three pipeline levels**:
   - `quick`: <10s, instant feedback
   - `standard`: <60s, pre-commit
   - `comprehensive`: <5min, pre-PR

3. **Feedback loop philosophy**: Validation is continuous feedback, not a gate
   - Record results in `.memory/validations/`
   - Detect patterns over time
   - Learn and adapt pipeline behavior
   - Recommend prevention measures

4. **Auto-trigger rules**: Context-aware activation
   - `git add` → quick
   - Commit → standard
   - PR/MR → comprehensive

## Consequences

### Positive
- Single entry point for all validation
- Validation history enables trend analysis
- Proactive prevention through pattern learning
- Better workflow integration

### Trade-offs
- Another skill to maintain
- Some overlap with refining (coordinated, not duplicated)
- Requires discipline to persist results

### Implementation Notes
- Validators delegate to existing skills via documented interfaces
- Custom validators configurable in `.validation.yml`
- Results persist to `.memory/validations/` with index

## Skill Workflow Integration

```
User Request
    │
    ├─► engineering (design)
    │       │
    │       ▼
    │   [implement]
    │       │
    │       ▼
    │   validation ◄── NEW: continuous quality check
    │       │
    ▼       ▼
refining ◄─────────
```

## Files Created

- `skills/validation/SKILL.md` - Main skill file
- `skills/validation/reference/validators.md` - Built-in validators
- `skills/validation/reference/pipelines.md` - Pipeline configuration
- `skills/validation/reference/persistence.md` - Result storage
- `skills/validation/reference/feedback-loop.md` - Learning mechanism
- `skills/validation/reference/custom-validators.md` - Custom validator guide
- `skills/validation/templates/validation-report.md` - Report template

## Iteration: Learning from Ecosystem

After researching [superpowers](https://github.com/obra/superpowers) and [openclaw](https://github.com/openclaw/openclaw), added:

1. **The Iron Law** (from superpowers)
   - No completion claims without fresh verification evidence
   - 5-step verification protocol
   - Prohibited language patterns ("should", "probably", "Done!")

2. **Defense-in-Depth** (from superpowers)
   - Four validation layers
   - Each layer catches what others miss
   - Context-sensitive strictness

3. **Anti-Rationalization Table** (from superpowers)
   - Counter common excuses for skipping validation
   - Explicit blockers for known failure modes

4. **Metrics Tracking** (from openclaw)
   - Duration, findings, cost tracking
   - JSONL format for efficient querying
   - Weekly summaries and trend analysis

## Iteration: Core Methodology

Established system-wide methodology in CLAUDE.md:

1. **Understanding Over Rules** - Teach WHY, agents that understand handle novel situations
2. **Adaptive Workflows** - No universal workflow, skill is knowing when to deviate
3. **Divide and Conquer** - Decompose → Smallest unit → Order → Compose
4. **Memory as Evolution** - Recording enables learning, problems across sessions
5. **Progressive Disclosure** - Load as needed, context space is precious

These principles now guide the entire system, not just validation.

## Related

- [Project Vision](2026-01-31-project-vision.md) - Autonomous workflow skills
- [superpowers](https://github.com/obra/superpowers) - Verification discipline inspiration
- [openclaw](https://github.com/openclaw/openclaw) - Metrics tracking inspiration
- skills/refining - Reviewability and impact analysis
- skills/housekeeping - Consistency checks
