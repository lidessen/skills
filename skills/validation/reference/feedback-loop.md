# Validation Feedback Loop

How the system learns from validation results to prevent future issues.

## Table of Contents

- [The Learning Cycle](#the-learning-cycle)
- [Pattern Detection](#pattern-detection)
- [Adaptive Behavior](#adaptive-behavior)
- [Trend Analysis](#trend-analysis)
- [Proactive Prevention](#proactive-prevention)

---

## The Learning Cycle

Validation is not just checking—it's continuously improving.

```
┌─────────────────────────────────────────────────────────────┐
│                    FEEDBACK LOOP                            │
│                                                             │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐           │
│   │ VALIDATE │ ──► │  RECORD  │ ──► │ ANALYZE  │           │
│   └──────────┘     └──────────┘     └──────────┘           │
│        ▲                                  │                 │
│        │                                  ▼                 │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐           │
│   │ PREVENT  │ ◄── │  LEARN   │ ◄── │ PATTERN  │           │
│   └──────────┘     └──────────┘     └──────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Cycle Stages

1. **Validate**: Run pipeline, find issues
2. **Record**: Persist findings to .memory/validations/
3. **Analyze**: Aggregate data across time
4. **Pattern**: Identify recurring issues
5. **Learn**: Understand root causes
6. **Prevent**: Adjust validation or workflow

---

## Pattern Detection

The system identifies recurring patterns in validation history.

### Pattern Types

```
Recurring Issue Patterns:
│
├── Frequency Pattern
│   └── "console.log detected 5x in last 2 weeks"
│
├── Timing Pattern
│   └── "Size warnings always occur on Fridays"
│
├── Author Pattern (team context)
│   └── "Security issues often in authentication code"
│
├── File Pattern
│   └── "src/legacy/ triggers most consistency warnings"
│
└── Sequence Pattern
    └── "Noise issues followed by cohesion issues"
```

### Detection Algorithm

```
For each issue type in history:
│
├── Count occurrences in time window
│   └── threshold: 3+ in 30 days = pattern
│
├── Identify correlations
│   └── Same files? Same time? Same context?
│
├── Calculate trend
│   └── increasing / decreasing / stable
│
└── Generate insight
    └── "Console.log issues are decreasing (was 8/month, now 2/month)"
```

### Pattern Report

```markdown
# Detected Patterns (Last 30 Days)

## High Frequency Issues

### 1. Size Warnings (12 occurrences)
- **Trend**: ↑ Increasing
- **Common contexts**: Feature commits
- **Typical size**: 500-700 lines
- **Insight**: Features often too large for single commit
- **Recommendation**: Break features into smaller PRs

### 2. Console.log Noise (8 occurrences)
- **Trend**: ↓ Decreasing (was 15 last month)
- **Common locations**: src/components/
- **Insight**: Team awareness improving
- **Recommendation**: Continue current approach

### 3. Doc Freshness (5 occurrences)
- **Trend**: → Stable
- **Stale docs**: README.md, CONTRIBUTING.md, API.md
- **Insight**: Documentation updates not part of workflow
- **Recommendation**: Add doc update to PR template

## Positive Patterns

- **Zero security issues**: 47 validations, 0 security findings
- **Improving cohesion**: Mixed-concern warnings down 60%
```

---

## Adaptive Behavior

The system adapts based on learned patterns.

### Pipeline Adaptation

```
Pattern: Security issues rare
Adaptation: Move security validator later in pipeline (save time)

Pattern: Size warnings frequent
Adaptation: Add size check to quick pipeline (catch earlier)

Pattern: Specific file triggers many issues
Adaptation: Flag file for extra scrutiny

Pattern: Friday commits have more issues
Adaptation: Suggest comprehensive validation on Fridays
```

### Adaptation Rules

```yaml
# Auto-adaptation rules
adaptations:
  # Promote validators for frequent issues
  - condition: "issue_count(noise) > 5 in 14_days"
    action: "add_to_pipeline(quick, noise_check)"
    reason: "Catch console.log earlier"

  # Demote validators for rare issues
  - condition: "issue_count(security) == 0 in 30_days"
    action: "move_later_in_pipeline(security)"
    reason: "Low risk, optimize for speed"

  # Escalate for problematic areas
  - condition: "issues_in_path(src/legacy/) > 10"
    action: "always_comprehensive(src/legacy/**)"
    reason: "Legacy code needs more scrutiny"
```

### Threshold Adaptation

```
Original size thresholds:
├── Excellent: <200 lines
├── Good: <400 lines
└── Warning: >800 lines

Observed: Average commit is 350 lines, warnings rarely useful

Adapted thresholds:
├── Excellent: <300 lines
├── Good: <500 lines
└── Warning: >1000 lines

Note: Thresholds adapt to project reality
```

---

## Trend Analysis

Understanding how validation health changes over time.

### Trend Metrics

```
Key metrics tracked:
│
├── Pass rate
│   └── % of validations with no critical/important issues
│
├── Issue density
│   └── Issues per 100 lines validated
│
├── Time to fix
│   └── How long issues stay unresolved
│
├── Recurrence rate
│   └── % of issues that reappear after fix
│
└── Validation coverage
    └── % of commits/PRs that were validated
```

### Trend Visualization

```
Pass Rate Trend (12 weeks)
│
│  100% ─┬─────────────────────────────────
│        │    ╭──╮       ╭────────────────
│   90% ─┼───╯  ╰──╮   ╭╯
│        │         ╰──╯
│   80% ─┼─────────────────────────────────
│        │
│   70% ─┼─────────────────────────────────
│        └───┬───┬───┬───┬───┬───┬───┬───┬─
│           W1  W2  W3  W4  W5  W6  W7  W8
│
│  Trend: Improving (82% → 94%)
```

### Weekly Summary

```markdown
# Validation Weekly Summary

**Week**: Jan 24-31, 2026
**Validations**: 23

## Health Score: 87/100 (↑ 5 from last week)

### Breakdown

| Metric | Value | Trend |
|--------|-------|-------|
| Pass rate | 91% | ↑ +8% |
| Avg issues/validation | 0.8 | ↓ -0.3 |
| Critical issues | 0 | ✅ |
| Avg fix time | 2.3 hrs | ↓ -1 hr |

### Top Improvements

1. Console.log issues eliminated (pre-commit hook working)
2. Cohesion improved (smaller, focused commits)
3. Security checks passing consistently

### Areas for Attention

1. Documentation still getting stale
2. Size warnings slightly up (large feature in progress)
```

---

## Proactive Prevention

The ultimate goal: prevent issues before they happen.

### Prevention Strategies

```
Prevention Levels:
│
├── Level 1: Early Warning
│   └── Flag high-risk changes before validation
│   └── "This file has historically had security issues"
│
├── Level 2: Guided Workflow
│   └── Suggest best practices during development
│   └── "Consider splitting this commit (already 400 lines)"
│
├── Level 3: Automated Guards
│   └── Pre-commit hooks for common issues
│   └── Block console.log at commit time
│
└── Level 4: Structural Prevention
    └── Architecture changes to prevent issue categories
    └── "Add input validation layer to prevent injection issues"
```

### Early Warning System

```
On file change detection:
│
├── Check file history
│   └── "src/auth/session.ts: 5 security issues in past 6 months"
│
├── Check pattern matches
│   └── "Authentication code often has security issues"
│
├── Generate warning
│   └── "⚠️ High-risk file. Consider:
│         - Extra security review
│         - Comprehensive validation
│         - Pair programming"
│
└── Track if warning was heeded
    └── Learn if warnings are useful
```

### Prevention Recommendations

Based on validation history, system recommends:

```markdown
# Prevention Recommendations

Based on last 30 days of validation data:

## Recommended Pre-commit Hooks

```bash
# Add to .husky/pre-commit or similar

# Remove console.log (8 occurrences caught)
npx eslint --rule 'no-console: error' --fix

# Check file size (12 size warnings)
./scripts/check-commit-size.sh --max 400
```

## Recommended Workflow Changes

1. **Split large features**: Features over 500 lines should be multiple PRs
2. **Update docs with code**: Add "Documentation" checkbox to PR template
3. **Review legacy code changes**: Require second reviewer for src/legacy/

## Recommended Tooling

1. **ESLint no-console rule**: Would have caught 8 issues
2. **Commit size checker**: Would have flagged 12 large commits
3. **Doc freshness CI check**: Would remind about stale docs
```

### Learning Loop Closure

```
Issue detected → Recorded → Pattern identified
        ↓
    Prevention recommended
        ↓
    Prevention implemented (or not)
        ↓
    Track effectiveness
        ↓
    Adjust recommendations
```

Example:

```
Week 1: Console.log detected 8 times
Week 2: Recommend pre-commit hook
Week 3: Hook implemented
Week 4: Console.log detected 0 times
Week 5: Mark recommendation as "effective"
Week 6: Suggest similar hooks for other noise patterns
```

---

## Configuration

### Feedback Loop Settings

```yaml
# .validation.yml

feedback_loop:
  # Pattern detection
  pattern_threshold: 3         # Min occurrences to detect pattern
  pattern_window: 30_days      # Time window for pattern detection

  # Adaptation
  auto_adapt: true             # Enable automatic adaptations
  adaptation_cooldown: 7_days  # Wait before adapting again

  # Reporting
  weekly_summary: true         # Generate weekly summary
  trend_window: 12_weeks       # Trend analysis window

  # Prevention
  early_warnings: true         # Show warnings for high-risk files
  suggest_hooks: true          # Recommend pre-commit hooks
```

### Disabling Learning

For projects that want static validation:

```yaml
feedback_loop:
  enabled: false  # Disable all learning
```

Or selective:

```yaml
feedback_loop:
  pattern_detection: true
  auto_adapt: false        # Detect but don't auto-adapt
  suggest_prevention: true
```
