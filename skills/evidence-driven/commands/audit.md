# evidence-driven:audit — Review evidence quality

Run periodically to surface evidence-quality drift in recent build
work. Audit reads blueprints (from design-driven if installed, else
whatever task structure the project uses) and asks: is the evidence
supporting each "done" claim actually evidence?

If the project doesn't use blueprints or any structured task records,
audit becomes a more general code review of recently shipped changes
— still useful, but with less concrete material to point at.

## When to run

- ≥ 2 weeks of build activity since the last evidence audit
- A bug shipped that "should have been caught" — diagnose whether
  evidence discipline failed
- Recurring sense that "tests pass but quality feels off"
- A new agent picks up a project and wants to assess inherited rigor
- Before declaring a sprint or release done, when stakes warrant it

## Phase 1 — Surface evidence drift

Read recent blueprints (in-progress and done within the last few
weeks). For each, walk through the evidence quality patterns. Don't
write to files yet; record findings in conversation.

**Naked Verify check-offs.** Verify section items marked `✓` without
a parenthetical citing what was observed. Format expected:
`- [x] Endpoint returns paginated results (curl test, 5/5 cases pass)`,
not just `- [x] Endpoint returns paginated results`. Count and
collect the worst offenders.

**Hollow State entries.** State entries that signal progress without
specifying what changed. "TODO 2 done" vs. "TODO 2 done — added
`limit` parameter to `query()` at store.ts:42, 14/14 existing tests
pass". The first is checkbox theater; the second is auditable. List
hollow entries by blueprint.

**Tests that don't catch their target.** This is the hardest pattern
to detect mechanically. Look for:
- Tests that mock everything and only assert on the mock being called
  (the real behavior isn't exercised)
- Tests that assert on coverage rather than effect
- Tests written without a comment or commit message naming the
  specific failure they catch
- Tests that pass even if you delete the function under test (try
  this manually for suspect cases)

If the codebase has many tests, sample rather than scan. Pick 5–10
recently added tests and check them against the falsifiability
criterion: "what specific failure does this catch?" If you can't
answer for ≥ 30% of the sample, the test culture has drifted and the
finding is broad rather than per-test.

**Verify forms inconsistent with task type.** A blueprint that's
purely UI work but Verify is "all unit tests pass" — the unit tests
probably don't catch the visual regressions that matter. Or a
blueprint that's a refactor (no behavior change) but Verify includes
"new behavior X works" — confused scope. Flag these for review.

**STOP-evidence chain breaks.** If the project also uses goal-driven:
when a journal STOP cited "we've measured X", does the build work
actually have an evidence trail showing X? If goal-level claims
aren't backed by build-level evidence, the upward feedback loop is
unreliable. (Skip this check if goal-driven isn't installed.)

## Phase 2 — Report

Compile findings into a single report posted in chat:

```
## Evidence audit findings — YYYY-MM-DD

### Naked Verify check-offs
- <count> in last <N> blueprints
- worst offenders (cite blueprint + check item)

### Hollow State entries
- <count>; pattern is "<typical hollow form>"
- specific examples: <blueprint:line>

### Tests not catching their target
- sampled <N> recent tests; <X> failed the "what does this catch" check
- example pattern: <generic description>

### Form / task mismatch
- <blueprint>: <type of work> verified with <type of check>; mismatch is <why>

### Cross-skill (if goal-driven installed)
- <STOP> at <date> cited <claim>; build evidence supporting it: <yes / partial / no>
```

For each finding, propose a specific action. Some examples:
- Naked check-offs → ask the human to recheck and add evidence; if
  evidence doesn't exist, surface as a Type A STOP candidate (the
  work may not actually be done)
- Hollow State → noted in next session's State; next entries
  required to be specific
- Cargo-culted tests → name the test, propose a rewrite that fails
  before the fix and passes after; or surface as known limitation

## Phase 3 — Apply changes (after human approval)

Audit doesn't silently rewrite. Each proposed action needs human
approval in chat.

### 3.1 Retroactive evidence

Don't fabricate evidence for past work. If a Verify check-off was
naked, the honest fixes are:
- **Re-verify now** — actually run the check, capture output, append
  to the blueprint with today's date
- **Demote** — change `✓` to `unclear` and surface as a candidate
  STOP if the work might not actually be done
- **Document the gap** — if re-verifying isn't feasible, leave the
  check-off as-is but add a note to the blueprint that this item
  lacks evidence

The wrong fix is to backfill plausible-sounding evidence text. That's
fabrication and it pollutes the record permanently.

### 3.2 Tightening the protocol

If naked check-offs or hollow State entries are pervasive, the
project's local discipline has drifted. Tightening:
- Re-read SKILL.md's evidence rule with the human
- Update agent configs (CLAUDE.md etc.) to be more specific about
  what evidence looks like
- Consider opt-in pre-commit hooks if the project warrants

### 3.3 Test rewrites

For tests that don't catch their target, the fix is per-test:
- Delete the cargo-culted test (better than keeping it as theater)
- Rewrite it to actually fail when the bug it nominally catches is
  introduced
- Document why each test exists in a comment near it

The rewrite typically produces a chain of evidence: the test failed
on the parent commit (proving it catches something), and passes on
the rewrite commit (proving the test is correct).

### 3.4 Audit's own record

If design-driven is installed, append a brief entry to the relevant
blueprint or to a top-level evidence-audit log. If neither, just
mention in the conversation log; audit doesn't require its own
artifact.

### 3.5 Commit

If files changed (blueprints, agent configs, tests), commit them as
one: `evidence-driven: audit YYYY-MM-DD — <one-line summary>`.

## What audit is NOT

- **Not a code review.** Audit reads evidence quality, not code
  correctness. A correctly-written function with poor evidence
  trail is still flagged; a buggy function with great evidence
  trail isn't audit's concern.
- **Not a witch hunt.** Findings are about patterns, not individual
  blame. The framing is "the discipline drifted" not "this person
  failed".
- **Not a STOP.** Audit reports findings; the human decides actions.
  If a finding warrants a STOP (work that may not actually be done,
  systemic test theater), surface as a candidate.
- **Not a redesign.** Don't propose new evidence rules during audit.
  The rules live in SKILL.md; audit applies them to existing work.
