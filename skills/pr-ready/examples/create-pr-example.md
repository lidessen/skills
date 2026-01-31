# Create PR Example

A walkthrough of creating a well-described pull request.

## Scenario

User says: "create a pr for my changes"

## Stage 1: Gather Changes

```bash
$ git remote show origin | grep 'HEAD branch'
  HEAD branch: main

$ git log --oneline main..HEAD
a1b2c3d feat(checkout): add coupon code validation
b2c3d4e feat(checkout): implement coupon input UI
c3d4e5f feat(checkout): add coupon API endpoints
d4e5f6g test(checkout): add coupon validation tests

$ git diff --stat main...HEAD
 src/api/routes/coupons.ts           |  87 ++++++++++++++
 src/api/routes/index.ts             |   3 +
 src/components/checkout/Cart.tsx    |  15 ++-
 src/components/checkout/Coupon.tsx  | 124 +++++++++++++++++++
 src/services/coupon.ts              | 156 ++++++++++++++++++++++++
 src/types/coupon.ts                 |  42 +++++++
 tests/api/coupons.test.ts           | 178 ++++++++++++++++++++++++++++
 tests/services/coupon.test.ts       | 145 +++++++++++++++++++++++
 8 files changed, 748 insertions(+), 2 deletions(-)
```

**Metrics**:
- 8 files changed
- 750 lines added
- 4 commits
- Single feature: Coupon code system

## Stage 2: Reviewability Check

### Size Assessment

750 lines - **Acceptable** (400-800 range)

Breakdown:
- Production code: 427 lines
- Test code: 323 lines
- Effective size: 427 + (323 * 0.5) = 588 lines

### Mixed Concerns Check

All changes relate to coupon functionality:
- API endpoints for coupons
- UI component for coupon input
- Service layer with business logic
- Type definitions
- Tests

**Result**: Single purpose - no split needed.

```
✓ Reviewability Check Passed

Size: 750 lines (588 effective)
Purpose: Single feature - Coupon code system
Recommendation: Proceed with PR creation
```

## Stage 3: Analyze for Description

### Understand the Changes

**API Layer** (`src/api/routes/coupons.ts`):
- `POST /coupons/validate` - Validate coupon code
- `GET /coupons/:code` - Get coupon details

**Service Layer** (`src/services/coupon.ts`):
- Validation rules (expiry, usage limits, minimum order)
- Discount calculation (percentage, fixed amount)
- Usage tracking

**UI Layer** (`src/components/checkout/Coupon.tsx`):
- Input field with apply button
- Loading state during validation
- Success/error display
- Integration with cart total

**Data Flow**:
```
User Input → API Validation → Service Rules → Discount Applied → Cart Updated
```

## Stage 4: Generate Description

### Title

```
feat(checkout): add coupon code system with validation and discounts
```

### Full Description

```markdown
## Summary

Adds a complete coupon code system to the checkout flow. Users can enter coupon codes to receive discounts on their orders, with real-time validation and clear feedback.

## Changes

### API Endpoints
- `POST /api/coupons/validate` - Validates code and returns discount details
- `GET /api/coupons/:code` - Retrieves coupon information (admin use)

### Business Logic
- Coupon validation rules: expiry date, usage limits, minimum order value
- Two discount types: percentage (e.g., 20% off) and fixed amount (e.g., $10 off)
- Usage tracking to enforce per-user and total usage limits

### UI Components
- New `Coupon` component with input field and apply button
- Real-time validation feedback (success/error states)
- Applied discount shown in cart summary

## How It Works

### Coupon Validation Flow

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│   User     │     │    API     │     │  Service   │
│  (Coupon   │────>│ /validate  │────>│  Coupon    │
│   Input)   │     │            │     │  Validator │
└────────────┘     └────────────┘     └─────┬──────┘
                                            │
           ┌────────────────────────────────┼────────────────────────────────┐
           │                                │                                │
           ▼                                ▼                                ▼
    ┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
    │ Check       │                 │ Check       │                 │ Check       │
    │ Expiry Date │                 │ Usage Limit │                 │ Min Order   │
    └──────┬──────┘                 └──────┬──────┘                 └──────┬──────┘
           │                                │                                │
           └────────────────────────────────┼────────────────────────────────┘
                                            │
                                            ▼
                                    ┌─────────────┐
                                    │  Calculate  │
                                    │  Discount   │
                                    └──────┬──────┘
                                            │
                                            ▼
                                    ┌─────────────┐
                                    │   Return    │
                                    │   Result    │
                                    └─────────────┘
```

### Discount Calculation

```
┌─────────────────────────────────────────────────────────┐
│                    Coupon Types                         │
├────────────────────────┬────────────────────────────────┤
│    PERCENTAGE          │         FIXED_AMOUNT           │
├────────────────────────┼────────────────────────────────┤
│ discount = subtotal    │ discount = coupon.amount       │
│            * (pct/100) │                                │
│                        │                                │
│ Example:               │ Example:                       │
│ $100 order, 20% off    │ $100 order, $15 off            │
│ discount = $20         │ discount = $15                 │
└────────────────────────┴────────────────────────────────┘
```

## Testing

### Automated Tests
```bash
npm test -- --grep "coupon"
```

Covers:
- Valid/invalid coupon codes
- Expiry date validation
- Usage limit enforcement
- Both discount types
- Edge cases (empty input, special characters)

### Manual Testing
1. Start dev server: `npm run dev`
2. Add items to cart (total > $50 for some test coupons)
3. Test coupons:
   - `SAVE20` - 20% off (valid)
   - `FLAT10` - $10 off (valid)
   - `EXPIRED` - Should show "Coupon expired"
   - `INVALID` - Should show "Invalid coupon code"

## Notes for Reviewer

- **Security**: Coupon validation happens server-side only. The client receives discount amount but cannot manipulate it.

- **Race condition handled**: `src/services/coupon.ts:78-92` uses database transaction to prevent same coupon being used beyond its limit.

- **Question**: Should we add rate limiting to the validate endpoint? Currently unlimited, could be abused for code enumeration.

## Related

- Design doc: [Coupon System RFC](link-to-rfc)
- Issue: Closes #456
```

## Stage 5: Create PR

```bash
$ gh pr create \
  --title "feat(checkout): add coupon code system with validation and discounts" \
  --body "$(cat << 'EOF'
## Summary

Adds a complete coupon code system to the checkout flow...
[full description as above]
EOF
)"

Creating pull request for feature/coupon-codes into main in org/repo

https://github.com/org/repo/pull/789
```

## Final Output

```
✓ Pull Request Created

Title: feat(checkout): add coupon code system with validation and discounts
URL: https://github.com/org/repo/pull/789

Summary:
- 8 files changed (+750 lines)
- 4 commits
- Includes tests (323 lines)
- Closes #456

Description includes:
- Summary of the feature
- Grouped changes by layer
- ASCII diagrams for validation flow and discount types
- Testing instructions
- Security considerations
- Open question for reviewer

The PR description helps reviewers:
1. Understand the purpose in 30 seconds (Summary)
2. Navigate the changes (Grouped list)
3. Understand complex logic (ASCII diagrams)
4. Verify the changes work (Testing section)
5. Know where to focus (Notes for Reviewer)
```
