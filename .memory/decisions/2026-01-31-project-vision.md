---
type: decision
status: active
tags: [vision, architecture, automation]
created: 2026-01-31
updated: 2026-01-31
---

# Project Vision: Autonomous Workflow Skills

## Context

This project provides reusable skills for AI agents. Need to clarify positioning and goals.

## Decision

**Position**: A cohesive skill ecosystem for Claude Code, Cursor, OpenClaude and similar tools.

**Core Principles**:

1. **Autonomous Triggering** - Skills should auto-invoke based on context, not require user commands
2. **Tight Collaboration** - Skills form a complete workflow, not isolated utilities
3. **Minimal User Burden** - Agent should never need reminding about what to do
4. **Dogfooding First** - Every skill iterated through real usage on this project

## Skill Collaboration Map

```
Session Start
    │
    ▼
orientation ──► memory (load context)
    │
    ▼
User Request
    │
    ├─► dive (investigate)
    ├─► engineering (design)
    │       │
    │       ▼
    │   [implement]
    │       │
    ▼       ▼
refining ◄──────────────────┐
    │                       │
    ▼                       │
memory (record decisions) ──┘
    │
    ▼
housekeeping (maintain health)
```

## Automation Goals

| Trigger | Skill | Auto-Behavior |
|---------|-------|---------------|
| Session start | orientation | Scan project, load memory |
| "How does X work?" | dive | Investigate with citations |
| Architecture discussion | engineering | Guide design |
| Code changes ready | refining | Validate, commit, PR |
| Decision made | memory | Record ADR |
| Session end | memory | Summarize session |
| Periodic | housekeeping | Track debt, suggest cleanup |

## Consequences

- Need smarter trigger patterns in skill descriptions
- May need hooks for session lifecycle events
- Skills must expose collaboration interfaces
- Documentation should emphasize workflow, not individual tools

## Related

- CLAUDE.md - project instructions
- authoring-skills - skill design patterns
