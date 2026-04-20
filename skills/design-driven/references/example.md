# Example walkthrough

One task, end to end, through the design-driven loop. Use this as a 
feel-for-the-rhythm reference, not a literal script.

## The task

> "Add a `/history` endpoint that returns the last N messages in a 
> conversation."

## Step 1 — Read current state + check pending claims

**Current state** (what the system actually is):

Open `design/DESIGN.md` and read the relevant code.

- There's a `ConversationStore` module that owns message persistence.
- The `API` module owns HTTP routing.
- "Doesn't do" on `API`: no business logic, only shape conversion.
- Key mechanism: all reads go through `ConversationStore.query()`.
- Skim `ConversationStore` source to confirm `query()` actually matches 
  what DESIGN.md says. If they disagree, stop — that's drift and 
  calls for `/design-driven audit`, not new work on a stale skeleton.

**Pending claims** (what's queued or in flight):

- `blueprints/` for `in-progress` files — none (no concurrent work)
- Recent done blueprints' `## Follow-ups` sections — anything that 
  sounds like this task or blocks it? None.
- `design/decisions/` for `proposed` files — none in this area

Nothing blocks the plan. Proceed.

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
### Behavior
- [ ] GET /history/:id returns last N messages, default 50
- [ ] Returns 404 for missing conversation
- [ ] Integration test passes against the real store

### Design constraints
- [ ] Stays within API module — no store internals exposed
- [ ] ConversationStore.query() still the only read path
- [ ] No new module introduced (no shape change → no proposal needed)

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

- Behavior: all four pass → ✓
- Design constraints: API stayed thin, store was only read via query(), 
  no new modules → ✓

Re-read the blueprint. Nothing out of scope crept in. Pagination 
cursors stayed out — good.

## Step 6 — Close out

Feed learnings back before tearing down scaffolding:

- **Doc-only drift?** `ConversationStore.query()` gained a `limit` arg 
  during build. DESIGN.md only says "reads go through query()", which 
  is still accurate — no update needed. (If DESIGN.md had enumerated 
  query()'s parameters, we'd update it here.)
- **Follow-ups?** Yes — pagination cursors, which got scope-shaved. 
  Add a `## Follow-ups` section to this blueprint:
  ```
  ## Follow-ups
  - paginate-history — cursor-based pagination for /history; 
    current endpoint returns newest N only, no way to page back
  ```
- **Recurring pattern?** "Endpoint → query() with new param" is likely 
  to repeat. Not yet worth a DESIGN.md edit, but flag for the next 
  time it happens.

Strip TODO and State sections (keep Follow-ups). Flip Status to `done`. 
Commit the blueprint together with the code.

---

## Next session — Task B picks up

Days later, a new session arrives with: "add keyword search to /history".

Task B doesn't care what Task A did. It reads **current state**:

- `DESIGN.md` says `ConversationStore.query()` is the single read path 
  and supports id/time-based retrieval.
- Reading `query()` in the code: signature takes id, time range, and 
  a `limit`. DESIGN.md still matches the code — the `limit` is a 
  dimension within "read by id/time" (it bounds results, doesn't 
  change the query *kind*). No drift.

Then pending-claims scan:

- `blueprints/in-progress/*` — none
- Recent done blueprints' Follow-ups — `paginate-history` is the only 
  hit, and it's about cursor pagination, not keyword search. Not this 
  task.
- `design/decisions/` for `proposed` files — none near this area

**Shape question**: adding keyword filter to `query()`. DESIGN.md says 
`query()` supports id/time retrieval. Keyword search is a different 
**kind** of query (content-based vs metadata-based), not another bound 
on the same kind. That's a mechanism extension, not a parameter tweak.

Verdict: shape territory. Write proposal `009-query-text-filter.md` 
before coding. If adopted, update DESIGN.md's Key Mechanisms to widen 
`query()`'s description, then plan Task B's blueprint.

**The point**: Task B made this judgment entirely by reading current 
DESIGN.md and current code — zero dependency on what Task A's 
blueprint said. That's the invariant worth preserving.

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
