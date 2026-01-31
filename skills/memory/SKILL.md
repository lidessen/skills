---
name: memory
description: Manages project-level memory using local filesystem (.memory/) with optional GitHub/GitLab Issues sync (via MCP tools or CLI). Stores notes, decisions, todos, sessions locally; uses Issues for cross-device task tracking. Triggers on "remember", "recall", "what did we", "save this", "todo", "decision", "sync memory".
---

# Memory

Local filesystem memory for cross-session knowledge persistence. Zero dependencies for local use; optional GitHub/GitLab sync for cross-device.

## When to Use

- **Persist knowledge**: "Remember this", "Save this decision"
- **Recall context**: "What did we discuss about X?"
- **Track tasks**: "Add todo", "What's pending?"
- **Record decisions**: "We decided X because..."
- **Session handoff**: Summarize for next session

**Not this skill**: Project docs (edit directly), code comments, git history.

## Storage Structure

```
.memory/
├── context.md          # Current context + Issue references
├── notes/              # Knowledge, learnings
├── decisions/          # Architecture Decision Records
├── todos/              # Local task tracking (or use Issues)
└── sessions/           # Session summaries
```

File naming: `YYYY-MM-DD-kebab-slug.md` (natural sort, grep-friendly).

## Record Format

```markdown
---
type: note | decision | todo | session
status: active | completed | archived
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Title

Content...
```

See [templates/](templates/) for type-specific formats.

## Core Operations

| Operation | Action |
|-----------|--------|
| Create | Write to appropriate subdirectory with template |
| Search | `grep -ri "term" .memory/` |
| Update | Modify file, update `updated:` date |
| List active | `grep -l "status: active" .memory/**/*.md` |

## Workflows

**Remember decision**: Create `.memory/decisions/YYYY-MM-DD-slug.md` with rationale.

**Recall context**: Search `.memory/`, summarize findings with file references.

**Track task**: Create `.memory/todos/YYYY-MM-DD-slug.md` or create GitHub/GitLab Issue.

**Session summary**: Create `.memory/sessions/YYYY-MM-DD-summary.md` at session end.

## Integration

```
Memory provides context for:
├── dive        → Past learnings inform investigation
├── engineering → Past decisions inform new ones
├── refining    → Session history helps PR descriptions
└── orientation → Memory supplements project docs
```

## Anti-Patterns

- Storing code snippets (use gists or project files)
- Duplicating documentation (link instead)
- Large files (split into focused records)
- Sensitive data (credentials, API keys)
- Binary files (text-only)

## Setup

See [reference/setup.md](reference/setup.md) for initialization options:
- Automatic via hooks (Claude Code, Cursor)
- Manual setup
- Git configuration

## Remote Sync (Optional)

Use GitHub/GitLab Issues for cross-device task tracking. See [reference/remote-sync.md](reference/remote-sync.md) for:
- MCP tools vs CLI usage
- context.md format
- Sync workflow and conflict handling
