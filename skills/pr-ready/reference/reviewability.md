# Reviewability Assessment

A deep dive into evaluating whether changes are ready for effective review.

## Why Reviewability Matters

Studies show:
- PRs >400 lines have significantly higher defect rates post-merge
- Reviewers spend ~60% less time per line on large PRs
- Mixed-purpose PRs receive 3x more "LGTM" rubber-stamp approvals
- Review quality drops sharply after 60 minutes of review time

**Goal**: Make it easy for reviewers to give your code the attention it deserves.

## Size Guidelines

### Line Count Thresholds

| Category | Lines Changed | Review Quality | Action |
|----------|---------------|----------------|--------|
| **Ideal** | <200 | Excellent - thorough review | Proceed |
| **Good** | 200-400 | Good - focused review | Proceed |
| **Acceptable** | 400-800 | Moderate - key areas only | Consider split |
| **Large** | 800-1500 | Poor - will miss issues | Should split |
| **Too Large** | >1500 | Very poor - rubber stamp likely | Must split |

### What Counts

**Count these**:
- Logic changes (actual code)
- Configuration with logic impact
- Test code (but weight lower)

**Don't count**:
- Generated code (lock files, builds)
- Pure formatting/whitespace
- Import reordering
- Auto-generated migrations

### Calculating Effective Size

```
Effective Size = Logic Changes + (Test Changes * 0.5)

Example:
- 300 lines of feature code
- 200 lines of tests
- Effective size = 300 + (200 * 0.5) = 400 lines (still good)
```

## Mixed Concerns Detection

### Pattern 1: Feature + Refactor

**Symptoms**:
- New files/functions for feature
- Existing files modified for "cleanup"
- Commit messages mention both "add" and "refactor"

**Example**:
```
Files changed:
+ src/features/auth/login.ts      (new feature)
+ src/features/auth/oauth.ts      (new feature)
~ src/utils/http.ts               (refactored)
~ src/utils/validation.ts         (refactored)
~ src/core/logger.ts              (refactored)
```

**Split recommendation**:
```
PR 1: Refactor utilities (3 files)
PR 2: Add authentication feature (2 files, depends on PR 1)
```

### Pattern 2: Multiple Features

**Symptoms**:
- Changes span unrelated modules
- Commit messages mention different features
- No logical connection between file groups

**Example**:
```
Files changed:
+ src/features/notifications/*    (notification system)
+ src/features/search/*           (search feature)
~ src/api/routes.ts               (both features)
```

**Split recommendation**:
```
PR 1: Notification system
PR 2: Search feature
(Routes file will be touched by both - that's OK)
```

### Pattern 3: Bug Fix + Enhancement

**Symptoms**:
- Core fix is small
- "While I was here" additional changes
- Enhancement could exist independently

**Example**:
```
Commit 1: "fix: prevent null pointer in user lookup"
Commit 2: "feat: add user caching for performance"
Commit 3: "feat: add user search functionality"
```

**Split recommendation**:
```
PR 1: Bug fix only (urgent, can ship now)
PR 2: Performance enhancement (needs more review)
PR 3: Search functionality (new feature)
```

### Pattern 4: Format + Logic

**Symptoms**:
- Large diff with mostly whitespace/formatting
- Actual logic changes buried in formatting noise
- Linter/formatter was run on whole codebase

**Example**:
```
1,247 lines changed
- 1,100 lines: formatting (indentation, quotes, semicolons)
- 147 lines: actual feature code
```

**Split recommendation**:
```
PR 1: Formatting changes only (auto-approve if CI passes)
PR 2: Feature changes (actual review needed)
```

### Pattern 5: Dependency + Code

**Symptoms**:
- Package updates in lock file
- Code changes using new package features
- Version bumps mixed with feature work

**Example**:
```
~ package.json                    (add new dependency)
~ package-lock.json               (5000 lines)
+ src/features/charts/*           (use new charting library)
```

**Split recommendation**:
```
PR 1: Add dependency (quick review of package choice)
PR 2: Implement feature using dependency
```

## Detection Algorithm

```
1. Group files by primary directory
2. For each group:
   a. Identify primary purpose (feature/fix/refactor/config)
   b. Count lines changed

3. Calculate purpose distribution:
   - If >80% in single purpose → single concern (OK)
   - If 2 purposes >30% each → mixed concerns (split)
   - If >3 distinct purposes → multiple concerns (must split)

4. Check commits:
   - Parse commit messages for type prefixes
   - Flag if multiple types present (feat + refactor)

5. Special cases:
   - Generated files >50% of diff → exclude from calculation
   - Test files >50% → acceptable if testing single feature
```

## Helping Users Split

When split is recommended, provide concrete guidance:

### For Git Users

```bash
# Option 1: Interactive rebase to separate commits
git rebase -i HEAD~N

# Option 2: Soft reset and restage selectively
git reset --soft HEAD~N
git add -p  # Stage changes interactively

# Option 3: Cherry-pick specific commits to new branch
git checkout -b feature-only
git cherry-pick <commit1> <commit2>
```

### Suggested Splits

Provide specific split recommendations:

```
Recommended Split:

PR 1: "refactor: extract validation utilities"
- src/utils/validation.ts
- src/utils/validation.test.ts
Estimated: 150 lines

PR 2: "feat: add user registration" (after PR 1 merges)
- src/features/registration/*
- src/api/routes/auth.ts
Estimated: 280 lines

Order: PR 1 first (PR 2 depends on the refactored validation)
```

## When NOT to Split

Sometimes keeping changes together is correct:

1. **Atomic changes**: Refactor required for feature to work
2. **Migration + usage**: Schema change with code that uses it
3. **API + client**: Server change with required client update
4. **Small mixed**: <200 lines total, even if mixed

**Key question**: "Can each PR be merged independently and leave the codebase working?"

If no → keep together.
If yes → split for better review.

## Reviewability Checklist

Before requesting review, verify:

- [ ] **Single purpose**: PR does one thing
- [ ] **Appropriate size**: <800 lines (ideally <400)
- [ ] **Clear title**: Describes the change accurately
- [ ] **Complete description**: Explains what and why
- [ ] **No debug code**: console.log, debugger removed
- [ ] **Tests included**: Or testing instructions provided
- [ ] **CI passing**: All automated checks green

## Quick Decision Tree

```
                    START
                      │
                      ▼
              Lines changed > 1500?
                    /    \
                  YES     NO
                   │       │
                   ▼       ▼
              MUST SPLIT  Lines > 800?
                          /    \
                        YES     NO
                         │       │
                         ▼       ▼
                  SHOULD SPLIT  Multiple purposes?
                                /    \
                              YES     NO
                               │       │
                               ▼       ▼
                        CONSIDER   READY FOR
                          SPLIT     REVIEW
```
