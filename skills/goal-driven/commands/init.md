# goal-driven:init — First-time scaffolding

One-time plumbing for adopting goal-driven on a project: empty `goals/`
directory, stub files, agent config update, optional hook. Run once when
adopting the methodology.

This command does **not** write GOAL.md content. For that, run
`/goal-driven bootstrap` after init — or instead of init, since bootstrap
handles plumbing idempotently.

If the project doesn't yet have an overall agent context architecture
(CLAUDE.md, layer structure), consider setting that up first — the harness
skill covers this. Goal-driven focuses specifically on the goal/journal
layer, which is orthogonal to architectural docs.

## Steps

### 1. Check current state

If `goals/GOAL.md` already exists with non-stub content, stop and ask
whether the user meant `/goal-driven audit` or `/goal-driven bootstrap`
(re-bootstrap). Don't overwrite content silently.

### 2. AI agent config (most important)

Add goal-driven instructions to every AI agent config the project uses.
Common locations:

- `CLAUDE.md` — Claude Code
- `.cursorrules` — Cursor
- `AGENTS.md` or `codex.md` — Codex / OpenAI agents
- `.github/copilot-instructions.md` — GitHub Copilot
- `.windsurfrules` — Windsurf
- Any other agent instruction file the project uses

A minimal paste-ready snippet — append it to each agent config, adjusted
for the project's tone:

```markdown
## Goal-driven planning

When working on this initiative, follow the goal-driven protocol:

- At session start, read `goals/GOAL.md` and `goals/OPEN-STOPS.md`. List
  open STOPs to the human before starting new work. Verify the current
  month's journal file exists; create `goals/journal-YYYY-MM.md` if the
  month rolled over.
- At session end, draft a journal entry in chat (what done, observations,
  per-criterion check with evidence, judgment) and get confirmation before
  appending.
- If a criterion verdict is `✗`, or new evidence questions the north star,
  surface a STOP in chat and wait for the human's decision. Never silently
  rewrite the path past a STOP.
- Never edit `GOAL.md` without an explicit, confirmed change request from
  the human, echoed back line by line.
```

Trim or expand to match the project's conventions. The goal is the rules
land in the config, not a specific wording.

### 3. Directory and stub files

Create:

- `goals/` directory
- `goals/GOAL.md` — stub with a heading and a one-line note pointing to
  `/goal-driven bootstrap`. Example body:

  ```markdown
  # Goal

  > Run `/goal-driven bootstrap` to fill this in via interview.
  ```

- `goals/OPEN-STOPS.md` — heading and empty list:

  ```markdown
  # Open STOPs

  No open STOPs.
  ```

- `goals/journal-YYYY-MM.md` for the current month — heading only, empty
  body. The first real entry will be added at the next session end.

### 4. Hook (optional)

A SessionStart hook can enforce the "read GOAL + report open STOPs +
verify month rotation" ritual. The hook itself only emits a reminder; the
agent reads the reminder and performs the actions.

Default: **do not install the hook.** Mention it as opt-in. Agents that
read SKILL.md correctly should perform these steps unprompted at session
start. The hook is a backstop for sessions where the skill description
isn't matched, not the primary enforcement.

If the user wants the hook, the harness skill covers hook configuration
methodology, and the fewer-permission-prompts / hookify skills can
generate the JSON. The reminder text should look like:

```
goal-driven: read goals/GOAL.md, list goals/OPEN-STOPS.md, verify
journal for current month exists.
```

### 5. Commit

Commit the `goals/` directory, agent config updates, and any hook configs
together as the initial goal-driven setup.

### 6. Next step

Tell the user:

- If they're ready to articulate the goal now, run `/goal-driven bootstrap`
  to do the interview-driven fill-in.
- If they want to think first, leave `goals/GOAL.md` as-is; come back to
  bootstrap when ready.

The skill is harmless without a real GOAL.md, but useless. Encourage them
not to leave the stub for long — a half-set-up `goals/` is worse than no
goals/ at all because it implies discipline that isn't there.
