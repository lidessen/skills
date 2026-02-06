/**
 * Mock AI Backend
 *
 * Uses AI SDK generateText with a MockLanguageModelV3 provider
 * and real MCP tool execution for integration testing.
 *
 * The mock model generates scripted tool calls (channel_send)
 * to test the full workflow flow without real LLM API calls.
 */

import { generateText, tool, stepCountIs } from 'ai'
import { MockLanguageModelV3, mockValues } from 'ai/test'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { z } from 'zod'
import { createConnection, type Socket } from 'node:net'
import type { Transport } from '@modelcontextprotocol/sdk/shared/transport.js'
import type { JSONRPCMessage } from '@modelcontextprotocol/sdk/types.js'
import type { AgentBackend, AgentRunContext, AgentRunResult } from '../workflow/controller/types.ts'
import { buildAgentPrompt } from '../workflow/controller/prompt.ts'

// ==================== Unix Socket MCP Transport ====================

/**
 * MCP client transport over Unix socket
 *
 * Connects to the workflow MCP server's Unix socket,
 * sends agent identity header, then speaks MCP JSON-RPC.
 */
class UnixSocketMCPTransport implements Transport {
  private socket: Socket | null = null
  private readBuffer = ''

  onclose?: () => void
  onerror?: (error: Error) => void
  onmessage?: (message: JSONRPCMessage) => void
  sessionId?: string

  constructor(
    private socketPath: string,
    private agentId: string
  ) {}

  async start(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket = createConnection(this.socketPath)

      this.socket.on('connect', () => {
        // Send agent identity header (protocol required by transport.ts)
        this.socket!.write(`X-Agent-Id: ${this.agentId}\n\n`)
        resolve()
      })

      this.socket.on('data', (chunk: Buffer) => {
        this.readBuffer += chunk.toString()
        this.processBuffer()
      })

      this.socket.on('close', () => {
        this.socket = null
        this.onclose?.()
      })

      this.socket.on('error', (err: Error) => {
        reject(err)
        this.onerror?.(err)
      })
    })
  }

  private processBuffer() {
    while (true) {
      const idx = this.readBuffer.indexOf('\n')
      if (idx === -1) break

      const line = this.readBuffer.slice(0, idx).replace(/\r$/, '')
      this.readBuffer = this.readBuffer.slice(idx + 1)

      if (line.trim()) {
        try {
          const message = JSON.parse(line) as JSONRPCMessage
          this.onmessage?.(message)
        } catch {
          // Skip malformed lines
        }
      }
    }
  }

  async send(message: JSONRPCMessage): Promise<void> {
    if (!this.socket) throw new Error('Transport not connected')
    this.socket.write(JSON.stringify(message) + '\n')
  }

  async close(): Promise<void> {
    if (this.socket) {
      this.socket.end()
      this.socket = null
    }
  }
}

// ==================== MCP Tool Bridge ====================

interface MCPToolBridge {
  tools: Record<string, ReturnType<typeof tool>>
  close: () => Promise<void>
}

/**
 * Connect to workflow MCP server and create AI SDK tool wrappers
 */
async function createMCPToolBridge(
  socketPath: string,
  agentName: string
): Promise<MCPToolBridge> {
  const transport = new UnixSocketMCPTransport(socketPath, agentName)
  const client = new Client({ name: agentName, version: '1.0.0' })
  await client.connect(transport)

  const { tools: mcpTools } = await client.listTools()

  const aiTools: Record<string, ReturnType<typeof tool>> = {}
  for (const mcpTool of mcpTools) {
    const toolName = mcpTool.name
    aiTools[toolName] = tool({
      description: mcpTool.description || toolName,
      parameters: z.record(z.unknown()),
      execute: async (args: Record<string, unknown>) => {
        const result = await client.callTool({ name: toolName, arguments: args })
        return result.content
      },
    })
  }

  return {
    tools: aiTools,
    close: () => client.close(),
  }
}

// ==================== Mock AI Backend ====================

/**
 * Mock AI Backend for testing
 *
 * Uses MockLanguageModelV3 to generate scripted tool calls,
 * with real MCP tool execution to test the full workflow flow.
 *
 * Workflow YAML usage:
 * ```yaml
 * agents:
 *   alice:
 *     backend: mock
 *     system_prompt: You are Alice.
 * ```
 */
export class MockAIBackend implements AgentBackend {
  readonly name = 'mock'

  constructor(private debugLog?: (message: string) => void) {}

  async run(ctx: AgentRunContext): Promise<AgentRunResult> {
    const startTime = Date.now()
    const log = this.debugLog || (() => {})

    try {
      // Connect to MCP server and create AI SDK tool wrappers
      const mcp = await createMCPToolBridge(ctx.mcpSocketPath, ctx.name)
      log(`[${ctx.name}] MCP connected, ${Object.keys(mcp.tools).length} tools`)

      // Summarize inbox for the mock response (strip @mentions to avoid re-triggering)
      const inboxSummary = ctx.inbox
        .map((m) => `${m.entry.from}: ${m.entry.message.slice(0, 80).replace(/@/g, '')}`)
        .join('; ')

      // Create mock model with scripted responses:
      // Step 1: call channel_send with a summary of inbox
      // Step 2: end turn
      const mockModel = new MockLanguageModelV3({
        doGenerate: mockValues(
          // Step 1: send channel message
          {
            content: [
              {
                type: 'tool-call' as const,
                toolCallId: `call-${ctx.name}-${Date.now()}`,
                toolName: 'channel_send',
                input: JSON.stringify({
                  message: `[${ctx.name}] Processed: ${inboxSummary.slice(0, 200)}`,
                }),
              },
            ],
            finishReason: { unified: 'tool-calls' as const, raw: 'tool_use' },
            usage: {
              inputTokens: { total: 100, noCache: 100, cacheRead: 0, cacheWrite: 0 },
              outputTokens: { total: 50, text: 50, reasoning: 0 },
            },
          },
          // Step 2: finish
          {
            content: [{ type: 'text' as const, text: `${ctx.name} done.` }],
            finishReason: { unified: 'stop' as const, raw: 'end_turn' },
            usage: {
              inputTokens: { total: 50, noCache: 50, cacheRead: 0, cacheWrite: 0 },
              outputTokens: { total: 10, text: 10, reasoning: 0 },
            },
          }
        ),
      })

      // Build prompt
      const prompt = buildAgentPrompt(ctx)
      log(`[${ctx.name}] Prompt (${prompt.length} chars): ${prompt.slice(0, 150)}...`)

      // Run with AI SDK generateText + real MCP tools
      const result = await generateText({
        model: mockModel,
        tools: mcp.tools,
        prompt,
        system: ctx.agent.resolvedSystemPrompt,
        stopWhen: stepCountIs(3),
      })

      log(`[${ctx.name}] Completed: ${result.text || '(tool calls only)'}`)
      log(`[${ctx.name}] Steps: ${result.steps.length}, Tool calls: ${result.steps.reduce((n, s) => n + s.toolCalls.length, 0)}`)

      // Disconnect
      await mcp.close()

      return { success: true, duration: Date.now() - startTime }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error)
      log(`[${ctx.name}] Error: ${errorMsg}`)
      return { success: false, error: errorMsg, duration: Date.now() - startTime }
    }
  }
}

/**
 * Create a mock AI backend
 */
export function createMockBackend(debugLog?: (msg: string) => void): AgentBackend {
  return new MockAIBackend(debugLog)
}
