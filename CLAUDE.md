# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Vision

**Autonomous Workflow Skills** - A cohesive skill ecosystem designed for Claude Code, Cursor, OpenClaude and similar AI-assisted development tools.

**Core Principles**:
1. **Autonomous Triggering** - Skills auto-invoke based on context, no manual `/skill` needed
2. **Tight Collaboration** - Skills form a complete workflow, not isolated utilities
3. **Minimal User Burden** - Agent knows what to do; user never needs to remind
4. **Dogfooding First** - Every skill iterated through real usage on this project

Install: `npx skills add lidessen/skills`

## Skill Workflow

Skills collaborate as an integrated workflow, not independent tools:

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

**Auto-Trigger Expectations**:

| Context | Skill | Behavior |
|---------|-------|----------|
| Session start | orientation | Scan project, load memory |
| "How does X work?" | dive | Investigate with file:line citations |
| Architecture discussion | engineering | Guide design decisions |
| Code changes ready | refining | Validate cohesion, commit, PR |
| Decision made | memory | Record ADR automatically |
| Session end | memory | Summarize session |
| Periodic / on request | housekeeping | Track debt, suggest cleanup |

## Dogfooding

All skills are dogfooded on this repository except `frontend-init` (project bootstrapping, not applicable here):

| Skill | Dogfood Usage |
|-------|---------------|
| orientation | Session/project entry |
| memory | Cross-session context (.memory/) |
| dive | Investigating skill implementations |
| engineering | Architecture decisions |
| refining | Commits and PRs |
| authoring-skills | Creating new skills |
| housekeeping | Project organization |

## Architecture

### Skill Structure

Progressive disclosure - SKILL.md is the hub linking to detailed docs:

```
skills/
└── skill-name/
    ├── SKILL.md           # Entry point with YAML frontmatter + navigation
    ├── reference/         # Detailed documentation (loaded on demand)
    ├── patterns/          # Common patterns and templates
    └── templates/         # Reusable templates
```

**Design principle**: SKILL.md stays under ~500 lines. Never nest references deeper than one level.

### YAML Frontmatter

Every SKILL.md requires:
```yaml
---
name: skill-name
description: Two sentences. What it does + When to use (with trigger keywords).
---
```

Constraints:
- Names: `lowercase-with-hyphens`, max 64 chars
- Descriptions: Max 1024 chars, third person ("Processes..." not "I process...")

### Skill Boundaries

| Skill | Responsibility |
|-------|----------------|
| orientation | Entry point: scan project, discover skills, suggest direction |
| memory | Persist knowledge: notes, decisions, todos, session summaries |
| dive | Investigate: evidence-based answers with citations |
| engineering | Design: architecture, tech choices, implementation guidance |
| refining | Quality: cohesive commits, reviews, PRs |
| housekeeping | Health: cleanup, organization, tech debt |
| authoring-skills | Meta: guide skill creation |
| frontend-init | Bootstrap: modern frontend projects |

## Contributing

1. Follow progressive disclosure - split content across files
2. Include trigger keywords in description for auto-invocation
3. Reference `skills/authoring-skills/` for design principles
4. Ensure skill collaborates with existing workflow
5. Dogfood before publishing
