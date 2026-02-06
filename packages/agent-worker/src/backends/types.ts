/**
 * Backend types for different AI execution engines
 */

export type BackendType = 'sdk' | 'claude' | 'codex' | 'cursor'

export interface BackendConfig {
  type: BackendType
  /** Model identifier (interpretation depends on backend) */
  model?: string
  /** Additional CLI flags or SDK options */
  options?: Record<string, unknown>
}

// ==================== Model Configuration ====================

/** Default model per backend */
export const BACKEND_DEFAULT_MODELS: Record<BackendType, string> = {
  sdk: 'claude-sonnet-4-5',
  claude: 'sonnet',
  cursor: 'sonnet-4.5',
  codex: 'gpt-5.2-codex',
}

/**
 * Model translation for Cursor backend
 * Cursor uses its own naming convention
 */
export const CURSOR_MODEL_MAP: Record<string, string> = {
  // Anthropic models
  sonnet: 'sonnet-4.5',
  opus: 'opus-4.5',
  'sonnet-4.5': 'sonnet-4.5',
  'opus-4.5': 'opus-4.5',
  'opus-4.6': 'opus-4.6',
  'claude-sonnet-4-5': 'sonnet-4.5',
  'claude-opus-4-5': 'opus-4.5',
  'anthropic/claude-sonnet-4-5': 'sonnet-4.5',
  'anthropic/claude-opus-4-5': 'opus-4.5',
  // Thinking models
  'sonnet-4.5-thinking': 'sonnet-4.5-thinking',
  'opus-4.5-thinking': 'opus-4.5-thinking',
  'opus-4.6-thinking': 'opus-4.6-thinking',
  // OpenAI/GPT models
  'gpt-5.2': 'gpt-5.2',
  'gpt-5.1': 'gpt-5.1-high',
  'gpt-4': 'gpt-5.2',
  // Gemini
  'gemini-pro': 'gemini-3-pro',
  'gemini-flash': 'gemini-3-flash',
  // Special
  auto: 'auto',
}

/**
 * Model translation for Claude CLI backend
 * Claude CLI uses short model names
 */
export const CLAUDE_MODEL_MAP: Record<string, string> = {
  sonnet: 'sonnet',
  opus: 'opus',
  haiku: 'haiku',
  'sonnet-4.5': 'sonnet',
  'opus-4.5': 'opus',
  'claude-sonnet-4-5': 'sonnet',
  'claude-opus-4': 'opus',
  'claude-haiku-3-5': 'haiku',
  'anthropic/claude-sonnet-4-5': 'sonnet',
  'anthropic/claude-opus-4': 'opus',
}

/**
 * Model translation for Codex CLI backend
 */
export const CODEX_MODEL_MAP: Record<string, string> = {
  'gpt-5.2-codex': 'gpt-5.2-codex',
  'gpt-5.2': 'gpt-5.2-codex',
  o3: 'o3',
  'o3-mini': 'o3-mini',
}

/**
 * Model aliases for SDK (Anthropic format)
 */
export const SDK_MODEL_ALIASES: Record<string, string> = {
  sonnet: 'claude-sonnet-4-5-20250514',
  opus: 'claude-opus-4-20250514',
  haiku: 'claude-haiku-3-5-20250514',
  'claude-sonnet-4-5': 'claude-sonnet-4-5-20250514',
  'claude-opus-4': 'claude-opus-4-20250514',
  'claude-haiku-3-5': 'claude-haiku-3-5-20250514',
}

/**
 * Get the model name for a specific backend
 * Translates generic model names to backend-specific format
 */
export function getModelForBackend(model: string | undefined, backend: BackendType): string {
  // Use default if no model specified
  if (!model) {
    return BACKEND_DEFAULT_MODELS[backend]
  }

  // Strip provider prefix if present (e.g., "anthropic/claude-sonnet-4-5" -> "claude-sonnet-4-5")
  const normalizedModel = model.includes('/') ? model.split('/').pop()! : model

  switch (backend) {
    case 'sdk':
      // For SDK, try alias first, otherwise preserve original model string
      return SDK_MODEL_ALIASES[normalizedModel] || model

    case 'cursor':
      return CURSOR_MODEL_MAP[model] || CURSOR_MODEL_MAP[normalizedModel] || normalizedModel

    case 'claude':
      return CLAUDE_MODEL_MAP[model] || CLAUDE_MODEL_MAP[normalizedModel] || normalizedModel

    case 'codex':
      return CODEX_MODEL_MAP[model] || CODEX_MODEL_MAP[normalizedModel] || normalizedModel

    default:
      return normalizedModel
  }
}

export interface BackendResponse {
  content: string
  /** Tool calls made during execution (if supported) */
  toolCalls?: Array<{
    name: string
    arguments: unknown
    result: unknown
  }>
  /** Usage statistics (if available) */
  usage?: {
    input: number
    output: number
    total: number
  }
}

export interface Backend {
  readonly type: BackendType
  /** Send a message and get a response */
  send(message: string, options?: { system?: string }): Promise<BackendResponse>
  /** Check if the backend is available (CLI installed, API key set, etc.) */
  isAvailable(): Promise<boolean>
  /** Get backend info for display */
  getInfo(): { name: string; version?: string; model?: string }
}
