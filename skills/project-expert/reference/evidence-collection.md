# Evidence Collection Reference

Comprehensive guide for collecting, organizing, and presenting evidence-based answers.

## Table of Contents
- [Evidence Quality Levels](#evidence-quality-levels)
- [Collection Templates](#collection-templates)
- [Citation Formats](#citation-formats)
- [Evidence Synthesis](#evidence-synthesis)
- [Handling Uncertainty](#handling-uncertainty)
- [Multi-Source Verification](#multi-source-verification)

## Evidence Quality Levels

Not all evidence is equal. Understand the hierarchy:

### Level 1: Definitive Evidence (Highest Quality)
**Source types**:
- Official documentation
- Type definitions and interfaces
- Test cases with assertions
- Configuration files
- Explicit comments explaining behavior

**Characteristics**:
- Authoritative
- Unambiguous
- Current and maintained
- Multiple confirming sources

**Example**:
```
Source: docs/api/authentication.md:45-50
Evidence: "Authentication uses JWT tokens with 15-minute expiry"

Source: src/auth/config.ts:12
Evidence: `const TOKEN_EXPIRY = '15m'`

Source: tests/auth.test.ts:89
Evidence: `expect(token.expiresIn).toBe('15m')`

Quality: Level 1 - Three authoritative sources confirm behavior
```

### Level 2: Strong Evidence
**Source types**:
- Implementation code
- API responses/schemas
- Code comments (non-TODO)
- Recent commits with explanations
- README files

**Characteristics**:
- Reliable but may require interpretation
- Single authoritative source
- Clear implementation

**Example**:
```
Source: src/services/payment.ts:234-245
Evidence: Implementation shows retry logic with 3 attempts

Quality: Level 2 - Implementation is clear but not documented
```

### Level 3: Circumstantial Evidence
**Source types**:
- Variable naming
- Code structure and patterns
- Import statements
- File organization

**Characteristics**:
- Suggestive but not definitive
- Requires inference
- Should be verified with stronger evidence

**Example**:
```
Source: src/services/email.ts:5
Evidence: `import { SESClient } from '@aws-sdk/client-ses'`

Quality: Level 3 - Suggests AWS SES for email, but not confirmed
```

### Level 4: Weak Evidence (Use Cautiously)
**Source types**:
- TODO comments
- Commented-out code
- Old documentation
- Inconsistent naming

**Characteristics**:
- May be outdated
- Potentially misleading
- Requires strong caveats

**Example**:
```
Source: src/legacy/old-auth.ts:12 (commented out)
Evidence: "// TODO: Migrate to OAuth2"

Quality: Level 4 - Indicates possible future direction, not current state
```

## Collection Templates

### Template 1: Feature Explanation

```markdown
**Question**: [Restate question]

**Answer**: [Direct answer in 1-2 sentences]

**Evidence**:

1. **Documentation** (Level 1)
   - Source: [file:line]
   - Finding: "[Quote or summary]"
   - Relevance: [How this answers the question]

2. **Implementation** (Level 2)
   - Source: [file:line]
   - Finding: "[Key code snippet or description]"
   - Relevance: [What this shows]

3. **Tests** (Level 1)
   - Source: [file:line]
   - Finding: "[Test assertion or behavior]"
   - Relevance: [What this confirms]

**Summary**: [Synthesis of evidence in 2-3 sentences]
```

### Template 2: Technical Detail

```markdown
**Question**: [Restate question]

**Answer**: [Direct answer]

**Evidence**:

**Configuration** (Level 1):
- [file:line]: [Config value]

**Implementation** (Level 2):
- [file:line]: [How it's implemented]

**Usage Example** (Level 2):
- [file:line]: [Real usage in codebase]

**Verification**: [How evidence confirms answer]
```

### Template 3: Uncertain Answer

```markdown
**Question**: [Restate question]

**Partial Answer**: [What can be confirmed]

**Evidence Found**:
- [file:line]: [Partial information]
- [file:line]: [Related information]

**Gaps**:
- Cannot confirm: [Specific missing information]
- Not found in: [Where searched]

**Next Steps**:
Would you like me to:
1. [Alternative search location]
2. [Different approach]
3. [Related information that might help]
```

### Template 4: Multi-Aspect Answer

For complex questions with multiple parts:

```markdown
**Question**: [Restate question]

**Overview**: [High-level answer]

**Aspect 1: [Name]**
- Answer: [Specific answer]
- Evidence: [file:line] - [Finding]

**Aspect 2: [Name]**
- Answer: [Specific answer]
- Evidence: [file:line] - [Finding]

**Aspect 3: [Name]**
- Answer: [Specific answer]
- Evidence: [file:line] - [Finding]

**Integration**: [How aspects work together]
```

## Citation Formats

### Standard Citation Format

```
[file-path]:[line-number] - [description]
```

**Examples**:
```
src/auth/handler.ts:45 - JWT generation logic
docs/api/endpoints.md:120-135 - POST /auth/login documentation
tests/user.test.ts:89 - User creation test case
config/database.ts:12 - Database connection config
```

### Code Snippet Citation

```markdown
**Source**: [file:line]
```typescript
[relevant code snippet]
```
**Explanation**: [What this code shows]
```

**Example**:
```markdown
**Source**: src/auth/jwt.ts:34-38
```typescript
export function generateToken(userId: string): string {
  return jwt.sign({ userId }, SECRET_KEY, {
    expiresIn: '15m'
  });
}
```
**Explanation**: Tokens expire after 15 minutes as configured
```

### Range Citation

For multi-line evidence:

```
[file:line-start-line-end] - [description]
```

**Example**:
```
src/payment/processor.ts:120-150 - Complete payment flow implementation
```

### Multiple File Citation

When evidence spans multiple files:

```markdown
**Evidence across multiple sources**:
1. [file1:line] - [aspect 1]
2. [file2:line] - [aspect 2]
3. [file3:line] - [aspect 3]

These sources collectively show: [synthesis]
```

## Evidence Synthesis

### Combining Multiple Sources

**Pattern**: Start with strongest evidence, support with additional sources

```markdown
**Primary Evidence** (Level 1):
docs/api/README.md:23 - Documents rate limit of 100 req/min

**Supporting Evidence** (Level 2):
src/middleware/rateLimit.ts:15 - Implements limit with express-rate-limit
config/api.ts:8 - Configuration: `maxRequests: 100, windowMs: 60000`

**Verification** (Level 1):
tests/rateLimit.test.ts:45 - Test confirms 429 status after 100 requests

**Synthesis**: Rate limiting is set to 100 requests per minute,
confirmed by documentation, implementation, and tests.
```

### Resolving Conflicting Evidence

When sources contradict:

```markdown
**Conflict Identified**:

**Source A** (Level 2):
src/config/old.ts:12 - Shows limit of 50 req/min

**Source B** (Level 1):
docs/api/README.md:23 - Documents limit of 100 req/min

**Resolution**:
1. Checked git history: config/old.ts last modified 6 months ago
2. docs/api/README.md updated last week
3. Production config checked: config/production.ts:15 shows 100

**Conclusion**: Current limit is 100 req/min (documentation and
production config), old config file is outdated.
```

### Inferential Evidence

When direct evidence is unavailable:

```markdown
**Direct Evidence**: None found

**Inferential Evidence**:
1. src/database/connection.ts:8 - Uses PostgreSQL driver
2. package.json:34 - Dependency: pg@8.11.0
3. config/database.ts:15 - Connection string format matches PostgreSQL

**Inference**: System uses PostgreSQL database (confidence: high)

**Caveat**: No explicit documentation confirms database choice,
inference based on implementation details.
```

## Handling Uncertainty

### Degrees of Certainty

**Confirmed** (100% certain):
- Multiple Level 1 sources agree
- Documentation + implementation + tests align

```markdown
✓ Confirmed: [Finding]
Evidence: [Multiple Level 1 sources]
```

**Highly Likely** (90% certain):
- Strong implementation evidence
- No contradicting sources
- Aligns with project patterns

```markdown
Highly Likely: [Finding]
Evidence: [Level 2 sources]
Note: Not explicitly documented but implementation is clear
```

**Probable** (70% certain):
- Circumstantial evidence
- Consistent patterns
- Reasonable inference

```markdown
Probable: [Finding]
Evidence: [Level 3 sources]
Note: Based on code patterns and structure, not explicit confirmation
```

**Uncertain** (<70% certain):
- Weak or conflicting evidence
- Gaps in information
- Requires assumption

```markdown
Uncertain: [Finding]
Evidence: [Limited sources]
Gaps: [What's missing]
Recommendation: [What needs verification]
```

### Communicating Uncertainty

**Clear statement of confidence**:
```markdown
Based on available evidence, I am [certainty level] that [finding].

I searched:
- [Location 1] - [Result]
- [Location 2] - [Result]
- [Location 3] - [Result]

To confirm definitively, would need:
- [Missing piece 1]
- [Missing piece 2]
```

**Acknowledge limitations**:
```markdown
I found evidence for [partial answer], but cannot confirm [aspect]
without access to [missing resource].
```

### When to Stop Searching

**Stop when**:
- ✓ Multiple Level 1 sources confirm finding
- ✓ Documentation + implementation align
- ✓ Tests verify behavior
- ✓ All reasonable search locations exhausted

**Continue when**:
- ✗ Only circumstantial evidence
- ✗ Contradicting sources unresolved
- ✗ Obvious search locations not checked
- ✗ Critical information still missing

## Multi-Source Verification

### Triangle Verification Pattern

**Strongest evidence**: Three independent sources

```markdown
**Documentation**: [file:line] - States X
**Implementation**: [file:line] - Implements X
**Tests**: [file:line] - Verifies X

Triangle verified: All three sources confirm [finding]
```

### Cross-Reference Pattern

Trace through multiple layers:

```markdown
**Layer 1 - Entry Point**:
src/routes/api.ts:45 - Route definition for POST /users

**Layer 2 - Handler**:
src/controllers/user.ts:89 - Calls userService.create()

**Layer 3 - Service**:
src/services/user.ts:123 - Implements user creation logic

**Layer 4 - Data**:
src/models/user.ts:15 - User model definition

**Layer 5 - Persistence**:
src/repositories/user.ts:34 - Database insertion

**Verification**: Complete flow traced from API to database
```

### Contradiction Investigation Pattern

When sources disagree:

```markdown
**Investigate**:
1. Check timestamps: Which is newer?
2. Check git history: What changed and why?
3. Check environment: Dev vs production config?
4. Check scope: Different features or edge cases?
5. Check comments: Deprecated or experimental?

**Resolution**: [Finding with explanation of discrepancy]
```

## Evidence Organization Strategies

### By Strength (Recommended)

Present strongest evidence first:

```markdown
**Level 1 Evidence**:
- [Source 1]
- [Source 2]

**Level 2 Evidence**:
- [Source 3]

**Level 3 Evidence**:
- [Source 4]
```

### By Topic

For complex multi-faceted questions:

```markdown
**Authentication Method**:
- [Evidence 1]
- [Evidence 2]

**Token Expiry**:
- [Evidence 3]
- [Evidence 4]

**Refresh Logic**:
- [Evidence 5]
- [Evidence 6]
```

### By Source Type

When source types matter:

```markdown
**Documentation**:
- [Doc source 1]
- [Doc source 2]

**Implementation**:
- [Code source 1]
- [Code source 2]

**Configuration**:
- [Config source 1]
- [Config source 2]
```

## Practical Examples

### Example 1: Complete Evidence Collection

**Question**: "How are errors handled in the payment processing?"

**Collection Process**:

```markdown
**Search performed**:
1. grep -r "payment.*error\|error.*payment" docs/
2. grep -r "class.*Payment.*Error" src/
3. grep -r "try.*payment\|catch" src/payment/
4. grep -r "test.*payment.*error" tests/

**Evidence collected**:

**Error Types** (Level 1):
- src/payment/errors.ts:5-25 - Defines PaymentError hierarchy
  - InsufficientFundsError
  - PaymentGatewayError
  - InvalidPaymentMethodError

**Error Handling** (Level 2):
- src/payment/processor.ts:89-110 - Try-catch wraps payment gateway call
- src/payment/processor.ts:95 - Retries on gateway timeout (3 attempts)
- src/payment/processor.ts:105 - Logs errors to monitoring service

**API Response** (Level 1):
- docs/api/errors.md:67 - Documents error response format
- src/controllers/payment.ts:145 - Returns 402 for InsufficientFunds
- src/controllers/payment.ts:150 - Returns 502 for gateway errors

**Tests** (Level 1):
- tests/payment.test.ts:234 - Verifies retry logic on timeout
- tests/payment.test.ts:267 - Verifies proper error codes returned

**Answer**:
Payment processing uses a hierarchy of custom error types
(InsufficientFundsError, PaymentGatewayError, InvalidPaymentMethodError).
Gateway errors trigger 3 retry attempts with exponential backoff.
All errors are logged to the monitoring service and return appropriate
HTTP status codes (402 for insufficient funds, 502 for gateway issues).

This is confirmed by error definitions, implementation code, API
documentation, and test cases.
```

### Example 2: Uncertain Answer with Gaps

**Question**: "What's the maximum file upload size?"

**Collection Process**:

```markdown
**Search performed**:
1. grep -ri "upload.*size\|file.*size.*limit\|max.*upload" docs/
2. grep -ri "multer\|upload.*limit\|file.*size" src/
3. grep -r "MAX.*FILE\|FILE.*LIMIT" config/
4. cat .env.example | grep -i "upload\|file"

**Evidence collected**:

**Partial Evidence** (Level 3):
- src/middleware/upload.ts:12 - Uses multer middleware
- src/middleware/upload.ts:15 - Configuration: `limits: { fileSize: MAX_UPLOAD_SIZE }`

**Gap Identified**:
- MAX_UPLOAD_SIZE imported from config but not defined
- No documentation found
- Not in .env.example

**Answer**:
I found that the application uses multer for file uploads with a
configurable size limit (MAX_UPLOAD_SIZE), but I cannot determine
the actual limit value.

Evidence:
- src/middleware/upload.ts:15 - References MAX_UPLOAD_SIZE constant

Searched but not found:
- Configuration files
- Environment variable documentation
- API documentation

To find the limit, I would need to:
1. Check deployed environment variables
2. Review config/constants.ts or similar constant definitions
3. Check infrastructure/deployment configuration

Would you like me to search these locations?
```

## Quality Checklist for Evidence

Before presenting evidence:

### Collection Quality
- [ ] Searched all relevant layers (docs, code, config, tests)
- [ ] Found multiple independent sources where possible
- [ ] Noted quality level of each source
- [ ] Resolved or acknowledged any contradictions
- [ ] Identified gaps in evidence

### Citation Quality
- [ ] All sources cited with file:line format
- [ ] Code snippets included where relevant
- [ ] Context provided for each piece of evidence
- [ ] Sources listed in strength order
- [ ] Range citations used for multi-line evidence

### Presentation Quality
- [ ] Direct answer stated first
- [ ] Evidence organized logically
- [ ] Certainty level communicated clearly
- [ ] Synthesis provided at end
- [ ] Uncertainty acknowledged explicitly
- [ ] Next steps offered if evidence incomplete

### Verification Quality
- [ ] Claims supported by specific evidence
- [ ] No speculation presented as fact
- [ ] Assumptions clearly labeled
- [ ] Multiple sources verify key claims
- [ ] Implementation matches documentation
- [ ] Tests confirm expected behavior
