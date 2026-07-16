# OpenCode Go validation routing evaluation

**Date:** 2026-07-16
**Decision:** [034 — Validation Model Routing](../../design/decisions/034-validation-model-routing.md)

## Question

Can every Work Cell validation entry prefer OpenCode Go's DeepSeek V4 Flash
model, move only an unavailable model call to the official DeepSeek API, and
retain enough evidence to audit the actual route without replaying prior tool
actions?

## Deterministic evidence

`bun run typecheck` passed. `bun test` passed 89 tests across 16 files with 385
expectations.

The added probes establish:

- provider-neutral preferred and reserve targets prove that route execution has
  no OpenCode or DeepSeek identity dependency;
- a target-owned failure policy moves one call to the next target and retains
  the failed target and classified reason;
- a caller cancellation makes zero fallback calls;
- the OpenCode adapter classifies 429 for fallback while keeping a 400 invalid
  request visible;
- after one successful `read_file`, a second-call 429 uses DeepSeek inside the
  same AI SDK loop and the read remains executed exactly once;
- the validation policy exposes only credentials that are actually configured;
- the OpenCode adapter's JSON Schema lowering retains the schema instruction,
  JSON-object response mode, and disabled-thinking setting.

## Live evidence

A minimal terminal-only Cell ran through the documented
[OpenCode Go endpoint](https://opencode.ai/docs/go/) with no read, write, or
command authority:

- run ID: `46ddf578-6ea9-42e6-911c-68207138446c`;
- status: `passed`;
- terminal contract: `confirm_route` called exactly once;
- usage: 698 input, 45 output, 743 total tokens;
- recorded route: `routeId=validation`, `servedBy=opencode-go`,
  `mode=preferred`, with no failed attempts.

A separate structured-output call returned and validated
`{"status":"ok"}` through the same preferred route using 101 input and 5
output tokens.

## Disconfirming observation and correction

The first structured-output probe declared native `json_schema` support. The
OpenCode Go upstream rejected it with HTTP 400 `invalid_request_error`. Removing
that declaration still failed because JSON-object mode requires the request
context to ask explicitly for JSON and no longer carries the schema itself.

The corrected adapter translates AI SDK's `json_schema` request into the
endpoint's accepted `json_object` form, injects the original schema as a
call-local system constraint, and leaves the returned object subject to the
original AI SDK/Zod validation. The corrected live probe passed. HTTP 400 was
deliberately not added to the fallback set; doing so would conceal invalid
requests and silently shift structured workloads to the paid fallback.

## Institutional probe

The first implementation gave a provider-specific function a generic name. The
substitution probe replaced OpenCode Go and DeepSeek with neutral preferred and
reserve targets and showed that provider IDs, request adaptation, error
classification, environment variables, and pricing still lived in the route
mechanism. The corrected implementation separates:

- provider-neutral route execution and evidence in `model-route.ts`;
- concrete protocol and error behavior in `providers/`;
- current project ordering and credential policy in `validation-model.ts`.

The repository's always-present `AGENTS.md` now requires this substitution probe
for implementations that claim reuse. It deliberately does not force the same
abstraction onto one-off code with no demonstrated variation.

## Finding

The routing mechanism is ready for validation use. OpenCode Go is the preferred
provider when its key is present; the official DeepSeek API is a real fallback
only when its key is also present. The fallback boundary is one model call, not
one Cell. The generic mechanism, concrete provider adapters, current policy, and
project-level prevention gate now have separate owners. AI SDK Harnesses remain
a separate, experimental future adapter for delegating to complete coding
runtimes and are not part of this provider route.
