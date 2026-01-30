# Search Strategies Reference

Comprehensive guide to finding information efficiently in project documentation and code.

## Table of Contents
- [Documentation Search Patterns](#documentation-search-patterns)
- [Keyword Selection Strategy](#keyword-selection-strategy)
- [Search Order Optimization](#search-order-optimization)
- [Common Documentation Locations](#common-documentation-locations)
- [Search Refinement Techniques](#search-refinement-techniques)

## Documentation Search Patterns

### Level 1: High-Level Overview

Start with project overview documents:

```bash
# Primary entry points
README.md
ARCHITECTURE.md
docs/README.md
docs/index.md

# Quick reference
CONTRIBUTING.md
DEVELOPMENT.md
```

**What to look for**:
- Project structure overview
- Key concepts and terminology
- Links to detailed documentation
- Quick start guides

### Level 2: Domain-Specific Documentation

Search by topic domain:

```bash
# API documentation
docs/api/
API.md
openapi.yaml
swagger.json
**/*.proto
graphql/schema.graphql

# Architecture and design
docs/architecture/
docs/design/
ADR/  # Architecture Decision Records
DESIGN.md

# User guides
docs/guides/
docs/tutorials/
docs/user/

# Developer documentation
docs/dev/
docs/development/
DEVELOPMENT.md
```

### Level 3: Component-Specific Documentation

Look for docs near code:

```bash
# Component READMEs
src/**/README.md
lib/**/README.md
packages/**/README.md

# Inline documentation
src/**/*.md
```

## Keyword Selection Strategy

### Primary Keywords

**For business logic questions**:
- Feature name (exact or partial)
- User action verbs (login, checkout, submit)
- Business domain terms (order, payment, subscription)

**For technical questions**:
- Technology names (Redis, PostgreSQL, JWT)
- Pattern names (factory, singleton, observer)
- Technical terms (cache, queue, middleware)

### Secondary Keywords

If primary search yields no results, try:

**Synonyms**:
- auth/authentication/authorize
- config/configuration/settings
- db/database/storage
- api/endpoint/route

**Related terms**:
- Feature → implementation, handler, service
- Error → exception, failure, validation
- Data → model, schema, entity

**Abbreviations and variations**:
- JWT, JSON Web Token
- HTTP, HTTPS, REST
- DB, database

### Keyword Expansion

Start narrow, expand if needed:

```bash
# Start specific
grep -r "userAuthentication" docs/

# Expand to partial match
grep -ri "authentication" docs/

# Broaden to related concepts
grep -ri "auth\|login\|session" docs/

# Include code patterns
grep -r "class.*Auth" src/
```

## Search Order Optimization

### For Feature/Business Logic Questions

1. **User-facing docs** → API docs → Implementation
2. **Search pattern**:
   ```bash
   # Step 1: User guides
   grep -ri "feature_name" docs/guides/ docs/user/

   # Step 2: API documentation
   grep -ri "feature_name" docs/api/ API.md

   # Step 3: README files
   find . -name "README.md" -exec grep -l "feature_name" {} \;

   # Step 4: Code comments
   grep -r "feature_name" src/ --include="*.ts" --include="*.js"
   ```

### For Technical Implementation Questions

1. **Technical docs** → Configuration → Code → Tests
2. **Search pattern**:
   ```bash
   # Step 1: Architecture/design docs
   grep -ri "technology_name" docs/architecture/ docs/design/ ARCHITECTURE.md

   # Step 2: Configuration files
   grep -ri "technology_name" config/ *.config.* package.json

   # Step 3: Implementation
   grep -r "import.*technology_name\|require.*technology_name" src/

   # Step 4: Tests (reveal usage patterns)
   grep -ri "technology_name" tests/ **/*.test.* **/*.spec.*
   ```

### For Debugging/Error Questions

1. **Error messages** → Validation code → Handlers → Tests
2. **Search pattern**:
   ```bash
   # Step 1: Exact error message
   grep -r "exact error message" .

   # Step 2: Error code or type
   grep -r "ErrorCode\|ErrorType" src/

   # Step 3: Throw/raise statements
   grep -r "throw.*Error\|raise.*Error" src/

   # Step 4: Test expectations
   grep -r "expect.*toThrow\|assert.*raises" tests/
   ```

## Common Documentation Locations

### Standard Locations by Type

**Getting Started**:
```
README.md
docs/README.md
docs/getting-started.md
docs/quickstart.md
QUICKSTART.md
```

**Architecture**:
```
ARCHITECTURE.md
docs/architecture/
docs/design/
docs/adr/  # Architecture Decision Records
```

**API Reference**:
```
API.md
docs/api/
api/
openapi.yaml
swagger.json
```

**Development Guides**:
```
CONTRIBUTING.md
DEVELOPMENT.md
docs/development/
docs/dev/
docs/contributing/
```

**Configuration**:
```
CONFIG.md
docs/configuration.md
docs/config/
.env.example
config/README.md
```

**Deployment**:
```
DEPLOYMENT.md
docs/deployment/
docs/ops/
docs/infrastructure/
```

### Technology-Specific Locations

**JavaScript/TypeScript**:
```
package.json - Dependencies and scripts
tsconfig.json - TypeScript configuration
.eslintrc.* - Code style rules
jsdoc comments - Inline documentation
```

**Python**:
```
requirements.txt, pyproject.toml - Dependencies
setup.py - Package configuration
docstrings - Inline documentation
```

**Go**:
```
go.mod - Dependencies
README in each package
godoc comments
```

**Java**:
```
pom.xml, build.gradle - Dependencies
javadoc comments
```

## Search Refinement Techniques

### Progressive Filtering

Start broad, narrow down:

```bash
# 1. Find all docs mentioning topic
grep -rl "authentication" docs/

# 2. Filter by file type
grep -rl "authentication" docs/ | grep "\.md$"

# 3. Search within results for specific aspect
grep -r "JWT" $(grep -rl "authentication" docs/)

# 4. Show context around matches
grep -r "JWT" docs/ -A 3 -B 3
```

### Context Expansion

Get more context from matches:

```bash
# Show 5 lines before and after
grep -r "search_term" docs/ -C 5

# Show 10 lines after
grep -r "search_term" docs/ -A 10

# Show line numbers
grep -rn "search_term" docs/
```

### Multi-Pattern Search

Combine related terms:

```bash
# OR pattern
grep -rE "auth|authentication|login" docs/

# AND pattern (using multiple greps)
grep -r "authentication" docs/ | grep "JWT"

# NOT pattern
grep -r "authentication" docs/ | grep -v "test"
```

### Case-Insensitive Search

Don't miss variations:

```bash
# Case insensitive
grep -ri "authentication" docs/

# Word boundary matching
grep -riw "auth" docs/  # Matches "auth" but not "author"
```

### File Type Filtering

Focus on relevant files:

```bash
# Only markdown files
grep -r "search_term" --include="*.md"

# Multiple file types
grep -r "search_term" --include="*.md" --include="*.txt"

# Exclude certain types
grep -r "search_term" --exclude="*.log"

# Exclude directories
grep -r "search_term" --exclude-dir="node_modules"
```

## Search Workflow Examples

### Example 1: Finding API Endpoint Documentation

**Question**: "How does the /users/profile endpoint work?"

**Search sequence**:
```bash
# 1. Check API docs
grep -r "users/profile\|users/:id/profile" docs/api/ API.md

# 2. Check OpenAPI/Swagger
grep -r "/users.*profile" openapi.yaml swagger.json

# 3. If not found, search all docs
grep -ri "profile.*endpoint\|user.*profile.*api" docs/

# 4. Check route definitions in code
grep -r "router.*get.*profile\|@Get.*profile" src/
```

### Example 2: Understanding Configuration

**Question**: "What environment variables are available?"

**Search sequence**:
```bash
# 1. Check environment example file
cat .env.example

# 2. Check config documentation
grep -r "environment variable\|env var" docs/ README.md

# 3. Search config files
grep -r "process.env\|os.getenv\|ENV" config/ src/config/

# 4. Check deployment docs
grep -r "environment\|configuration" docs/deployment/ DEPLOYMENT.md
```

### Example 3: Tracing Feature Implementation

**Question**: "How is password reset implemented?"

**Search sequence**:
```bash
# 1. User documentation
grep -ri "password reset\|forgot password" docs/user/ docs/guides/

# 2. API documentation
grep -ri "password.*reset\|reset.*password" docs/api/ API.md

# 3. Feature documentation
find docs/ -name "*password*" -o -name "*reset*"

# 4. If limited docs, move to code search
# (Continue with code-search-patterns.md strategies)
```

## Advanced Techniques

### Using Glob for File Discovery

```bash
# Find all markdown files
Glob: "**/*.md"

# Find specific doc types
Glob: "docs/**/*.{md,txt,rst}"

# Find README files
Glob: "**/README*"

# Find API specs
Glob: "**/{openapi,swagger}.{yaml,json}"
```

### Combining Tools

```bash
# 1. Find relevant files with Glob
Glob: "docs/**/*auth*.md"

# 2. Search within results with Grep
Grep: "JWT" in docs/authentication.md

# 3. Read full file with Read
Read: docs/authentication.md
```

### Iterative Refinement

1. **Initial search** - Broad keywords
2. **Scan results** - Identify relevant files
3. **Refine keywords** - Use terms from initial results
4. **Targeted search** - Focus on promising files
5. **Deep read** - Read full files for context

### Tracking Search Progress

Maintain mental note of:
- What's been searched: docs/ ✓, config/ ✓, src/ pending
- What yielded results: API.md mentions feature
- What's still unknown: Implementation details
- Next steps: Search src/ for handlers

## Common Pitfalls

**Don't**:
- ✗ Search only one location
- ✗ Use overly specific keywords first
- ✗ Ignore case variations
- ✗ Skip reading README files
- ✗ Forget to check examples/tutorials
- ✗ Overlook inline code comments
- ✗ Stop after first match

**Do**:
- ✓ Start with documentation
- ✓ Use progressive keyword expansion
- ✓ Search multiple locations
- ✓ Read surrounding context
- ✓ Check multiple file types
- ✓ Look for examples
- ✓ Verify with multiple sources
