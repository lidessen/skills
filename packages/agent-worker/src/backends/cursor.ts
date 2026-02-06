/**
 * Cursor CLI backend
 * Uses `cursor-agent -p` for non-interactive mode
 *
 * NOTE: cursor-agent does NOT support per-invocation MCP config.
 * MCP servers must be registered at project level before running:
 *   cursor agent mcp add workflow-context stdio -- agent-worker context mcp-stdio --socket <path>
 *
 * @see https://cursor.com/docs/cli/headless
 */

import { execa, ExecaError } from 'execa'
import type { Backend, BackendResponse } from './types.ts'

export interface CursorOptions {
  /** Model to use */
  model?: string
  /** Working directory */
  cwd?: string
  /** Timeout in milliseconds */
  timeout?: number
}

export class CursorBackend implements Backend {
  readonly type = 'cursor' as const
  private options: CursorOptions

  constructor(options: CursorOptions = {}) {
    this.options = {
      timeout: 120000, // 2 minute default
      ...options,
    }
  }

  async send(message: string, _options?: { system?: string }): Promise<BackendResponse> {
    const { command, args } = this.buildCommand(message)

    try {
      // IMPORTANT: stdin must be 'ignore' to prevent cursor-agent from hanging
      // See: https://forum.cursor.com/t/node-js-spawn-with-cursor-agent-hangs-and-exits-with-code-143-after-timeout/133709
      const { stdout } = await execa(command, args, {
        cwd: this.options.cwd,
        stdin: 'ignore',
        timeout: this.options.timeout,
      })

      return { content: stdout.trim() }
    } catch (error) {
      if (error instanceof ExecaError) {
        if (error.timedOut) {
          throw new Error(`cursor-agent timed out after ${this.options.timeout}ms`)
        }
        throw new Error(`cursor-agent failed (exit ${error.exitCode}): ${error.stderr || error.shortMessage}`)
      }
      throw error
    }
  }

  async isAvailable(): Promise<boolean> {
    // Try both 'agent' and 'cursor-agent' commands
    const commands = ['cursor-agent', 'agent']

    for (const cmd of commands) {
      try {
        await execa(cmd, ['--version'], { stdin: 'ignore', timeout: 5000 })
        return true
      } catch {
        // Try next command
      }
    }

    return false
  }

  getInfo(): { name: string; version?: string; model?: string } {
    return {
      name: 'Cursor Agent CLI',
      model: this.options.model,
    }
  }

  private buildCommand(message: string): { command: string; args: string[] } {
    // Use 'cursor-agent -p' command
    const args: string[] = ['-p', message]

    if (this.options.model) {
      args.push('--model', this.options.model)
    }

    return { command: 'cursor-agent', args }
  }
}
