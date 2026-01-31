# PR Description Guide

A comprehensive guide to writing PR descriptions that help reviewers understand your changes quickly and accurately.

## The 30-Second Rule

A reviewer should understand the PR's purpose within 30 seconds of opening it. This means:
- Title tells them WHAT
- First paragraph tells them WHY
- Rest helps them HOW (to review)

## Title Format

```
<type>(<scope>): <subject>

Examples:
feat(auth): add OAuth2 login with Google provider
fix(orders): prevent duplicate submissions on network retry
refactor(api): extract validation middleware
perf(search): add result caching with 5-minute TTL
```

### Type Reference

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New functionality | `feat: add user registration` |
| `fix` | Bug fix | `fix: correct price calculation rounding` |
| `refactor` | Code restructuring (no behavior change) | `refactor: extract email service` |
| `perf` | Performance improvement | `perf: batch database queries` |
| `docs` | Documentation only | `docs: add API authentication guide` |
| `test` | Test additions/changes | `test: add integration tests for checkout` |
| `chore` | Build, CI, tooling | `chore: upgrade webpack to v5` |

### Scope (Optional)

Scope identifies the affected module/area:
- `(auth)` - authentication
- `(api)` - API layer
- `(ui)` - user interface
- `(db)` - database
- Custom scope matching your project structure

### Subject Guidelines

- Use imperative mood: "add" not "added" or "adds"
- Don't capitalize first letter (after type/scope)
- No period at end
- Max 50 characters for subject
- Be specific: "fix null check" → "prevent crash when user has no email"

## Description Structure

### Template

```markdown
## Summary

[1-2 sentences explaining what this PR does and why it's needed]

## Changes

[Grouped bullet points of significant changes]

### [Group 1 - e.g., "API Changes"]
- Change 1
- Change 2

### [Group 2 - e.g., "Database"]
- Change 3

## How It Works

[For complex changes - explanation with diagrams]

## Testing

[How to verify the changes]

## Notes for Reviewer

[Areas needing attention, questions, known limitations]
```

### Summary Section

**Purpose**: Answer "What does this PR do?" in 1-2 sentences.

**Good**:
> Adds rate limiting to the public API to prevent abuse. Limits requests to 100/minute per API key with a sliding window algorithm.

**Bad**:
> Updates the API.

> This PR adds rate limiting functionality to prevent users from making too many requests to our API which could overload our servers and cause issues for other users...

### Changes Section

**Purpose**: Give reviewers a map of what changed.

**Good**:
```markdown
## Changes

### Rate Limiting
- Add `RateLimiter` class with sliding window algorithm
- Integrate limiter middleware into API router
- Return 429 status with `Retry-After` header when limited

### Configuration
- Add `RATE_LIMIT_REQUESTS` env var (default: 100)
- Add `RATE_LIMIT_WINDOW_MS` env var (default: 60000)

### Tests
- Unit tests for `RateLimiter` class
- Integration tests for rate limit responses
```

**Bad**:
```markdown
## Changes
- Modified api/middleware/rateLimiter.ts
- Modified api/router.ts
- Modified config/env.ts
- Added tests
```

### Testing Section

**Purpose**: Tell reviewers how to verify the change works.

**Include**:
- How to trigger the behavior locally
- What to look for in the result
- Any test data or setup needed

**Good**:
```markdown
## Testing

1. Start the dev server: `npm run dev`
2. Make rapid API calls: `for i in {1..110}; do curl -s http://localhost:3000/api/users; done`
3. Expected: First 100 calls succeed, remaining calls return 429

Automated tests: `npm test -- --grep "rate limit"`
```

### Notes for Reviewer

**Purpose**: Direct reviewer attention where it's most needed.

**Good**:
```markdown
## Notes for Reviewer

- **Security review needed**: The token validation in `auth/validate.ts:45-67` handles user input
- **Performance question**: The caching strategy in `services/cache.ts` uses memory - is Redis preferred?
- **Known limitation**: Rate limits are per-instance, not distributed (follow-up for Redis-based limits)
```

## ASCII Diagrams

### When to Use Diagrams

Use diagrams when:
- Flow involves 3+ steps
- Multiple components interact
- State changes occur
- Data transforms through stages
- Before/after comparison helps

### Basic Box Diagrams

**Component interaction**:
```
┌──────────┐         ┌──────────┐
│  Client  │────────>│   API    │
└──────────┘         └──────────┘
                          │
                          ▼
                     ┌──────────┐
                     │ Database │
                     └──────────┘
```

**Characters**:
- Boxes: `┌ ┐ └ ┘ │ ─`
- Arrows: `→ ← ↑ ↓ ▶ ◀ ▲ ▼`
- Corners: `┌ ┐ └ ┘`
- Junctions: `├ ┤ ┬ ┴ ┼`

### Sequence/Flow Diagrams

**Request flow**:
```
Client          API Gateway       Auth Service       Database
  │                  │                  │                │
  │─── Request ─────>│                  │                │
  │                  │─── Validate ────>│                │
  │                  │<── Token OK ─────│                │
  │                  │                  │                │
  │                  │───────── Query ──────────────────>│
  │                  │<──────── Result ─────────────────│
  │<── Response ─────│                  │                │
  │                  │                  │                │
```

### State Diagrams

**Order state machine**:
```
                    ┌─────────────┐
         ┌─────────>│   PENDING   │
         │          └─────────────┘
         │                 │
         │                 │ payment_received
         │                 ▼
         │          ┌─────────────┐
 cancel  │          │  CONFIRMED  │
         │          └─────────────┘
         │                 │
         │                 │ shipped
         │                 ▼
         │          ┌─────────────┐
         └──────────│   SHIPPED   │
                    └─────────────┘
                           │
                           │ delivered
                           ▼
                    ┌─────────────┐
                    │  DELIVERED  │
                    └─────────────┘
```

### Data Flow Diagrams

**Pipeline transformation**:
```
Raw Input          Parsed           Validated         Stored
    │                │                  │                │
    ▼                ▼                  ▼                ▼
┌────────┐      ┌────────┐        ┌────────┐      ┌────────┐
│ JSON   │─────>│ Object │───────>│ Entity │─────>│ Record │
│ String │      │ w/types│        │ w/rules│      │ in DB  │
└────────┘      └────────┘        └────────┘      └────────┘

    parse()       validate()       save()
```

### Before/After Diagrams

**Architecture change**:
```
BEFORE:
┌────────────────────────────────────────┐
│              Monolith                  │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐   │
│  │Auth │  │Users│  │Orders│ │Payment│  │
│  └─────┘  └─────┘  └─────┘  └─────┘   │
└────────────────────────────────────────┘

AFTER:
┌─────────┐    ┌─────────┐    ┌─────────┐
│Auth Svc │    │User Svc │    │Order Svc│
└────┬────┘    └────┬────┘    └────┬────┘
     │              │              │
     └──────────────┼──────────────┘
                    │
              ┌─────┴─────┐
              │  Message  │
              │   Queue   │
              └───────────┘
```

### Decision Trees

**Logic flow**:
```
                    START
                      │
                      ▼
               Is user logged in?
                   /      \
                 YES       NO
                  │         │
                  ▼         ▼
           Has permission?  Redirect to
              /    \        login page
            YES     NO           │
             │       │           │
             ▼       ▼           ▼
          Execute   Show        END
           action   403
             │       │
             ▼       ▼
            END     END
```

### Table Layouts

**Data structure comparison**:
```
┌──────────────┬──────────────┬──────────────┐
│    Field     │    Before    │    After     │
├──────────────┼──────────────┼──────────────┤
│ user_id      │ INT          │ UUID         │
│ email        │ VARCHAR(100) │ VARCHAR(255) │
│ created_at   │ TIMESTAMP    │ TIMESTAMPTZ  │
│ metadata     │ (none)       │ JSONB        │
└──────────────┴──────────────┴──────────────┘
```

## Language-Specific Tips

### Backend Changes

Include:
- API endpoint changes (method, path, params)
- Request/response format changes
- Database schema changes
- Performance implications

```markdown
### API Changes

`POST /api/orders` - Create order

Request body:
```json
{
  "items": [{"product_id": "...", "quantity": 1}],
  "shipping_address": {...}
}
```

Response (201):
```json
{
  "order_id": "...",
  "status": "pending",
  "estimated_delivery": "2024-01-15"
}
```
```

### Frontend Changes

Include:
- Screenshots or before/after (if visual)
- User interaction changes
- Component hierarchy changes

```markdown
### UI Changes

**Before**: Single "Submit" button
**After**: "Submit" button + "Save Draft" option

Component tree:
```
OrderForm
├── ItemList
├── ShippingForm
└── ActionBar (new)
    ├── SubmitButton
    └── SaveDraftButton (new)
```
```

### Database Changes

Include:
- Migration safety (backward compatible?)
- Data transformation needed
- Rollback plan

```markdown
### Database Migration

1. Add nullable column `new_field` (backward compatible)
2. Backfill existing records
3. Set NOT NULL constraint

Rollback: `rails db:rollback STEP=1` removes the column
```

## Common Mistakes

### Too Vague

**Bad**: "Fix issue with login"
**Good**: "Fix login failure when user email contains plus sign"

### Too Verbose

**Bad**: 500-word description for a 20-line change
**Good**: Match description length to change complexity

### Missing Context

**Bad**: "Refactor user service"
**Good**: "Refactor user service to support upcoming multi-tenant feature (see RFC-123)"

### Implementation Details as Description

**Bad**: "Change line 45 from X to Y, update function call on line 78..."
**Good**: "Fix race condition in concurrent user updates by adding optimistic locking"

## Checklist

Before submitting:

- [ ] Title follows `type(scope): subject` format
- [ ] Summary explains what AND why in 1-2 sentences
- [ ] Changes are grouped logically, not by file
- [ ] Complex logic has ASCII diagram or explanation
- [ ] Testing instructions are specific and actionable
- [ ] Reviewer attention directed to critical areas
- [ ] No implementation details masquerading as description
