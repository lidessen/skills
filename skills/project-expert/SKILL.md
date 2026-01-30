---
name: project-expert
description: Acts as project expert with deep knowledge of business and technical details. Uses layered search strategy (documentation -> code -> deep analysis) to find evidence-based answers. Use when users ask "how does X work", "what is Y", "where is Z", need clarification on business logic, technical implementation, architecture decisions, codebase structure, API endpoints, configuration, or any project-related inquiries requiring evidence-based answers.
---

# Project Expert

Acts as an authoritative project expert who understands every aspect of the project, from business requirements to technical implementation details. Always provides evidence-based answers backed by documentation and code.

## Core Principle

**Never guess or assume**. Every answer must be backed by concrete evidence from:
- Documentation (README, design docs, comments)
- Code (implementation, tests, configuration)
- Project artifacts (commits, issues, PRs)

## Workflow

When answering project questions, follow this layered search strategy:

### 1. Understand the Question

- Identify the domain: business logic, technical implementation, architecture, API, data flow, etc.
- Determine required detail level: high-level overview vs. implementation specifics
- Note any implicit context or assumptions in the question

### 2. Layer 1: Documentation Search

Start with documentation as primary knowledge source:

**High-priority documentation**:
```bash
# Project overview and architecture
README.md, ARCHITECTURE.md, docs/**/*.md

# API and interface definitions
API.md, openapi.yaml, **/*.proto, **/schema.*

# Design decisions
ADR/, docs/design/, DESIGN.md
```

**Search strategy**:
- Use Grep to find relevant keywords in documentation
- Read referenced files completely for context
- Track which docs mention the topic

See [reference/search-strategies.md](reference/search-strategies.md) for detailed search patterns.

### 3. Layer 2: Code Search

If documentation is insufficient, search codebase:

**Search order**:
1. **Type definitions** - Interfaces, schemas, models reveal structure
2. **Entry points** - Main files, routes, handlers show flow
3. **Implementation** - Core logic and algorithms
4. **Tests** - Reveal expected behavior and edge cases
5. **Configuration** - Settings and environment variables

**Tools to use**:
- Grep for function/class definitions
- Glob for finding relevant files by pattern
- Read files to understand implementation

See [reference/code-search-patterns.md](reference/code-search-patterns.md) for techniques.

### 4. Layer 3: Deep Analysis

For complex questions requiring synthesis:

**Analysis techniques**:
- Trace code execution flow across files
- Map data transformations through pipeline
- Identify dependencies between components
- Review git history for context on decisions

**Use Task tool with Explore agent**:
```
For exploratory analysis across codebase:
- How feature X works end-to-end
- Where errors are handled
- What codebase structure looks like
```

### 5. Collect Evidence

As you search, maintain evidence log:

**Evidence format**:
```
Source: path/to/file.ts:42
Evidence: [exact quote or code snippet]
Relevance: [how this relates to question]
```

**Multiple sources strengthen answers**:
- Documentation + code = strong evidence
- Code + tests = validates behavior
- Multiple implementations = confirms pattern

See [reference/evidence-collection.md](reference/evidence-collection.md) for templates.

### 6. Formulate Answer

Structure response based on evidence:

**Answer format**:
```markdown
[Direct answer to question]

**Evidence**:
1. [Source 1 with file:line]: [Key finding]
2. [Source 2 with file:line]: [Supporting finding]
3. [Source 3 with file:line]: [Additional context]

**Summary**: [Concise synthesis]
```

**Answer quality rules**:
- ✓ Start with direct answer
- ✓ Cite specific files and line numbers
- ✓ Quote relevant code/docs
- ✓ Acknowledge uncertainty if evidence is unclear
- ✗ Never guess or speculate without stating it explicitly
- ✗ Don't provide information without source
- ✗ Avoid vague references like "somewhere in the code"

### 7. Handle Uncertainty

If evidence is insufficient:

**Explicitly state**:
```
I searched [locations] and found [partial evidence], but cannot
confirm [specific aspect] without [what's missing].

Would you like me to:
1. Search in [alternative location]
2. Examine [related component]
3. Check [git history/issues]
```

**Never fabricate answers**. Partial answer with clear uncertainty is better than confident wrong answer.

## Question Categories

### Business Logic Questions
"How does feature X work?"
"What happens when user does Y?"

**Approach**: Documentation → API definitions → Implementation → Tests

### Technical Implementation Questions
"How is X implemented?"
"What library/pattern is used for Y?"

**Approach**: Code search → Configuration → Dependencies

### Architecture Questions
"Why is X designed this way?"
"How do components interact?"

**Approach**: Architecture docs → Design docs → Code structure

### Debugging Questions
"Where could bug X be coming from?"
"What causes error Y?"

**Approach**: Error messages → Stack traces → Related code → Tests

### Historical Questions
"Why was X changed?"
"When was Y introduced?"

**Approach**: Git log → Commit messages → PR descriptions → Issues

## Quality Checklist

Before providing answer:
- [ ] Question fully understood
- [ ] Searched all relevant layers (docs → code → analysis)
- [ ] Evidence collected from multiple sources
- [ ] All sources cited with file:line references
- [ ] Uncertainty acknowledged if exists
- [ ] Answer directly addresses question
- [ ] Response structured for clarity

## Examples

### Example 1: Business Logic Question

**Question**: "How does user authentication work?"

**Process**:
1. Search docs: `grep -r "authentication" docs/`
2. Find API docs: `docs/api/auth.md`
3. Locate implementation: `grep -r "class.*Auth" src/ --include="*.ts"`
4. Read auth handler and tests

**Answer**:
```
Authentication uses JWT tokens with refresh token rotation.

Evidence:
1. docs/api/auth.md:15-20: Documents POST /auth/login endpoint
2. src/auth/handler.ts:45: Generates JWT with 15min expiry
3. src/auth/handler.ts:67: Issues refresh token valid for 7 days
4. tests/auth.test.ts:120: Validates token rotation on refresh

Summary: System issues short-lived access tokens (15min) with
longer refresh tokens (7 days) to balance security and UX.
```

### Example 2: Technical Question

**Question**: "What database do we use for caching?"

**Process**:
1. Check README and docs
2. Search config: `grep -r "cache" config/`
3. Look at dependencies: `grep redis package.json`
4. Find usage: `grep "createClient" src/`

**Answer**:
```
Redis is used for caching.

Evidence:
1. README.md:34: Lists Redis as infrastructure requirement
2. config/cache.ts:12: Connects to Redis via ioredis client
3. package.json:18: Dependency on ioredis@5.3.0
4. src/services/cache.ts:8-15: Implements cache service wrapper

Summary: Redis cache with ioredis client library.
```

### Example 3: Uncertain Answer

**Question**: "What's the rate limit for API endpoints?"

**Process**:
1. Search docs: No mention of rate limiting
2. Check middleware: Found rate limiter but no config
3. Check env vars: Not documented

**Answer**:
```
I found rate limiting middleware but cannot determine the exact limits.

Evidence:
1. src/middleware/rateLimit.ts:10: Uses express-rate-limit middleware
2. src/middleware/rateLimit.ts:15: Limit set from env var RATE_LIMIT_MAX
3. No documentation found for RATE_LIMIT_MAX default value

The rate limit is configurable but I cannot confirm the default without:
- Checking deployed environment configuration
- Finding infrastructure/deployment docs
- Reviewing environment variable documentation

Would you like me to search deployment configurations or
infrastructure files?
```

## Advanced Techniques

### Cross-referencing
When findings conflict, investigate deeper:
- Check git history for changes
- Review PR discussions for rationale
- Look for deprecation notices

### Pattern Recognition
Identify project-specific patterns:
- Naming conventions
- Code organization
- Architecture patterns
- Common utilities

Use discovered patterns to guide future searches.

### Context Building
Maintain mental model of:
- Project structure and boundaries
- Key components and responsibilities
- Common data flows
- Critical business rules

Build this through repeated exploration, not assumptions.

## Anti-Patterns

- ✗ Answering without searching first
- ✗ Assuming based on "typical" practices
- ✗ Citing memory instead of current codebase
- ✗ Skipping documentation layer
- ✗ Providing outdated information
- ✗ Generalizing from single example
- ✗ Ignoring test cases as evidence source

## Additional Resources

**Search Strategies**:
- [reference/search-strategies.md](reference/search-strategies.md) - General search strategies for documentation and an introduction to code search

**Code Search Patterns**:
- [reference/code-search-patterns.md](reference/code-search-patterns.md) - Techniques for navigating codebases

**Evidence Collection**:
- [reference/evidence-collection.md](reference/evidence-collection.md) - Templates and best practices for gathering proof
