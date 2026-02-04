/**
 * Backend factory and exports
 */

export * from './types.ts'
export { ClaudeCliBackend, type ClaudeCliOptions } from './claude-cli.ts'
export { CodexCliBackend, type CodexCliOptions } from './codex-cli.ts'
export { CursorCliBackend, type CursorCliOptions } from './cursor-cli.ts'
export { SdkBackend, type SdkBackendOptions } from './sdk.ts'

import type { Backend, BackendType } from './types.ts'
import { ClaudeCliBackend, type ClaudeCliOptions } from './claude-cli.ts'
import { CodexCliBackend, type CodexCliOptions } from './codex-cli.ts'
import { CursorCliBackend, type CursorCliOptions } from './cursor-cli.ts'
import { SdkBackend, type SdkBackendOptions } from './sdk.ts'

export type BackendOptions =
  | { type: 'sdk'; model: string; maxTokens?: number }
  | { type: 'claude'; model?: string; options?: Omit<ClaudeCliOptions, 'model'> }
  | { type: 'codex'; model?: string; options?: Omit<CodexCliOptions, 'model'> }
  | { type: 'cursor'; model?: string; options?: Omit<CursorCliOptions, 'model'> }

/**
 * Create a backend instance
 */
export function createBackend(config: BackendOptions): Backend {
  switch (config.type) {
    case 'sdk':
      return new SdkBackend({ model: config.model, maxTokens: config.maxTokens })
    case 'claude':
      return new ClaudeCliBackend({ ...config.options, model: config.model })
    case 'codex':
      return new CodexCliBackend({ ...config.options, model: config.model })
    case 'cursor':
      return new CursorCliBackend({ ...config.options, model: config.model })
    default:
      throw new Error(`Unknown backend type: ${(config as { type: string }).type}`)
  }
}

/**
 * Check which backends are available
 */
export async function checkBackends(): Promise<Record<BackendType, boolean>> {
  const claude = new ClaudeCliBackend()
  const codex = new CodexCliBackend()
  const cursor = new CursorCliBackend()

  const [claudeAvailable, codexAvailable, cursorAvailable] = await Promise.all([
    claude.isAvailable(),
    codex.isAvailable(),
    cursor.isAvailable(),
  ])

  return {
    sdk: true, // Always available (depends on API keys at runtime)
    claude: claudeAvailable,
    codex: codexAvailable,
    cursor: cursorAvailable,
  }
}

/**
 * List available backends with info
 */
export async function listBackends(): Promise<
  Array<{ type: BackendType; available: boolean; name: string }>
> {
  const availability = await checkBackends()

  return [
    { type: 'sdk', available: availability.sdk, name: 'Vercel AI SDK' },
    { type: 'claude', available: availability.claude, name: 'Claude Code CLI' },
    { type: 'codex', available: availability.codex, name: 'OpenAI Codex CLI' },
    { type: 'cursor', available: availability.cursor, name: 'Cursor Agent CLI' },
  ]
}
