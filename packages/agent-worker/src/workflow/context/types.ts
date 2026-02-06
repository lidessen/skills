/**
 * Context types for workflow
 * Shared context for agent collaboration via channel + document
 */

/** A single channel entry */
export interface ChannelEntry {
  /** ISO timestamp */
  timestamp: string
  /** Author agent name or 'system' */
  from: string
  /** Message content */
  message: string
  /** Extracted @mentions */
  mentions: string[]
}

/** @mention notification */
export interface MentionNotification {
  /** Who sent the message */
  from: string
  /** Who was mentioned */
  target: string
  /** The message content */
  message: string
  /** Entry timestamp */
  timestamp: string
}

/**
 * Context configuration in workflow file
 *
 * - undefined (not set): default file provider enabled
 * - false: explicitly disabled
 * - { provider: 'file', config?: {...} }: file provider with optional config
 * - { provider: 'memory' }: memory provider (for testing)
 */
export type ContextConfig = false | FileContextConfig | MemoryContextConfig

/** File-based context provider configuration */
export interface FileContextConfig {
  provider: 'file'
  config?: FileProviderConfig
}

/** Memory-based context provider configuration (for testing) */
export interface MemoryContextConfig {
  provider: 'memory'
}

/** Configuration for file provider */
export interface FileProviderConfig {
  /** Context directory (default: .workflow/${{ instance }}/) */
  dir?: string
  /** Channel file name (default: channel.md) */
  channel?: string
  /** Document file name (default: notes.md) */
  document?: string
}

/** Default context configuration values */
export const CONTEXT_DEFAULTS = {
  dir: '.workflow/${{ instance }}/',
  channel: 'channel.md',
  document: 'notes.md',
} as const

/** Mention pattern for extracting @mentions */
export const MENTION_PATTERN = /@([a-zA-Z][a-zA-Z0-9_-]*)/g

/**
 * Extract @mentions from a message
 */
export function extractMentions(message: string, validAgents: string[]): string[] {
  const mentions: string[] = []
  let match: RegExpExecArray | null

  // Reset regex state
  MENTION_PATTERN.lastIndex = 0

  while ((match = MENTION_PATTERN.exec(message)) !== null) {
    const agent = match[1]
    if (validAgents.includes(agent) && !mentions.includes(agent)) {
      mentions.push(agent)
    }
  }

  return mentions
}
