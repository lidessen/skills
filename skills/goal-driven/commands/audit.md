# goal-driven:audit — Periodic maintenance

Run periodically to keep `goals/` honest. Audit catches the slow drift
that the per-session protocol can't: stale criteria, naked verdicts,
forgotten STOPs, missed month rotation, GOAL.md inconsistencies.

If `goals/GOAL.md` does not exist or is still a stub, stop and ask
whether the human meant `/goal-driven bootstrap` instead.

## When to run

- ≥ 2 weeks since the last audit
- ≥ 30 new journal entries since the last audit
- A new agent picks up the project (sanity-check inherited state)
- The human says "things feel off" or "I'm not sure where we are"
- Before a major decision that depends on knowing where you actually stand

## Phase 1 — Collect findings

Run each check. Record findings in conversation; don't write to files yet.

### 1.1 OPEN-STOPS sync

Cross-check `goals/OPEN-STOPS.md` against journal entries:

- Every line in OPEN-STOPS should resolve to a real STOP entry in some
  `journal-*.md`. Flag orphan lines.
- Every STOP entry in the journals that lacks a `→ resolved` follow-up
  should appear as a line in OPEN-STOPS. Flag missing index entries.

If sync is broken, the protocol has been violated somewhere. The audit
fixes it but should also note when the violation happened (which entry,
which session).

### 1.2 Stale criteria scan

For each active criterion in GOAL.md, count how many of the last 20
journal entries reference it (✓, ✗, or unclear with evidence about it).

- 0 references in 20 entries → candidate for retirement. The criterion
  isn't being measured; either nobody cares anymore or there's no
  instrumentation.
- All `unclear` references → candidate for instrumentation. The
  criterion matters but no observation ever lands on it.
- Mostly ✓ with no ✗ ever → not necessarily wrong, but worth checking:
  is the bar set too low?

### 1.3 Naked verdicts

Scan recent entries (last 20–30) for criteria checks. Any `✓` or `✗`
without a parenthetical citing evidence is a violation of the evidence
rule — flag them. Format expected: `C2 ✓ (P95 measured 320ms)` not
`C2 ✓`.

If many recent entries have naked verdicts, the protocol is decaying.
Surface this prominently — it's the leading indicator of the skill
failing.

### 1.4 Month rotation

Check the most recent `journal-YYYY-MM.md`:

- Does its filename match the current month? If not, an entry was
  appended to a previous month's file or the new month's file was never
  created.
- Does it start with a carry-over entry summarizing the previous month
  (open STOPs, current path, last-month close)? If not, rotation
  happened but the carry-over was skipped.

### 1.5 GOAL.md self-consistency

Read GOAL.md end-to-end as if you'd never seen it:

- Do criteria contradict each other? (e.g., "C1: ship in 6 weeks" and
  "C5: zero technical debt")
- Do invariants conflict with criteria? (e.g., invariant "no new infra"
  vs. C2 requiring something that needs new infra)
- Are non-goals consistent with the north star?
- Has the Revisions section been updated for each change?

### 1.6 Cross-check with design-driven (if installed)

Only if `design/` exists:

- Recent `design/decisions/` adopted but not mentioned in the journal? A
  shape change happened that the goal layer didn't notice.
- Any design decision that would violate a GOAL invariant?
- Any GOAL pivot logged in the journal that crossed module boundaries
  but didn't open a `design/decisions/` proposal?

These are not errors per se — sometimes they're fine — but they're worth
the human's attention.

## Phase 2 — Report and propose

Compile findings into a report posted in chat. Structure:

```
## Audit findings — YYYY-MM-DD

### Open STOPs sync
- <one bullet per orphan or missing line, with proposed fix>

### Stale criteria (candidates for retirement or instrumentation)
- C<N>: <0 / all-unclear / always-✓> in last 20 entries
  → suggest: <retire | instrument | leave>

### Naked verdicts
- <count> verdicts without evidence in last <N> entries
  (examples: <2-3 entry refs>)
  → suggest: ask human to recheck; tighten future verdicts

### Rotation
- <ok | issue with description>

### GOAL.md consistency
- <findings or "consistent">

### Cross-check with design-driven
- <findings or "no issues" or "n/a">
```

For each finding, propose a specific action.

## Phase 3 — Apply changes (after human approval)

Audit doesn't silently rewrite things. Each proposed action needs human
approval in chat.

### 3.1 Sync fixes

For OPEN-STOPS sync issues:
- If a STOP exists but isn't indexed: add the line to OPEN-STOPS.
- If OPEN-STOPS lists a STOP that was actually resolved: append the
  `→ resolved` follow-up to the original journal entry (date the audit if
  unclear when), then remove the OPEN-STOPS line.
- If a "STOP" entry is ambiguous (was it a real STOP or just a
  judgment?), surface it; don't guess.

### 3.2 Criterion retirement

Retiring a criterion is a GOAL.md change — it requires the same
line-by-line confirmation as bootstrap edits.

- Don't delete; mark `RETIRED YYYY-MM-DD (reason)`. Keep the ID. Old
  journal entries reference C2; if C2 disappears, the references break.
- Add a Revisions line: `- YYYY-MM-DD: retired C<N> (reason)`.

### 3.3 Naked verdict followup

Don't retroactively edit old entries to add evidence — that's
fabrication. Instead:

- Note the issue in the next journal entry's Observations.
- Tighten the protocol: agent re-reads SKILL.md's evidence rule and
  states: "I'll be stricter about evidence going forward."
- If a specific verdict was clearly wrong (e.g., "C2 ✓" three weeks ago
  but ongoing failures suggest C2 was never ✓), surface that as a
  Type A STOP candidate now.

### 3.4 Rotation fix

If May entries are in `journal-2026-04.md`:
- Move them to the correct file (cut from April, paste into a new
  May file).
- Add a carry-over entry at the top of May.
- Note in the audit's own journal entry that rotation was missed.

### 3.5 GOAL.md inconsistency

Each inconsistency is a small GOAL change. Same line-by-line confirmation
protocol as bootstrap. Do not bulk-edit GOAL.md.

### 3.6 Audit's own journal entry

Audit always logs a journal entry summarizing what was found and what was
applied:

```markdown
## YYYY-MM-DD — Audit
- What I did: ran /goal-driven audit.
- Observations: <summary of findings>.
- Criteria check: C1 unclear, C2 unclear, ... (audit doesn't measure
  criteria; just records that an audit happened)
- Judgment: no change to GOAL; <N> sync fixes applied; C<X> retired.
```

This makes audit visible in the timeline. Future audits can see when the
last one happened.

### 3.7 Commit

If files changed (OPEN-STOPS, GOAL.md, journals), commit them as one:
"goal-driven: audit YYYY-MM-DD — <one-line summary>".

## What audit is NOT

- Not a re-bootstrap. Don't propose new criteria during audit. If the
  human wants to add a criterion, they'll request it; audit's job is
  only to surface drift, not redesign.
- Not a STOP. Audit reports findings; the human acts. If a finding
  warrants a STOP (e.g., "we've been failing C2 for a month silently"),
  surface it as a candidate STOP, not a unilateral one.
- Not a code review. Audit reads `goals/`. If the underlying work has
  problems unrelated to the goal layer, that's outside scope.
