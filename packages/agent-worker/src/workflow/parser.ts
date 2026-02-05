/**
 * Workflow file parser
 */

import { readFileSync, existsSync } from 'node:fs'
import { basename, dirname, join, resolve } from 'node:path'
import { parse as parseYaml } from 'yaml'
import type {
  WorkflowFile,
  ParsedWorkflow,
  ResolvedAgent,
  ValidationResult,
  ValidationError,
  Task,
  AgentDefinition,
} from './types.ts'
import {
  isShellTask,
  isSendTask,
  isConditionalTask,
  isParallelTask,
} from './types.ts'

/**
 * Parse a workflow file
 */
export async function parseWorkflowFile(filePath: string): Promise<ParsedWorkflow> {
  const absolutePath = resolve(filePath)

  if (!existsSync(absolutePath)) {
    throw new Error(`Workflow file not found: ${absolutePath}`)
  }

  const content = readFileSync(absolutePath, 'utf-8')
  const workflowDir = dirname(absolutePath)

  let raw: WorkflowFile
  try {
    raw = parseYaml(content) as WorkflowFile
  } catch (error) {
    throw new Error(`Failed to parse YAML: ${error instanceof Error ? error.message : String(error)}`)
  }

  // Validate basic structure
  const validation = validateWorkflow(raw)
  if (!validation.valid) {
    const messages = validation.errors.map(e => `  - ${e.path}: ${e.message}`).join('\n')
    throw new Error(`Invalid workflow file:\n${messages}`)
  }

  // Extract name from filename if not specified
  const name = raw.name || basename(absolutePath, '.yml').replace('.yaml', '')

  // Resolve agents
  const agents: Record<string, ResolvedAgent> = {}
  for (const [agentName, agentDef] of Object.entries(raw.agents)) {
    agents[agentName] = await resolveAgent(agentDef, workflowDir)
  }

  return {
    name,
    filePath: absolutePath,
    agents,
    tasks: raw.tasks || [],
  }
}

/**
 * Resolve agent definition (load system prompt from file if needed)
 */
async function resolveAgent(agent: AgentDefinition, workflowDir: string): Promise<ResolvedAgent> {
  let resolvedSystemPrompt = agent.system_prompt

  // Check if system_prompt is a file path
  if (agent.system_prompt.endsWith('.txt') || agent.system_prompt.endsWith('.md')) {
    const promptPath = agent.system_prompt.startsWith('/')
      ? agent.system_prompt
      : join(workflowDir, agent.system_prompt)

    if (existsSync(promptPath)) {
      resolvedSystemPrompt = readFileSync(promptPath, 'utf-8')
    }
    // If file doesn't exist, use as-is (might be intentional literal)
  }

  return {
    ...agent,
    resolvedSystemPrompt,
  }
}

/**
 * Validate workflow structure
 */
export function validateWorkflow(workflow: unknown): ValidationResult {
  const errors: ValidationError[] = []

  if (!workflow || typeof workflow !== 'object') {
    errors.push({ path: '', message: 'Workflow must be an object' })
    return { valid: false, errors }
  }

  const w = workflow as Record<string, unknown>

  // Validate agents (required)
  if (!w.agents || typeof w.agents !== 'object') {
    errors.push({ path: 'agents', message: 'Required field "agents" must be an object' })
  } else {
    const agents = w.agents as Record<string, unknown>
    for (const [name, agent] of Object.entries(agents)) {
      validateAgent(name, agent, errors)
    }
  }

  // Validate tasks (optional)
  if (w.tasks !== undefined) {
    if (!Array.isArray(w.tasks)) {
      errors.push({ path: 'tasks', message: 'Tasks must be an array' })
    } else {
      for (let i = 0; i < w.tasks.length; i++) {
        validateTask(`tasks[${i}]`, w.tasks[i], errors)
      }
    }
  }

  return { valid: errors.length === 0, errors }
}

function validateAgent(name: string, agent: unknown, errors: ValidationError[]): void {
  const path = `agents.${name}`

  if (!agent || typeof agent !== 'object') {
    errors.push({ path, message: 'Agent must be an object' })
    return
  }

  const a = agent as Record<string, unknown>

  if (!a.model || typeof a.model !== 'string') {
    errors.push({ path: `${path}.model`, message: 'Required field "model" must be a string' })
  }

  if (!a.system_prompt || typeof a.system_prompt !== 'string') {
    errors.push({ path: `${path}.system_prompt`, message: 'Required field "system_prompt" must be a string' })
  }

  if (a.tools !== undefined && !Array.isArray(a.tools)) {
    errors.push({ path: `${path}.tools`, message: 'Optional field "tools" must be an array' })
  }
}

function validateTask(path: string, task: unknown, errors: ValidationError[]): void {
  if (!task || typeof task !== 'object') {
    errors.push({ path, message: 'Task must be an object' })
    return
  }

  const t = task as Record<string, unknown>

  // Check task type
  const hasShell = 'shell' in t
  const hasSend = 'send' in t
  const hasIf = 'if' in t
  const hasParallel = 'parallel' in t

  const typeCount = [hasShell, hasSend, hasIf, hasParallel].filter(Boolean).length

  if (typeCount === 0) {
    errors.push({ path, message: 'Task must have one of: shell, send, if, parallel' })
    return
  }

  if (hasParallel) {
    // Parallel task
    if (!Array.isArray(t.parallel)) {
      errors.push({ path: `${path}.parallel`, message: 'Parallel tasks must be an array' })
    } else {
      for (let i = 0; i < t.parallel.length; i++) {
        validateTask(`${path}.parallel[${i}]`, t.parallel[i], errors)
      }
    }
  } else if (hasIf) {
    // Conditional task
    if (typeof t.if !== 'string') {
      errors.push({ path: `${path}.if`, message: 'Condition must be a string' })
    }
    // Conditional must have either shell or send
    if (!hasShell && !hasSend) {
      errors.push({ path, message: 'Conditional task must have "shell" or "send"' })
    }
  } else if (hasSend) {
    // Send task
    if (typeof t.send !== 'string') {
      errors.push({ path: `${path}.send`, message: 'Send message must be a string' })
    }
    if (!t.to || typeof t.to !== 'string') {
      errors.push({ path: `${path}.to`, message: 'Send task requires "to" field' })
    }
  } else if (hasShell) {
    // Shell task
    if (typeof t.shell !== 'string') {
      errors.push({ path: `${path}.shell`, message: 'Shell command must be a string' })
    }
  }
}

/**
 * Get all agent names referenced in tasks
 */
export function getReferencedAgents(tasks: Task[]): Set<string> {
  const agents = new Set<string>()

  function collectFromTask(task: Task): void {
    if (isSendTask(task) || (isConditionalTask(task) && task.to)) {
      agents.add(task.to!)
    }
    if (isParallelTask(task)) {
      for (const subTask of task.parallel) {
        collectFromTask(subTask)
      }
    }
  }

  for (const task of tasks) {
    collectFromTask(task)
  }

  return agents
}
