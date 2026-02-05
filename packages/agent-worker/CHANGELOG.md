# agent-worker

## 0.2.0

### Minor Changes

- [#26](https://github.com/lidessen/skills/pull/26) [`1e921f4`](https://github.com/lidessen/skills/commit/1e921f43ee3efcff9ce5710e985f44ce65d3600f) Thanks [@lidessen](https://github.com/lidessen)! - Add `--import-skill` for temporary Git repository imports

  This release adds support for importing agent skills directly from Git repositories during session creation. Skills are cloned to a session-specific temporary directory and automatically cleaned up when the session ends.

  **New Features:**

  - `--import-skill` CLI option for importing skills from Git repositories
  - Import spec format: `[provider:]owner/repo[@ref]:{skill1,skill2,...}`
  - Brace expansion support for importing multiple skills: `{a,b,c}`
  - Multi-provider support: GitHub (default), GitLab, Gitee
  - Session-scoped temporary directory with automatic cleanup on shutdown
  - `SkillImporter` class for programmatic skill imports
  - New exports: `SkillImporter`, `parseImportSpec`, `buildGitUrl`, `getSpecDisplayName`

  **Examples:**

  ```bash
  # CLI usage
  agent-worker session new --import-skill vercel-labs/agent-skills:dive
  agent-worker session new --import-skill lidessen/skills:{memory,orientation}
  agent-worker session new --import-skill gitlab:myorg/skills@v1.0.0:custom
  ```

  ```typescript
  // SDK usage
  import {
    SkillImporter,
    SkillsProvider,
    createSkillsTool,
  } from "agent-worker";

  const importer = new SkillImporter(sessionId);
  await importer.import("vercel-labs/agent-skills:dive");
  await skillsProvider.addImportedSkills(importer);

  // Cleanup when done
  await importer.cleanup();
  ```

  **Security:**

  - Input validation to prevent git argument injection attacks
  - Path traversal protection for skill file access
  - Strict validation of owner/repo/ref names (alphanumeric, hyphen, underscore, dot only)
  - Protection against shell metacharacters and malicious input

  **Note:** For permanent skill installation, use the Vercel skills CLI (`npx skills add`). This feature is designed for temporary, session-scoped skill imports.

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
