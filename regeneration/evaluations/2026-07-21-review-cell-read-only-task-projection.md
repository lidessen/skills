# Review Cell read-only Task projection

**Question:** can a host run a review Cell without granting Task mutation
authority, while retaining the normal terminal-contract proof of completion?

**Decision:** support a host-selected `read-only` Task projection and expose it
through the Work Cell CLI. Keep review methodology in the review instruction or
skill; do not specialize the generic Work Cell manifest for review.

## Baseline

The independent PR 48 review exposed `task_create` to a read-only reviewer. One
reviewer created an unnecessary Task, left it unsettled, and caused an otherwise
useful review run to fail its mechanical verification. The runtime already had
`manage` and `read-update` projections, but the CLI could not select either and
there was no projection that matched the accepted review authority: inspect
Tasks without mutating them.

## Candidate and evidence

The runtime now accepts three host-selected projections:

- `manage`: list, get, create, and update;
- `read-update`: list, get, and status updates; and
- `read-only`: list and get only.

The choice remains a host option rather than a model-authored Cell field. A
focused driver test verifies both the exposed tool set and the model-facing
authority instructions. The complete Work Cell suite passed 133/133 tests with
561 assertions, and package type checking passed.

A live CLI probe then ran `deepseek-chat` with `--task-tools read-only`:

- run `d6c3cd1a-bc53-4cc5-9d8c-c6ff638ce6d5` passed;
- the trace projected exactly `task_list` and `task_get`;
- no `task_create` or `task_update` call was possible;
- `submit_review` was called exactly once and accepted; and
- observed usage was 2,060 total tokens.

The model first listed Tasks, then made an invalid `task_get` call, and reached
the required terminal action only after terminal-contract recovery. This is
useful negative evidence: removing excess authority prevents accidental Task
mutation, but does not make a Flash-class model reliably follow every direct
instruction. The existing recovery loop remained necessary and worked.

## Boundary and residuals

This change closes an authority-projection gap. It does not claim to solve the
large-review context or cumulative-token problem, and it does not move impact
analysis, evidence standards, or false-positive rejection out of the review
skill. A read-only Cell also cannot settle seeded pending Tasks; callers should
use this projection for observational review packets, not for Task-backed work
that must update its own lifecycle.
