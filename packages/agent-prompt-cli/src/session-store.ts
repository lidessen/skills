import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'
import { AgentSession, type SessionConfig, type Transcript } from 'agent-prompt'

const CONFIG_DIR = join(homedir(), '.agent-prompt')
const SESSIONS_FILE = join(CONFIG_DIR, 'sessions.json')

interface StoredSession {
  id: string
  model: string
  system: string
  tools: SessionConfig['tools']
  createdAt: string
}

interface SessionsData {
  current: string | null
  sessions: Record<string, StoredSession>
}

function ensureConfigDir(): void {
  if (!existsSync(CONFIG_DIR)) {
    mkdirSync(CONFIG_DIR, { recursive: true })
  }
}

function loadSessionsData(): SessionsData {
  ensureConfigDir()
  if (!existsSync(SESSIONS_FILE)) {
    return { current: null, sessions: {} }
  }
  return JSON.parse(readFileSync(SESSIONS_FILE, 'utf-8'))
}

function saveSessionsData(data: SessionsData): void {
  ensureConfigDir()
  writeFileSync(SESSIONS_FILE, JSON.stringify(data, null, 2))
}

// In-memory session instances
const activeSessions = new Map<string, AgentSession>()

export function createSession(config: SessionConfig): AgentSession {
  const session = new AgentSession(config)

  // Store session metadata
  const data = loadSessionsData()
  data.sessions[session.id] = {
    id: session.id,
    model: config.model,
    system: config.system,
    tools: config.tools,
    createdAt: session.createdAt,
  }
  data.current = session.id
  saveSessionsData(data)

  // Keep in memory
  activeSessions.set(session.id, session)

  return session
}

export function getCurrentSession(): AgentSession | null {
  const data = loadSessionsData()
  if (!data.current) return null

  // Check if already in memory
  if (activeSessions.has(data.current)) {
    return activeSessions.get(data.current)!
  }

  // Recreate from stored config
  const stored = data.sessions[data.current]
  if (!stored) return null

  const session = new AgentSession({
    model: stored.model,
    system: stored.system,
    tools: stored.tools,
  })

  // Note: This creates a new session ID, we need to restore the original
  // For now, this is a limitation - sessions don't persist across CLI invocations
  activeSessions.set(session.id, session)

  return session
}

export function listSessions(): StoredSession[] {
  const data = loadSessionsData()
  return Object.values(data.sessions)
}

export function useSession(id: string): boolean {
  const data = loadSessionsData()
  if (!data.sessions[id]) return false
  data.current = id
  saveSessionsData(data)
  return true
}

export function closeSession(id?: string): boolean {
  const data = loadSessionsData()
  const targetId = id ?? data.current
  if (!targetId || !data.sessions[targetId]) return false

  delete data.sessions[targetId]
  activeSessions.delete(targetId)

  if (data.current === targetId) {
    data.current = null
  }

  saveSessionsData(data)
  return true
}

export function getCurrentSessionId(): string | null {
  return loadSessionsData().current
}
