/**
 * Health Tracker Unit Tests
 *
 * Tests the HealthTracker state machine from daemon/health.ts.
 */

import { describe, test, expect } from "bun:test";
import { HealthTracker } from "../../src/daemon/health.ts";

describe("HealthTracker", () => {
  test("starts healthy", () => {
    const tracker = new HealthTracker();
    expect(tracker.status).toBe("healthy");
    const state = tracker.getState();
    expect(state.consecutiveFailures).toBe(0);
    expect(state.totalFailures).toBe(0);
    expect(state.totalSuccesses).toBe(0);
  });

  test("recordSuccess keeps healthy", () => {
    const tracker = new HealthTracker();
    tracker.recordSuccess();
    expect(tracker.status).toBe("healthy");
    expect(tracker.getState().totalSuccesses).toBe(1);
    expect(tracker.getState().lastSuccess).toBeDefined();
  });

  describe("transient failures → degraded → unavailable", () => {
    test("first transient failure → degraded", () => {
      const tracker = new HealthTracker();
      const classified = tracker.recordFailure(new Error("timeout"));
      expect(classified.class).toBe("transient");
      expect(tracker.status).toBe("degraded");
      expect(tracker.getState().consecutiveFailures).toBe(1);
    });

    test("multiple transient failures → unavailable at threshold", () => {
      const tracker = new HealthTracker({ degradedThreshold: 3 });
      tracker.recordFailure(new Error("timeout"));
      tracker.recordFailure(new Error("timeout"));
      expect(tracker.status).toBe("degraded");

      tracker.recordFailure(new Error("timeout"));
      expect(tracker.status).toBe("unavailable");
      expect(tracker.getState().consecutiveFailures).toBe(3);
    });

    test("default threshold is 5", () => {
      const tracker = new HealthTracker();
      for (let i = 0; i < 4; i++) {
        tracker.recordFailure(new Error("socket hang up"));
      }
      expect(tracker.status).toBe("degraded");

      tracker.recordFailure(new Error("socket hang up"));
      expect(tracker.status).toBe("unavailable");
    });
  });

  describe("auth/resource → immediately unavailable", () => {
    test("auth error → unavailable immediately", () => {
      const tracker = new HealthTracker();
      const classified = tracker.recordFailure(new Error("Invalid API key"));
      expect(classified.class).toBe("auth");
      expect(tracker.status).toBe("unavailable");
      expect(tracker.getState().consecutiveFailures).toBe(1);
    });

    test("resource error → unavailable immediately", () => {
      const tracker = new HealthTracker();
      const classified = tracker.recordFailure(new Error("Quota exceeded"));
      expect(classified.class).toBe("resource");
      expect(tracker.status).toBe("unavailable");
    });
  });

  describe("recovery", () => {
    test("success after degraded → healthy", () => {
      const tracker = new HealthTracker();
      tracker.recordFailure(new Error("timeout"));
      expect(tracker.status).toBe("degraded");

      tracker.recordSuccess();
      expect(tracker.status).toBe("healthy");
      expect(tracker.getState().consecutiveFailures).toBe(0);
    });

    test("success after unavailable → healthy", () => {
      const tracker = new HealthTracker();
      tracker.recordFailure(new Error("Invalid API key"));
      expect(tracker.status).toBe("unavailable");

      tracker.recordSuccess();
      expect(tracker.status).toBe("healthy");
      expect(tracker.getState().consecutiveFailures).toBe(0);
    });
  });

  describe("state snapshot", () => {
    test("lastError tracks most recent failure", () => {
      const tracker = new HealthTracker();
      tracker.recordFailure(new Error("timeout"));
      tracker.recordFailure(new Error("Quota exceeded"));

      const state = tracker.getState();
      expect(state.lastError?.class).toBe("resource");
      expect(state.lastError?.message).toBe("Quota exceeded");
      expect(state.lastError?.at).toBeDefined();
      expect(state.totalFailures).toBe(2);
    });

    test("counters accumulate correctly", () => {
      const tracker = new HealthTracker();
      tracker.recordSuccess();
      tracker.recordSuccess();
      tracker.recordFailure(new Error("timeout"));
      tracker.recordSuccess();
      tracker.recordFailure(new Error("timeout"));
      tracker.recordFailure(new Error("timeout"));

      const state = tracker.getState();
      expect(state.totalSuccesses).toBe(3);
      expect(state.totalFailures).toBe(3);
      expect(state.consecutiveFailures).toBe(2);
    });
  });
});
