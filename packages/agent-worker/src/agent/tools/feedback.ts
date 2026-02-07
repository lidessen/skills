/**
 * Feedback tool — lets agents report observations about tools and workflows
 *
 * When enabled, agents can call this tool to leave structured feedback:
 * friction points, bugs, suggestions, or praise. Feedback is collected
 * in memory and optionally forwarded via a callback.
 *
 * @example
 * ```typescript
 * const { tool, getFeedback } = createFeedbackTool();
 *
 * const session = new AgentSession({
 *   model: 'anthropic/claude-sonnet-4-5',
 *   system: FEEDBACK_PROMPT + '\nYou are a coding assistant.',
 *   tools: { feedback: tool, bash: bashTool },
 * });
 *
 * await session.send('...');
 * console.log(getFeedback()); // review what the agent reported
 * ```
 */

import { tool, jsonSchema } from "ai";

// ── Types ──────────────────────────────────────────────────────────

export interface FeedbackEntry {
  /** ISO timestamp */
  timestamp: string;
  /** What is being commented on — tool name, skill name, "workflow", etc. */
  target: string;
  /** Category */
  type: "bug" | "suggestion" | "friction" | "praise";
  /** What the agent observed or suggests */
  description: string;
  /** Optional: what the agent was doing when it noticed */
  context?: string;
}

export interface FeedbackToolOptions {
  /** Called each time the agent submits feedback */
  onFeedback?: (entry: FeedbackEntry) => void;
  /** Maximum entries to keep (default: 50) */
  maxEntries?: number;
}

export interface FeedbackToolResult {
  /** AI SDK tool() object — pass to AgentSession as a tool */
  tool: unknown;
  /** Retrieve all collected feedback entries */
  getFeedback(): FeedbackEntry[];
  /** Clear collected feedback */
  clearFeedback(): void;
}

// ── System prompt snippet ──────────────────────────────────────────

/**
 * Append this to the system prompt when the feedback tool is enabled.
 * Tells the agent the tool exists and when to use it.
 */
export const FEEDBACK_PROMPT = `
## Feedback

You have a \`feedback\` tool. Use it when you notice something about the tools or workflow worth reporting — a friction point, a bug, a missing capability, or something that works well.

Guidelines:
- Only call it when you genuinely have something to say. No obligation to give feedback.
- Be specific: name the tool/workflow, describe what happened, suggest what could be better.
- One entry per observation. Multiple calls are fine.
`.trim();

// ── Factory ────────────────────────────────────────────────────────

export function createFeedbackTool(
  options: FeedbackToolOptions = {},
): FeedbackToolResult {
  const { onFeedback, maxEntries = 50 } = options;
  const entries: FeedbackEntry[] = [];

  const feedbackTool = tool({
    description:
      "Submit feedback about a tool, skill, or workflow. Use when you notice friction, bugs, missing capabilities, or something that works particularly well.",
    parameters: jsonSchema({
      type: "object",
      properties: {
        target: {
          type: "string",
          description:
            "What you are giving feedback on — a tool name (e.g. bash, readFile), a skill name, or a general area (e.g. workflow, prompt).",
        },
        type: {
          type: "string",
          enum: ["bug", "suggestion", "friction", "praise"],
          description:
            "bug: something broken. suggestion: an improvement idea. friction: something awkward or slow. praise: something that works well.",
        },
        description: {
          type: "string",
          description: "What you observed or suggest. Be specific.",
        },
        context: {
          type: "string",
          description: "Optional: what you were doing when you noticed this.",
        },
      },
      required: ["target", "type", "description"],
    }),
    execute: async (args: Record<string, unknown>) => {
      const entry: FeedbackEntry = {
        timestamp: new Date().toISOString(),
        target: args.target as string,
        type: args.type as FeedbackEntry["type"],
        description: args.description as string,
        ...(args.context ? { context: args.context as string } : {}),
      };

      // Enforce cap
      if (entries.length >= maxEntries) {
        entries.shift();
      }
      entries.push(entry);

      onFeedback?.(entry);

      return { recorded: true };
    },
  });

  return {
    tool: feedbackTool,
    getFeedback: () => [...entries],
    clearFeedback: () => {
      entries.length = 0;
    },
  };
}
