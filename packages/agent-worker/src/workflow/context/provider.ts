/**
 * Context Provider interface
 * Abstract storage layer for channel, inbox, document, and resource operations
 */

import type { ChannelEntry, InboxMessage, ResourceResult, ResourceType } from './types.js'

/**
 * Context Provider interface - storage abstraction for workflow context
 *
 * Implementations:
 * - MemoryContextProvider: In-memory storage for testing
 * - FileContextProvider: File-based storage with markdown format
 */
export interface ContextProvider {
  // ==================== Channel ====================

  /**
   * Append a message to the channel
   * @param from - Agent name or 'system'
   * @param message - Message content (may include @mentions)
   * @returns The created channel entry with extracted mentions
   */
  appendChannel(from: string, message: string): Promise<ChannelEntry>

  /**
   * Read channel entries
   * @param since - Optional timestamp to read entries after
   * @param limit - Optional max entries to return
   * @returns Array of channel entries
   */
  readChannel(since?: string, limit?: number): Promise<ChannelEntry[]>

  // ==================== Inbox ====================

  /**
   * Get unread inbox messages for an agent
   * Does NOT acknowledge - use ackInbox() after processing
   * @param agent - Agent name to get inbox for
   * @returns Array of unread inbox messages with priority
   */
  getInbox(agent: string): Promise<InboxMessage[]>

  /**
   * Acknowledge inbox messages up to a timestamp
   * @param agent - Agent name acknowledging
   * @param until - Timestamp to acknowledge up to (inclusive)
   */
  ackInbox(agent: string, until: string): Promise<void>

  // ==================== Team Documents ====================

  /**
   * Read a document
   * @param file - Document file path (default: notes.md)
   * @returns Document content (empty string if not exists)
   */
  readDocument(file?: string): Promise<string>

  /**
   * Write/replace a document
   * @param content - New document content
   * @param file - Document file path (default: notes.md)
   */
  writeDocument(content: string, file?: string): Promise<void>

  /**
   * Append to a document
   * @param content - Content to append
   * @param file - Document file path (default: notes.md)
   */
  appendDocument(content: string, file?: string): Promise<void>

  /**
   * List all document files
   * @returns Array of document file paths (relative to document directory)
   */
  listDocuments(): Promise<string[]>

  /**
   * Create a new document
   * @param file - Document file path
   * @param content - Initial content
   * @throws Error if document already exists
   */
  createDocument(file: string, content: string): Promise<void>

  // ==================== Resources ====================
  // General-purpose resource reference mechanism.
  // Resources can be referenced from channel messages, documents, or anywhere.

  /**
   * Create a resource
   * @param content - Resource content
   * @param createdBy - Agent creating the resource
   * @param type - Content type hint (default: 'text')
   * @returns Resource ID and ready-to-use reference
   */
  createResource(
    content: string,
    createdBy: string,
    type?: ResourceType
  ): Promise<ResourceResult>

  /**
   * Read resource content by ID
   * @param id - Resource ID (e.g., res_abc123)
   * @returns Resource content or null if not found
   */
  readResource(id: string): Promise<string | null>
}
