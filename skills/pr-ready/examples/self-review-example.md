# Self-Review Example

A walkthrough of the self-review workflow before requesting review.

## Scenario

User says: "review my changes before I ask for review"

## Stage 1: Gather Changes

```bash
$ git diff --stat main...HEAD
 src/api/handlers/payment.ts         | 234 ++++++++++++++++++++
 src/api/middleware/rateLimit.ts     |  67 ++++++
 src/services/payment/processor.ts   | 312 +++++++++++++++++++++++++++
 src/services/payment/validator.ts   |  89 ++++++++
 src/types/payment.ts                |  56 +++++
 tests/services/payment.test.ts      | 145 +++++++++++++
 6 files changed, 903 insertions(+)

$ git log --oneline main..HEAD
f1a2b3c feat(payment): add payment processing with Stripe
e2b3c4d feat(payment): add payment validation
d3c4e5f feat(payment): add rate limiting to payment endpoints
```

**Metrics**:
- 6 files changed
- 903 lines added
- 3 commits
- Feature: Payment processing system

## Stage 2: Reviewability Assessment

### Size

903 lines total
- Production code: 758 lines
- Test code: 145 lines
- Effective: 758 + (145 * 0.5) = 830 lines

**Assessment**: Large (800-1500 range) - Reviewer will need focused attention.

### Purpose

All payment-related:
- API handler for payment processing
- Rate limiting middleware
- Payment processor service
- Validation service
- Type definitions
- Tests

**Assessment**: Single purpose - OK.

```
Size Assessment: Large (830 effective lines)
- Reviewer may miss issues in a change this size
- Consider: Can any part be a separate PR?

Potential splits identified:
1. Rate limiting middleware (67 lines) - Could be separate
2. Everything else is tightly coupled

Recommendation: Rate limiting could be its own PR, but
the coupling is low enough to proceed if preferred.

Proceeding with self-review to identify issues...
```

## Stage 3: Self-Review Analysis

### 3.1 Reviewer First Impression

Simulating what a reviewer sees first:

**Title**: `feat(payment): add payment processing with Stripe`

**Files at a glance**:
```
 payment.ts         | 234 ++ (API handler)
 rateLimit.ts       |  67 ++ (middleware)
 processor.ts       | 312 ++ (core logic)
 validator.ts       |  89 ++ (validation)
 payment.ts         |  56 ++ (types)
 payment.test.ts    | 145 ++ (tests)
```

**First impression**: Clear feature, files named sensibly, reasonable structure.

**Issue**: No description yet - reviewer won't understand the scope or approach.

### 3.2 Code Quality Scan

Scanning for common issues...

**Debug Code Found**:
```
src/services/payment/processor.ts:156
  console.log('Processing payment:', paymentData);

src/services/payment/processor.ts:201
  // TODO: Add retry logic for transient failures
```

**Potential Security Issues**:
```
src/api/handlers/payment.ts:45
  const apiKey = process.env.STRIPE_API_KEY;
  // ⚠️ No check for undefined - will crash if not set

src/services/payment/processor.ts:78
  const amount = req.body.amount;
  // ⚠️ No validation before passing to Stripe
  // (validator.ts exists but not used here)
```

**Error Handling Gaps**:
```
src/services/payment/processor.ts:123-145
  // Network call to Stripe API
  // ⚠️ No timeout configured
  // ⚠️ Generic catch block loses error context
```

### 3.3 Architecture Review

**Data Flow**:
```
Request → Handler → Validator → Processor → Stripe API
                                    ↓
                              Response ← ←
```

**Issue identified**: Validator exists but handler calls processor directly:

```typescript
// src/api/handlers/payment.ts:32
export async function handlePayment(req, res) {
  const result = await processor.process(req.body);  // Skips validator!
  ...
}
```

### 3.4 Test Coverage Analysis

```
Tests found: 145 lines covering:
✓ Successful payment processing
✓ Invalid card number
✓ Insufficient funds
✓ Network timeout (mocked)

Missing coverage:
✗ Rate limit behavior
✗ Validation edge cases (negative amounts, overflow)
✗ Concurrent payment handling
✗ Idempotency key behavior
```

## Stage 4: Self-Review Report

```markdown
## Self-Review Report

### Reviewer First Impression
A reviewer opening this PR will see a clear payment feature with sensibly
named files. However, without a description, they'll need to read code to
understand the approach.

**Action needed**: Add comprehensive PR description with flow diagram.

### Issues Found

#### MUST FIX (Before requesting review)

1. **Security: Unvalidated input passed to Stripe**
   - File: `src/api/handlers/payment.ts:32`
   - Issue: Handler bypasses validator, passes raw input to processor
   - Fix: Add `validator.validate(req.body)` before processing
   ```typescript
   // Current (dangerous)
   const result = await processor.process(req.body);

   // Should be
   const validated = await validator.validate(req.body);
   const result = await processor.process(validated);
   ```

2. **Security: Missing environment variable check**
   - File: `src/api/handlers/payment.ts:45`
   - Issue: `STRIPE_API_KEY` used without checking if defined
   - Fix: Add startup check or throw clear error
   ```typescript
   const apiKey = process.env.STRIPE_API_KEY;
   if (!apiKey) {
     throw new ConfigurationError('STRIPE_API_KEY is required');
   }
   ```

3. **Debug code present**
   - File: `src/services/payment/processor.ts:156`
   - Issue: `console.log` with payment data (PCI compliance risk)
   - Fix: Remove or use structured logger without sensitive data

#### SHOULD FIX (Improves quality)

4. **Missing timeout on Stripe API call**
   - File: `src/services/payment/processor.ts:123`
   - Issue: No timeout - could hang indefinitely
   - Suggestion: Add 30s timeout with clear error message

5. **Generic error handling loses context**
   - File: `src/services/payment/processor.ts:140-145`
   - Issue: `catch (e) { throw new Error('Payment failed') }`
   - Suggestion: Preserve original error, log for debugging

6. **TODO left in code**
   - File: `src/services/payment/processor.ts:201`
   - Issue: `// TODO: Add retry logic`
   - Suggestion: Implement now, or create issue and reference it

#### CONSIDER (Optional improvements)

7. **Test coverage gaps**
   - Missing: Rate limit tests, validation edge cases
   - Suggestion: Add tests or note as known limitation

8. **Rate limiting could be separate PR**
   - The middleware is independent and adds 67 lines
   - Splitting would make both PRs easier to review

### Potential Reviewer Questions

Prepare answers for:

1. **Q: Why Stripe over other payment processors?**
   A: [Prepare: Business decision? API quality? Cost?]

2. **Q: How are failed payments retried?**
   A: [Currently: They aren't - add TODO issue reference]

3. **Q: What happens if Stripe is down?**
   A: [Returns 503 with retry-after header - verify this is true]

4. **Q: Is this PCI compliant?**
   A: [Using Stripe Elements = card data never hits our servers]

### Suggested Description Improvements

Current description: (none)

Suggested description should include:
1. Summary of the payment flow
2. ASCII diagram of request flow
3. Security considerations addressed
4. Testing instructions with test card numbers
5. Note about PCI compliance approach

### Summary

Before requesting review:
- [ ] Fix 3 MUST FIX issues (security, debug code)
- [ ] Add comprehensive PR description
- [ ] Consider 3 SHOULD FIX items
- [ ] Prepare answers for likely questions

Estimated fixes: 30-60 minutes

After fixes, this PR will be ready for effective review.
```

## Stage 5: User Actions

User reviews the report and addresses issues:

```bash
# Fix validation bypass
# Fix env var check
# Remove debug code
# Add timeout
# Improve error handling
# Remove TODO (create issue instead)

$ git add -A
$ git commit -m "fix: address self-review findings

- Add input validation before payment processing
- Add startup check for required STRIPE_API_KEY
- Remove debug console.log (PCI compliance)
- Add 30s timeout on Stripe API calls
- Preserve error context in catch blocks
- Create #789 for retry logic (remove TODO)"
```

## Final Output

```
✓ Self-Review Complete

Issues identified: 8
- MUST FIX: 3 (critical for security/quality)
- SHOULD FIX: 3 (improves quality)
- CONSIDER: 2 (optional)

Status after your fixes:
✓ Security issues addressed
✓ Debug code removed
✓ Error handling improved
✓ Description ready to add

Remaining suggestions (optional):
- Add rate limit tests
- Consider splitting rate limit middleware

Your PR is now ready for external review. The self-review
process helped identify issues that reviewers would have
flagged, saving time for everyone.

Ready to create the PR with the suggested description?
```
