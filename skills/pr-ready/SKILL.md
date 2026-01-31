---
name: pr-ready
description: Prepares changes for review - validates reviewability, generates PR descriptions with ASCII diagrams, and creates PRs/MRs. Think like a reviewer to make changes easy to review. Use when user mentions "commit", "create pr", "create mr", "prepare for review", "ready for review".
---

# PR Ready

Prepares changes for review by thinking like a reviewer. Validates reviewability, generates clear descriptions, and creates PRs/MRs.

## Core Principle

> **What makes a good PR?** One that a reviewer can understand in 5 minutes, review in 20 minutes, and approve with confidence.

A reviewer-friendly PR:
- Has a **single clear purpose** (one feature, one fix, or one refactor)
- Tells the reviewer **what changed and why** upfront
- Explains **complex logic visually** (ASCII diagrams)
- Is **small enough to review carefully** (<400 lines ideal)

## Modes

Detect mode from user intent:

| User says | Mode | Action |
|-----------|------|--------|
| "commit", "commit staged" | commit | Validate staged → commit |
| "create pr", "create mr", "open pr" | create-pr | Validate branch → create PR/MR |
| "prepare for review", "ready for review" | prepare | Validate + generate description only |
| "review my changes", "self review" | self-review | Deep self-review before requesting |

## Workflow

Use TodoWrite to track progress.

### Stage 1: Gather Changes

**For commit mode**:
```bash
git diff --cached --stat
git diff --cached
```

**For create-pr/prepare mode**:
```bash
# Determine base branch
git remote show origin | grep 'HEAD branch'
BASE_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')

# Get diff stats
git diff --stat $BASE_BRANCH...HEAD
git log --oneline $BASE_BRANCH..HEAD
git diff $BASE_BRANCH...HEAD
```

If no changes found, inform user and exit.

**Capture metrics**: files changed, lines added/deleted, commits count.

### Stage 2: Reviewability Check

**This is the most critical stage.** A PR that's hard to review will get superficial reviews or long delays.

#### 2.1 Size Assessment

| Size | Lines | Verdict |
|------|-------|---------|
| Ideal | <400 | Easy to review thoroughly |
| Acceptable | 400-800 | Needs focused attention |
| Large | 800-1500 | Consider splitting |
| Too Large | >1500 | **Must split** - reviewers will miss issues |

#### 2.2 Mixed Concerns Detection

Scan for common mixing patterns. See [reviewability.md](reference/reviewability.md) for details.

**Red flags**:
1. **Feature + Refactor**: New functionality mixed with code cleanup
2. **Multiple Features**: Unrelated features in one PR
3. **Bug Fix + Enhancement**: Fix mixed with improvements
4. **Format + Logic**: Large formatting changes with logic changes
5. **Dependency + Code**: Package updates with feature work

**Detection approach**:
```
1. Group files by directory/module
2. Identify the primary change purpose
3. Flag files that don't fit the primary purpose
4. Check commit messages for mixed intents
```

#### 2.3 Decision

**If issues found**:
```
⚠️ Reviewability Issues Detected

This PR mixes multiple concerns:
1. Feature: User authentication (4 files, 280 lines)
2. Refactor: Database utilities (3 files, 150 lines)

Recommendation: Split into 2 PRs for easier review.

Options:
- [S]plit: I'll help you separate the changes
- [P]roceed: Continue with current changes (not recommended)
```

Wait for user decision. If split requested, help separate changes.

### Stage 3: Pre-commit Checks (commit mode only)

Quick quality checks before committing:

#### 3.1 Debug Code
Search for: `console.log`, `print(`, `debugger`, `TODO`, `FIXME`, `XXX`, commented code blocks.

If found, list with file:line and ask if intentional.

#### 3.2 Breaking Changes
Identify: removed/renamed exports, changed signatures, schema changes, CLI/env changes.

If found, note for commit message footer.

### Stage 4: Generate Description

See [pr-description.md](reference/pr-description.md) for comprehensive guide.

#### 4.1 Title

Format: `<type>: <concise summary>`

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`

**Good titles**:
- `feat: add OAuth2 login with Google provider`
- `fix: prevent duplicate order submissions`
- `refactor: extract payment processing to service layer`

**Bad titles**:
- `Update code` (too vague)
- `Fix bug` (what bug?)
- `WIP` (not ready for review)

#### 4.2 Description Structure

```markdown
## Summary
[1-2 sentences: what this PR does and why]

## Changes
[Bullet points of key changes, grouped logically]

## How It Works
[For complex logic - use ASCII diagrams]

## Testing
[How to verify the changes work]

## Notes for Reviewer
[Areas needing extra attention, known limitations]
```

#### 4.3 ASCII Diagrams

**Use diagrams when**:
- Flow involves 3+ steps
- State transitions exist
- Component interactions change
- Data transformations occur

See [pr-description.md](reference/pr-description.md) for diagram patterns.

**Example - Authentication flow**:
```
┌──────────┐    ┌───────────┐    ┌──────────┐
│  Client  │───>│  Gateway  │───>│  Auth    │
└──────────┘    └───────────┘    │  Service │
                     │           └──────────┘
                     │                │
                     v                v
               ┌──────────┐    ┌──────────┐
               │  Cache   │<───│  Token   │
               └──────────┘    │  Store   │
                               └──────────┘
```

### Stage 5: Execute Action

#### Commit Mode

```bash
git commit -m "<type>: <summary>

<body if needed>

<BREAKING CHANGE footer if applicable>"
```

Do NOT push unless explicitly requested.

#### Create-PR Mode

**GitHub**:
```bash
gh pr create --title "<title>" --body "<description>"
```

**GitLab**:
```bash
glab mr create --title "<title>" --description "<description>"
```

**Bitbucket** (manual):
Provide title and description for user to copy.

#### Prepare Mode

Output the generated title and description without creating PR.

### Stage 6: Self-Review (self-review mode)

Perform reviewer simulation before requesting review.

**Reviewer checklist**:
1. Can I understand the purpose in 30 seconds? (read title + summary)
2. Are the changes focused on one thing?
3. Is the diff size manageable? (<800 lines preferred)
4. Are complex parts explained with diagrams?
5. Are there obvious issues I'd flag?

**Output format**:
```markdown
## Self-Review Report

### Reviewer First Impression
[What a reviewer sees in first 30 seconds]

### Potential Reviewer Questions
- Q: Why was X approach chosen over Y?
- Q: How does this affect existing feature Z?

### Issues to Fix Before Review
1. [MUST] Missing error handling in api/handler.ts:45
2. [SHOULD] Add test for edge case when input is empty

### Suggested Improvements to Description
[Concrete suggestions to improve clarity]
```

## Quick Reference

**Ideal PR characteristics**:
- Single purpose clearly stated
- <400 lines of actual logic changes
- Title follows conventional format
- Description explains "what" and "why"
- Complex logic has ASCII diagrams
- Tests included or testing instructions provided

**Anti-patterns to avoid**:
- "Miscellaneous fixes" PRs
- Mixing feature + refactor
- Giant PRs (>1000 lines)
- Vague titles like "Update" or "Fix"
- No description
- Description that just lists files changed

## Reference Documentation

- [reviewability.md](reference/reviewability.md) - Deep dive on reviewability assessment
- [pr-description.md](reference/pr-description.md) - Complete guide to writing PR descriptions
- [ascii-diagrams.md](reference/ascii-diagrams.md) - ASCII diagram patterns for code explanation

## Examples

- [commit-example.md](examples/commit-example.md) - Commit workflow with split detection
- [create-pr-example.md](examples/create-pr-example.md) - Creating a well-described PR
- [self-review-example.md](examples/self-review-example.md) - Self-review before requesting review
