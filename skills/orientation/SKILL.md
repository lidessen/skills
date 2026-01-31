---
name: orientation
description: Orients agents in new projects by scanning entry documents (CLAUDE.md, AGENTS.md, README) and discovering available skills. Use at session start, when entering unfamiliar projects, when asking "what can you do", "where do I start", or needing project overview.
---

# Orientation

Helps agents quickly orient themselves in a project - understanding context, available capabilities, and where to start. This is the "look around before diving in" skill.

## When to Use

- **Session start**: First interaction with a project
- **New project**: Unfamiliar codebase, need overview
- **Capability discovery**: "What skills are available?", "What can you help with?"
- **Direction needed**: "Where should I start?", "How is this organized?"

**Not this skill**:
- Deep investigation → use `dive`
- Technical decisions → use `engineering`
- Project maintenance → use `housekeeping`

## Core Workflow

### 1. Scan Entry Documents

Check for project entry points in order:

```
Priority 1 (Agent-specific):
  CLAUDE.md          → Claude Code instructions
  AGENTS.md          → General agent guidance
  .claude/           → Claude-specific config

Priority 2 (Project docs):
  README.md          → Project overview
  CONTRIBUTING.md    → Contribution guidelines
  docs/              → Documentation directory

Priority 3 (Structure):
  package.json       → Node.js project metadata
  pyproject.toml     → Python project metadata
  Cargo.toml         → Rust project metadata
  go.mod             → Go project metadata
```

### 2. Discover Available Skills

Skills can be installed at multiple locations:

```
Project-level:
  .claude/skills/           → Claude Code skills
  .cursor/skills/           → Cursor skills
  .agents/skills/           → Generic agent skills

Personal (user home):
  ~/.claude/skills/         → User Claude skills
  ~/.cursor/skills/         → User Cursor skills
  ~/.agents/skills/         → User generic skills
```

For each skill found, extract from SKILL.md frontmatter:
- `name`: Skill identifier
- `description`: What it does and when to use

### 3. Assess Project Type

Identify project characteristics:

| Signal | Indicates |
|--------|-----------|
| `package.json` | Node.js/JavaScript |
| `pyproject.toml` / `requirements.txt` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pom.xml` / `build.gradle` | Java |
| `.github/workflows/` | CI/CD configured |
| `docker-compose.yml` | Containerized |
| `terraform/` / `*.tf` | Infrastructure as Code |

### 4. Diagnose Documentation Health

Check agent documentation status and report issues:

| Check | Status | Action |
|-------|--------|--------|
| CLAUDE.md missing | ⚠️ Warning | Suggest `housekeeping` to create |
| AGENTS.md missing | ⚠️ Warning | Suggest `housekeeping` to create |
| Both missing | 🔴 Issue | Recommend creating agent docs |
| Docs outdated (>6 months) | ⚠️ Warning | Suggest `housekeeping` to update |
| Docs incomplete (no structure) | ⚠️ Warning | Suggest `housekeeping` to improve |

**Include in report** if issues found:
```markdown
## Documentation Health

⚠️ **Issues detected:**
- No AGENTS.md found - consider creating one for agent guidance
- CLAUDE.md last updated 8 months ago - may need refresh

**Recommendation:** Use `housekeeping` skill to maintain agent documentation.
```

### 5. Generate Orientation Report

Output format:

```markdown
## Project Overview

[Summary from README/CLAUDE.md - 2-3 sentences]

## Key Entry Points

- **CLAUDE.md**: [brief description if exists]
- **README.md**: [brief description if exists]
- [other relevant docs]

## Available Skills

| Skill | Purpose | Trigger |
|-------|---------|---------|
| [name] | [what it does] | [when to use] |

## Project Type

- **Stack**: [detected technologies]
- **Structure**: [monorepo/single-package/etc]
- **Notable**: [CI/CD, Docker, etc]

## Suggested Starting Points

Based on [project type/context], consider:
1. [Relevant suggestion]
2. [Relevant suggestion]
```

## Integration with Other Skills

Orientation is the **entry point** that routes to specialized skills:

```
┌─────────────────┐
│   orientation   │  ← Start here (read-only)
└────────┬────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  dive        → Investigation questions     │
│  engineering → Build/design questions      │
│  housekeeping → Maintenance, agent docs    │
│  refining    → Commits, PRs                │
│  authoring-skills → Create new skills      │
└────────────────────────────────────────────┘
```

**Key collaboration**: Orientation diagnoses, housekeeping treats.
- Orientation finds missing/outdated agent docs → recommend `housekeeping`
- Orientation is read-only; never modifies files

## Anti-Patterns

- ❌ Deep diving into code (use `dive` instead)
- ❌ Making architectural decisions (use `engineering`)
- ❌ Modifying documentation (use `housekeeping`)
- ❌ Executing project tasks without understanding context first
- ❌ Assuming project structure without scanning

## Example Outputs

### Example 1: Node.js Project (Healthy Docs)

```markdown
## Project Overview

A CLI tool for managing cloud infrastructure, built with TypeScript and Commander.js.

## Key Entry Points

- **CLAUDE.md**: Project conventions, testing requirements
- **README.md**: Installation, usage examples
- **docs/architecture.md**: System design

## Documentation Health

✅ Agent documentation is healthy.

## Available Skills

| Skill | Purpose |
|-------|---------|
| dive | Investigate codebase questions |
| engineering | Technical decisions |
| refining | Commits and PRs |

## Project Type

- **Stack**: TypeScript, Node.js, Commander.js
- **Structure**: Single package
- **Notable**: GitHub Actions CI, Jest tests

## Suggested Starting Points

1. Review `src/index.ts` for CLI entry point
2. Check `docs/architecture.md` for system design
3. Use `dive` skill to investigate specific features
```

### Example 2: Monorepo (Docs Need Attention)

```markdown
## Project Overview

Monorepo containing frontend (React), backend (Python), and shared infrastructure.

## Key Entry Points

- **README.md**: Basic project overview
- **packages/frontend/README.md**: React app docs
- **packages/backend/README.md**: API docs

## Documentation Health

⚠️ **Issues detected:**
- No AGENTS.md or CLAUDE.md found
- README.md lacks agent-specific guidance

**Recommendation:** Use `housekeeping` skill to create AGENTS.md with:
- Cross-package conventions
- Navigation for monorepo structure
- Common workflows

## Available Skills

| Skill | Purpose |
|-------|---------|
| dive | Investigate any package |
| housekeeping | Maintain dependencies, create agent docs |
| engineering | Cross-package decisions |

## Project Type

- **Stack**: React, Python, PostgreSQL
- **Structure**: Monorepo (pnpm workspaces)
- **Notable**: Docker Compose, Turborepo

## Suggested Starting Points

1. Review root `package.json` for workspace config
2. Check `docker-compose.yml` for local dev setup
3. Consider creating AGENTS.md for better agent guidance
```
