# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

A collection of reusable skills (plugins) for AI agents. Skills provide procedural knowledge loaded into Claude's context to accomplish specialized tasks. Installed via `npx skills add lidessen/skills`.

## Dogfooding

Most skills in this repository are dogfooded - used to develop the project itself:
- **refining**: commits and PRs for this repo
- **authoring-skills**: guides skill creation
- **dive**: investigates skill implementations
- **engineering**: architectural decisions
- **housekeeping**: project organization

**Not dogfooded**: frontend-init (project bootstrapping, not applicable to this repo)

## Architecture

### Skill Structure Pattern

Each skill follows progressive disclosure - SKILL.md is the hub that links to detailed docs:

```
skills/
└── skill-name/
    ├── SKILL.md           # Entry point with YAML frontmatter + navigation
    ├── reference/         # Detailed documentation (loaded on demand)
    ├── patterns/          # Common patterns and templates
    ├── examples/          # Implementation examples
    └── best-practices/    # Best practice guides
```

**Design principle**: SKILL.md stays under ~500 lines and links to granular reference files. Never nest references deeper than one level from SKILL.md.

### YAML Frontmatter Format

Every SKILL.md requires:
```yaml
---
name: skill-name
description: Two sentences. What it does + When to use it (with trigger keywords).
---
```

Constraints:
- Names: `lowercase-with-hyphens`, max 64 chars
- Descriptions: Max 1024 chars, third person ("Processes files..." not "I process...")

### Available Skills

| Skill | Purpose |
|-------|---------|
| **refining** | Code review workflow: commit → review → PR/MR creation |
| **authoring-skills** | Meta-skill for creating effective Agent Skills |
| **dive** | Evidence-based investigation with file:line citations |
| **engineering** | Technical decisions, architecture, implementation guidance |
| **housekeeping** | Project maintenance: docs, deps, structure, tech debt |
| **frontend-init** | Bootstrap modern frontend projects (Bun, Oxlint, tsdown) |

### Skill Boundaries

- **Engineering** designs capability (architecture, tech choices, refactoring strategies)
- **Housekeeping** maintains health (cleanup, organization, tracking)
- **Refining** ensures quality (commits, reviews, PRs)
- **Dive** investigates (evidence-based answers about code)

## Contributing Skills

1. Follow progressive disclosure - split content across files
2. Include proper YAML frontmatter with trigger keywords in description
3. Reference `skills/authoring-skills/` for design principles and anti-patterns
4. Keep SKILL.md as a navigation hub, not a complete manual
