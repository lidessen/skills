/**
 * Workflow file type definitions
 * Supports both v1 (tasks) and v2 (setup + kickoff) formats
 */

import type { ContextConfig } from './context/types.js'

// Re-export context types for convenience
export type { ContextConfig, ChannelConfig, DocumentConfig } from './context/types.js'

// ==================== Workflow File ====================

/**
 * Workflow file structure (supports v1 and v2 formats)
 */
export interface WorkflowFile {
  /** Workflow name (defaults to filename) */
  name?: string

  /** Agent definitions */
  agents: Record<string, AgentDefinition>

  /**
   * Shared context configuration (v2)
   * - undefined: no context (agents can't communicate)
   * - null/empty: enable with all defaults
   * - object: custom configuration
   */
  context?: ContextConfig | null

  /**
   * Setup commands (v2) - run before kickoff
   * Shell commands to prepare variables for kickoff
   */
  setup?: SetupTask[]

  /**
   * Kickoff message (v2) - initiates workflow via @mention
   * Optional: if omitted, agents start but wait for external trigger
   */
  kickoff?: string

  /**
   * Task sequence (v1) - deprecated, use setup + kickoff instead
   * @deprecated Use setup + kickoff for new workflows
   */
  tasks?: Task[]
}

// ==================== Agent Definition ====================

export interface AgentDefinition {
  /** Model identifier (e.g., 'anthropic/claude-sonnet-4-5') */
  model: string

  /** System prompt - inline string or file path */
  system_prompt: string

  /** Tool names to enable */
  tools?: string[]

  /** Maximum tokens for response */
  max_tokens?: number

  /** Maximum tool call steps per turn */
  max_steps?: number
}

// ==================== v2: Setup Task ====================

export interface SetupTask {
  /** Shell command to execute */
  shell: string

  /** Variable name to store output */
  as?: string
}

// ==================== v1: Task Types (deprecated) ====================

export type Task = ShellTask | SendTask | ConditionalTask | ParallelTask

export interface ShellTask {
  /** Shell command to execute */
  shell: string

  /** Variable name to store output */
  as?: string
}

export interface SendTask {
  /** Message to send */
  send: string

  /** Target agent name */
  to: string

  /** Output variable - string or object with prompt */
  as?:
    | string
    | {
        name: string
        prompt: string
      }
}

export interface ConditionalTask {
  /** Condition expression */
  if: string

  /** Task to execute if condition is true */
  send?: string
  shell?: string
  to?: string
  as?: string | { name: string; prompt: string }
}

export interface ParallelTask {
  /** Tasks to execute in parallel */
  parallel: Task[]
}

// ==================== Type Guards ====================

export function isShellTask(task: Task): task is ShellTask {
  return 'shell' in task && typeof task.shell === 'string'
}

export function isSendTask(task: Task): task is SendTask {
  return 'send' in task && typeof task.send === 'string'
}

export function isConditionalTask(task: Task): task is ConditionalTask {
  return 'if' in task && typeof task.if === 'string'
}

export function isParallelTask(task: Task): task is ParallelTask {
  return 'parallel' in task && Array.isArray(task.parallel)
}

/** Check if workflow uses v2 format (has context, setup, or kickoff) */
export function isV2Workflow(workflow: WorkflowFile): boolean {
  return (
    workflow.context !== undefined || workflow.setup !== undefined || workflow.kickoff !== undefined
  )
}

/** Check if workflow uses v1 format (has tasks) */
export function isV1Workflow(workflow: WorkflowFile): boolean {
  return workflow.tasks !== undefined && workflow.tasks.length > 0
}

// ==================== Parsed Workflow ====================

export interface ParsedWorkflow {
  name: string
  filePath: string
  agents: Record<string, ResolvedAgent>

  /** v2: Resolved context configuration */
  context?: ResolvedContext

  /** v2: Setup tasks */
  setup: SetupTask[]

  /** v2: Kickoff message (with variables interpolated) */
  kickoff?: string

  /** v1: Task sequence (deprecated) */
  tasks: Task[]
}

export interface ResolvedAgent extends AgentDefinition {
  /** Resolved system prompt content */
  resolvedSystemPrompt: string
}

/** Resolved context configuration with actual paths */
export interface ResolvedContext {
  /** Context directory path */
  dir: string

  /** Channel configuration (if enabled) */
  channel?: {
    file: string
    path: string // Full path: dir + file
  }

  /** Document configuration (if enabled) */
  document?: {
    file: string
    path: string // Full path: dir + file
  }
}

// ==================== Validation ====================

export interface ValidationError {
  path: string
  message: string
}

export interface ValidationResult {
  valid: boolean
  errors: ValidationError[]
}
