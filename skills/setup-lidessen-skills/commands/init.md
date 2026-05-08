# Setup lidessen skills — `init`

Scaffold the lidessen section in a project that doesn't yet have one.

## Steps

1. **Detect host tool** per SKILL.md "Tool detection". If multiple configs are present, ask the user which to target. If none, ask the user to confirm which tool they're configuring before creating the target file.
2. **Identify target file** based on detected tool.
3. **Check for existing markers** (`<!-- lidessen-setup:begin -->`) in the target file. If found, abort and recommend `sync` instead — `init` is for fresh scaffolding only and would clobber existing user state.
4. **Read current canonical content** from `references/cross-cutting-principles.md`. This is the single source of truth for what goes between the markers.
5. **Compose the section**:
   - Open marker with version: `<!-- lidessen-setup:begin v=1 -->`
   - Heading: `## Lidessen skills (managed by /setup-lidessen-skills)`
   - One-line preamble: this section is managed by `/setup-lidessen-skills`; do not hand-edit; run `/setup-lidessen-skills sync` to update.
   - Optional list of installed lidessen skills if discoverable in the project (look for `skills/<name>/SKILL.md` whose author/source is lidessen). If undetectable, leave a placeholder line for the user to fill in.
   - The cross-cutting principles, copied verbatim from the canonical reference.
   - Close marker: `<!-- lidessen-setup:end -->`
6. **Write the section** at an appropriate position in the target file:
   - If the file already exists and has a `## Guiding Principles` section, insert the lidessen section *after* that section (so the user's own principles come first).
   - Otherwise, append at the bottom.
   - If the file doesn't exist, create it with a minimal scaffold: a top-level title (`# <Project name>`), a single sentence stating it provides agent guidance, then the lidessen section.
7. **Report what happened** to the user — which file, where the section was inserted, the version, and any user action required (e.g., "the principles refer to skills X/Y/Z; make sure you've cloned or symlinked them into your `skills/` directory").

## Failure modes

- Target file is binary, malformed, or unreadable → abort, report the underlying error.
- User cannot or will not specify which tool when ambiguous → abort; this skill does not guess.
- Existing markers detected → instruct the user to run `sync` instead; do not overwrite.
- Canonical reference file missing or unreadable → abort; surface the read error to the user. Do not write a partial section.

## Output

A short status: target file path, version written, lines added, and any user follow-up required.
