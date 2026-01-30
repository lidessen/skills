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

### 📝 authoring-skills

Guide for authoring effective Agent Skills using a principle-based approach inspired by Claude's constitutional AI.

**Philosophy:**
- Understanding *why* patterns matter, not just *what* rules to follow
- Three core principles: Progressive Disclosure, Respect Intelligence, Enable Discovery
- Focus on judgment and trade-offs over mechanical compliance

**Features:**
- Principle-based design framework for creating and improving skills
- Deep understanding of anti-patterns and their underlying causes
- Progressive disclosure patterns and best practices
- Comprehensive examples and templates

**Use when:** Creating new skills, improving existing ones, refactoring skill structure, reviewing skill quality, or asking about skill design, best practices, anti-patterns, or organization.

### 🎯 project-expert

Acts as a project expert with comprehensive knowledge of business and technical details, using layered search strategies to provide evidence-based answers.

**Features:**
- Layered search strategy (documentation → code → deep analysis)
- Evidence-based answers with citations (file:line references)
- Never guesses - all answers backed by documentation or code
- Multi-source verification for accuracy
- Comprehensive search patterns for docs and code
- Handles uncertainty transparently

**Use when:** You have questions about the project, need clarification on business logic, technical implementation, architecture decisions, or any project-related inquiries that require deep knowledge and evidence-based answers.

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

Want to create a new skill? Use the `authoring-skills` skill to guide you through the process:

1. Understand the goal and core principles
2. Draft clear metadata (name and description with triggers)
3. Design structure with progressive disclosure
4. Write concisely (respect Claude's intelligence)
5. Review against principle-based checklist

See [`skills/authoring-skills/SKILL.md`](skills/authoring-skills/SKILL.md) for detailed guidance.

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
