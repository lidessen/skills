/**
 * Error classification for daemon reliability.
 *
 * Categorizes errors into actionable types so the daemon can
 * make intelligent decisions: retry transient failures, stop
 * on auth/resource errors, and surface unknowns.
 */

export type ErrorClass = "transient" | "auth" | "resource" | "unknown";

export interface ClassifiedError {
  class: ErrorClass;
  message: string;
  /** Original error for logging/debugging */
  cause?: unknown;
  /** HTTP status code if available */
  status?: number;
  /** Whether this error is worth retrying */
  retryable: boolean;
}

/**
 * Classify an error into an actionable type.
 *
 * Inspects multiple signals: HTTP status codes, Node.js error codes,
 * CLI exit codes, and message patterns. Returns the most specific
 * classification possible.
 */
export function classifyError(error: unknown): ClassifiedError {
  const message = error instanceof Error ? error.message : String(error);
  if (error == null) {
    return { class: "unknown", message, cause: error, retryable: false };
  }
  const err = typeof error === "object" ? (error as Record<string, unknown>) : {};

  // 1. Check HTTP status code (API errors from SDK / fetch)
  const status = (err.status ?? err.statusCode ?? err.code) as number | string | undefined;
  if (typeof status === "number") {
    if (status === 401 || status === 403) {
      return { class: "auth", message, cause: error, status, retryable: false };
    }
    if (status === 429) {
      return { class: "transient", message, cause: error, status, retryable: true };
    }
    if (status >= 500 && status < 600) {
      return { class: "transient", message, cause: error, status, retryable: true };
    }
  }

  // 2. Check Node.js network error codes
  if (typeof status === "string") {
    const networkCodes = [
      "ECONNRESET",
      "ECONNREFUSED",
      "ECONNABORTED",
      "ETIMEDOUT",
      "EPIPE",
      "EAI_AGAIN",
      "EHOSTUNREACH",
      "ENETUNREACH",
    ];
    if (networkCodes.includes(status)) {
      return { class: "transient", message, cause: error, retryable: true };
    }
  }

  // 3. Check CLI exit code (from execa errors)
  const exitCode = err.exitCode as number | undefined;
  if (typeof exitCode === "number" && exitCode !== 0) {
    // Exit code alone isn't enough — fall through to message patterns
  }

  // 4. Check if the error was a timeout (execa timedOut flag)
  if (err.timedOut === true) {
    return { class: "transient", message, cause: error, retryable: true };
  }

  // 5. Message-pattern matching (case insensitive)
  const lower = message.toLowerCase();

  // Auth patterns
  const authPatterns = [
    "unauthorized",
    "invalid api key",
    "invalid x-api-key",
    "api key not found",
    "authentication failed",
    "forbidden",
    "permission denied",
    "access denied",
  ];
  if (authPatterns.some((p) => lower.includes(p))) {
    return { class: "auth", message, cause: error, retryable: false };
  }

  // Resource / quota patterns
  const resourcePatterns = [
    "rate limit",
    "quota exceeded",
    "token limit",
    "context length exceeded",
    "context window",
    "maximum context",
    "billing",
    "insufficient_quota",
    "budget",
    "credit",
    "too many tokens",
    "max_tokens",
  ];
  // Distinguish rate limits (transient, will recover) from hard quota (resource)
  if (lower.includes("rate limit") || lower.includes("too many requests")) {
    return { class: "transient", message, cause: error, retryable: true };
  }
  if (resourcePatterns.some((p) => lower.includes(p))) {
    return { class: "resource", message, cause: error, retryable: false };
  }

  // Transient patterns
  const transientPatterns = [
    "timeout",
    "timed out",
    "network error",
    "socket hang up",
    "econnreset",
    "econnrefused",
    "fetch failed",
    "server error",
    "internal server error",
    "bad gateway",
    "service unavailable",
    "overloaded",
  ];
  if (transientPatterns.some((p) => lower.includes(p))) {
    return { class: "transient", message, cause: error, retryable: true };
  }

  return { class: "unknown", message, cause: error, retryable: false };
}

/**
 * Retry a function with exponential backoff for transient errors.
 *
 * Only retries when classifyError returns retryable: true.
 * Auth/resource errors fail immediately.
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
    label?: string;
  } = {},
): Promise<T> {
  const { maxRetries = 3, baseDelay = 2000, maxDelay = 16000, label } = options;

  let lastError: ClassifiedError | undefined;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = classifyError(error);

      // Non-retryable: fail immediately
      if (!lastError.retryable) {
        throw error;
      }

      // Last attempt: don't sleep, just throw
      if (attempt === maxRetries) {
        break;
      }

      // Exponential backoff with jitter
      const delay = Math.min(baseDelay * 2 ** attempt, maxDelay);
      const jitter = delay * (0.5 + Math.random() * 0.5);

      if (label) {
        console.warn(
          `[${label}] ${lastError.class} error (attempt ${attempt + 1}/${maxRetries + 1}), retrying in ${Math.round(jitter / 1000)}s: ${lastError.message}`,
        );
      }

      await new Promise((resolve) => setTimeout(resolve, jitter));
    }
  }

  // All retries exhausted — throw original error
  throw lastError?.cause ?? new Error(lastError?.message ?? "Unknown error after retries");
}
