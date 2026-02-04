# agent-worker

## 0.1.0

### Minor Changes

- [#19](https://github.com/lidessen/skills/pull/19) [`9e65da6`](https://github.com/lidessen/skills/commit/9e65da6858480aaae93eb7f9bfabeaacf77a4998) Thanks [@lidessen](https://github.com/lidessen)! - Add CLI backend support for Claude Code, Codex, and Cursor

  - New pluggable backend system supporting multiple execution engines
  - `sdk`: Vercel AI SDK (default)
  - `claude`: Claude Code CLI (`claude -p` for non-interactive mode)
  - `codex`: OpenAI Codex CLI (`codex exec`)
  - `cursor`: Cursor Agent CLI (`cursor-agent -p`)
  - New `agent-worker backends` command to check CLI tool availability
  - Unified model specification across all backends with `createBackend()`
