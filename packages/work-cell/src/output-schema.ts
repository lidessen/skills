import { jsonSchema } from "ai";
import type { JSONSchema7 } from "@ai-sdk/provider";
import { z } from "zod";
import type { OutputSchema } from "./contracts";

export interface OutputValidation {
  passed: boolean;
  errors: string[];
}

export interface CompiledOutputSchema {
  validate(value: unknown): OutputValidation;
  forAiSdk(): ReturnType<typeof jsonSchema>;
}

/**
 * Compile the one public output definition once. The same Zod validator backs
 * the SDK adapter and run settlement, so a provider cannot turn schema
 * guidance into an unchecked claim.
 */
export function compileOutputSchema(schema: OutputSchema): CompiledOutputSchema {
  const validator = z.fromJSONSchema(schema as JSONSchema7);
  const check = (value: unknown): OutputValidation => {
    const result = validator.safeParse(value);
    return {
      passed: result.success,
      errors: result.success ? [] : result.error.issues.map((issue) => `${issue.path.join(".") || "/"} ${issue.message}`),
    };
  };
  return {
    validate: check,
    forAiSdk: () => jsonSchema(schema as JSONSchema7, {
      validate(value) {
        const result = check(value);
        return result.passed
          ? { success: true, value }
          : { success: false, error: new Error(result.errors.join("; ")) };
      },
    }),
  };
}
