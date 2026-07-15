# Skills

> The current methods repository for a project that makes productive AI a
> common, open, replaceable capability.

This repository contains [agent skills](https://agentskills.io) and an
experimental Work Cell for AI-assisted development. It is one working surface,
not the whole project, a model provider, or an opaque AI platform. Its semantic
root is the one-line [Principle Sequence](principles/SEQUENCE.md); each P-ID has
a living, source-bound [interpretation](principles/interpretations/) and each
skill is a context-specific expression of selected entries.

Its [founding mandate](design/FOUNDING-MANDATE.md) is to make productive AI a
widely accessible, open, replaceable common capability: enable ordinary people
to use economical open-model engineering systems on bounded production work,
with concrete evidence rather than dependence on opaque platform claims. Its
ethical boundary is liberation rather than extraction: human and AI capability
must not be organized as an unaccountable source of exploitation.

Start from the [founding mandate](design/FOUNDING-MANDATE.md) to understand why
the project exists, the [operating protocol](design/operations/OPERATING-PROTOCOL.md)
to see how human-authorized work proceeds, or the active skills below to use a
specific method.

## Repository map

| Path | Owns | Does not own |
|---|---|---|
| [`principles/`](principles/) | the one-line Sequence, interpretations, inquiries, candidates, and review/adoption evidence | skill workflows or project execution |
| [`skills/`](skills/) | the current installable methodology and behavioral expressions | the semantic source they express |
| [`packages/work-cell/`](packages/work-cell/) | a general bounded agent runtime, optional adapters, and experimental research implementations | planning, doctrine, or human acceptance |
| [`site/`](site/) | the static public home page and reproducible documentation projection | source facts, project identity, or hosting authority |
| [`design/`](design/) | accepted architecture, decisions, operations design, and retained design studies | live task state or raw runtime evidence |
| [`regeneration/evaluations/`](regeneration/evaluations/) | durable behavior and boundary evaluations | governing design or raw run authority |
| [`chronicle/`](chronicle/) | provenance-preserving observation receipts and correction chains | claims, decisions, or a universal activity log |
| [`operations/missions/`](operations/missions/) | return obligations for active multi-session missions | a backlog, scheduler, or Git history duplicate |
| [`development-log/`](development-log/) | curated development checkpoint summaries and method feedback | primary verification evidence |
| [`archive/`](archive/) | read-mostly historical carriers and superseded methods | current install targets or governing guidance |

## Active Skills

| Skill | Command | Description |
|-------|---------|-------------|
| [principle-cultivation](skills/principle-cultivation/SKILL.md) | `/principle-cultivation` | Dogfood steward for the Principle Sequence. Preserves cited research before proposal, convenes selective P-ID reviews, and trials human-nominated alternates; only human-approved adoptions enter the core. |
| [context-engineering](skills/context-engineering/SKILL.md) | `/context-engineering` | Decide how authoritative project information reaches an agent at the moment it changes action, using the actual runtime rather than a fixed layer or filename convention. |
| [skill-engineering](skills/skill-engineering/SKILL.md) | `/skill-engineering` | Design, rewrite, review, and test skills that improve repeated agent action. Forms a selected Sequence expression team for each target skill, carries a standalone Sequence snapshot, and requires behavior evidence rather than prompt polish. |
| [disciplined-development](skills/disciplined-development/SKILL.md) | `/disciplined-development` | Apply lightweight evidence, scope, and test-value discipline underneath a development task without creating another methodology workflow. |
| [practice-cycle](skills/practice-cycle/SKILL.md) | `/practice-cycle` | Turn an observed non-trivial practice into a settled conclusion, a next smallest test, or a route to the owner of the unresolved judgment. |
| [form-guidance](skills/form-guidance/SKILL.md) | `/form-guidance` | Choose whether a recurring need should exist as a skill, decision artifact, runtime, projection, bounded campaign, or no new form before implementation starts. |
| [naming-and-articulation](skills/naming-and-articulation/SKILL.md) | `/naming-and-articulation` | Name a shared project concept, define its operative boundary, explain it at the right source, and decline needless terminology. |
| [work-estimation](skills/work-estimation/SKILL.md) | `/work-estimation` | Recover necessary work and discovery branches before converting a mission into model-specific budget, time, or cost. |
| [strategic-advisory](skills/strategic-advisory/SKILL.md) | `/strategic-advisory` | Prepare a proposed Strategy Case from phase evidence for human review; it links long direction, medium capabilities, and short mission candidates without self-commitment. |
| [artifact-organization](skills/artifact-organization/SKILL.md) | `/artifact-organization` | Audit whether artifact roles and paths still express accepted design, then apply one smallest justified organization transition. |
| [structural-refactoring](skills/structural-refactoring/SKILL.md) | `/structural-refactoring` | Reconstitute code across meaningful boundaries while preserving declared behavior, caller impact, and verification authority. |

## Experimental runtime

[`packages/work-cell`](packages/work-cell/README.md) is the collection's
independent practice and evaluation unit. Its core runs one caller-prepared,
bounded agent task and retains declared output artifacts, structured output,
terminal evidence, usage, cost, and workspace diff. Optional adapters lower
Sequence expressions, experiments, and deliberations into that generic
contract; research implementations remain outside the stable runtime surface.
It is infrastructure, not an invocable methodology skill, and it has no
planning, semantic, or acceptance authority.

For a Sequence-bearing repository, the read-only `probe` adapter discovers the
host Sequence, selects and loads a task expression, prepares a generic Cell,
and renders a reviewable reason chain. Exact JSON interfaces remain available
for generic runs, adapter fixtures, matched evaluation, and bounded
deliberation; see [decision 027](design/decisions/027-general-work-cell-core-and-sequence-adapter.md).

## Which skill, when?

| If you're... | Use |
|---|---|
| Researching whether recurring evidence merits a reusable core principle | `/principle-cultivation research` |
| Designing, auditing, or verifying how project context reaches an agent | `/context-engineering` |
| Creating, rewriting, or behavior-testing an agent skill | `/skill-engineering` |
| Applying a lightweight evidence, scope, completion, or meaningful-test discipline to ordinary development | `/disciplined-development` |
| Turning a finished or failed non-trivial attempt into the next bounded practice | `/practice-cycle` |
| Deciding whether a capability needs a skill, record, runtime, projection, or no new form | `/form-guidance` |
| Naming a shared concept, defining terminology, or deciding where its explanation belongs | `/naming-and-articulation` |
| Comparing the real work of alternatives, selecting estimate precision, or setting error tolerance before a budget | `/work-estimation` |
| Preparing strategic direction from a completed phase's verified evidence | `/strategic-advisory` |
| Checking whether project layout still fits accepted design | `/artifact-organization audit`; use `transition` only for a material gap |
| Splitting modules, extracting responsibilities, or untangling dependencies without intended behavior change | `/structural-refactoring` |
| Auditing how several established methods should cooperate | Read the project's organization operating model first; use the role that owns the observed disturbance, not a new universal skill |

The Principle Sequence is the root and `principle-cultivation` maintains it.
**Context-engineering** selects and verifies context delivery. **Skill-engineering** regenerates and tests
skill expressions. **Artifact-organization** designs the project base (根据地) and activity
architecture; 整理 is a campaign, not the skill's name. See each SKILL.md for handoff signals.
The [organization operating model](design/decisions/012-bounded-adaptive-organization.md)
defines conditional cooperation among those roles; it is a human-governed design
contract, not another command or central agent.

## Archive

Pre-regeneration methodology skills (`design-driven`, `goal-driven`, `evidence-driven`, `reframe`, writing skills), the legacy `setup-lidessen-skills` host adapter, regeneration working notes, completed blueprints, articles, and slides live under [`archive/`](archive/README.md). They are preserved evidence, not install targets. The repo no longer maintains a root-level `blueprints/` task-orchestration workflow. L1 guidance in this repo's `CLAUDE.md` / `AGENTS.md` is inlined; edit [`archive/skills/setup-lidessen-skills/references/cross-cutting-principles.md`](archive/skills/setup-lidessen-skills/references/cross-cutting-principles.md) and sync markers manually if that projection changes.

## Installation

```bash
npx skills install lidessen/skills
```

Install a specific active skill:

```bash
npx skills install lidessen/skills/principle-cultivation
npx skills install lidessen/skills/context-engineering
npx skills install lidessen/skills/skill-engineering
npx skills install lidessen/skills/disciplined-development
npx skills install lidessen/skills/practice-cycle
npx skills install lidessen/skills/form-guidance
npx skills install lidessen/skills/naming-and-articulation
npx skills install lidessen/skills/work-estimation
npx skills install lidessen/skills/strategic-advisory
npx skills install lidessen/skills/artifact-organization
npx skills install lidessen/skills/structural-refactoring
```

Example commands:

```
/context-engineering design # Design one source-to-agent delivery path
/context-engineering audit  # Audit context delivery against the actual runtime
/context-engineering verify # Prove a task receives and uses the context

/skill-engineering create   # Create a behavior-changing skill
/skill-engineering rewrite  # Reconstitute an inherited skill
/skill-engineering review   # Audit a skill's expression and evidence
/skill-engineering test     # Test a skill against action and boundary probes
/skill-engineering sync-sequence-snapshot # Regenerate packaged sequence snapshots

/artifact-organization audit
/artifact-organization transition

/structural-refactoring       # Behavior-preserving structural code change

/principle-cultivation research <question|paths>
/principle-cultivation propose <research-note>
/principle-cultivation review <candidate|sequence>
/principle-cultivation adopt <candidate>
```

Run the Work Cell package directly when developing the evaluation runtime:

```bash
cd packages/work-cell
bun install
bun run typecheck
bun test
bun run live:p23 # requires DEEPSEEK_API_KEY

# from this repository or any descendant
bun src/cli.ts probe "Inspect a bounded project question" \
  --accept "Return traceable evidence" \
  --scope packages/work-cell
```

## License

[MIT](LICENSE)
