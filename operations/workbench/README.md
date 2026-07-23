# Rossovia Workbench

Workbench is the repository's high-frequency project, mission, preference, and
hook runtime. Its checked-in entrypoint is:

```sh
./operations/workbench/rossovia --help
```

The launcher uses the self-contained `dist/rossovia.mjs` bundle with Node
22.12–26. Bun is a development and test tool, not a target-machine requirement.
Rebuild the bundle with:

```sh
npm run build
```

The build uses a local Bun installation when present. With Node and Docker but
no Bun, use `npm run build:docker`; Docker supplies Bun only inside the build
container and exports the same Node bundle.

## Hook projections

The portable hook behavior lives in `src/hooks.ts`; `.codex/hooks.json`,
`.claude/settings.json`, and `.cursor/hooks.json` are thin lifecycle bindings.
They share privacy-preserving intervention state and path-only artifact
observations without claiming identical host capabilities.

| Capability | Codex | Claude Code | Cursor |
|---|---|---|---|
| Principal-message observation | yes | yes | no useful binding |
| Reconciliation context injection | yes | yes | unavailable on `beforeSubmitPrompt` |
| Changed-artifact observation | `PostToolUse` | `PostToolUse` | `afterFileEdit` |
| One bounded stop continuation | `decision: block` | `decision: block` | `followup_message` |

Cursor's prompt hook can currently validate or deny a submission but cannot add
context to it, so Rossovia does not install a pretend intervention adapter.
The active Agent still receives Principal corrections through ordinary
conversation. All three artifact bindings retain only relevant repository
paths in operating-system temporary state and clear them after the continuation.

The binding shapes were checked on 2026-07-23 against the
[Codex Hooks guide](https://learn.chatgpt.com/docs/hooks),
[Claude Code hooks reference](https://code.claude.com/docs/en/hooks), and
[Cursor hooks reference](https://cursor.com/docs/hooks). Recheck the owning
tool's current documentation before changing its JSON projection.
