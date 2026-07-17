import { createDeepSeek, type DeepSeekLanguageModelOptions } from "@ai-sdk/deepseek";
import { APICallError, type LanguageModelV4 } from "@ai-sdk/provider";
import { defaultSettingsMiddleware, wrapLanguageModel } from "ai";
import type { ModelRouteFailure } from "../model-route";

export const DEEPSEEK_PROVIDER_ID = "deepseek";

const deepSeekProviderOptions = {
  deepseek: {
    thinking: { type: "disabled" },
  } satisfies DeepSeekLanguageModelOptions,
};

export const deepSeekFlashPricing = {
  inputPerMillionUsd: 0.14,
  cachedInputPerMillionUsd: 0.0028,
  outputPerMillionUsd: 0.28,
  source: "https://api-docs.deepseek.com/quick_start/pricing",
  revision: "2026-07-16",
};

export function createDeepSeekModel(options: {
  apiKey: string;
  model: string;
  baseURL?: string;
}): LanguageModelV4 {
  const provider = createDeepSeek({
    apiKey: options.apiKey,
    ...(options.baseURL ? { baseURL: options.baseURL } : {}),
  });
  return wrapLanguageModel({
    model: provider(options.model),
    middleware: defaultSettingsMiddleware({
      settings: { providerOptions: deepSeekProviderOptions },
    }),
  });
}

export function classifyDeepSeekFailure(
  error: unknown,
  context: { signal?: AbortSignal },
): ModelRouteFailure | undefined {
  if (context.signal?.aborted || isAbortError(error)) return undefined;
  if (!APICallError.isInstance(error)) return undefined;
  const status = error.statusCode;
  if (
    status === undefined
    || status === 401
    || status === 402
    || status === 403
    || status === 408
    || status === 429
    || (status !== undefined && status >= 500)
  ) {
    return { reason: classifyStatus(status) };
  }
  return undefined;
}

function classifyStatus(status: number | undefined): string {
  if (status === 401 || status === 403) return "authentication_or_permission";
  if (status === 402 || status === 429) return "quota_or_rate_limit";
  if (status === 408) return "timeout";
  if (status !== undefined && status >= 500) return "provider_unavailable";
  return "transport_or_retryable_provider_error";
}

function isAbortError(error: unknown): boolean {
  return error instanceof Error && error.name === "AbortError";
}
