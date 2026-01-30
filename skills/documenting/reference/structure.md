# Directory Structure & Classification

Detailed guide for organizing documentation in code repositories with best practices for directory layout and document classification.

## Table of Contents

- [Standard Repository Structure](#standard-repository-structure)
- [Directory Organization Patterns](#directory-organization-patterns)
- [Classification Dimensions](#classification-dimensions)
- [File Naming Conventions](#file-naming-conventions)
- [Index Files and Navigation](#index-files-and-navigation)

## Standard Repository Structure

### Minimal Structure (Small Projects)

```
project-root/
├── README.md          # Project overview and quick start
├── AGENTS.md          # Agent navigation and context
├── LICENSE            # Legal
├── src/               # Source code
└── docs/              # All other documentation
    ├── guides/        # How-to guides
    └── notes/         # Temporary notes
```

### Standard Structure (Medium Projects)

```
project-root/
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── src/
├── tests/
└── docs/
    ├── internal/      # Internal team documentation
    │   ├── architecture/
    │   ├── processes/
    │   └── notes/     # Temporary, reviewed quarterly
    ├── public/        # User-facing documentation
    │   ├── guides/
    │   ├── api/
    │   └── examples/
    └── rfcs/          # Design proposals
        ├── README.md  # RFC process
        ├── template.md
        └── 0001-initial-architecture.md
```

### Comprehensive Structure (Large Projects)

```
project-root/
├── README.md
├── AGENTS.md
├── CLAUDE.md          # Claude-specific context (if needed)
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
├── CHANGELOG.md
├── src/
├── tests/
├── scripts/
├── docs/
│   ├── internal/
│   │   ├── architecture/
│   │   │   ├── decisions/     # ADRs (Architecture Decision Records)
│   │   │   ├── diagrams/
│   │   │   └── overview.md
│   │   ├── processes/
│   │   │   ├── development.md
│   │   │   ├── release.md
│   │   │   └── code-review.md
│   │   ├── onboarding/
│   │   │   ├── new-developer.md
│   │   │   └── setup-guide.md
│   │   ├── investigations/    # Research and exploration
│   │   └── notes/             # Temporary, time-bounded
│   │       ├── README.md      # Cleanup policy
│   │       └── YYYY-MM-DD-topic.md
│   ├── public/
│   │   ├── getting-started.md
│   │   ├── guides/
│   │   │   ├── installation.md
│   │   │   ├── configuration.md
│   │   │   └── troubleshooting.md
│   │   ├── api/
│   │   │   ├── reference.md
│   │   │   └── examples/
│   │   ├── tutorials/
│   │   └── faq.md
│   ├── rfcs/
│   │   ├── README.md
│   │   ├── template.md
│   │   ├── 0001-title.md      # Accepted RFCs
│   │   ├── 0002-title.md
│   │   └── drafts/            # Work in progress
│   └── archive/               # Deprecated documentation
│       └── YYYY-MM-old-doc.md
└── website/                   # Generated public docs (optional)
    └── build/
```

## Directory Organization Patterns

### Pattern 1: By Audience

Organize top-level by who reads the documentation.

**When to use:**
- Clear separation between internal and external documentation
- Different publication pipelines (e.g., public docs → website)
- Different maintenance processes for different audiences

**Structure:**
```
docs/
├── internal/    # Team only
├── public/      # External users
└── partners/    # Trusted third parties (if applicable)
```

### Pattern 2: By Document Type

Organize by the kind of document.

**When to use:**
- Single audience but varied document types
- Documentation tooling that processes by type
- Similar maintenance processes across audiences

**Structure:**
```
docs/
├── guides/          # Step-by-step how-tos
├── reference/       # API docs, specs
├── explanations/    # Concept deep-dives
├── tutorials/       # Learning-oriented
└── decisions/       # ADRs, RFCs
```

### Pattern 3: By Feature/Component

Organize by what the documentation describes.

**When to use:**
- Microservices or multi-component systems
- Documentation maintained by feature teams
- Strong code-to-docs mapping needed

**Structure:**
```
docs/
├── authentication/
├── api-gateway/
├── user-service/
└── payment-processing/
```

### Pattern 4: Hybrid

Combine patterns for different levels.

**Example: Audience → Type**
```
docs/
├── internal/
│   ├── architecture/
│   ├── processes/
│   └── notes/
└── public/
    ├── guides/
    ├── api/
    └── tutorials/
```

**Example: Component → Type**
```
docs/
├── authentication/
│   ├── architecture.md
│   ├── api-reference.md
│   └── integration-guide.md
└── payments/
    ├── architecture.md
    ├── api-reference.md
    └── integration-guide.md
```

## Classification Dimensions

### By Audience

**Internal**
- Development team members
- Internal stakeholders
- Future team members (onboarding)

**Public**
- End users
- API consumers
- Contributors

**Agent**
- AI assistants (Claude, etc.)
- Automated tools
- Navigation and discovery focus

### By Lifecycle Stage

**Permanent**
- Core architecture docs
- Stable API references
- User guides for released features
- Accepted RFCs (as historical record)

**Temporary** (explicit expiration)
- Meeting notes (keep 3 months)
- Investigation notes (review after project)
- Draft RFCs (promote or discard)
- Brainstorming docs (consolidate or delete)

**Archived**
- Superseded architecture decisions
- Deprecated feature documentation
- Old RFC proposals (rejected or obsolete)
- Historical process docs

### By Update Frequency

**High-frequency** (changes with code)
- API documentation
- Feature documentation
- Integration guides
- Changelog

**Medium-frequency** (quarterly/release)
- Architecture overviews
- Process documentation
- Contributing guides
- Public tutorials

**Low-frequency** (rarely)
- Project vision
- Architectural decisions (ADRs)
- Historical RFCs
- Foundational guides

### By Access Control

**Public** (open repository)
- All documentation is public
- Classify by sensitivity of content
- Be mindful of security details

**Private** (private repository)
- Internal vs. external still matters for publication
- Consider what would be public if open-sourced
- Separate truly confidential content

## File Naming Conventions

### General Rules

- Use lowercase
- Use hyphens for spaces: `my-document.md` (not underscores)
- Be descriptive: `api-authentication-guide.md` (not `guide.md`)
- Use `.md` extension for Markdown

### Temporary Documents

Include date prefix for time-bounded documents:
- `YYYY-MM-DD-topic.md` for dated notes
- `YYYY-QN-quarterly-review.md` for periodic reviews
- Example: `2026-01-30-oauth-investigation.md`

### Numbered Documents (RFCs, ADRs)

Use zero-padded numbers:
- `0001-initial-architecture.md`
- `0042-migrate-to-postgres.md`
- `1337-new-feature-proposal.md`

Benefits:
- Sortable by creation order
- Unique identifiers
- Easy to reference (#42)

### Versioned Documents

Avoid version numbers in filenames when possible:
- **Good:** Use git history for versions
- **Acceptable:** `api-v2-reference.md` (if v1 and v2 coexist)
- **Bad:** `api-reference-2024-01-30.md`

### Component-Specific

Use component prefix if not in component directory:
- In `docs/authentication/`: `overview.md`
- In flat `docs/`: `authentication-overview.md`

## Index Files and Navigation

### Root README.md

Purpose: Project overview and navigation hub

**Essential sections:**
1. What the project does (1-2 paragraphs)
2. Quick start (installation + hello world)
3. Links to key documentation
4. How to contribute
5. License

**Example structure:**
```markdown
# Project Name

[One-line description]

[1-2 paragraph overview]

## Quick Start

[Installation steps]
[Basic usage example]

## Documentation

- [User Guide](docs/public/guides/user-guide.md)
- [API Reference](docs/public/api/reference.md)
- [Contributing](CONTRIBUTING.md)
- [Architecture](docs/internal/architecture/overview.md)

## License

[License info]
```

### AGENTS.md

Purpose: Agent discovery and navigation (see [agent-docs.md](agent-docs.md))

**Essential sections:**
1. Project context (what and why)
2. Key workflows and entry points
3. Important constraints
4. Links to detailed documentation

**Keep it concise:**
- Assume agent intelligence ("Assume Claude is smart")
- Progressive disclosure (link to details)
- Update when structure changes

### docs/ README Files

Each major docs directory should have a README explaining its purpose:

**docs/internal/notes/README.md**
```markdown
# Internal Notes

Temporary documentation for investigations, meetings, and drafts.

## Lifecycle Policy

- Notes older than 3 months reviewed quarterly
- Valuable content consolidated into permanent docs
- Outdated content deleted
- Investigation notes kept until project completion

## Naming Convention

Use date prefix: `YYYY-MM-DD-topic.md`
```

**docs/rfcs/README.md**
See [rfc-process.md](rfc-process.md) for complete RFC process documentation.

### Table of Contents

For long documents (>100 lines), include TOC:

```markdown
## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)
  - [Subsection 2.1](#subsection-21)
- [Section 3](#section-3)
```

Use consistent heading anchors:
- GitHub/GitLab auto-generate anchors from headings
- Lowercase, hyphens for spaces
- Remove special characters

## Best Practices

### Keep It Shallow

- **Maximum 3 levels** of directory nesting
- **Prefer 1-2 levels** for most projects
- Flat is better than nested

### Make It Discoverable

- Index important docs in README.md and AGENTS.md
- Use descriptive directory names
- Link between related documents
- Search-friendly file names (use keywords)

### Align with Code Structure

For technical docs, mirror code organization:
```
src/
├── auth/
├── api/
└── payments/

docs/internal/architecture/
├── auth/
├── api/
└── payments/
```

### Plan for Growth

Start simple, add structure as needed:
1. **0-100 docs:** Flat `docs/` directory
2. **100-500 docs:** Add `internal/` and `public/`
3. **500+ docs:** Add topic subdirectories

### Document the Structure

In README.md or AGENTS.md, explain your documentation organization:

```markdown
## Documentation Structure

- `docs/internal/` - Team documentation (architecture, processes)
- `docs/public/` - User guides and API docs
- `docs/rfcs/` - Design proposals and decisions
- `AGENTS.md` - Agent navigation and context
```

## Anti-Patterns

### ❌ Too Deep

```
docs/internal/team/engineering/backend/services/auth/documentation/guides/setup.md
```

Too many levels make navigation difficult.

### ❌ Unclear Names

```
docs/stuff/things/misc/file.md
```

Non-descriptive names provide no context.

### ❌ Inconsistent Organization

```
docs/
├── user-guide.md        # Mixed in root
├── api/
│   └── reference.md
└── guides/
    └── user-guide-2.md  # Duplicate?
```

No clear organizing principle.

### ❌ Code-Embedded Docs (for general documentation)

```
src/auth/README.md       # General auth documentation
src/auth/docs/guide.md   # Not code-specific
```

General documentation should be in `docs/`, not scattered in code.
Code-adjacent docs should be limited to that component's specifics.

### ✅ Good Code-Adjacent Docs

```
src/auth/README.md       # How this auth module works
src/auth/api.md          # This module's API specifics
docs/internal/architecture/auth.md  # Overall auth architecture
docs/public/guides/authentication.md  # User guide for auth
```

## Migration Strategies

### From Unorganized to Organized

1. **Inventory** - List all existing docs
2. **Classify** - Determine audience and type for each
3. **Create structure** - Set up directory hierarchy
4. **Move files** - Relocate to appropriate locations
5. **Update links** - Fix all internal references
6. **Update indexes** - Refresh README.md and AGENTS.md
7. **Clean up** - Remove duplicates and outdated docs

### From Flat to Hierarchical

1. **Group by similarity** - Identify natural clusters
2. **Create categories** - Define 3-5 main directories
3. **Move in batches** - Relocate related docs together
4. **Maintain redirects** - Consider adding a "moved" note in old locations
5. **Update references** - Fix links incrementally
6. **Communicate** - Tell team about new structure

### From Monorepo to Separate Repos

1. **Identify scope** - What docs belong with what code?
2. **Duplicate shared docs** - Copy common documentation to each repo
3. **Link to central docs** - Reference single source of truth when appropriate
4. **Update ownership** - Clarify who maintains what
5. **Synchronize critical docs** - Ensure consistency for shared content
