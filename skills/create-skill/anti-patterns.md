# Anti-Patterns: Common Mistakes to Avoid

This document lists common mistakes when creating skills and how to fix them.

## Table of Contents
1. [Windows-Style Paths](#1-windows-style-paths)
2. [Deeply Nested References](#2-deeply-nested-references)
3. [Time-Sensitive Information](#3-time-sensitive-information)
4. [Inconsistent Terminology](#4-inconsistent-terminology)
5. [Offering Too Many Options](#5-offering-too-many-options)
6. [Vague Skill Names](#6-vague-skill-names)
7. [First or Second Person Descriptions](#7-first-or-second-person-descriptions)
8. [SKILL.md Over 500 Lines](#8-skillmd-over-500-lines)
9. [Vague Descriptions Without Triggers](#9-vague-descriptions-without-triggers)
10. [Over-Explaining Basics](#10-over-explaining-basics)
11. [No Examples for Format-Specific Tasks](#11-no-examples-for-format-specific-tasks)
12. [Missing Error Handling](#12-missing-error-handling)
13. [Template Too Complex](#13-template-too-complex)
14. [Wrong Directory](#14-wrong-directory)
15. [Vague Workflow Steps](#15-vague-workflow-steps)
16. [No Verification Before Critical Ops](#16-no-verification-before-critical-ops)
17. [Mixed Naming Patterns](#17-mixed-naming-patterns)
- [Quick Reference Checklist](#quick-reference-checklist)

## 1. Windows-Style Paths

**Bad**: `reference\guide.md`, `scripts\helper.py`  
**Good**: `reference/guide.md`, `scripts/helper.py`  
**Rule**: Always use forward slashes.

---

## 2. Deeply Nested References

### Problem
Claude may partially read nested reference files, missing content.

**Bad - Too Deep**:
```markdown
# SKILL.md
See [advanced.md](advanced.md) for details...

# advanced.md
See [implementation.md](implementation.md) for specifics...

# implementation.md
Here's the actual information you need...
```

**Good - One Level Deep**:
```markdown
# SKILL.md

**Basic usage**: [instructions in SKILL.md]
**Advanced features**: See [advanced.md](advanced.md)
**API reference**: See [reference.md](reference.md)
**Examples**: See [examples.md](examples.md)
```

**Why**: Nested references may trigger `head -100` previews instead of full reads, resulting in incomplete information.

**Rule**: All reference files should link directly from SKILL.md.

---

## 3. Time-Sensitive Information

### Problem
Time-based instructions become wrong after the date passes.

**Bad - Will Become Wrong**:
```markdown
If you're doing this before August 2025, use the old API.
After August 2025, use the new API.
```

**Good - Use "Old Patterns" Section**:
```markdown
## Current Method

Use the v2 API endpoint: `api.example.com/v2/messages`

## Old Patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>

The v1 API used: `api.example.com/v1/messages`

This endpoint is no longer supported.
</details>
```

**Why**: Instructions with specific dates become incorrect and misleading over time.

**Rule**: Use "current" and "legacy/old patterns" sections instead of date-based conditionals.

---

## 4. Inconsistent Terminology

**Bad**: Mixing "API endpoint", "URL", "route"  
**Good**: Choose one term, use consistently  
**Rule**: Pick one from each group:
- "API endpoint" / "URL" / "route" / "path"
- "field" / "box" / "element" / "control"
- "extract" / "pull" / "get" / "retrieve"

---

## 5. Offering Too Many Options

**Bad**: "You can use pypdf, pdfplumber, PyMuPDF, pdf2image, camelot, tabula..."  
**Good**: Provide one default + specific condition for alternative  
**Rule**: Default approach with escape hatch only.

---

## 6. Vague Skill Names

**Bad**: `helper`, `utils`, `tools`, `documents`, `data`  
**Good**: `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`  
**Rule**: Use gerund form (verb + -ing).

---

## 7. First or Second Person Descriptions

**Bad**: "I can help...", "You can use..."  
**Good**: "Processes files...", "Analyzes data..."  
**Rule**: Always third person (descriptions injected into system prompt).

---

## 8. SKILL.md Over 500 Lines

### Problem
Large SKILL.md files consume too much context.

**Bad - Monolithic**:
```markdown
---
name: data-analysis
---

# Data Analysis

## Finance Data
[2000 lines of schemas and examples]

## Sales Data
[2000 lines of schemas and examples]

## Product Data
[2000 lines of schemas and examples]
```

**Good - Progressive Disclosure**:
```markdown
---
name: data-analysis
---

# Data Analysis

## Available Domains
- **Finance**: See [reference/finance.md](reference/finance.md)
- **Sales**: See [reference/sales.md](reference/sales.md)
- **Product**: See [reference/product.md](reference/product.md)
```

**Why**: Claude loads SKILL.md when skill is triggered. Large files waste tokens on irrelevant context.

**Rule**: Keep SKILL.md under 500 lines. Use progressive disclosure for additional content.

---

## 9. Vague Descriptions Without Triggers

### Problem
Generic descriptions don't help Claude discover when to use the skill.

**Bad - No Triggers**:
```yaml
description: Helps with documents and data processing
```

**Good - Specific Triggers**:
```yaml
description: Extract text from PDF and Word documents, convert between formats. Use when processing PDFs, .docx files, or document conversion.
```

**Why**: Claude uses descriptions to match skills to tasks. Specific trigger terms improve discovery.

**Rule**: Include specific file types, technology names, and activity phrases.

---

## 10. Over-Explaining Basics

**Bad**: "PDF stands for Portable Document Format. It's a file format developed by Adobe. PDFs can contain text, images..."  
**Good**: Direct code/instructions only  
**Rule**: Skip common knowledge (file formats, imports, package managers, etc.).

---

## 11. No Examples for Format-Specific Tasks

**Bad**: "Write in conventional format with type, scope, description"  
**Good**: 2-3 concrete examples showing exact format  
**Rule**: Show, don't just describe format.

---

## 12. Missing Error Handling

**Bad**: Steps with no failure path  
**Good**: Include "If step fails: check X, fix Y, return to step Z"  
**Rule**: Add error handling for critical operations.

---

## 13. Template Too Complex

**Bad**: Over-specified (exact word counts, rigid patterns)  
**Good**: Simple placeholders + examples  
**Rule**: Keep templates simple, use examples for details.

---

## 14. Wrong Directory

**Bad**: `~/.cursor/skills-cursor/` (reserved for built-ins)  
**Good**: `~/.cursor/skills/` (personal) or `.cursor/skills/` (project)  
**Rule**: Never create in `skills-cursor/`.

---

## 15. Vague Workflow Steps

**Bad**: "Prepare data", "Process everything", "Generate output"  
**Good**: "Load from X", "Clean by doing Y", "Export to Z"  
**Rule**: Each step = what + how.

---

## 16. No Verification Before Critical Ops

**Bad**: Make changes → Deploy production  
**Good**: Changes → Test → Stage → Verify → Production  
**Rule**: Add verification gates before destructive operations.

---

## 17. Mixed Naming Patterns

**Bad**: Mixing gerund, noun, verb forms  
**Good**: All gerund (processing-pdfs, analyzing-excel) OR all noun  
**Rule**: Pick one pattern, use consistently.

---

## Quick Reference Checklist

Before finalizing a skill, check for these anti-patterns:

- [ ] ✗ Windows-style paths (`\`)
- [ ] ✗ Deeply nested references (>1 level)
- [ ] ✗ Time-sensitive information (dates in conditions)
- [ ] ✗ Inconsistent terminology
- [ ] ✗ Too many options without default
- [ ] ✗ Vague skill name
- [ ] ✗ First or second person description
- [ ] ✗ SKILL.md over 500 lines
- [ ] ✗ Description without trigger terms
- [ ] ✗ Over-explaining basic concepts
- [ ] ✗ No examples for format-specific outputs
- [ ] ✗ Missing error handling
- [ ] ✗ Template too complex
- [ ] ✗ Created in `~/.cursor/skills-cursor/`
- [ ] ✗ Vague workflow steps
- [ ] ✗ No verification before critical operations
- [ ] ✗ Mixed naming patterns

If you find any of these, fix them before using the skill.
