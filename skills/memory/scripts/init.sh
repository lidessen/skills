#!/bin/bash
# Memory initialization hook
# Run on SessionStart to ensure .memory/ structure exists

MEMORY_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.memory"

# Only initialize if directory doesn't exist
if [ ! -d "$MEMORY_DIR" ]; then
  mkdir -p "$MEMORY_DIR"/{notes,decisions,todos,sessions}

  # Create initial context.md
  cat > "$MEMORY_DIR/context.md" << 'EOF'
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
EOF

  # Create README
  cat > "$MEMORY_DIR/README.md" << 'EOF'
# Project Memory

Local memory storage for cross-session context.

## Structure

- `context.md` - Current context + Issue references
- `notes/` - Knowledge, learnings, references
- `decisions/` - Architecture Decision Records
- `todos/` - Local task tracking
- `sessions/` - Session summaries

## Search

```bash
grep -ri "keyword" .memory/
```
EOF

  echo "Initialized .memory/ directory"
fi

exit 0
