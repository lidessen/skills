/**
 * Claude Code CLI backend
 * Uses `claude -p` for non-interactive mode
 *
 * @see https://code.claude.com/docs/en/headless
 */

import { execa, ExecaError } from 'execa'
import type { Backend, BackendResponse } from './types.ts'

export interface ClaudeCodeOptions {
  /** Model to use (e.g., 'opus', 'sonnet') */
  model?: string
  /** Additional system prompt to append */
  appendSystemPrompt?: string
  /** Allowed tools (permission rule syntax) */
  allowedTools?: string[]
  /** Output format: 'text' | 'json' | 'stream-json' */
  outputFormat?: 'text' | 'json' | 'stream-json'
  /** Continue most recent conversation */
  continue?: boolean
  /** Resume specific session by ID */
  resume?: string
  /** Working directory */
  cwd?: string
  /** Timeout in milliseconds */
  timeout?: number
}

export class ClaudeCodeBackend implements Backend {
  readonly type = 'claude' as const
  private options: ClaudeCodeOptions

  constructor(options: ClaudeCodeOptions = {}) {
    this.options = {
      timeout: 300000, // 5 minute default
      ...options,
    }
  }

  async send(message: string, options?: { system?: string }): Promise<BackendResponse> {
    const args = this.buildArgs(message, options)

    try {
      const { stdout } = await execa('claude', args, {
        cwd: this.options.cwd,
        stdin: 'ignore',
        timeout: this.options.timeout,
      })

      // Parse response based on output format
      if (this.options.outputFormat === 'json') {
        try {
          const parsed = JSON.parse(stdout)
          return {
            content: parsed.content || parsed.result || stdout,
            toolCalls: parsed.toolCalls,
            usage: parsed.usage,
          }
        } catch {
          return { content: stdout.trim() }
        }
      }

      return { content: stdout.trim() }
    } catch (error) {
      if (error instanceof ExecaError) {
        throw new Error(`claude failed (exit ${error.exitCode}): ${error.stderr || error.shortMessage}`)
      }
      throw error
    }
  }

  async isAvailable(): Promise<boolean> {
    try {
      await execa('claude', ['--version'], { stdin: 'ignore', timeout: 5000 })
      return true
    } catch {
      return false
    }
  }

  getInfo(): { name: string; version?: string; model?: string } {
    return {
      name: 'Claude Code CLI',
      model: this.options.model,
    }
  }

  private buildArgs(message: string, options?: { system?: string }): string[] {
    const args: string[] = ['-p', message]

    if (this.options.model) {
      args.push('--model', this.options.model)
    }

    if (options?.system || this.options.appendSystemPrompt) {
      const system = options?.system || this.options.appendSystemPrompt
      args.push('--append-system-prompt', system!)
    }

    if (this.options.allowedTools?.length) {
      args.push('--allowed-tools', this.options.allowedTools.join(','))
    }

    if (this.options.outputFormat) {
      args.push('--output-format', this.options.outputFormat)
    }

    if (this.options.continue) {
      args.push('--continue')
    }

    if (this.options.resume) {
      args.push('--resume', this.options.resume)
    }

    return args
  }
}
