/**
 * Workflow file type definitions
 */

export interface WorkflowFile {
  /** Workflow name (defaults to filename) */
  name?: string

  /** Agent definitions */
  agents: Record<string, AgentDefinition>

  /** Task sequence (optional) */
  tasks?: Task[]
}

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
  as?: string | {
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

// Type guards
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

// Parsed workflow with resolved paths
export interface ParsedWorkflow {
  name: string
  filePath: string
  agents: Record<string, ResolvedAgent>
  tasks: Task[]
}

export interface ResolvedAgent extends AgentDefinition {
  /** Resolved system prompt content */
  resolvedSystemPrompt: string
}

// Validation
export interface ValidationError {
  path: string
  message: string
}

export interface ValidationResult {
  valid: boolean
  errors: ValidationError[]
}
