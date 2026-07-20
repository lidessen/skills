# Decision 023 — AI review evidence and Principal confirmation

**Status:** approved
**Date:** 2026-07-12
**Authority:** direct Principal direction

## Decision

For material code integration, replace the impractical requirement that a human
independently reproduce a line-by-line code review with this gate:

```text
independent AI review evidence → concise traceable review packet → Principal confirmation
```

The AI reviewer must be independent of the implementing agent's active context
or role. Its record names reviewed scope, current head, findings ranked by
merge effect, source/line evidence, checks, unresolved uncertainty, and an
explicit merge/return recommendation. A green CI check is supporting evidence,
not an AI review.

The Principal reviews the compact packet—not the entire diff by default—and
confirms whether the stated scope, unresolved risks, and merge consequence are
acceptable. The Principal may reopen evidence, return work, hold, or merge.

## Completion and asynchronous review

Review is complete only when the named independent reviewer submits the
required record for the current head. An empty review list, a pending request,
a passing CI check, elapsed waiting time, or the temporary absence of comments
is not review evidence. A reviewer whose completion cannot be observed cannot
serve as the named gate for that integration.

An asynchronous platform reviewer may add useful evidence, but it is
supplemental unless it supplies the explicit current-head record above. Before
settling or pruning the integration Mission, re-read the source PR for review
observations that arrived after the merge decision and give each one a traced
disposition. A late observation can open correction work; it cannot silently
rewrite the accepted change or retroactively become approval authority.

## Boundary

AI review evidence is neither fact admission nor merge authority. It cannot
resolve its own findings, waive missing evidence, or merge. Human confirmation
does not become performative: it remains responsible for accepting residual
risk, scope, and the durable integration consequence.

## Reopening observation

Reopen this decision if AI review repeatedly fails to submit a traceable
conclusion, misses material defects found shortly after merge, produces a
packet too large for the Principal to understand the actual decision, or a
named reviewer cannot expose a reliable completion signal for the current
runtime.
