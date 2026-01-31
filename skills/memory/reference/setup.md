# Setup

## Automatic (Hook-based)

### Claude Code

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'DIR=\"${CLAUDE_PROJECT_DIR:-.}/.memory\"; [ -d \"$DIR\" ] || mkdir -p \"$DIR\"/{notes,decisions,todos,sessions}'"
          }
        ]
      }
    ]
  }
}
```

### Cursor

Add to `.cursor/hooks.json`:

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [
      {
        "command": "bash -c 'DIR=\"$(pwd)/.memory\"; [ -d \"$DIR\" ] || mkdir -p \"$DIR\"/{notes,decisions,todos,sessions}'"
      }
    ]
  }
}
```

## Manual

```bash
mkdir -p .memory/{notes,decisions,todos,sessions}
```

## Git Configuration

**Personal memory** (not shared):
```gitignore
.memory/
```

**Team memory** (shared): Commit `.memory/` to repository.

**Hybrid approach**:
```gitignore
# Share decisions and notes, keep sessions personal
.memory/sessions/
.memory/context.md
```

## Initial context.md

After creating directories, optionally create `.memory/context.md`:

```markdown
---
tracking: ""
active_issues: []
synced: ""
---

# Project Context

## Active Work

## Local Context

## Key Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
```

This file becomes the anchor for remote sync if configured.
