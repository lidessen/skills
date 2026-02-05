# Backend Compatibility Matrix

This document compares feature support across different agent-worker backends.

## Overview

Agent-worker supports multiple backends with different capabilities:

- **SDK Backend** (default): Full-featured, uses Vercel AI SDK directly
- **CLI Backends**: Delegates to external CLI tools (claude, codex, cursor)

## Feature Support Matrix

| Feature | SDK | Claude CLI | Codex CLI | Cursor CLI | Notes |
|---------|-----|------------|-----------|------------|-------|
| **Core Messaging** |
| Send messages | ✅ | ✅ | ✅ | ✅ | All backends support basic messaging |
| Conversation history | ✅ | ⚠️ | ⚠️ | ⚠️ | CLI backends: simplified history |
| Session persistence | ✅ | ✅ | ✅ | ✅ | |
| **Skills** |
| Skills via tool | ✅ | ❌ | ❌ | ❌ | SDK only |
| Skills via filesystem | ❌ | ✅ | ✅ | ✅ | CLI backends load from disk |
| `--import-skill` | ✅ | ❌ | ❌ | ❌ | Requires SDK backend |
| `--skill` | ✅ | ⚠️ | ⚠️ | ⚠️ | SDK loads, CLI shows warning |
| `--skill-dir` | ✅ | ⚠️ | ⚠️ | ⚠️ | SDK loads, CLI shows warning |
| **Tool Management** |
| Dynamic tool addition | ✅ | ❌ | ❌ | ❌ | `tool_add` SDK only |
| Tool mocking | ✅ | ❌ | ❌ | ❌ | `tool_mock` SDK only |
| Tool import | ✅ | ❌ | ❌ | ❌ | `tool_import` SDK only |
| List tools | ✅ | ⚠️ | ⚠️ | ⚠️ | CLI returns empty array |
| **Approval System** |
| Pending approvals | ✅ | ❌ | ❌ | ❌ | SDK only |
| Approve/deny | ✅ | ❌ | ❌ | ❌ | SDK only |
| Auto-approve mode | ✅ | N/A | N/A | N/A | |
| **Statistics** |
| Token usage | ✅ | ⚠️ | ⚠️ | ⚠️ | CLI: limited stats |
| Latency tracking | ✅ | ❌ | ❌ | ❌ | |
| **Other** |
| Export transcript | ✅ | ✅ | ✅ | ✅ | All backends |
| Clear history | ✅ | ✅ | ✅ | ✅ | All backends |

**Legend:**
- ✅ Full support
- ⚠️ Partial support or different implementation
- ❌ Not supported
- N/A Not applicable

## Skills Support Details

### SDK Backend (Default)

Skills work through the **Skills tool** that agents can call programmatically:

```typescript
// Agent can:
// - Call Skills({operation: 'list'}) to see available skills
// - Call Skills({operation: 'view', skillName: 'dive'}) to load a skill
// - Call Skills({operation: 'readFile', skillName: 'dive', filePath: 'reference.md'})
```

**Features:**
- ✅ Dynamic skill loading
- ✅ Skill file reading (references, examples, etc.)
- ✅ `--import-skill` for temporary Git imports
- ✅ Skills discoverable by agent during conversation

**Skill Locations:**
- Project: `.agents/skills/`, `.claude/skills/`, `.cursor/skills/`
- Global: `~/.agents/skills/`, `~/.claude/skills/`

### Claude CLI Backend

Skills are loaded by Claude Code CLI from **filesystem locations**:

**Skill Locations:**
- Project: `.claude/skills/`
- Global: `~/.claude/skills/`

**Behavior:**
- ✅ Claude CLI auto-discovers skills at startup
- ✅ Slash commands work: `/skill-name`
- ❌ No Skills tool (not needed, CLI handles it)
- ❌ `--import-skill` not supported (use `npx skills add --global`)

**If you specify** `--skill` or `--import-skill`:
```bash
agent-worker session new --backend claude --import-skill repo:skill
```

You'll see:
```
⚠️  --import-skill is only supported with SDK backend.
   Claude CLI loads skills from filesystem locations.
   To use imported skills, install them manually:
     npx skills add <repo> --global  # Install to ~/.claude/skills
   Or use SDK backend: --backend sdk

ℹ️  Claude CLI will load skills from: ~/.claude/skills/
```

### Codex CLI Backend

Skills are loaded by Codex CLI from **filesystem locations**:

**Skill Locations:**
- Project: `.agents/skills/`
- Global: `~/.codex/skills/`, `~/.agents/skills/`

**Behavior:**
- ✅ Codex CLI auto-discovers skills at startup
- ✅ Dollar commands work: `$skill-name`
- ❌ No Skills tool
- ❌ `--import-skill` not supported

### Cursor CLI Backend

Skills are loaded by Cursor CLI from **filesystem locations**:

**Skill Locations:**
- Project: `.agents/skills/`, `.cursor/skills/`
- Global: `~/.agents/skills/`

**Behavior:**
- ✅ Cursor CLI auto-discovers skills at startup (added Jan 16, 2026)
- ✅ Slash commands work
- ❌ No Skills tool
- ❌ `--import-skill` not supported

## Tool Management

### SDK Backend

Full dynamic tool management through AgentSession:

```typescript
// Add tool at runtime
session.addTool({
  name: 'custom_tool',
  description: 'My custom tool',
  parameters: { /* ... */ },
  execute: async (args) => { /* ... */ }
})

// Mock tool for testing
session.setMockResponse('tool_name', { result: 'mocked' })

// Import tools from file
await session.importTools('./my-tools.ts')
```

### CLI Backends

**Not supported.** CLI tools have their own fixed set of tools.

Attempting to use tool management will result in:
```
Error: Tool management not supported for CLI backends
```

## Approval System

### SDK Backend

Full approval system for tool calls:

```typescript
// Agent makes tool calls
const response = await session.send('Fix the bug')

// Check for pending approvals
if (response.pendingApprovals.length > 0) {
  // User can approve or deny
  await session.approve(response.pendingApprovals[0].id)
}

// Or use auto-approve mode
await session.send('Fix the bug', { autoApprove: true })
```

### CLI Backends

**Not supported.** CLI tools handle tool execution internally.

Attempting to approve/deny will result in:
```
Error: Approvals not supported for CLI backends
```

## Choosing a Backend

### Use SDK Backend (default) when:
- ✅ You need dynamic tool management
- ✅ You want to use `--import-skill`
- ✅ You need approval workflow
- ✅ You want programmatic skill access
- ✅ You need detailed token usage stats

### Use Claude CLI Backend when:
- ✅ You already use Claude Code
- ✅ Skills installed in `~/.claude/skills/`
- ✅ You prefer Claude's native experience
- ✅ You want MCP server support

### Use Codex CLI Backend when:
- ✅ You already use OpenAI Codex CLI
- ✅ Skills installed in `~/.codex/skills/`
- ✅ You prefer OpenAI's tooling

### Use Cursor CLI Backend when:
- ✅ You already use Cursor
- ✅ Skills installed in `~/.cursor/skills/`
- ✅ You want Cursor's agent modes (Plan, Ask)

## Migration Tips

### From CLI Backend to SDK

If you need features only available in SDK:

```bash
# Before (CLI backend)
agent-worker session new --backend claude

# After (SDK backend with same skills)
# 1. Copy skills to SDK-visible location
cp -r ~/.claude/skills/* ~/.agents/skills/

# 2. Use SDK backend
agent-worker session new --backend sdk
```

### Installing Skills for CLI Backends

```bash
# For Claude CLI
npx skills add vercel-labs/agent-skills --global

# For Codex CLI
npx skills add vercel-labs/agent-skills --global

# For Cursor CLI
npx skills add vercel-labs/agent-skills --global
```

Skills will be installed to the appropriate global directory for each CLI.

## API Compatibility

When building applications on agent-worker, check backend compatibility:

```typescript
import { BackendType } from 'agent-worker'

function supportsToolManagement(backend: BackendType): boolean {
  return backend === 'sdk'
}

function supportsImportSkills(backend: BackendType): boolean {
  return backend === 'sdk'
}

function supportsApprovals(backend: BackendType): boolean {
  return backend === 'sdk'
}
```

Or use the compatibility utilities:

```typescript
import { getSkillsCompatibility } from 'agent-worker/cli/skills-compatibility'

const compat = getSkillsCompatibility('claude')
if (compat.method === 'filesystem') {
  console.log('This backend loads skills from:', compat.locations)
}
```

## References

- [Agent Skills Specification](https://agentskills.io)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Codex CLI Skills](https://developers.openai.com/codex/skills/)
- [Cursor CLI Update](https://cursor.com/changelog/cli-jan-16-2026)
