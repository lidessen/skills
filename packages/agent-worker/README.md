# agent-worker

SDK and CLI for creating and testing agent workers with multiple AI backends.

## Installation

```bash
npm install agent-worker
# or
bun add agent-worker
```

## Quick Start

### CLI

```bash
# Create a session
agent-worker session new -m anthropic/claude-sonnet-4-5

# Send a message
agent-worker send "What is 2+2?"

# End session
agent-worker session end
```

### SDK

```typescript
import { AgentSession } from 'agent-worker'

const session = new AgentSession({
  model: 'anthropic/claude-sonnet-4-5',
  system: 'You are a helpful assistant.',
})

const response = await session.send('Hello')
console.log(response.content)
```

## Features

- **Multiple backends**: SDK (Anthropic, OpenAI, etc.), Claude CLI, Codex, Cursor
- **Persistent sessions**: State maintained across commands
- **Tool injection**: Add, import, and mock tools
- **Approval workflow**: Human-in-the-loop for sensitive operations

## Backends

| Backend | Command | Best For |
|---------|---------|----------|
| SDK | `-m provider/model` | Full control, tool injection |
| Claude CLI | `-b claude` | Existing Claude installation |
| Codex | `-b codex` | OpenAI Codex workflows |
| Cursor | `-b cursor` | Cursor Agent integration |

## CLI Commands

```
session new       Create session
session list      List sessions
session end       End session
send              Send message
tool add          Add tool (SDK only)
tool mock         Mock tool response
history           Show conversation
```

## Requirements

- Node.js 18+ or Bun
- API key for chosen provider (e.g., `ANTHROPIC_API_KEY`)

## License

MIT
