import { describe, test, expect, beforeEach, afterEach, mock, spyOn } from 'bun:test'
import { existsSync, mkdirSync, writeFileSync, rmSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

// ==================== Server Module Tests ====================

import {
  registerSession,
  unregisterSession,
  getSessionInfo,
  listSessions,
  setDefaultSession,
  type SessionInfo,
} from '../src/cli/server.ts'

describe('Server Session Management', () => {
  // Note: These tests use the actual registry file in ~/.agent-worker
  // In a real test environment, you'd want to mock the filesystem

  const testSessionId = `test-session-${Date.now()}`
  const testSessionInfo: SessionInfo = {
    id: testSessionId,
    name: `test-agent-${Date.now()}`,
    socketPath: `/tmp/test-${testSessionId}.sock`,
    pid: process.pid,
    backend: 'sdk',
    model: 'test-model',
    pidFile: `/tmp/test-${testSessionId}.pid`,
  }

  afterEach(() => {
    // Cleanup: unregister test sessions
    try {
      unregisterSession(testSessionId)
    } catch {
      // Ignore cleanup errors
    }
  })

  test('registerSession adds session to registry', () => {
    registerSession(testSessionInfo)
    const info = getSessionInfo(testSessionId)
    expect(info).not.toBeNull()
    expect(info?.id).toBe(testSessionId)
    expect(info?.backend).toBe('sdk')
  })

  test('getSessionInfo returns session by id', () => {
    registerSession(testSessionInfo)
    const info = getSessionInfo(testSessionId)
    expect(info?.id).toBe(testSessionId)
    expect(info?.name).toBe(testSessionInfo.name)
  })

  test('getSessionInfo returns session by name', () => {
    registerSession(testSessionInfo)
    const info = getSessionInfo(testSessionInfo.name)
    expect(info?.id).toBe(testSessionId)
  })

  test('getSessionInfo returns null for unknown session', () => {
    const info = getSessionInfo('nonexistent-session-id')
    expect(info).toBeNull()
  })

  test('listSessions returns registered sessions', () => {
    registerSession(testSessionInfo)
    const sessions = listSessions()
    const found = sessions.find(s => s.id === testSessionId)
    expect(found).toBeDefined()
  })

  test('listSessions deduplicates sessions', () => {
    registerSession(testSessionInfo)
    const sessions = listSessions()
    // Should not have duplicates even though we register by both id and name
    const testSessions = sessions.filter(s => s.id === testSessionId)
    expect(testSessions.length).toBe(1)
  })

  test('unregisterSession removes session from registry', () => {
    registerSession(testSessionInfo)
    unregisterSession(testSessionId)
    const info = getSessionInfo(testSessionId)
    expect(info).toBeNull()
  })

  test('unregisterSession removes by name too', () => {
    registerSession(testSessionInfo)
    unregisterSession(testSessionInfo.name!)
    const info = getSessionInfo(testSessionId)
    expect(info).toBeNull()
  })

  test('setDefaultSession sets the default', () => {
    registerSession(testSessionInfo)
    const result = setDefaultSession(testSessionId)
    expect(result).toBe(true)
  })

  test('setDefaultSession returns false for unknown session', () => {
    const result = setDefaultSession('nonexistent-session')
    expect(result).toBe(false)
  })
})

// ==================== Client Module Tests ====================

import { sendRequest, isSessionActive } from '../src/cli/client.ts'

describe('Client Module', () => {
  test('sendRequest returns error for nonexistent session', async () => {
    const res = await sendRequest(
      { action: 'status' },
      'nonexistent-session-12345'
    )
    expect(res.success).toBe(false)
    expect(res.error).toContain('Session not found')
  })

  test('sendRequest returns error when no active session', async () => {
    // Without specifying a target, it should look for default session
    // If no default exists, it should return an error
    const res = await sendRequest({ action: 'status' })
    // This will either find a session or return "No active session"
    if (!res.success) {
      expect(res.error).toBeDefined()
    }
  })

  test('isSessionActive returns false for nonexistent session', () => {
    const active = isSessionActive('definitely-not-a-real-session-xyz')
    expect(active).toBe(false)
  })
})

// ==================== Workflow CLI Command Logic Tests ====================

// These tests verify the logic that CLI commands use, without spawning actual processes

import { buildAgentId, parseAgentId } from '../src/cli/instance.ts'
import { parseWorkflowFile, runWorkflow } from '../src/workflow/index.ts'
import type { ParsedWorkflow, ResolvedAgent } from '../src/workflow/types.ts'

describe('Workflow CLI Command Logic', () => {
  const testDir = join(tmpdir(), `workflow-cli-test-${Date.now()}`)

  beforeEach(() => {
    mkdirSync(testDir, { recursive: true })
  })

  afterEach(() => {
    rmSync(testDir, { recursive: true, force: true })
  })

  describe('workflow run command logic', () => {
    test('parses workflow file correctly', async () => {
      const workflowPath = join(testDir, 'test.yaml')
      writeFileSync(workflowPath, `
name: test-workflow
agents:
  helper:
    model: test-model
    system_prompt: You are helpful
tasks:
  - shell: echo "hello"
    as: greeting
`)
      const workflow = await parseWorkflowFile(workflowPath)
      expect(workflow.name).toBe('test-workflow')
      expect(workflow.agents.helper).toBeDefined()
      expect(workflow.tasks.length).toBe(1)
    })

    test('builds agent IDs with instance', () => {
      const agentId = buildAgentId('reviewer', 'pr-123')
      expect(agentId).toBe('reviewer@pr-123')

      const parsed = parseAgentId(agentId)
      expect(parsed.agent).toBe('reviewer')
      expect(parsed.instance).toBe('pr-123')
    })

    test('runs shell-only workflow without agents', async () => {
      const workflowPath = join(testDir, 'shell-only.yaml')
      writeFileSync(workflowPath, `
name: shell-workflow
agents: {}
tasks:
  - shell: echo "test output"
    as: result
`)
      const workflow = await parseWorkflowFile(workflowPath)

      const result = await runWorkflow({
        workflow,
        instance: 'test',
        startAgent: async () => {},
        sendToAgent: async () => '',
      })

      expect(result.success).toBe(true)
      expect(result.results.result).toBe('test output')
    })

    test('handles workflow with verbose logging', async () => {
      const workflowPath = join(testDir, 'verbose.yaml')
      writeFileSync(workflowPath, `
name: verbose-workflow
agents: {}
tasks:
  - shell: echo "step1"
    as: s1
  - shell: echo "step2"
    as: s2
`)
      const workflow = await parseWorkflowFile(workflowPath)

      const logs: string[] = []
      const result = await runWorkflow({
        workflow,
        instance: 'test',
        verbose: true,
        startAgent: async () => {},
        sendToAgent: async () => '',
        log: (msg) => logs.push(msg),
      })

      expect(result.success).toBe(true)
      expect(logs.length).toBeGreaterThan(0)
      expect(logs.some(l => l.includes('Task'))).toBe(true)
    })
  })

  describe('workflow up command logic', () => {
    test('starts agents from workflow definition', async () => {
      const workflowPath = join(testDir, 'agents.yaml')
      writeFileSync(workflowPath, `
name: multi-agent
agents:
  reviewer:
    model: test-model
    system_prompt: You review code
  coder:
    model: test-model
    system_prompt: You write code
tasks: []
`)
      const workflow = await parseWorkflowFile(workflowPath)

      const startedAgents: string[] = []
      const result = await runWorkflow({
        workflow,
        instance: 'test',
        startAgent: async (name) => {
          startedAgents.push(name)
        },
        sendToAgent: async () => '',
      })

      expect(result.success).toBe(true)
      expect(startedAgents).toContain('reviewer')
      expect(startedAgents).toContain('coder')
    })

    test('supports lazy agent startup', async () => {
      const workflowPath = join(testDir, 'lazy.yaml')
      writeFileSync(workflowPath, `
name: lazy-workflow
agents:
  worker:
    model: test
    system_prompt: test
tasks:
  - send: "do something"
    to: worker
    as: result
`)
      const workflow = await parseWorkflowFile(workflowPath)

      const startedAgents: string[] = []
      const result = await runWorkflow({
        workflow,
        instance: 'test',
        lazy: true,
        startAgent: async (name) => {
          startedAgents.push(name)
        },
        sendToAgent: async () => 'done',
      })

      expect(result.success).toBe(true)
      // In lazy mode, agents are started only when needed
      expect(startedAgents).toContain('worker')
    })
  })

  describe('workflow ps command logic', () => {
    test('listSessions returns array', () => {
      const sessions = listSessions()
      expect(Array.isArray(sessions)).toBe(true)
    })

    test('session info contains required fields', () => {
      // Create a temporary session for testing
      const testId = `ps-test-${Date.now()}`
      const info: SessionInfo = {
        id: testId,
        socketPath: `/tmp/${testId}.sock`,
        pid: process.pid,
        backend: 'sdk',
        model: 'test',
        pidFile: `/tmp/${testId}.pid`,
      }

      registerSession(info)

      try {
        const sessions = listSessions()
        const found = sessions.find(s => s.id === testId)
        expect(found).toBeDefined()
        expect(found?.id).toBe(testId)
        expect(found?.backend).toBe('sdk')
        expect(found?.pid).toBe(process.pid)
      } finally {
        unregisterSession(testId)
      }
    })
  })

  describe('down command logic', () => {
    test('can check if session is running', () => {
      // For a non-existent session, should return false
      const running = isSessionActive('nonexistent-session-xyz')
      expect(running).toBe(false)
    })

    test('sendRequest handles shutdown action format', async () => {
      // Verify the shutdown request format is correct
      const req = { action: 'shutdown' }
      expect(req.action).toBe('shutdown')

      // Sending to nonexistent session should return error
      const res = await sendRequest(req, 'nonexistent')
      expect(res.success).toBe(false)
    })
  })

  describe('ls command logic', () => {
    test('lists all registered sessions', () => {
      const id1 = `ls-test-1-${Date.now()}`
      const id2 = `ls-test-2-${Date.now()}`

      registerSession({
        id: id1,
        socketPath: `/tmp/${id1}.sock`,
        pid: process.pid,
        backend: 'sdk',
        model: 'test',
        pidFile: `/tmp/${id1}.pid`,
      })

      registerSession({
        id: id2,
        socketPath: `/tmp/${id2}.sock`,
        pid: process.pid,
        backend: 'claude',
        model: 'test',
        pidFile: `/tmp/${id2}.pid`,
      })

      try {
        const sessions = listSessions()
        const found1 = sessions.find(s => s.id === id1)
        const found2 = sessions.find(s => s.id === id2)

        expect(found1).toBeDefined()
        expect(found2).toBeDefined()
        expect(found1?.backend).toBe('sdk')
        expect(found2?.backend).toBe('claude')
      } finally {
        unregisterSession(id1)
        unregisterSession(id2)
      }
    })
  })
})

// ==================== Workflow JSON Output Tests ====================

describe('Workflow Command Output Formats', () => {
  const testDir = join(tmpdir(), `workflow-output-test-${Date.now()}`)

  beforeEach(() => {
    mkdirSync(testDir, { recursive: true })
  })

  afterEach(() => {
    rmSync(testDir, { recursive: true, force: true })
  })

  test('runWorkflow result has correct structure for JSON output', async () => {
    const workflowPath = join(testDir, 'json-test.yaml')
    writeFileSync(workflowPath, `
name: json-test
agents: {}
tasks:
  - shell: echo "output1"
    as: first
  - shell: echo "output2"
    as: second
`)
    const workflow = await parseWorkflowFile(workflowPath)

    const result = await runWorkflow({
      workflow,
      startAgent: async () => {},
      sendToAgent: async () => '',
    })

    // Verify JSON-serializable structure
    const json = JSON.stringify(result)
    const parsed = JSON.parse(json)

    expect(parsed).toHaveProperty('success')
    expect(parsed).toHaveProperty('output')
    expect(parsed).toHaveProperty('results')
    expect(parsed).toHaveProperty('duration')
    expect(typeof parsed.duration).toBe('number')
    expect(parsed.results.first).toBe('output1')
    expect(parsed.results.second).toBe('output2')
  })

  test('error result has error field', async () => {
    const workflowPath = join(testDir, 'error-test.yaml')
    writeFileSync(workflowPath, `
name: error-test
agents: {}
tasks:
  - shell: "exit 1"
`)
    const workflow = await parseWorkflowFile(workflowPath)

    const result = await runWorkflow({
      workflow,
      startAgent: async () => {},
      sendToAgent: async () => '',
    })

    expect(result.success).toBe(false)
    expect(result.error).toBeDefined()
  })
})

// ==================== Agent Instance Lifecycle Tests ====================

describe('Agent Instance Lifecycle', () => {
  test('buildAgentId handles workflow instance naming', () => {
    // Simulating workflow run --instance pr-123
    const reviewerId = buildAgentId('reviewer', 'pr-123')
    const coderId = buildAgentId('coder', 'pr-123')

    expect(reviewerId).toBe('reviewer@pr-123')
    expect(coderId).toBe('coder@pr-123')

    // All agents in same workflow instance share the instance suffix
    const parsed1 = parseAgentId(reviewerId)
    const parsed2 = parseAgentId(coderId)
    expect(parsed1.instance).toBe(parsed2.instance)
  })

  test('default instance is used when not specified', () => {
    const id = buildAgentId('worker', undefined)
    expect(id).toBe('worker@default')

    const parsed = parseAgentId(id)
    expect(parsed.instance).toBe('default')
  })
})
