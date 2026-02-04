---
type: design
created: 2026-02-04
status: draft
tags: [agent-testing, vercel-ai-sdk, cli, sdk]
---

# Agent Prompt Testing Tool

## Problem

Current sub-agent testing through Claude Code's Task tool has limitations:

| Issue | Impact |
|-------|--------|
| Context not controllable | Can't isolate system prompt effects |
| Tool calls invisible | Can't verify tool-related behaviors |
| Model not selectable | Can't compare across models |
| No mock capabilities | Can't test tool-dependent instructions |
| Linear execution | Can't improvise based on observed behavior |

## Design Goals

1. **上下文可控** - Explicit control over system prompt, messages, tools
2. **过程完全透明** - See all tool calls, thinking, token usage
3. **区分模型** - Test same prompt across different models
4. **Mock 工具** - Define tools with controlled responses
5. **即兴交互** - Observe response, decide next action (like agent-browser)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    agent-prompt CLI                          │
│  session new | send | tool | history | stats                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AgentSession (SDK)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Conversation│  │ Tool        │  │ Model       │         │
│  │ State       │  │ Registry    │  │ Adapter     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Vercel AI SDK                             │
│  generateText() | streamText() | tool execution             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Model Providers                                │
│  Anthropic | OpenAI | Google | Groq | ...                   │
└─────────────────────────────────────────────────────────────┘
```

## CLI Interface

Inspired by agent-browser's command pattern: `agent-browser <command> [args]`

### Session Management

```bash
# Create new session with model and system prompt
agent-prompt session new --model anthropic:claude-3-5-sonnet --system "Your prompt here"
agent-prompt session new --model openai:gpt-4o --system-file ./prompt.md

# List and switch sessions (stateful like agent-browser)
agent-prompt session list
agent-prompt session use <session-id>
agent-prompt session close [session-id]
```

### Message Exchange

```bash
# Send message, see response
agent-prompt send "Analyze this code for security issues"

# Full JSON output (tool calls, tokens, timing)
agent-prompt send "Analyze this code" --json

# Output format
# {
#   "content": "Let me analyze...",
#   "toolCalls": [{"name": "read_file", "args": {...}, "result": {...}}],
#   "tokens": {"input": 150, "output": 280},
#   "latency": 1234
# }
```

### Tool Definition & Mocking

```bash
# Define a tool
agent-prompt tool add read_file --desc "Read file contents" \
  --param "path:string:File path to read"

# Set mock response (crucial for controlled testing)
agent-prompt tool mock read_file '{"content": "function transfer(to, amount) {\n  balance -= amount;\n  send(to, amount);\n}"}'

# List tools
agent-prompt tool list
```

### Observation

```bash
# Full conversation history
agent-prompt history
agent-prompt history --json

# Stats (tokens, timing, tool usage)
agent-prompt stats

# Export transcript for analysis
agent-prompt export > transcript.json
```

## SDK Interface

```typescript
import { AgentSession } from 'agent-prompt';

// Programmatic session for improvisational testing
const session = new AgentSession({
  model: 'anthropic:claude-3-5-sonnet',
  system: `You care deeply about code quality...`,
  tools: [
    {
      name: 'read_file',
      description: 'Read file contents',
      parameters: {
        type: 'object',
        properties: { path: { type: 'string' } },
        required: ['path']
      },
      // Mock function - can be dynamic
      execute: async (args) => ({
        content: 'function transfer...'
      })
    }
  ]
});

// Send and observe
const response = await session.send('Review this code.');

// Full transparency
console.log(response.content);      // Final text
console.log(response.toolCalls);    // All tool invocations
console.log(response.steps);        // Full agentic loop
console.log(response.usage);        // Token counts

// Improvisational: decide next based on observation
if (response.content.includes('race condition')) {
  const followup = await session.send('Explain how to fix it.');
}

// Export for analysis
const transcript = session.export();  // Full conversation
```

## Key Design Decisions

### 1. Stateful Sessions (like agent-browser)

Agent-browser maintains browser state across CLI calls. Similarly, agent-prompt maintains conversation state:

```bash
# Session persists across commands
agent-prompt session new --model claude-3-5-sonnet --system "..."
agent-prompt send "First message"      # Turn 1
agent-prompt send "Follow up"          # Turn 2, sees turn 1
agent-prompt history                   # See full conversation
```

This enables improvisational testing - observe response, decide next action.

### 2. Mock Tools with Controlled Responses

Unlike sub-agent testing where tool results are invisible, we control exactly what the tool "returns":

```bash
agent-prompt tool mock read_file '{"content": "VULNERABLE CODE HERE"}'
agent-prompt send "Analyze the code"
# Now we know exactly what context the agent received
```

### 3. Transparent Tool Execution

Every tool call is visible:

```json
{
  "content": "I found a race condition...",
  "toolCalls": [
    {
      "name": "read_file",
      "arguments": {"path": "transfer.ts"},
      "result": {"content": "function transfer..."},
      "timing": 0
    }
  ]
}
```

### 4. Model-Agnostic via Vercel AI SDK

Same test, different models:

```bash
agent-prompt session new --model anthropic:claude-3-5-sonnet --system "..."
agent-prompt send "Test message"

agent-prompt session new --model openai:gpt-4o --system "..."
agent-prompt send "Test message"

# Compare results
```

## Implementation Plan

### Phase 1: Core SDK

```
packages/agent-prompt/
├── src/
│   ├── session.ts       # AgentSession class
│   ├── tools.ts         # Tool registry and mocking
│   ├── models.ts        # Model adapters (via Vercel AI SDK)
│   └── index.ts         # Public API
├── package.json
└── tsconfig.json
```

### Phase 2: CLI

```
packages/agent-prompt-cli/
├── src/
│   ├── commands/
│   │   ├── session.ts   # session new/list/use/close
│   │   ├── send.ts      # send message
│   │   ├── tool.ts      # tool add/mock/list
│   │   └── history.ts   # conversation history
│   └── index.ts         # CLI entry
├── package.json
└── bin/agent-prompt
```

## Usage Examples

### Example 1: Quick Compliance Test

```bash
# Does this instruction work?
agent-prompt session new --model claude-3-5-sonnet \
  --system "Always cite code with file:line format."

agent-prompt send "How does authentication work in this project?"
# Observe: Did it use file:line?
```

### Example 2: Decay Test (Improvisational)

```bash
agent-prompt session new --model claude-3-5-sonnet \
  --system "Always cite code with file:line format."

agent-prompt send "Analyze the auth system."  # Check compliance
agent-prompt send "Analyze the auth system."  # Turn 2
agent-prompt send "Now summarize the key points."  # Different task type

agent-prompt history --json | jq '.messages[].content'
# Analyze when citation format decayed
```

## Integration with prompt-lab Skill

This tool becomes the "execution engine" for prompt-lab experiments:

```
┌──────────────────────────────────────────────────┐
│              prompt-lab SKILL.md                  │
│  Methodology: Hypothesize → Design → Execute     │
└──────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────┐
│              agent-prompt Tool                    │
│  CLI + SDK for controlled agent testing          │
└──────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────┐
│        .memory/prompt-lab/experiments/           │
│  Transcripts + analysis results                  │
└──────────────────────────────────────────────────┘
```

## Open Questions

1. **Session persistence**: File-based? In-memory daemon? SQLite?
2. **Streaming**: Support for streaming responses during interactive use?
3. **Cost tracking**: Track API costs across sessions?
4. **Multi-agent**: Test agent-to-agent interactions?

---

*Design inspired by [agent-browser](https://github.com/vercel-labs/agent-browser) CLI patterns*
