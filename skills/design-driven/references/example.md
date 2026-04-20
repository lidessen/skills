# Example walkthrough

One task, end to end, through the design-driven loop. Use this as a 
feel-for-the-rhythm reference, not a literal script.

## The task

> "Add a `/history` endpoint that returns the last N messages in a 
> conversation."

## Step 1 — Read design/

Open `design/DESIGN.md`. Key things to notice:

- There's a `ConversationStore` module that owns message persistence.
- The `API` module owns HTTP routing.
- "Doesn't do" on `API`: no business logic, only shape conversion.
- Key mechanism: all reads go through `ConversationStore.query()`.

Also scan `blueprints/` for any `in-progress` files — none.

## Step 2 — Does this change the shape?

Adding an endpoint to an existing module (`API`) that already talks to 
an existing module (`ConversationStore`), using the existing query 
mechanism. No new modules, no new mechanism, no boundary change.

→ 70% territory. No proposal needed.

## Step 3 — Plan

Create `blueprints/add-history-endpoint.md`:

```markdown
# Add /history endpoint

Status: in-progress
Date: 2026-04-20
Design context: API module, ConversationStore

## Approach
New GET /history/:conversationId in API. Delegates to 
ConversationStore.query() with a `limit` param. No new storage, 
no new business logic.

## Scope
In: route, handler, input validation, integration test.
Out: pagination cursors (future), filtering by sender.

## Verification
- [ ] GET /history/:id returns last N messages, default 50
- [ ] Returns 404 for missing conversation
- [ ] Integration test passes against the real store
- [ ] Stays within API module — no store internals exposed

## TODO
- [ ] Add route
- [ ] Add handler calling store.query
- [ ] Add input validation (limit bounds)
- [ ] Add integration test
- [ ] Run verify checklist

## State
(empty — nothing built yet)
```

## Step 4 — Build

Work through TODO. Halfway through, discover `ConversationStore.query()` 
doesn't accept a `limit` arg — it always returns everything.

Is adding `limit` a shape change?

- New module? No.
- New mechanism? No — same query mechanism, just a new parameter.
- Changes what the module *does*? Slightly broader now.
- Changes the boundary? No.

→ Still 70% territory. Add the arg. Note it in State:

```markdown
## State
Extended ConversationStore.query() with optional `limit: number` 
arg (defaulting to no limit to preserve existing callers). Route 
and handler done; validation + test still ahead.
```

Check off TODOs as you go.

## Step 5 — Verify

Run the checklist:

- GET /history/:id returns last N messages → ✓
- 404 on missing conversation → ✓
- Integration test passes → ✓
- API didn't reach into store internals → ✓

Re-read the blueprint. Nothing out of scope crept in. Pagination 
cursors stayed out — good.

Strip TODO and State sections. Flip Status to `done`. Commit the 
blueprint together with the code that implements it.

---

## Variant: the shape-change version

Same task, but this time performance requires a new `HistoryCache` 
module (not in DESIGN.md).

→ **Stop. Don't code.** Write `design/decisions/007-add-history-cache.md`:

```markdown
# Add HistoryCache module

Status: proposed
Date: 2026-04-20

## Context
/history endpoint hits ConversationStore on every call; p99 
latency degrades above 10k messages per conversation.

## Proposal
Add a HistoryCache module between API and ConversationStore. 
Read-through cache, invalidated on write. API → HistoryCache 
→ ConversationStore.

## Rejected alternatives
- Add caching inside ConversationStore: violates its "doesn't do 
  performance heuristics" boundary.
- Cache at the HTTP layer: couples cache to transport; internal 
  callers would bypass it.
```

Wait for the human. Once adopted:

1. Update DESIGN.md to include HistoryCache in Modules, 
   Architecture diagram, and Data Flow.
2. Mark the proposal adopted, fill in Outcome.
3. Commit the design change alone (no code yet).
4. Now go to Step 3 above and plan the implementation blueprint.
