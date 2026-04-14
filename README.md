# Skills

A collection of [agent skills](https://agentskills.io) — reusable methodology plugins for AI-assisted development, invocable via slash commands.

## Available Skills

| Skill | Command | Description |
|-------|---------|-------------|
| [design-driven](skills/design-driven/SKILL.md) | `/design-driven` | Design-driven development methodology. The `design/` directory is the single source of architectural truth — read it before coding, update the design before changing the system's shape. |
| [harness](skills/harness/SKILL.md) | `/harness` | Agent harness architecture — structure a project's agent context across layers (L1 architecture → L2 design → L3 implementation) for effective AI-assisted development. |

## Installation

```bash
npx skills install lidessen/skills
```

This installs all skills from the repository. To install a specific skill:

```bash
npx skills install lidessen/skills/design-driven
npx skills install lidessen/skills/harness
```

Then invoke a skill in any conversation:

```
/design-driven          # Run the main loop
/design-driven init     # Bootstrap design from existing codebase
/design-driven setup    # First-time project configuration

/harness                # Context layer methodology
/harness audit          # Evaluate existing project's context architecture
/harness init           # Bootstrap harness from scratch
```

## License

[MIT](LICENSE)
