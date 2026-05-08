# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Guiding Principles

<!-- lidessen-setup:begin v=1 -->
### Principles over rules

Skills should help agents understand *why*, not just specify *what*. A skill that explains reasoning and principles produces better judgment across novel situations than one that mechanically lists rules. Favor broad principles over rigid prescriptions — give the agent enough context to generalize, not just enough rules to comply. ([Anthropic's constitution](https://www.anthropic.com/constitution): "If we want models to exercise good judgment across a wide range of novel situations, they need to be able to generalize — to apply broad principles rather than mechanically following specific rules.")

### Hierarchical context management

Agent context is finite — structure it in layers: L1 (architecture, always present), L2 (design, on activation), L3 (implementation, on demand). The higher the layer, the smaller and more stable. Keep SKILL.md under 500 lines; split details into supporting files. See the [harness skill](skills/harness/SKILL.md) for the full methodology and the [Agent Skills Specification](https://agentskills.io/specification#progressive-disclosure) for the underlying spec.

### Design for finite human bandwidth

Agent throughput keeps rising; human review capacity doesn't. When designing a skill or shaping any output that lands in front of a human, treat the output like code architecture: humans review the skeleton (the 20% whose failure invalidates the rest), agents own the details within, and details should be cheap to throw out without disturbing the skeleton. Generalizes design-driven's 30/70 to all agent-human collaboration. See [harness Part III](skills/harness/SKILL.md) for the full principle and consequences.

### Principal contradiction first

When a task has many decisions or moving parts, agents drift unless something forces sequencing. Identify the *principal contradiction* — the load-bearing decision whose resolution changes the shape of all downstream work — and lock it before drafting details. Operational test (cascade): for each candidate, ask "if this is wrong and the rest is right, does the rest still hold?" If no, it's principal; lock it first. If yes, it's secondary; defer. The same logic recurs across this repo at different layers — design-driven's 30/70 (skeleton vs flesh), goal-driven's General Line (destination before path), reframe's 3-5 abstract functions (essence before shape). This principle adds the *execution layer*: within a single task, locate the load-bearing decision before drafting downstream artifacts. Roots in Mao's [On Contradiction](https://www.marxists.org/reference/archive/mao/selected-works/volume-1/mswv1_17.htm) — the principal contradiction's existence and development determines the form of the others; grasp it and "纲举目张" follows. Re-evaluate at transitions: once the principal is resolved, the next layer's contradiction may become principal.
<!-- lidessen-setup:end -->

> The principles between the markers above are managed by `/setup-lidessen-skills` and sourced from [`skills/setup-lidessen-skills/references/cross-cutting-principles.md`](skills/setup-lidessen-skills/references/cross-cutting-principles.md). Do not hand-edit between markers; edit the canonical reference instead, then run `/setup-lidessen-skills sync` to propagate.

## Project Overview

This is a collection of agent skills — reusable methodology plugins for AI-assisted development. Skills are installed into a project and invoked via slash commands (e.g., `/design-driven`).

MIT licensed, maintained by Lidessen.

## Repository Structure

```
skills/
  <skill-name>/
    SKILL.md           ← Skill definition (frontmatter + main prompt)
    commands/           ← Subcommand instructions dispatched by SKILL.md
    references/         ← Reference material loaded on demand
    scripts/            ← Executable code (if needed)
    assets/             ← Templates, images, data files (if needed)
```

Each skill is a self-contained directory under `skills/`. The `SKILL.md` file is the entry point — its YAML frontmatter defines the skill's name, description, and argument hints, while the markdown body is the prompt that the agent executes when the skill is invoked. Subdirectories follow the [Agent Skills Specification](https://agentskills.io/specification) conventions; only create the ones the skill actually needs.

## Skill Format Specification

Skills follow the [Agent Skills Specification](https://agentskills.io/specification). Also see [Claude Code skills docs](https://code.claude.com/docs/en/skills).

A `SKILL.md` has two parts:

1. **Frontmatter** (`---` delimited YAML): `name`, `description` (used for trigger matching), and optional fields (`license`, `compatibility`, `metadata`, `allowed-tools`).
2. **Body** (markdown): The actual instructions Claude follows. May dispatch to sibling `.md` files based on arguments.

The `description` field is critical — it determines when the agent auto-triggers the skill. It should list concrete trigger phrases and use cases.

## Writing and Editing Skills

- Keep skill prompts methodology-focused, not implementation-focused. Skills teach Claude *how to think about a task*, not specific code to write.
- The body of SKILL.md is a prompt, not documentation. Write it as instructions Claude will follow, not as a reference humans will read.
- Subcommand files in `commands/` should be self-contained instructions — SKILL.md dispatches to them, they don't reference each other. Reference material goes in `references/`.
- Frontmatter `description` acts as the trigger classifier and shares an *aggregate* budget — Codex (and any harness following the [Agent Skills spec](https://developers.openai.com/codex/skills)) caps the combined skill list at ~2% of the context window, or ~8,000 chars when unknown, and tail-truncates descriptions when over budget. Two consequences: (a) **front-load** the key use case and trigger phrases so the value still matches even if its tail is clipped — treat methodology background, cross-skill relations, and `Args:` notes as tail content that's safe to lose; (b) keep each description compact (rough target: under ~800 chars) so a project with several installed skills doesn't push the list over the cap. Prefer a single-line YAML string; if readability really suffers, use the *folded* form (`description: >`), which still parses to one logical line. Avoid the *literal* form (`description: |`), which preserves line breaks and fragments triggers across short lines. Long prose and arg details belong in the SKILL.md body, not the frontmatter.
- When referencing another skill, use concept references: describe the *goal* first, then mention the skill as one way to achieve it. E.g., "Set up architectural documentation for the project — the design-driven skill can help with this." This keeps the skill functional even when the referenced skill isn't installed.
