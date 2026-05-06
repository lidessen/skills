---
name: goal-driven
description: |
  Goal-driven methodology for initiatives where the destination is clearer
  than the path. GOAL.md is the stable compass — north star plus falsifiable
  success criteria. The journal is the living record of what was tried, what
  was observed, and whether each criterion is still served. The agent writes
  both files; the human approves edits via chat.

  Use this skill for multi-week initiatives where upfront design is the
  wrong tool: research, exploratory features, personal quarterly planning,
  learning projects, writing a book or article series, job search. Trigger
  on phrases like "set a goal", "track my progress on X", "manage my
  quarterly work", "this is exploratory", "I know the goal but not the
  path", "plan my Q2", or when starting a months-long initiative without a
  clear technical shape.

  Pairs with design-driven. Goal-driven manages why and how-far;
  design-driven manages what-shape. Use both when a project is uncertain on
  direction AND structure. Each works alone — they cross-reference but do
  not depend on each other.

  Supports arguments: `/goal-driven init` to create empty goals/
  scaffolding, `/goal-driven bootstrap` to interview-drive an initial
  GOAL.md, `/goal-driven audit` to run periodic maintenance on the journal
  and STOPs.
argument-hint: "[init | bootstrap | audit]"
---

# Goal-Driven

A mini methodology for initiatives where the destination is fixed but the
path isn't. Human owns the compass; agent walks the path and keeps the log.

GOAL.md is the institutional memory of *why*. The journal is the
institutional memory of *what was tried*. Together they let a fresh agent —
or future-you — pick up a months-long initiative without losing direction.

## Commands

When invoked with an argument, dispatch to the corresponding file:

- `/goal-driven init` → Read and follow `commands/init.md`.
  One-time scaffolding: create `goals/` directory, empty stub files,
  optional hook. Does not write GOAL.md content.
- `/goal-driven bootstrap` → Read and follow `commands/bootstrap.md`.
  Interview the human and produce the initial GOAL.md. Idempotently handles
  scaffolding if `init` wasn't run first.
- `/goal-driven audit` → Read and follow `commands/audit.md`.
  Periodic maintenance: check OPEN-STOPS sync, scan stale criteria, find
  "naked ✓" entries without evidence, propose month rotation if missed.
- No argument → continue with the methodology below (the normal loop).

**Which command when:**

- New initiative, no `goals/` yet → `bootstrap` (does init plumbing too)
- Want plumbing without committing to content yet → `init`
- ≥ 2 weeks since last audit, or journal feels overgrown → `audit`
- Mid-task, just logging progress → no argument (normal loop)

## When to use this skill (and when not)

**Good fit:**
- Multi-week or longer; ≥ 3 uncertain decision points likely
- The path is genuinely unclear — you'd rewrite a detailed plan in 2 weeks
- Success criteria can be stated, even if some are observable proxies

**Bad fit:**
- One-off scripts, bug fixes, week-long features with a clear plan → use a
  TODO list
- Pure execution where the path is known and only the doing remains → use
  design-driven blueprints
- Goals you can't articulate at all → spend an hour writing first; come
  back

## Directory structure

```
project/
└── goals/
    ├── GOAL.md                  ← Stable compass (north star, criteria, invariants)
    ├── OPEN-STOPS.md            ← Index of unresolved STOP signals
    ├── journal-2026-04.md       ← Past month
    └── journal-2026-05.md       ← Current month (auto-rotates monthly)
```

Two stable files (GOAL.md, OPEN-STOPS.md) plus monthly journals. No
`archive/` directory by default — old months stay in place. If `goals/`
becomes crowded after a year, move them under `goals/journal-archive/`
manually; the convention is informal.

## The compass / path asymmetry

GOAL.md is the compass. It changes rarely, by deliberate human decision.
The path is everything else: what you're trying this week, what you tried
last week, what worked, what didn't.

The path mutates constantly. The compass mutates only when:

- A success criterion turns out to be the wrong measure (replace it)
- The north star itself is questioned by new evidence (rethink it)

Both are deliberate, human-approved events. They are NOT what happens when
"I tried X and it didn't work, let me try Y" — that's just walking.

This asymmetry is the whole point. If GOAL.md and the journal change at the
same rate, you don't have a compass; you have a notebook.

## Permission gradient

| File | Who writes | When | Human's role |
|---|---|---|---|
| `GOAL.md` | agent | Only at bootstrap or explicit GOAL change | Approves each section, line by line |
| `journal-YYYY-MM.md` | agent | End of each work session | Reviews entry draft in chat before write |
| `OPEN-STOPS.md` | agent | When a STOP is created or resolved | Confirms the line in chat |
| STOP signals | agent surfaces | When trigger condition hit | Decides: change path / change goal / agent misjudged |

**Never let the agent silently edit GOAL.md.** Every change must be echoed
in chat first. Even adding a single criterion is a deliberate event.

The agent is not a passive scribe — it drafts, proposes, surfaces. The
human is not a writer — they approve, redirect, decide. This asymmetry
prevents two failure modes at once: human laziness ("I'll write the goal
later") and agent drift (silent rewording into something subtly different).

## The three-moment protocol

The skill imposes specific behaviors on the agent at three moments. These
are the only mandatory rituals; everything else is the normal flow of work.

### Moment 1 — Bootstrap (creating GOAL.md)

The agent interviews the human via chat. It does **not** draft GOAL.md
alone and present it for review. It asks, in order:

1. **North star** — "In one or two sentences, what should be true when
   this is done?"
2. **Success criteria** — for each thing implied: "How would you know
   that's achieved?" Push for falsifiable; if soft, push for a proxy
   indicator.
3. **Invariants** — "What must stay true regardless of how we get there?"
4. **Non-goals** — "What's tempting to call success but isn't?"

The agent **echoes each section back as it's drafted**, gets confirmation,
moves on. GOAL.md is written only after all sections are confirmed. See
`commands/bootstrap.md` for the full interview script.

### Moment 2 — End of every work session

Before the session ends, the agent drafts a journal entry **in the chat**:

```
Entry draft:
- What I did: ...
- Observations: ...
- Criteria check:
    C1 ✓ (cite specific evidence)
    C2 ✗ (cite specific evidence)
    C3 unclear (no observation this session)
- Judgment: path-level / goal-level / no change
Confirm and append?
```

The human confirms or edits in chat. Only then does the agent append to
the current month's journal.

**The criteria check is the heart of the discipline.** Each ✓/✗ must cite
a concrete observation from the session. `C1 ✓` without evidence is
forbidden — it must be `C1 ✓ (ran 30 queries, recall 76%)` or
`C1 unclear (no test this session)`. Bare verdicts hide drift.

### Moment 3 — STOP signals

Two types of STOP, each with a different escalation path. Both halt work
until the human decides.

**Type A — Criterion not served.**
A criterion is failing or has been violated. The path is wrong, or this
particular criterion is wrong.
- Example: "C2: P95 < 500ms" but production shows 720ms after three
  attempts at different storage layers.
- Agent surfaces in chat, proposes three options:
  - (a) Change path (try Y instead of X)
  - (b) Change criterion (require human-approved GOAL edit)
  - (c) Agent misjudged

**Type B — North star questioned.**
Criteria are met (or close), but new evidence suggests the goal itself
solves the wrong problem.
- Example: criteria all green, but user research reveals users wanted
  topic clustering, not semantic search.
- Agent surfaces in chat, proposes:
  - (a) Reframe north star (deliberate GOAL edit)
  - (b) Stay course because the evidence is weak

**Critical:** STOPs are never silently logged and walked past. The agent
must surface them in chat AND wait for the human's choice before continuing
work. A STOP entry in the journal without a chat exchange is a protocol
violation.

## Anti-flattery: the evidence rule

Agents writing their own progress reports have an obvious bias toward ✓
verdicts (they want to keep working, not stop and wait for review). The
defenses, in order of strength:

1. **Every ✓ must cite an observation from THIS session.** Not "criterion
   still reasonable", not "no reason to think it broke". A specific thing
   that happened.
2. **If no observation touches a criterion this session, the verdict is
   `unclear`, not ✓.** Default to unclear. ✓ is earned, not assumed.
3. **`unclear` accumulating across many sessions is itself a signal** —
   that criterion isn't being measured. The audit command catches this and
   nominates such criteria for retirement or for explicit instrumentation.

This rule is the single biggest reason this skill might survive contact
with reality. Without it, the criteria check decays into checkbox theater
within weeks.

## Maintenance

### Monthly rotation

At session start, the agent checks: is today's month different from the
highest `journal-YYYY-MM.md` in `goals/`? If yes, it creates a new file
for the current month. The first entry of a new month is a brief
"carry-over" summary: open STOPs, which path is being walked, what last
month closed with.

This is automatic; no human action needed. The failure mode to avoid:
agent appending May entries to April's file. Always verify the filename
matches today's month before appending.

### OPEN-STOPS.md

Format (see `references/templates.md`):

```
- 2026-05-02 [Type B] north star questioned by user feedback → see journal-2026-05.md
- 2026-04-27 [Type A] C2 violated 3rd time this month → see journal-2026-04.md
```

Two-way sync rule:
- **New STOP:** add to OPEN-STOPS AND write the STOP entry in current
  journal — both writes in the same agent action.
- **Resolved STOP:** append `→ resolved YYYY-MM-DD: <decision>` to the
  original journal entry AND remove the line from OPEN-STOPS — both
  writes in the same agent action.

The audit command verifies sync — every line in OPEN-STOPS resolves to a
real journal entry; every STOP entry not yet resolved appears in
OPEN-STOPS.

### Audit cadence

Run `/goal-driven audit` whenever:
- ≥ 2 weeks since the last audit
- ≥ 30 new entries since the last audit
- A new agent picks up the project (sanity-check the inherited state)

Audit is the only event that catches slow drift: criteria that became
irrelevant but never retired, ✓ verdicts without evidence, OPEN-STOPS that
quietly went stale. See `commands/audit.md` for the full procedure.

## With design-driven

When a project uses both, each skill manages its own files:

| Concern | Lives in |
|---|---|
| Why we're doing this; success measure | `goals/GOAL.md` |
| What system shape implements it | `design/DESIGN.md` |
| Path attempted, observations, criteria check | `goals/journal-*.md` |
| Shape decisions and tradeoffs | `design/decisions/` |
| Per-task implementation plan | `design/blueprints/` |

**Cross-references by ID, not by content.** A journal entry says "adopted
decision 003 to switch storage"; a decision says "blocks goal STOP
2026-05-02 if rejected". Each skill reads its own files; cross-refs are
pointers, not embeds.

**Four interaction points to watch:**

1. **Goal pivot crosses design boundaries** → also open a
   `design/decisions/NNN-*.md` proposal. The journal entry doesn't replace
   the design proposal flow.
2. **Design proposal would violate GOAL invariants** → trigger a goal
   Type A STOP first; don't let design adopt and then quietly fail
   criteria.
3. **STOP resolution requires shape change** → resolve the goal STOP
   first, then open a design decision; don't shortcut.
4. **Audits cross-check** — goal audit notes design decisions not
   reflected in the journal; design audit notes GOAL invariants
   potentially at risk.

When design-driven isn't installed, none of this applies. Goal-driven
still works alone — shape decisions just live as journal observations,
without a separate proposal flow.

## Lightweight mode

For solo personal scenarios with one stream and ≤ 1 expected STOP, you can:

- Skip OPEN-STOPS.md (track the rare STOP inline in the journal)
- Use a single `journal.md` if the project is < 2 months total
- Keep GOAL.md regardless — that's the irreducible core

The skill scales down by dropping the maintenance scaffolding, never by
dropping the compass. If you find yourself dropping GOAL.md, you don't
need this skill — use a notebook.

## Example walkthrough

For a concrete end-to-end example — bootstrap, several journal entries,
two STOP scenarios, resolution — see `references/example.md`.
