/**
 * Context MCP Server — thin orchestrator.
 *
 * Creates an McpServer and registers tools from each category.
 * The actual tool implementations live in their own files:
 *   channel.ts, resource.ts, inbox.ts, team.ts, proposal.ts,
 *   feedback.ts, skills.ts
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { ContextProvider } from "../provider.ts";
import type { Message } from "../types.ts";
import type { ProposalManager } from "../proposals.ts";
import type { FeedbackEntry } from "../../../agent/tools/feedback.ts";
import type { SkillsProvider } from "../../../agent/skills/provider.ts";
import type { MCPToolContext } from "./types.ts";
import { getAgentId, createLogTool } from "./helpers.ts";
import { registerChannelTools } from "./channel.ts";
import { registerResourceTools } from "./resource.ts";
import { registerInboxTools } from "./inbox.ts";
import { registerTeamTools } from "./team.ts";
import { registerProposalTools } from "./proposal.ts";
import { registerFeedbackTool } from "./feedback.ts";
import { registerSkillsTools } from "./skills.ts";

// ── Options ──────────────────────────────────────────────────────

export interface ContextMCPServerOptions {
  /** Context provider for storage */
  provider: ContextProvider;
  /** Valid agent names for @mention validation */
  validAgents: string[];
  /** Server name (default: 'workflow-context') */
  name?: string;
  /** Server version (default: '1.0.0') */
  version?: string;
  /** Callback when an agent is @mentioned in channel_send */
  onMention?: (from: string, target: string, msg: Message) => void;
  /** Proposal manager for voting tools (optional) */
  proposalManager?: ProposalManager;
  /** Enable feedback tool (optional) */
  feedback?: boolean;
  /** Skills provider for shared skills (optional) */
  skills?: SkillsProvider;
  /** Debug log function for tool calls (optional) */
  debugLog?: (message: string) => void;
}

// ── Factory ──────────────────────────────────────────────────────

export function createContextMCPServer(options: ContextMCPServerOptions) {
  const {
    provider,
    validAgents,
    name = "workflow-context",
    version = "1.0.0",
    onMention,
    proposalManager,
    feedback: feedbackEnabled,
    skills,
    debugLog,
  } = options;

  const server = new McpServer({ name, version });

  // Build shared context for all tool categories
  const ctx: MCPToolContext = {
    provider,
    validAgents,
    getAgentId,
    logTool: createLogTool(provider),
  };

  // Track connected agents (placeholder for future MCP notification support)
  const agentConnections = new Map<string, unknown>();

  // Register tool categories
  registerChannelTools(server, ctx, { onMention });
  registerResourceTools(server, ctx);
  registerInboxTools(server, ctx, { debugLog });
  registerTeamTools(server, ctx);

  if (proposalManager) {
    registerProposalTools(server, ctx, proposalManager);
  }

  let getFeedback: () => FeedbackEntry[] = () => [];
  if (feedbackEnabled) {
    const fb = registerFeedbackTool(server, ctx);
    getFeedback = fb.getFeedback;
  }

  if (skills) {
    registerSkillsTools(server, skills);
  }

  return {
    server,
    agentConnections,
    validAgents,
    proposalManager,
    getFeedback,
  };
}

export type ContextMCPServer = ReturnType<typeof createContextMCPServer>;
