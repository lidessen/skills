# Templates

Reference templates for blueprints, proposals, and DESIGN.md structure.
Load this file when you need to create one of these artifacts.

## Blueprint format

```markdown
# <Task Name>

**Status:** in-progress | done
**Date:** YYYY-MM-DD
**Design context:** Which design/ sections this task relates to

## Approach
What this task builds and the approach chosen. More detailed than design/ 
but still not code — think "which pieces to build, in what order, how they 
connect" rather than "which functions to call".

## Scope
What's in / what's out for this task specifically.

## Verification                  ← Define done criteria upfront
### Behavior
- [ ] Functional check 1 (e.g., "returns expected shape", "tests pass")
- [ ] Functional check 2

### Design constraints
- [ ] Stays within module boundaries as defined in DESIGN.md
- [ ] Honors relevant Constraints and Non-goals
- [ ] If shape changed: an adopted proposal exists in design/decisions/

## TODO                          ← Scaffolding — removed at close out
- [ ] Step 1 description
- [ ] Step 2 description
- [ ] ...

## State                         ← Scaffolding — removed at close out
Decisions made during build, current progress, and anything needed to 
resume if the session is interrupted. Update this as you go.

## Follow-ups                    ← Kept after close out (if any)
Items that got scope-shaved but remain worth doing. Names and one-line 
intents, not full blueprints.
- `<task-name>` — one-line intent
```

## Proposal format

Keep it short. One file, under 50 lines.

**Filename:** `design/decisions/NNN-kebab-title.md`, where `NNN` is the 
next unused three-digit number — scan the directory, take max+1, pad 
to three digits (start at `001` if empty).

```markdown
# <Title>

**Status:** proposed | adopted | rejected | adopted (retroactive)
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

Use `adopted (retroactive)` only during audit, when the shape change 
already happened in code without a proposal at the time — the file 
records the change after the fact.

## DESIGN.md structure

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
