/**
 * Health tracking for daemon agent sessions.
 *
 * Tracks success/failure patterns to determine agent health status.
 * The daemon uses this to make adaptive decisions: pause scheduling
 * when unavailable, backoff on failures, report status to clients.
 */

import { classifyError, type ClassifiedError, type ErrorClass } from "./errors.ts";

export type HealthStatus = "healthy" | "degraded" | "unavailable";

export interface HealthState {
  status: HealthStatus;
  consecutiveFailures: number;
  lastError?: { class: ErrorClass; message: string; at: string };
  lastSuccess?: string;
  totalFailures: number;
  totalSuccesses: number;
}

export interface HealthTrackerConfig {
  /** Consecutive transient failures before marking unavailable (default: 5) */
  degradedThreshold?: number;
}

export class HealthTracker {
  private _status: HealthStatus = "healthy";
  private consecutiveFailures = 0;
  private lastError?: { class: ErrorClass; message: string; at: string };
  private lastSuccess?: string;
  private totalFailures = 0;
  private totalSuccesses = 0;
  private degradedThreshold: number;

  constructor(config: HealthTrackerConfig = {}) {
    this.degradedThreshold = config.degradedThreshold ?? 5;
  }

  get status(): HealthStatus {
    return this._status;
  }

  /** Record a successful operation — resets failure count */
  recordSuccess(): void {
    this.totalSuccesses++;
    this.consecutiveFailures = 0;
    this.lastSuccess = new Date().toISOString();

    if (this._status !== "healthy") {
      const prev = this._status;
      this._status = "healthy";
      console.log(`[health] ${prev} → healthy (success after ${this.totalFailures} total failures)`);
    }
  }

  /** Record a failed operation — classify and update state */
  recordFailure(error: unknown): ClassifiedError {
    const classified = classifyError(error);
    this.totalFailures++;
    this.consecutiveFailures++;
    this.lastError = {
      class: classified.class,
      message: classified.message,
      at: new Date().toISOString(),
    };

    const prev = this._status;

    // Auth/resource errors → immediately unavailable
    if (classified.class === "auth" || classified.class === "resource") {
      this._status = "unavailable";
    }
    // Transient errors → degraded, then unavailable after threshold
    else if (this.consecutiveFailures >= this.degradedThreshold) {
      this._status = "unavailable";
    } else if (this.consecutiveFailures >= 1) {
      this._status = "degraded";
    }

    if (this._status !== prev) {
      console.log(
        `[health] ${prev} → ${this._status} (${classified.class}: ${classified.message})`,
      );
    }

    return classified;
  }

  /** Get current health state snapshot */
  getState(): HealthState {
    return {
      status: this._status,
      consecutiveFailures: this.consecutiveFailures,
      lastError: this.lastError ? { ...this.lastError } : undefined,
      lastSuccess: this.lastSuccess,
      totalFailures: this.totalFailures,
      totalSuccesses: this.totalSuccesses,
    };
  }
}
