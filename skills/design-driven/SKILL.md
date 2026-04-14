---
name: design-driven
description: |
  Design-driven development methodology. The design/ directory is the single 
  source of architectural truth — read it before coding, stay within its 
  boundaries, and when the system's shape needs to change, update the design 
  first.

  Use this skill whenever starting any development work on this project. Also 
  use when the user asks to: create or update architecture docs, add a new 
  module or feature that might cross existing boundaries, refactor system 
  structure, or understand the codebase architecture. Trigger on phrases like 
  "design first", "update the design", "does this change the architecture", 
  "write a design for", "what's the current design", or when onboarding to 
  understand a codebase's shape.

  Supports arguments: `/design-driven init` to bootstrap design from an 
  existing codebase, `/design-driven setup` to configure a project for 
  design-driven development.
argument-hint: "[init | setup]"
---

# Design-Driven Development

A mini methodology: design/ is the skeleton, code is the muscle. 
Human shapes the skeleton, agent builds the muscle.

## Commands

When invoked with an argument, dispatch to the corresponding file:

- `/design-driven init` → Read and follow `init.md` in this skill directory.
  Bootstrap the initial `design/` directory from an existing codebase.
- `/design-driven setup` → Read and follow `setup.md` in this skill directory.
  First-time project configuration (agent configs, hooks, directory structure).
- No argument → Continue with the methodology below (the normal loop).

## Directory Structure

```
project/
├── design/                                        ← Permanent skeleton
│   ├── DESIGN.md                                  ← System shape
│   ├── DESIGN-<aspect>.md                         ← Complex mechanisms (optional)
│   └── decisions/
│       ├── 001-outbox-over-direct-push.md         ← adopted
│       └── 002-split-memory-tiers.md              ← rejected
│
└── blueprints/                                    ← Implementation records
    ├── add-semantic-memory-search.md              ← done (clean, no TODO)
    └── refactor-agent-delegation.md               ← in-progress (has TODO)
```

Two directories, clear separation: `design/` is the architect's drawings 
(system shape, permanent), `blueprints/` is the builder's records 
(task-level approach, kept for reference).

## The Loop

Every development task follows one path:

```
  ┌───────────────────────────────┐
  │  Read design/DESIGN.md        │  ← Always start here
  │  Understand the skeleton      │
  └────────────┬──────────────────┘
               │
       ┌───────▼────────┐
       │ Does this task  │
       │ change the      │
       │ system's shape? │
       └───┬─────────┬───┘
           │         │
          NO        YES
           │         │
           │    ┌────▼───────────────────┐
           │    │ Write proposal in      │
           │    │ design/decisions/      │  ← Context + proposal + alternatives
           │    └────┬───────────────────┘
           │         │
           │    ┌────▼───────────────────┐
           │    │ Human reviews          │  ← Wait. Don't code until approved.
           │    └────┬───────────────────┘
           │         │
           │    ┌────▼───────────────────┐
           │    │ Update design/DESIGN.md│  ← Commit design change separately
           │    └────┬───────────────────┘
           │         │
       ┌───▼─────────▼───┐
       │   Plan           │  ← Draw the blueprint, set up scaffolding
       ├──────────────────┤
       │   Build          │  ← Code freely, track progress on scaffolding
       ├──────────────────┤
       │   Verify         │  ← Check against blueprint, tear down scaffolding
       └──────────────────┘
```

**"Changes the shape"** = adding/removing/merging modules, changing how modules 
connect, altering a key mechanism, introducing a new architectural pattern. 
If you're unsure, it probably doesn't — just code.

## Implementation: Plan → Build → Verify

The implementation phase has its own rhythm. Think of it like construction:
design/ is the architectural drawings (permanent), the blueprint is the 
construction drawing for a specific job, and the plan+TODO is scaffolding 
that comes down when the building stands.

### Artifacts

```
design/                      ← Architectural skeleton (permanent)
blueprints/
  └── <task-name>.md         ← Construction drawing (kept as record)
```

The blueprint file serves double duty during work — it's both the drawing 
and the scaffolding. After verification, the scaffolding (TODO section) is 
stripped, leaving a clean record of what was built and why.

### Blueprint format

```markdown
# <Task Name>

**Status:** planning | in-progress | done
**Date:** YYYY-MM-DD
**Design context:** Which design/ sections this task relates to

## Approach
What this task builds and the approach chosen. More detailed than design/ 
but still not code — think "which pieces to build, in what order, how they 
connect" rather than "which functions to call".

## Scope
What's in / what's out for this task specifically.

## TODO                          ← ⚠ Scaffolding — removed after verify
- [ ] Step 1 description
- [ ] Step 2 description
- [ ] ...
```

### Granularity

The blueprint sits between design/ and code:

```
design/      "The system has a memory layer with shared facts and 
              per-conversation short-term context"

blueprint    "Add semantic search to memory: integrate embedding model, 
              build index on startup, query during context assembly. 
              Reuse existing IMemoryManager interface."

code         The actual embedder, vector store, query functions, tests
```

The blueprint captures approach and scope decisions that the agent makes 
within the 70% freedom — not to constrain, but to leave a record of what 
was planned and make verification possible.

### The three phases

**Plan** — Read design/, understand the task, write the blueprint. The TODO 
section is the scaffolding: a checklist of concrete steps. Keep it short — 
this is a progress tracker, not a spec. For trivial tasks (bug fixes, small 
changes), skip the blueprint — just do it.

**Build** — Code freely within design/ boundaries, following the blueprint's 
approach. Check off TODO items as you go. The blueprint is a guide, not a 
prison — if you discover a better approach mid-build, update the blueprint 
first, then continue.

**Verify** — Check the implementation against the blueprint:
1. Does what was built match the approach described?
2. Is the scope respected (nothing extra, nothing missing)?
3. Does it stay within design/ boundaries?

Then tear down the scaffolding: remove the TODO section from the blueprint, 
mark status as `done`. The clean blueprint stays in `blueprints/` as a 
record of what was built — useful for future reference and onboarding.

### When to skip the blueprint

Not every task needs construction drawings. Skip for:
- Bug fixes with obvious cause and fix
- Small config changes, dependency updates
- Tasks that take less time to do than to plan

Use a blueprint when the task has meaningful scope, touches multiple files 
or modules, or when you want a record of the approach for future reference.

## Proposals and Decisions

Design proposals and decisions live in `design/decisions/`. Each is a short 
markdown file, same abstraction level as DESIGN.md — no implementation details.

### Proposal format

Keep it short. One file, under 50 lines:

```markdown
# <Title>

**Status:** proposed | adopted | rejected
**Date:** YYYY-MM-DD

## Context
One paragraph: what situation prompted this proposal.

## Proposal
What changes to the system's shape. Same level as DESIGN.md — 
module boundaries, data flow, mechanisms. No implementation details.

## Rejected alternatives
What else was considered and why it lost.

## Outcome
(Filled in after decision)
If adopted: which DESIGN.md sections were updated.
If rejected: why, in one paragraph.
```

### Flow

```
Propose:   Write design/decisions/NNN-title.md with status: proposed
              └── Present to human for review
                    │
            ┌───────┴────────┐
         adopted          rejected
            │                 │
   Update DESIGN.md     Record why in
   Mark status: adopted   Outcome section
   Commit both together  Mark status: rejected
```

Adopted proposals update DESIGN.md — the proposal file stays as the reasoning 
record. Rejected proposals stay too — so the next person with the same idea 
can see why it was already considered and turned down.

DESIGN.md's **Key Decisions** section is a curated summary of the most 
significant adopted decisions. The `decisions/` directory is the full history.

## The 30/70 Principle

The design/ directory captures 30% — the critical skeleton. 
The agent has 70% freedom.

**The 30% (in design/):**
- Module boundaries — what exists, what each does and doesn't do
- Data flow — how information moves through the system
- Key mechanisms — patterns that define system behavior
- Tradeoffs — choices where you picked A over B, and why

**The 70% (agent decides freely):**
- API design, function signatures, error handling
- Data structures, algorithms, file organization
- Internal module architecture, naming, patterns
- Parameter values, configuration, tooling

**Litmus test:** If changing it would change the system's *shape*, it's the 30%. 
If it changes *behavior within the same shape*, it's the 70%.

## Reading an Existing Design

When design/DESIGN.md already exists, read it before every task. Pay attention to:

1. **Module boundaries** — Which module owns the thing you're touching?
2. **"Doesn't do"** — Is the task something a module explicitly doesn't do?
3. **Key mechanisms** — Does your approach align with established patterns?
4. **Non-goals** — Is the feature explicitly out of scope?

If the task fits within boundaries, just implement — no need to explain yourself.
If it conflicts, surface the conflict before writing code.

## Creating a Design from Scratch

When no design/DESIGN.md exists, build one by exploring the codebase.

**Explore in this order:**
1. Project shape — packages, directories, build config
2. Entry points — where does execution start?
3. Boundaries — how do pieces communicate?
4. Key mechanisms — the 2-3 things that make this system unique 
   (read actual source code for these, not just file listings)
5. Existing docs — build on what's already documented

**Then write design/DESIGN.md:**

```markdown
# Project — Design

> One sentence: what is this system.

## Architecture
(ASCII diagram: modules and how they connect)

## Modules
(Each: does / doesn't do — two lines max)

## Data Flow
(ASCII diagram: the main happy path, ONE path only)

## Key Mechanisms
(2-3 patterns that define how the system works.
 Describe the pattern and why it matters, not the implementation.)

## Key Decisions
(Choices where you picked A over B, and what you rejected.)

## Constraints
(Hard limits)

## Non-goals
(What this system explicitly doesn't do)
```

Split into additional DESIGN-<aspect>.md files only when a complex mechanism 
deserves its own page. Never more than 3 design files total.

### What good looks like

**Module descriptions** — two lines:
```
### Auth Service
- **Does**: User auth, token management, permission checks
- **Doesn't**: User profiles, billing, audit logs
```

**Key mechanisms** — the pattern, not the schema:
```
Good:  "Workers are disposable — continuity lives in the workspace. 
        When a worker hits its limits, a fresh one picks up from a 
        structured handoff, not from the old worker's history."

Bad:   "WorkerRun { id, status, startedAt, runner_type, input_packet }"
```

**Key decisions** — only real tradeoffs:
```
Good:  "Outbox over direct push — decouples core from platforms, 
        guarantees delivery. Direct push simpler but fragile."

Bad:   "We use TypeScript." (not a real decision)
```

**ASCII diagrams** — answer "what talks to what" in 5 seconds:
```
[Module]         you control
(External)       you don't control
──>              sync call
..>              async / event
```

### What to avoid

- API endpoints, types, config — that's code
- Diagrams with every branch — happy path only
- Over 200 lines per file
- Module "does" longer than 3 lines — split the module
- Decisions without a rejected alternative

## Updating the Design

When a task requires changing the shape:

1. Write a proposal in `design/decisions/NNN-title.md`
2. Wait for the human to review
3. If adopted: update DESIGN.md, mark proposal adopted, commit both together
4. If rejected: record why in Outcome, mark rejected
5. Then implement freely within the (new) boundaries

## Setup

See `setup.md` — run once when adopting design-driven on a project.

## Tone

Match the team's language. Write like explaining to a smart colleague who 
just joined — they need the shape and the non-obvious choices, not details.
