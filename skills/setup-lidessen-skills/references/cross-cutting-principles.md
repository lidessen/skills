# Lidessen cross-cutting principles

This file is the **canonical source** of cross-cutting principles that span multiple lidessen skills. The `setup-lidessen-skills` skill copies the content below this header into target-project harness configs (CLAUDE.md / AGENTS.md / .cursor/rules/), between paired `<!-- lidessen-setup:* -->` markers.

The principles below are not skill-specific methodology — each lidessen skill carries its own. These are *aspect* principles that apply across the collection: how an agent should sequence decisions, balance shape vs flesh, manage finite context, etc. They are kept here, not in any single skill, because no single skill owns them — they are properties of working with the collection as a whole.

When adding a new principle: add a section below, keep it self-contained (a downstream consumer reading only this file's contents must be able to act on it without further context), and bump the canonical version tracked by `setup-lidessen-skills`. Consumers pick up changes on next `/setup-lidessen-skills sync`.

---

## Principal contradiction first

When a task has many decisions or moving parts, agents drift unless something forces sequencing. Identify the *principal contradiction* — the load-bearing decision whose resolution changes the shape of all downstream work — and lock it before drafting details.

**Operational test (cascade):** for each candidate decision, ask "if this is wrong and the rest is right, does the rest still hold?" If no, it's principal — lock it first. If yes, it's secondary — defer.

This pattern recurs at every layer in the lidessen collection — design-driven's 30/70 (skeleton vs flesh), goal-driven's General Line (destination before path), reframe's 3-5 abstract functions (essence before shape). This principle adds the *execution layer*: within a single task, locate the load-bearing decision before drafting downstream artifacts.

Roots in Mao's [On Contradiction](https://www.marxists.org/reference/archive/mao/selected-works/volume-1/mswv1_17.htm) — the principal contradiction's existence and development determines the form of the others; grasp it and "纲举目张" follows. Re-evaluate at transitions: once the principal is resolved, the next layer's contradiction may become principal.
