# Validation History

This directory stores validation results for trend analysis and learning.

## Structure

```
validations/
├── index.md                    # This file
├── YYYY-MM-DD-context.md       # Individual validation records
└── archive/                    # Archived old records
```

## Recent Validations

| Date | Context | Status | Critical | Important | Link |
|------|---------|--------|----------|-----------|------|
| 2026-01-31 | Feature: validation-skill-creation | ✅ pass | 0 | 0 | [→](2026-01-31-validation-skill-creation.md) |

## Trends

- First validation recorded! More data needed for trend analysis.
- Current focus: establishing validation workflow

## How to Use

1. **Run validation**: Say "validate" or let it auto-trigger
2. **View history**: Say "validation history"
3. **Analyze trends**: Say "validation trends"
4. **Check issues**: Say "validation issues"

## Configuration

Create `.validation.yml` in project root to customize:

```yaml
pipelines:
  quick:
    validators: [syntax, lint]
  standard:
    validators: [syntax, lint, security, reviewability]
```

See `skills/validation/reference/pipelines.md` for details.
