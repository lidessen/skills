/**
 * Error Classification Unit Tests
 *
 * Tests classifyError() and withRetry() from daemon/errors.ts.
 */

import { describe, test, expect } from "bun:test";
import { classifyError, withRetry, type ClassifiedError } from "../../src/daemon/errors.ts";

describe("classifyError", () => {
  describe("HTTP status codes", () => {
    test("401 → auth", () => {
      const err = Object.assign(new Error("Unauthorized"), { status: 401 });
      const result = classifyError(err);
      expect(result.class).toBe("auth");
      expect(result.retryable).toBe(false);
      expect(result.status).toBe(401);
    });

    test("403 → auth", () => {
      const err = Object.assign(new Error("Forbidden"), { status: 403 });
      const result = classifyError(err);
      expect(result.class).toBe("auth");
      expect(result.retryable).toBe(false);
    });

    test("429 → transient", () => {
      const err = Object.assign(new Error("Too Many Requests"), { status: 429 });
      const result = classifyError(err);
      expect(result.class).toBe("transient");
      expect(result.retryable).toBe(true);
    });

    test("500 → transient", () => {
      const err = Object.assign(new Error("Internal Server Error"), { status: 500 });
      const result = classifyError(err);
      expect(result.class).toBe("transient");
      expect(result.retryable).toBe(true);
    });

    test("502 → transient", () => {
      const err = Object.assign(new Error("Bad Gateway"), { status: 502 });
      const result = classifyError(err);
      expect(result.class).toBe("transient");
      expect(result.retryable).toBe(true);
    });

    test("503 → transient", () => {
      const err = Object.assign(new Error("Service Unavailable"), { status: 503 });
      const result = classifyError(err);
      expect(result.class).toBe("transient");
      expect(result.retryable).toBe(true);
    });
  });

  describe("Node.js error codes", () => {
    test("ECONNRESET → transient", () => {
      const err = Object.assign(new Error("Connection reset"), { code: "ECONNRESET" });
      const result = classifyError(err);
      expect(result.class).toBe("transient");
      expect(result.retryable).toBe(true);
    });

    test("ETIMEDOUT → transient", () => {
      const err = Object.assign(new Error("Timed out"), { code: "ETIMEDOUT" });
      const result = classifyError(err);
      expect(result.class).toBe("transient");
      expect(result.retryable).toBe(true);
    });

    test("ECONNREFUSED → transient", () => {
      const err = Object.assign(new Error("Connection refused"), { code: "ECONNREFUSED" });
      const result = classifyError(err);
      expect(result.class).toBe("transient");
      expect(result.retryable).toBe(true);
    });
  });

  describe("timeout flag", () => {
    test("timedOut: true → transient", () => {
      const err = Object.assign(new Error("Command timed out"), { timedOut: true });
      const result = classifyError(err);
      expect(result.class).toBe("transient");
      expect(result.retryable).toBe(true);
    });
  });

  describe("message patterns", () => {
    test("'invalid api key' → auth", () => {
      expect(classifyError(new Error("Invalid API key provided")).class).toBe("auth");
    });

    test("'unauthorized' → auth", () => {
      expect(classifyError(new Error("Request unauthorized")).class).toBe("auth");
    });

    test("'rate limit' → transient (not resource)", () => {
      const result = classifyError(new Error("Rate limit exceeded"));
      expect(result.class).toBe("transient");
      expect(result.retryable).toBe(true);
    });

    test("'quota exceeded' → resource", () => {
      const result = classifyError(new Error("Quota exceeded for this month"));
      expect(result.class).toBe("resource");
      expect(result.retryable).toBe(false);
    });

    test("'context length exceeded' → resource", () => {
      expect(classifyError(new Error("Context length exceeded")).class).toBe("resource");
    });

    test("'insufficient_quota' → resource", () => {
      expect(classifyError(new Error("insufficient_quota")).class).toBe("resource");
    });

    test("'timeout' → transient", () => {
      expect(classifyError(new Error("Request timeout")).class).toBe("transient");
    });

    test("'socket hang up' → transient", () => {
      expect(classifyError(new Error("socket hang up")).class).toBe("transient");
    });

    test("'overloaded' → transient", () => {
      expect(classifyError(new Error("API is overloaded")).class).toBe("transient");
    });

    test("unknown message → unknown", () => {
      const result = classifyError(new Error("Something unexpected happened"));
      expect(result.class).toBe("unknown");
      expect(result.retryable).toBe(false);
    });
  });

  describe("non-Error inputs", () => {
    test("string → classifies by message", () => {
      const result = classifyError("socket hang up");
      expect(result.class).toBe("transient");
    });

    test("null → unknown", () => {
      const result = classifyError(null);
      expect(result.class).toBe("unknown");
    });
  });
});

describe("withRetry", () => {
  test("returns immediately on success", async () => {
    let calls = 0;
    const result = await withRetry(async () => {
      calls++;
      return "ok";
    });
    expect(result).toBe("ok");
    expect(calls).toBe(1);
  });

  test("retries transient errors", async () => {
    let calls = 0;
    const result = await withRetry(
      async () => {
        calls++;
        if (calls < 3) throw Object.assign(new Error("timeout"), { code: "ETIMEDOUT" });
        return "recovered";
      },
      { maxRetries: 3, baseDelay: 10 },
    );
    expect(result).toBe("recovered");
    expect(calls).toBe(3);
  });

  test("does not retry auth errors", async () => {
    let calls = 0;
    try {
      await withRetry(
        async () => {
          calls++;
          throw new Error("Invalid API key");
        },
        { maxRetries: 3, baseDelay: 10 },
      );
    } catch (e) {
      expect((e as Error).message).toBe("Invalid API key");
    }
    expect(calls).toBe(1); // No retry
  });

  test("does not retry resource errors", async () => {
    let calls = 0;
    try {
      await withRetry(
        async () => {
          calls++;
          throw new Error("Quota exceeded");
        },
        { maxRetries: 3, baseDelay: 10 },
      );
    } catch (e) {
      expect((e as Error).message).toBe("Quota exceeded");
    }
    expect(calls).toBe(1);
  });

  test("throws after max retries exhausted", async () => {
    let calls = 0;
    try {
      await withRetry(
        async () => {
          calls++;
          throw Object.assign(new Error("Service unavailable"), { status: 503 });
        },
        { maxRetries: 2, baseDelay: 10 },
      );
      expect(true).toBe(false); // Should not reach here
    } catch (e) {
      expect((e as Error).message).toBe("Service unavailable");
    }
    expect(calls).toBe(3); // 1 initial + 2 retries
  });
});
