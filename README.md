# Skills for AI Agents

A collection of reusable capabilities for AI agents. Skills provide procedural knowledge that helps agents accomplish specific tasks more effectively.

## What are skills?

Skills are like plugins or extensions that enhance what your AI agent can do. Each skill is a self-contained capability with clear instructions, workflows, and best practices that help AI agents perform specialized tasks.

## Installation

To install these skills, use the `skills` CLI:

```bash
npx skills add lidessen/skills
```

This will install all available skills and make them available to your AI agent.

## Available Skills

### 🔍 commit-staged

Reviews staged changes for common issues before generating commit message and committing.

**Features:**
- Pre-commit validation for debug code, mixed concerns, and breaking changes
- Automatic commit message generation following repository style
- Quality checks before committing

**Use when:** You want to commit staged changes with pre-commit validation, or mention "commit", "staged", "review before commit".

### 📝 create-skill

Guide for creating effective Agent Skills with progressive disclosure patterns and best practices.

**Features:**
- Step-by-step skill creation workflow
- Best practices for skill design
- Progressive disclosure patterns
- Quality checklists and anti-patterns
- Comprehensive examples and templates

**Use when:** You want to create a new skill, author a SKILL.md file, or ask about skill structure, naming conventions, descriptions, or how to organize skill content.

## Skill Structure

Each skill follows a consistent structure:

```
skills/
├── skill-name/
│   ├── SKILL.md           # Main skill file with metadata and workflow
│   ├── patterns/          # Common patterns and templates
│   ├── examples/          # Example implementations
│   ├── best-practices/    # Best practice guides
│   └── reference/         # Detailed reference documentation
```

## Creating Your Own Skills

Want to create a new skill? Use the `create-skill` skill to guide you through the process:

1. Define the skill's purpose and scope
2. Write clear metadata (name and description)
3. Design the workflow with progressive disclosure
4. Add examples and reference documentation
5. Validate against quality checklist

See [`skills/create-skill/SKILL.md`](skills/create-skill/SKILL.md) for detailed guidance.

## Contributing

Contributions are welcome! Please ensure:

- Skills follow the progressive disclosure pattern
- SKILL.md files include proper YAML frontmatter
- Names use lowercase-with-hyphens format
- Descriptions are specific and actionable
- Workflows are clear and well-structured

## License

See [LICENSE](LICENSE) for details.

## Learn More

- [Skills.sh Documentation](https://skills.sh/docs) - Official skills documentation
- [Skills Leaderboard](https://skills.sh/) - Browse popular skills in the ecosystem
