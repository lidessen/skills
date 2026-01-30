---
name: create-skill
description: Guide for creating effective Agent Skills with progressive disclosure patterns and best practices. Use when the user wants to create a new skill, author a SKILL.md file, or asks about skill structure, naming conventions, descriptions, or how to organize skill content.
---

# Creating Agent Skills

## Quick Start

When creating a skill:

1. **Gather requirements** - Understand purpose, scope, and trigger scenarios
2. **Draft metadata** - Write name (lowercase-with-hyphens) and specific description
3. **Design structure** - Plan SKILL.md content and any reference files
4. **Implement with progressive disclosure** - Keep SKILL.md concise, defer details to reference files
5. **Verify quality** - Check against the [quality checklist](#quality-checklist)

## Core Principle: Progressive Disclosure

**The most important concept**: Layer information so Claude only reads what it needs.

- **SKILL.md**: Core workflow and navigation (~500 lines max)
- **Reference files**: Detailed content loaded only when needed
- **Single-level references**: Link directly from SKILL.md (avoid nested references)

See [best-practices/progressive-disclosure.md](best-practices/progressive-disclosure.md) for detailed patterns.

## Essential Requirements

### Name Requirements
- Lowercase letters, numbers, hyphens only
- Max 64 characters
- No XML tags, no "anthropic" or "claude"
- Use gerund form: `processing-pdfs`, `analyzing-data`

### Description Requirements
- Max 1024 characters
- Write in third person: "Processes files..." not "I can process..."
- Include WHAT it does AND WHEN to use it
- Use specific trigger terms

**Good description example**:
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

See [best-practices/description.md](best-practices/description.md) for more examples.

## Directory Structure

Basic: Single `SKILL.md`  
Complex: `SKILL.md` + `reference/`, `examples/`, `scripts/`

See [reference/file-organization.md](reference/file-organization.md) for strategies.

## Conciseness Principle

**Assume Claude is smart**. Skip common knowledge (file formats, imports, package managers).

Challenge: "Does this justify token cost?"

See [best-practices/conciseness.md](best-practices/conciseness.md).

## Common Patterns

1. **Template**: Output format templates
2. **Workflow**: Multi-step with checklists
3. **Feedback Loop**: Validate → fix → repeat
4. **Conditional**: Decision branches

See [patterns/](patterns/) for details.

## Degrees of Freedom

Match specificity to task fragility:

- **High freedom** (text instructions): Multiple valid approaches, context-dependent decisions
- **Medium freedom** (pseudocode/templates): Preferred pattern with acceptable variation
- **Low freedom** (specific scripts): Fragile operations, consistency critical

See [best-practices/degrees-of-freedom.md](best-practices/degrees-of-freedom.md) for examples.

## Anti-Patterns to Avoid

- ✗ Windows-style paths (`scripts\helper.py`)
- ✗ Deeply nested references (SKILL.md → file1.md → file2.md)
- ✗ Time-sensitive information ("before August 2025...")
- ✗ Inconsistent terminology
- ✗ Too many options without a default
- ✗ Vague names like "helper" or "utils"

See [anti-patterns.md](anti-patterns.md) for details.

## Quality Checklist

Before finalizing a skill:

### Metadata
- [ ] Name is lowercase-with-hyphens, max 64 chars
- [ ] Description is third person, specific, includes triggers
- [ ] Description max 1024 chars

### Structure
- [ ] SKILL.md body under 500 lines
- [ ] File references are one level deep
- [ ] Reference files have descriptive names
- [ ] Longer reference files (>100 lines) have table of contents

### Content
- [ ] No unnecessary explanations (assume Claude is smart)
- [ ] Consistent terminology throughout
- [ ] Concrete examples, not abstract descriptions
- [ ] No time-sensitive information
- [ ] Forward slashes in all paths

### Workflows (if applicable)
- [ ] Clear sequential steps
- [ ] Checklists for complex workflows
- [ ] Validation/feedback loops for quality-critical tasks

## Complete Examples

See [examples/](examples/) for complete skill examples:
- **simple-skill.md**: Basic skill with just SKILL.md
- **complex-skill.md**: Skill with progressive disclosure and reference files
- **with-scripts.md**: Skill including utility scripts

## Storage

**Determine location based on your environment:**

1. **Check existing setup** - Look for existing skill directories:
   - **Cursor**: `~/.cursor/skills/` (personal) or `.cursor/skills/` (project)
   - **Codex/Claude**: `$CODEX_HOME/skills/` (personal) or project-specific location
   - **Other tools**: Check tool-specific documentation

2. **If no existing setup**, use standard locations:
   - **Project-level**: `.agents/skills/` (standard Agent Skills format)
   - **Personal**: `~/.agents/skills/` or tool-specific home directory

3. **For project instructions** (not skills), use `AGENTS.md` in project root

**Important**: 
- **Never** use `~/.cursor/skills-cursor/` (reserved for Cursor built-ins)
- Prefer project-level storage (`.cursor/skills/` or `.agents/skills/`) for team collaboration

## Additional Resources

**Best Practices**:
- [description.md](best-practices/description.md) - Writing effective descriptions
- [conciseness.md](best-practices/conciseness.md) - Keeping content concise
- [progressive-disclosure.md](best-practices/progressive-disclosure.md) - Layering information
- [degrees-of-freedom.md](best-practices/degrees-of-freedom.md) - Setting appropriate specificity

**Patterns**:
- [template.md](patterns/template.md) - Template pattern for consistent outputs
- [workflow.md](patterns/workflow.md) - Workflow pattern for complex tasks
- [examples.md](patterns/examples.md) - Examples pattern for clarity
- [feedback-loop.md](patterns/feedback-loop.md) - Validation loops for quality

**Reference**:
- [yaml-requirements.md](reference/yaml-requirements.md) - YAML frontmatter specifications
- [file-organization.md](reference/file-organization.md) - File organization strategies

**Anti-patterns**:
- [anti-patterns.md](anti-patterns.md) - Common mistakes to avoid
