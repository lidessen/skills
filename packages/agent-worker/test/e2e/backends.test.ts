/**
 * E2E Backend Tests — Real API calls against actual CLI backends
 *
 * Prerequisites:
 *   - Run `scripts/e2e-setup.sh` to install CLIs
 *   - Set env vars:
 *     DEEPSEEK_API_KEY   — for Claude Code (via DeepSeek) and OpenCode
 *     OPENAI_API_KEY     — for Codex CLI (optional, or use ZENMUX_API_KEY)
 *     ZENMUX_API_KEY     — for Codex CLI via ZenMux proxy (optional)
 *     CURSOR_API_KEY     — for Cursor Agent (optional)
 *
 * Usage:
 *   # Run all E2E tests
 *   DEEPSEEK_API_KEY=sk-... bun test test/e2e/
 *
 *   # Run specific backend
 *   DEEPSEEK_API_KEY=sk-... bun test test/e2e/ -t "OpenCode"
 *
 * Notes:
 *   - Claude Code E2E may hang when run from within a claude session.
 *     Set SKIP_CLAUDE_E2E=1 to skip it.
 *   - Codex requires Responses API (wire_api="responses"). ZenMux supports this.
 *   - Cursor requires paid subscription + API key from cursor.com/dashboard
 */

import { describe, test, expect, beforeAll, afterAll } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { ClaudeCodeBackend } from "../../src/backends/claude-code.ts";
import { CodexBackend } from "../../src/backends/codex.ts";
import { CursorBackend } from "../../src/backends/cursor.ts";
import { OpenCodeBackend } from "../../src/backends/opencode.ts";

// Generous timeout for real API calls (2 minutes)
const E2E_TIMEOUT = 120_000;

// Simple math prompt that produces a deterministic short answer
const PROMPT = "What is 2+2? Reply with ONLY the number, nothing else.";

// ─── Helpers ─────────────────────────────────────────────────

function cliAvailable(cmd: string): boolean {
  try {
    Bun.spawnSync([cmd, "--version"], { stdin: "ignore" });
    return true;
  } catch {
    return false;
  }
}

function makeTmpDir(prefix: string): string {
  return mkdtempSync(join(tmpdir(), `e2e-${prefix}-`));
}

// ─── Claude Code (via DeepSeek) ──────────────────────────────

const hasClaudeCli = cliAvailable("claude");
const hasDeepSeekKey = !!process.env.DEEPSEEK_API_KEY;
const skipClaudeE2E = !!process.env.SKIP_CLAUDE_E2E;

describe.skipIf(!hasClaudeCli || !hasDeepSeekKey || skipClaudeE2E)(
  "E2E: Claude Code (DeepSeek)",
  () => {
    let savedEnv: Record<string, string | undefined>;
    let tmpDir: string;

    beforeAll(() => {
      // Save env and configure DeepSeek backend
      savedEnv = {
        ANTHROPIC_BASE_URL: process.env.ANTHROPIC_BASE_URL,
        ANTHROPIC_AUTH_TOKEN: process.env.ANTHROPIC_AUTH_TOKEN,
        ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
        ANTHROPIC_MODEL: process.env.ANTHROPIC_MODEL,
        CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:
          process.env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC,
        DISABLE_AUTOUPDATER: process.env.DISABLE_AUTOUPDATER,
      };

      process.env.ANTHROPIC_BASE_URL = "https://api.deepseek.com/anthropic";
      process.env.ANTHROPIC_AUTH_TOKEN = process.env.DEEPSEEK_API_KEY;
      process.env.ANTHROPIC_API_KEY = "";
      process.env.ANTHROPIC_MODEL = "deepseek-chat";
      process.env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1";
      process.env.DISABLE_AUTOUPDATER = "1";

      // Use temp dir as workspace to avoid CLAUDE.md triggering agent operations
      tmpDir = makeTmpDir("claude");
    });

    afterAll(() => {
      // Restore env
      for (const [key, value] of Object.entries(savedEnv)) {
        if (value === undefined) {
          delete process.env[key];
        } else {
          process.env[key] = value;
        }
      }
      try {
        rmSync(tmpDir, { recursive: true, force: true });
      } catch { /* ignore */ }
    });

    test(
      "sends prompt and receives response",
      async () => {
        const backend = new ClaudeCodeBackend({
          outputFormat: "text",
          cwd: tmpDir,
          appendSystemPrompt:
            "You are a simple calculator. Reply with ONLY the number. No explanation. No tools.",
          timeout: E2E_TIMEOUT,
        });

        const result = await backend.send(PROMPT);
        expect(result.content).toBeDefined();
        expect(result.content.length).toBeGreaterThan(0);
        // Response should contain "4" somewhere
        expect(result.content).toContain("4");
      },
      E2E_TIMEOUT,
    );
  },
);

// ─── OpenCode (via DeepSeek) ─────────────────────────────────

const hasOpenCode = cliAvailable("opencode");

describe.skipIf(!hasOpenCode || !hasDeepSeekKey)(
  "E2E: OpenCode (DeepSeek)",
  () => {
    let tmpDir: string;

    beforeAll(() => {
      tmpDir = makeTmpDir("opencode");
    });

    afterAll(() => {
      try {
        rmSync(tmpDir, { recursive: true, force: true });
      } catch { /* ignore */ }
    });

    test(
      "sends prompt and receives response",
      async () => {
        const backend = new OpenCodeBackend({
          model: "deepseek/deepseek-chat",
          cwd: tmpDir,
          timeout: E2E_TIMEOUT,
        });

        const result = await backend.send(PROMPT);
        expect(result.content).toBeDefined();
        expect(result.content.length).toBeGreaterThan(0);
        expect(result.content).toContain("4");
      },
      E2E_TIMEOUT,
    );
  },
);

// ─── Codex CLI (OpenAI) ─────────────────────────────────────

const hasCodex = cliAvailable("codex");
const hasOpenAIKey = !!process.env.OPENAI_API_KEY;
const hasZenMuxKey = !!process.env.ZENMUX_API_KEY;
// Codex needs Responses API — either OpenAI directly or ZenMux proxy
const hasCodexAuth = hasOpenAIKey || hasZenMuxKey;

describe.skipIf(!hasCodex || !hasCodexAuth)(
  "E2E: Codex CLI",
  () => {
    let tmpDir: string;
    let savedEnv: Record<string, string | undefined>;

    beforeAll(() => {
      tmpDir = makeTmpDir("codex");

      // If using ZenMux instead of OpenAI, set up env
      if (hasZenMuxKey && !hasOpenAIKey) {
        savedEnv = { OPENAI_API_KEY: process.env.OPENAI_API_KEY };
        process.env.OPENAI_API_KEY = process.env.ZENMUX_API_KEY;
      }
    });

    afterAll(() => {
      if (savedEnv) {
        for (const [key, value] of Object.entries(savedEnv)) {
          if (value === undefined) delete process.env[key];
          else process.env[key] = value;
        }
      }
      try {
        rmSync(tmpDir, { recursive: true, force: true });
      } catch { /* ignore */ }
    });

    test(
      "sends prompt and receives response",
      async () => {
        const backend = new CodexBackend({
          cwd: tmpDir,
          timeout: E2E_TIMEOUT,
        });

        const result = await backend.send(PROMPT);
        expect(result.content).toBeDefined();
        expect(result.content.length).toBeGreaterThan(0);
        expect(result.content).toContain("4");
      },
      E2E_TIMEOUT,
    );
  },
);

// ─── Cursor Agent ────────────────────────────────────────────

const hasCursor =
  cliAvailable("agent") || cliAvailable("cursor-agent");
const hasCursorKey = !!process.env.CURSOR_API_KEY;

describe.skipIf(!hasCursor || !hasCursorKey)(
  "E2E: Cursor Agent",
  () => {
    let tmpDir: string;

    beforeAll(() => {
      tmpDir = makeTmpDir("cursor");
    });

    afterAll(() => {
      try {
        rmSync(tmpDir, { recursive: true, force: true });
      } catch { /* ignore */ }
    });

    test(
      "sends prompt and receives response",
      async () => {
        const backend = new CursorBackend({
          cwd: tmpDir,
          timeout: E2E_TIMEOUT,
        });

        const result = await backend.send(PROMPT);
        expect(result.content).toBeDefined();
        expect(result.content.length).toBeGreaterThan(0);
        expect(result.content).toContain("4");
      },
      E2E_TIMEOUT,
    );
  },
);

// ─── Availability Summary ────────────────────────────────────

describe("E2E: Backend Availability", () => {
  test("reports which backends are testable", () => {
    const status = {
      "Claude Code CLI": hasClaudeCli ? "installed" : "missing",
      "Codex CLI": hasCodex ? "installed" : "missing",
      "Cursor Agent": hasCursor ? "installed" : "missing",
      "OpenCode CLI": hasOpenCode ? "installed" : "missing",
      DEEPSEEK_API_KEY: hasDeepSeekKey ? "set" : "not set",
      OPENAI_API_KEY: hasOpenAIKey ? "set" : "not set",
      ZENMUX_API_KEY: hasZenMuxKey ? "set" : "not set",
      CURSOR_API_KEY: hasCursorKey ? "set" : "not set",
      SKIP_CLAUDE_E2E: skipClaudeE2E ? "yes (skipped)" : "no",
    };

    console.log("\n=== E2E Backend Availability ===");
    for (const [name, value] of Object.entries(status)) {
      const icon = value === "installed" || value === "set" ? "+" : "-";
      console.log(`  [${icon}] ${name}: ${value}`);
    }
    console.log("");

    // This test always passes — it's just informational
    expect(true).toBe(true);
  });
});
