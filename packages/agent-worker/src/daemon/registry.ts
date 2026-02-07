/**
 * Session Registry — Directory-per-session design.
 *
 * Each session is stored as its own file: sessions/{id}.json
 * Only the owning daemon process writes to its session file.
 * No shared mutable state → no locks needed.
 *
 * Default session ID is stored in a separate file: default
 */

import {
  existsSync,
  unlinkSync,
  writeFileSync,
  readFileSync,
  mkdirSync,
  readdirSync,
} from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import type { BackendType } from "../backends/types.ts";

export const CONFIG_DIR = join(homedir(), ".agent-worker");
export const SESSIONS_DIR = join(CONFIG_DIR, "sessions");
const DEFAULT_FILE = join(CONFIG_DIR, "default");

export interface SessionInfo {
  id: string;
  name?: string;
  model: string;
  system: string;
  backend: BackendType;
  socketPath: string;
  pidFile: string;
  readyFile: string;
  pid: number;
  createdAt: string;
  idleTimeout?: number; // ms, 0 = no timeout
}

export function ensureDirs(): void {
  mkdirSync(SESSIONS_DIR, { recursive: true });
}

/** Path to a session's metadata file */
function sessionFile(id: string): string {
  return join(SESSIONS_DIR, `${id}.json`);
}

/** Read all session metadata files from the sessions directory */
function readAllSessions(): SessionInfo[] {
  ensureDirs();
  const entries: SessionInfo[] = [];
  for (const file of readdirSync(SESSIONS_DIR)) {
    if (!file.endsWith(".json")) continue;
    try {
      entries.push(JSON.parse(readFileSync(join(SESSIONS_DIR, file), "utf-8")));
    } catch {
      // Ignore malformed files
    }
  }
  return entries;
}

function readDefault(): string | undefined {
  try {
    return readFileSync(DEFAULT_FILE, "utf-8").trim() || undefined;
  } catch {
    return undefined;
  }
}

export function registerSession(info: SessionInfo): void {
  ensureDirs();
  writeFileSync(sessionFile(info.id), JSON.stringify(info, null, 2));
  // Set as default if it's the first session
  if (!readDefault()) {
    writeFileSync(DEFAULT_FILE, info.id);
  }
}

export function unregisterSession(idOrName: string): void {
  const info = getSessionInfo(idOrName);
  if (!info) return;
  try {
    unlinkSync(sessionFile(info.id));
  } catch {
    // Already removed
  }
  // Update default if needed
  const currentDefault = readDefault();
  if (currentDefault === info.id) {
    const remaining = readAllSessions();
    if (remaining.length > 0) {
      writeFileSync(DEFAULT_FILE, remaining[0]!.id);
    } else {
      try {
        unlinkSync(DEFAULT_FILE);
      } catch {}
    }
  }
}

export function getSessionInfo(idOrName?: string): SessionInfo | null {
  if (!idOrName) {
    // Return default session
    const defaultId = readDefault();
    if (defaultId) {
      return getSessionInfo(defaultId);
    }
    // Return the only session if there's just one
    const sessions = readAllSessions();
    if (sessions.length === 1) {
      return sessions[0] ?? null;
    }
    return null;
  }

  // Try exact ID match (direct file lookup — O(1))
  const filePath = sessionFile(idOrName);
  if (existsSync(filePath)) {
    try {
      return JSON.parse(readFileSync(filePath, "utf-8"));
    } catch {
      return null;
    }
  }

  // Scan for name match or ID prefix match
  const sessions = readAllSessions();

  // Name match
  const byName = sessions.find((s) => s.name === idOrName);
  if (byName) return byName;

  // Prefix match on IDs (supports short IDs like "e8ab33e7")
  const prefixMatches = sessions.filter((s) => s.id.startsWith(idOrName));
  if (prefixMatches.length === 1) {
    return prefixMatches[0]!;
  }

  return null;
}

export function listSessions(): SessionInfo[] {
  return readAllSessions();
}

export function setDefaultSession(idOrName: string): boolean {
  const info = getSessionInfo(idOrName);
  if (!info) return false;
  ensureDirs();
  writeFileSync(DEFAULT_FILE, info.id);
  return true;
}

export function isSessionRunning(idOrName?: string): boolean {
  const info = getSessionInfo(idOrName);
  if (!info) return false;

  try {
    // Check if process exists
    process.kill(info.pid, 0);
    return true;
  } catch {
    // Process doesn't exist, clean up
    if (existsSync(info.socketPath)) {
      unlinkSync(info.socketPath);
    }
    if (existsSync(info.pidFile)) {
      unlinkSync(info.pidFile);
    }
    if (info.readyFile && existsSync(info.readyFile)) {
      unlinkSync(info.readyFile);
    }
    unregisterSession(info.id);
    return false;
  }
}

/**
 * Wait for a session to be ready (ready file exists)
 * Returns session info if ready, null if timeout
 */
export async function waitForReady(
  nameOrId: string | undefined,
  timeoutMs: number = 5000,
): Promise<SessionInfo | null> {
  const start = Date.now();
  const pollInterval = 50;

  while (Date.now() - start < timeoutMs) {
    const info = getSessionInfo(nameOrId);
    if (info?.readyFile && existsSync(info.readyFile)) {
      return info;
    }
    await new Promise((resolve) => setTimeout(resolve, pollInterval));
  }

  return null;
}
