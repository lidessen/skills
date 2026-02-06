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
  ResolvedContext,
  ValidationResult,
  ValidationError,
  SetupTask,
  AgentDefinition,
} from './types.ts'
import { CONTEXT_DEFAULTS } from './context/types.js'

/**
 * Parse options
 */
export interface ParseOptions {
  /** Instance name for context directory (default: 'default') */
  instance?: string
}

/**
 * Parse a workflow file
 */
export async function parseWorkflowFile(
  filePath: string,
  options?: ParseOptions
): Promise<ParsedWorkflow> {
  const absolutePath = resolve(filePath)
  const instance = options?.instance || 'default'

  if (!existsSync(absolutePath)) {
    throw new Error(`Workflow file not found: ${absolutePath}`)
  }

  const content = readFileSync(absolutePath, 'utf-8')
  const workflowDir = dirname(absolutePath)

  let raw: WorkflowFile
  try {
    raw = parseYaml(content) as WorkflowFile
  } catch (error) {
    throw new Error(
      `Failed to parse YAML: ${error instanceof Error ? error.message : String(error)}`
    )
  }

  // Validate basic structure
  const validation = validateWorkflow(raw)
  if (!validation.valid) {
    const messages = validation.errors.map((e) => `  - ${e.path}: ${e.message}`).join('\n')
    throw new Error(`Invalid workflow file:\n${messages}`)
  }

  // Extract name from filename if not specified
  const name = raw.name || basename(absolutePath, '.yml').replace('.yaml', '')

  // Resolve agents
  const agents: Record<string, ResolvedAgent> = {}
  for (const [agentName, agentDef] of Object.entries(raw.agents)) {
    agents[agentName] = await resolveAgent(agentDef, workflowDir)
  }

  // Resolve context configuration (v2)
  const context = resolveContext(raw.context, workflowDir, instance)

  return {
    name,
    filePath: absolutePath,
    agents,
    context,
    setup: raw.setup || [],
    kickoff: raw.kickoff,
  }
}

/**
 * Resolve context configuration
 */
function resolveContext(
  config: WorkflowFile['context'],
  workflowDir: string,
  instance: string
): ResolvedContext | undefined {
  // undefined = no context
  if (config === undefined) {
    return undefined
  }

  // null or empty object = enable with defaults
  const isDefaultConfig = config === null || (typeof config === 'object' && Object.keys(config).length === 0)

  // Base directory with instance interpolation
  const dirTemplate = isDefaultConfig ? CONTEXT_DEFAULTS.dir : (config?.dir || CONTEXT_DEFAULTS.dir)
  const dir = join(workflowDir, dirTemplate.replace('${{ instance }}', instance))

  const result: ResolvedContext = { dir }

  // Channel configuration
  const channelConfig = isDefaultConfig ? {} : config?.channel
  if (channelConfig !== undefined) {
    const channelFile = channelConfig?.file || CONTEXT_DEFAULTS.channel.file
    result.channel = {
      file: channelFile,
      path: join(dir, channelFile),
    }
  }

  // Document configuration
  const documentConfig = isDefaultConfig ? {} : config?.document
  if (documentConfig !== undefined) {
    const documentFile = documentConfig?.file || CONTEXT_DEFAULTS.document.file
    result.document = {
      file: documentFile,
      path: join(dir, documentFile),
    }
  }

  // If default config, enable both channel and document
  if (isDefaultConfig) {
    result.channel = {
      file: CONTEXT_DEFAULTS.channel.file,
      path: join(dir, CONTEXT_DEFAULTS.channel.file),
    }
    result.document = {
      file: CONTEXT_DEFAULTS.document.file,
      path: join(dir, CONTEXT_DEFAULTS.document.file),
    }
  }

  return result
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

  // Validate context (v2, optional)
  if (w.context !== undefined && w.context !== null) {
    validateContext(w.context, errors)
  }

  // Validate setup (v2, optional)
  if (w.setup !== undefined) {
    if (!Array.isArray(w.setup)) {
      errors.push({ path: 'setup', message: 'Setup must be an array' })
    } else {
      for (let i = 0; i < w.setup.length; i++) {
        validateSetupTask(`setup[${i}]`, w.setup[i], errors)
      }
    }
  }

  // Validate kickoff (optional)
  if (w.kickoff !== undefined && typeof w.kickoff !== 'string') {
    errors.push({ path: 'kickoff', message: 'Kickoff must be a string' })
  }

  return { valid: errors.length === 0, errors }
}

function validateContext(context: unknown, errors: ValidationError[]): void {
  if (typeof context !== 'object') {
    errors.push({ path: 'context', message: 'Context must be an object or null' })
    return
  }

  const c = context as Record<string, unknown>

  if (c.dir !== undefined && typeof c.dir !== 'string') {
    errors.push({ path: 'context.dir', message: 'Context dir must be a string' })
  }

  if (c.channel !== undefined && c.channel !== null && typeof c.channel !== 'object') {
    errors.push({ path: 'context.channel', message: 'Context channel must be an object or null' })
  }

  if (c.document !== undefined && c.document !== null && typeof c.document !== 'object') {
    errors.push({ path: 'context.document', message: 'Context document must be an object or null' })
  }
}

function validateSetupTask(path: string, task: unknown, errors: ValidationError[]): void {
  if (!task || typeof task !== 'object') {
    errors.push({ path, message: 'Setup task must be an object' })
    return
  }

  const t = task as Record<string, unknown>

  if (!t.shell || typeof t.shell !== 'string') {
    errors.push({ path: `${path}.shell`, message: 'Setup task requires "shell" field as string' })
  }

  if (t.as !== undefined && typeof t.as !== 'string') {
    errors.push({ path: `${path}.as`, message: 'Setup task "as" field must be a string' })
  }
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
    errors.push({
      path: `${path}.system_prompt`,
      message: 'Required field "system_prompt" must be a string',
    })
  }

  if (a.tools !== undefined && !Array.isArray(a.tools)) {
    errors.push({ path: `${path}.tools`, message: 'Optional field "tools" must be an array' })
  }
}

/**
 * Get all agent names mentioned in kickoff
 */
export function getKickoffMentions(kickoff: string, validAgents: string[]): string[] {
  const mentions: string[] = []
  const pattern = /@([a-zA-Z][a-zA-Z0-9_-]*)/g
  let match: RegExpExecArray | null

  while ((match = pattern.exec(kickoff)) !== null) {
    const agent = match[1]
    if (validAgents.includes(agent) && !mentions.includes(agent)) {
      mentions.push(agent)
    }
  }

  return mentions
}
