/**
 * OpenAI Codex CLI backend
 * Uses `codex exec` for non-interactive mode
 *
 * @see https://developers.openai.com/codex/noninteractive/
 */

import { execa, ExecaError } from 'execa'
import type { Backend, BackendResponse } from './types.ts'

export interface CodexOptions {
  /** Model to use (e.g., 'gpt-5.2-codex') */
  model?: string
  /** Output as JSON events */
  json?: boolean
  /** Working directory */
  cwd?: string
  /** Skip git repo check */
  skipGitRepoCheck?: boolean
  /** Approval mode: 'suggest' | 'auto-edit' | 'full-auto' */
  approvalMode?: 'suggest' | 'auto-edit' | 'full-auto'
  /** Resume a previous session */
  resume?: string
  /** Timeout in milliseconds */
  timeout?: number
}

export class CodexBackend implements Backend {
  readonly type = 'codex' as const
  private options: CodexOptions

  constructor(options: CodexOptions = {}) {
    this.options = {
      timeout: 300000, // 5 minute default
      ...options,
    }
  }

  async send(message: string, _options?: { system?: string }): Promise<BackendResponse> {
    const args = this.buildArgs(message)

    try {
      const { stdout } = await execa('codex', args, {
        cwd: this.options.cwd,
        stdin: 'ignore',
        timeout: this.options.timeout,
      })

      // Parse response based on output format
      if (this.options.json) {
        try {
          // Codex outputs newline-delimited JSON events
          const lines = stdout.trim().split('\n')
          const lastLine = lines[lines.length - 1]
          if (!lastLine) {
            return { content: stdout.trim() }
          }
          const lastEvent = JSON.parse(lastLine)
          return {
            content: lastEvent.message || lastEvent.content || stdout,
            toolCalls: lastEvent.toolCalls,
            usage: lastEvent.usage,
          }
        } catch {
          return { content: stdout.trim() }
        }
      }

      return { content: stdout.trim() }
    } catch (error) {
      if (error instanceof ExecaError) {
        throw new Error(`codex failed (exit ${error.exitCode}): ${error.stderr || error.shortMessage}`)
      }
      throw error
    }
  }

  async isAvailable(): Promise<boolean> {
    try {
      await execa('codex', ['--version'], { stdin: 'ignore', timeout: 5000 })
      return true
    } catch {
      return false
    }
  }

  getInfo(): { name: string; version?: string; model?: string } {
    return {
      name: 'OpenAI Codex CLI',
      model: this.options.model,
    }
  }

  private buildArgs(message: string): string[] {
    const args: string[] = ['exec', message]

    if (this.options.model) {
      args.push('--model', this.options.model)
    }

    if (this.options.json) {
      args.push('--json')
    }

    if (this.options.skipGitRepoCheck) {
      args.push('--skip-git-repo-check')
    }

    if (this.options.approvalMode) {
      args.push('--approval-mode', this.options.approvalMode)
    }

    if (this.options.resume) {
      args.push('--resume', this.options.resume)
    }

    return args
  }
}
