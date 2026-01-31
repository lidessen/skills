# Commit Example

A walkthrough of the commit workflow with split detection.

## Scenario

User says: "commit my changes"

## Stage 1: Gather Changes

```bash
$ git diff --cached --stat
 src/features/auth/login.ts       | 145 ++++++++++++++++
 src/features/auth/oauth.ts       |  98 +++++++++++
 src/services/auth.ts             |  67 ++++++++
 src/utils/http.ts                |  42 +++--
 src/utils/validation.ts          |  38 +++--
 src/core/logger.ts               |  25 ++-
 6 files changed, 378 insertions(+), 37 deletions(-)
```

**Metrics captured**:
- 6 files changed
- 378 lines added, 37 deleted
- Net: 341 lines

## Stage 2: Reviewability Check

### Analysis

Grouping by purpose:

**Group 1: Authentication Feature** (3 files, 310 lines)
- `src/features/auth/login.ts` - New login component
- `src/features/auth/oauth.ts` - New OAuth implementation
- `src/services/auth.ts` - New auth service

**Group 2: Utility Refactoring** (3 files, 68 lines)
- `src/utils/http.ts` - Refactored HTTP client
- `src/utils/validation.ts` - Refactored validators
- `src/core/logger.ts` - Refactored logger

### Detection Result

```
⚠️ Mixed Concerns Detected

Your staged changes contain two distinct purposes:

1. Feature: Authentication system (3 files, 310 lines)
   - src/features/auth/login.ts
   - src/features/auth/oauth.ts
   - src/services/auth.ts

2. Refactor: Utility improvements (3 files, 68 lines)
   - src/utils/http.ts
   - src/utils/validation.ts
   - src/core/logger.ts

Recommendation: Split into 2 commits for clearer history.

The refactoring appears independent of the feature.
Consider: Commit refactoring first, then the feature.

Options:
- [S]plit: I'll help you separate the changes
- [P]roceed: Continue with combined commit
```

## User Chooses: Split

### Split Guidance Provided

```
To split these changes:

Option 1: Reset and restage selectively
git reset HEAD                    # Unstage all
git add src/utils/ src/core/      # Stage refactoring only
# Then commit refactoring
git add src/features/ src/services/  # Stage feature
# Then commit feature

Option 2: I can help with:
git reset --soft HEAD             # Keep changes, unstage
Then I'll walk you through staging each group.

Which approach would you prefer?
```

User: "help me stage the refactoring first"

### Execute Split

```bash
# Unstage everything
$ git reset HEAD
Unstaged changes after reset:
M	src/core/logger.ts
M	src/features/auth/login.ts
...

# Stage refactoring
$ git add src/utils/http.ts src/utils/validation.ts src/core/logger.ts
```

## Stage 3: Pre-commit Checks (Refactoring)

### Debug Code Check

```bash
$ git diff --cached | grep -n "console.log\|debugger\|TODO\|FIXME"
```

Result: No debug code found.

### Breaking Change Check

Analyzing utility changes...

```
Potential Breaking Changes:

1. src/utils/http.ts:23
   - httpClient.get() now returns Promise<Response> instead of Promise<T>
   - 12 call sites in codebase may need updates

Do you want to:
- [C]heck call sites - I'll verify they're updated
- [P]roceed - I've already verified compatibility
- [A]bort - Let me fix this first
```

User: "check call sites"

```
Checking call sites for httpClient.get()...

All 12 call sites have been updated to handle Response type:
✓ src/services/user.ts:45 - Uses .json()
✓ src/services/orders.ts:23 - Uses .json()
... (10 more)

All call sites compatible. Safe to proceed.
```

## Stage 4: Generate Commit (Refactoring)

### Generated Commit Message

```
refactor: modernize utility functions

Improve HTTP client, validation, and logging utilities:
- HTTP client now returns raw Response for flexibility
- Validators use type predicates for better TypeScript inference
- Logger supports structured logging format

All existing call sites updated for new signatures.
```

### Execute Commit

```bash
$ git commit -m "refactor: modernize utility functions

Improve HTTP client, validation, and logging utilities:
- HTTP client now returns raw Response for flexibility
- Validators use type predicates for better TypeScript inference
- Logger supports structured logging format

All existing call sites updated for new signatures."

[feature-auth 7a3b2c1] refactor: modernize utility functions
 3 files changed, 68 insertions(+), 37 deletions(-)
```

## Continue with Feature Commit

```
✓ Refactoring committed

Now let's commit the authentication feature.
Staging remaining files...
```

```bash
$ git add src/features/auth/ src/services/auth.ts
```

### Pre-commit Checks (Feature)

Debug code check:
```
Debug statement found:
- src/features/auth/login.ts:42 console.log('user:', user)

Remove before committing? [Y/n]
```

User: "yes"

```bash
# Remove debug line
$ git diff --cached  # Verify removal
$ git add src/features/auth/login.ts
```

### Generated Commit Message (Feature)

```
feat(auth): add OAuth2 authentication with Google provider

Implement complete authentication flow:
- Login component with email/password and OAuth buttons
- OAuth2 integration with Google provider
- Auth service with token management
- Session persistence with secure cookie

Closes #123
```

### Execute Commit

```bash
$ git commit -m "feat(auth): add OAuth2 authentication with Google provider

Implement complete authentication flow:
- Login component with email/password and OAuth buttons
- OAuth2 integration with Google provider
- Auth service with token management
- Session persistence with secure cookie

Closes #123"

[feature-auth 8b4c3d2] feat(auth): add OAuth2 authentication with Google provider
 3 files changed, 310 insertions(+)
```

## Final Output

```
✓ Split completed successfully

Commits created:
1. 7a3b2c1 - refactor: modernize utility functions (3 files, 68 lines)
2. 8b4c3d2 - feat(auth): add OAuth2 authentication (3 files, 310 lines)

Your commit history now clearly separates:
- Infrastructure improvements (refactoring)
- New functionality (feature)

This makes it easier to:
- Revert the feature without losing refactoring
- Understand the history of changes
- Review each change independently

Ready to push? (not pushed yet)
```
