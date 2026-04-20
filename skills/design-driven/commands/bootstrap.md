# design-driven:bootstrap — Bootstrap design from existing codebase

Generate the initial `design/DESIGN.md` by exploring the current 
codebase. Use when adopting design-driven on a project that already 
has code but no design docs.

Bootstrap handles plumbing idempotently — it's fine to run without 
having run `/design-driven init` first. If directories or agent 
configs are missing, they are set up in Phase 4.

Work in four phases: **Plan → Implement → Verify → Wire up**. Don't 
skip Phase 1 to start writing, and don't skip Phase 3 to ship faster 
— each phase catches a different class of mistake.

## Phase 1 — Plan

Understand the project before writing anything. The goal of this phase 
is not to write docs — it's to decide *what* docs to write, *what* to 
put in them, and *what* you still need to learn.

### 1.1 Survey what already exists

Before exploring the code, see what's already written:

- `README*`, `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, and similar 
  agent configs — do they already describe the architecture?
- Existing `docs/`, `architecture/`, ADRs, or RFC folders — is there 
  prior art you should build on instead of duplicate?
- `design/` directory — if it already exists, this is probably an 
  audit or update, not a bootstrap. Stop and ask the human whether 
  they meant `/design-driven audit`.

### 1.2 Explore the codebase

Walk through these five lenses. Note what you find — you'll reference 
these notes when drafting.

```
Shape       What are the major pieces? (packages, services, modules)
            Look at: directory structure, package manifests, build config

Boundaries  How do the pieces talk to each other?
            Look at: imports, HTTP clients, event emitters, message queues

Entry       Where does execution start?
            Look at: main files, server startup, CLI entry points

Mechanisms  What are the 2-3 things that make this system unique?
            Look at: actual source code of the core logic, not glue code.
            This is the most important step — skim won't cut it.

Decisions   Where does the code show a deliberate tradeoff?
            Look at: places where the obvious approach was rejected. 
            Comments, commit messages, and "why is this so weird?" 
            patterns are the signal.
```

For a large codebase, it's fine to delegate exploration to subagents 
(Explore / general-purpose) — but you must still synthesize the findings 
yourself. Don't hand that over.

### 1.3 Decide the plan

Write a brief plan (in conversation, not as a file) covering:

- **Files to create:** Always `design/DESIGN.md`. Add 
  `design/DESIGN-<aspect>.md` *only* if a mechanism is complex enough 
  that folding it into DESIGN.md would push DESIGN.md past ~200 lines. 
  Most projects don't need this on day one — bias toward one file.
- **Modules to list:** The major pieces from the Shape survey, named 
  as they appear in the code.
- **Mechanisms to capture:** The 2-3 from the Mechanisms pass. Name 
  each and one-line why it matters.
- **Decisions to record:** Any real tradeoffs you could confirm from 
  the code, with their rejected alternatives. Don't invent decisions 
  to fill the section — if you can't name a rejected alternative, 
  it's not a decision worth recording.
- **Open questions:** Things you couldn't determine from the code and 
  will need to either confirm with the human or mark as "inferred".

If the open questions would fundamentally change the design, resolve 
them with the human *before* drafting. If they're minor, draft with 
your best guess and flag them in phase 3.

## Phase 2 — Implement

Now write the files per the plan.

### 2.1 Ensure the directory structure exists

Create these if they're missing (bootstrap is idempotent — skip any 
that already exist):

- `design/` and `design/decisions/` (with `.gitkeep`)
- `blueprints/` (with `.gitkeep`)

### 2.2 Draft DESIGN.md (and any DESIGN-<aspect>.md)

Follow the structure in `../references/templates.md`. Remember:

- **Module descriptions:** two lines max — what it *does* and what it 
  explicitly *doesn't* do
- **Mechanisms:** describe the pattern and why it matters, not the 
  schema or the code
- **Decisions:** only real tradeoffs with rejected alternatives
- **ASCII diagrams:** a reader should grasp "what talks to what" in 
  5 seconds
- **Under 200 lines per file.** If you're over, you're writing a 
  reference doc, not a skeleton — cut.
- Write in present tense, describing the system as it is. Don't 
  narrate how it got there.

Style guidance lives in `../references/writing-guide.md` — load it if 
you need a refresher on voice and level of detail.

## Phase 3 — Verify

The draft is not done until you've checked it against the code and 
against itself. This phase is where hallucinated APIs, wrong module 
names, and inconsistent mental models get caught.

### 3.1 Fact-check against the code

For each claim in the draft, confirm it from the source:

- **Module names and paths** — do they match the actual directory and 
  file names?
- **Boundaries (does / doesn't)** — does the code actually enforce or 
  respect the boundary you described, or is it aspirational?
- **Data flow diagram** — trace the happy path through the real code. 
  Every arrow should correspond to a real call, import, or message.
- **Mechanisms** — re-read the core source for each mechanism. Is 
  your description accurate, or did you pattern-match from the name?
- **Decisions** — can you point to the code (or a commit/comment) 
  that shows the rejected alternative was actually considered? If not, 
  demote it or cut it.

Mark anything you couldn't verify from the code as "inferred" — don't 
quietly launder guesses into the skeleton.

### 3.2 Consistency check

Read the draft end-to-end as if you'd never seen it:

- Do the modules in the **Architecture** diagram match the ones in the 
  **Modules** section? (Same names, same count.)
- Does the **Data Flow** only touch modules defined in **Modules**?
- Do **Key Mechanisms** reference modules and flows that exist above?
- Do **Non-goals** contradict anything claimed elsewhere?
- Across files (DESIGN.md + any DESIGN-<aspect>.md): same terminology, 
  no overlapping or contradicting descriptions.

### 3.3 Principle check

- Is every file under 200 lines?
- Is each module description two lines max?
- Is this the 30% (shape) or did 70% (implementation detail) leak in? 
  If you see function signatures, error codes, or schema fields, cut 
  them — they belong in code, not design.

## Phase 4 — Wire up, review, commit

### 4.1 Human review

Present the draft. Call out explicitly:

- Anything marked "inferred" — the human may know the real answer
- Boundaries you weren't sure about
- Mechanisms you may have misunderstood
- Open questions from Phase 1 that you guessed on

Don't commit until the human has reviewed and approved.

### 4.2 Wire up agent configs

Update AI agent configs (CLAUDE.md, .cursorrules, AGENTS.md, etc.) to 
reference the new `design/` directory. Check `init.md` in this 
directory for the full list of common config locations and the 
instruction template — reuse that content, don't re-derive it.

If the user wants hooks (proposal gate, boundary reminder, design-code 
separation), set them up now per `init.md`'s Hooks section.

### 4.3 Commit

Commit `design/`, `blueprints/`, the agent config updates, and any 
hook configs together as the initial design-driven setup.
