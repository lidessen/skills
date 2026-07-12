import { z } from "zod";

export const WORK_CELL_RECORD_VERSION = "work-cell.run.v1" as const;

export const BudgetSchema = z.object({
  maxSteps: z.number().int().positive().default(20),
  maxTokens: z.number().int().positive().default(100_000),
  tokenControl: z.enum(["audit", "hard"]).optional(),
  maxDurationMs: z.number().int().positive().default(300_000),
  maxCommandOutputBytes: z.number().int().positive().default(64_000),
});

export const WorkNodeSchema = z.object({
  id: z.string().min(1),
  requiredTransition: z.string().min(1),
  acceptance: z.string().min(1),
  dependsOn: z.array(z.string().min(1)).default([]),
});

export const DiscoveryBranchSchema = z.object({
  id: z.string().min(1),
  smallestWork: z.string().min(1),
  opensWhen: z.string().min(1),
  closesWhen: z.string().min(1),
});

export const WorkEstimateSchema = z.object({
  id: z.string().min(1),
  version: z.literal("work-estimate.v1"),
  decisionHorizon: z.enum(["direction", "capability", "mission"]),
  targetState: z.string().min(1),
  sources: z.array(z.string().min(1)).min(1),
  nodes: z.array(WorkNodeSchema).min(1),
  discoveryBranches: z.array(DiscoveryBranchSchema).default([]),
  reopeningObservation: z.string().min(1),
});

export const ExecutionProfileSchema = z.object({
  id: z.string().min(1),
  version: z.literal("execution-profile.v1"),
  provider: z.string().min(1),
  model: z.string().min(1),
  contextPolicy: z.string().min(1).optional(),
  toolSurface: z.string().min(1).optional(),
  parallelism: z.literal("serial").default("serial"),
  priceRevision: z.string().min(1).optional(),
});

export const BudgetEnvelopeSchema = z.object({
  id: z.string().min(1),
  version: z.literal("budget-envelope.v1"),
  maxTotalTokens: z.number().int().positive(),
  onExhaustion: z.literal("partial").default("partial"),
});

export const WorkspacePolicySchema = z.object({
  root: z.string().min(1),
  readPaths: z.array(z.string().min(1)).default(["."]),
  writePaths: z.array(z.string().min(1)).default([]),
  excludePaths: z.array(z.string().min(1)).default([]),
  allowedCommands: z.array(z.string().min(1)).default([]),
});

export const DnaSchema = z.object({
  baseInstructions: z.string().min(1),
  capabilities: z.array(z.string().min(1)).default([]),
});

const PidSchema = z.string().regex(/^P\d{2,}$/, "expected a P-ID such as P04");

export const GenomeSchema = z.object({
  sequencePath: z.string().min(1),
  interpretationsDir: z.string().min(1),
  inheritedLineage: z
    .object({
      primary: PidSchema,
      supporting: z.array(PidSchema).max(3).default([]),
    })
    .optional(),
});

export const GeneExpressionSchema = z
  .object({
    lead: PidSchema,
    supports: z.array(PidSchema).max(3).default([]),
    principalContradiction: z.string().min(1),
    contributions: z
      .array(
        z.object({
          pid: PidSchema,
          decision: z.string().min(1),
        }),
      )
      .min(1)
      .max(4),
  })
  .superRefine((value, context) => {
    const selected = [value.lead, ...value.supports];
    if (new Set(selected).size !== selected.length) {
      context.addIssue({ code: "custom", path: ["supports"], message: "selected P-IDs must be unique" });
    }
    const contributed = new Set(value.contributions.map((item) => item.pid));
    for (const pid of selected) {
      if (!contributed.has(pid)) {
        context.addIssue({
          code: "custom",
          path: ["contributions"],
          message: `missing decision contribution for ${pid}`,
        });
      }
    }
    for (const pid of contributed) {
      if (!selected.includes(pid)) {
        context.addIssue({
          code: "custom",
          path: ["contributions"],
          message: `contribution references unselected ${pid}`,
        });
      }
    }
  });

export const TreatmentSchema = z.object({
  id: z.string().min(1),
  instructions: z.string().min(1),
});

// A serializable JSON Schema is the portable boundary for a cell's final
// structured output. It intentionally does not belong to a tool input schema.
export const OutputSchemaSchema = z.record(z.string(), z.unknown()).superRefine((value, context) => {
  if (value.type !== "object") {
    context.addIssue({ code: "custom", message: "outputSchema must describe an object at its root" });
  }
});

export const ArtifactRequirementSchema = z.object({
  path: z.string().min(1),
  instructions: z.string().min(1),
});

export const TerminalToolSchema = z.object({
  name: z.string().regex(/^[a-z][a-z0-9_]*$/, "terminal tool names use lowercase snake_case"),
  description: z.string().min(1),
  inputSchema: OutputSchemaSchema,
});

export const CellInputSchema = z.object({
  id: z.string().min(1),
  intent: z.string().min(1),
  workspace: WorkspacePolicySchema,
  genome: GenomeSchema,
  dna: DnaSchema,
  capabilitiesRequired: z.array(z.string().min(1)).default([]),
  acceptance: z.array(z.string().min(1)).min(1),
  terminalTools: z.array(TerminalToolSchema).min(1).optional(),
  outputSchema: OutputSchemaSchema.optional(),
  artifacts: z.array(ArtifactRequirementSchema).min(1).optional(),
  budget: BudgetSchema.default({
    maxSteps: 20,
    maxTokens: 100_000,
    maxDurationMs: 300_000,
    maxCommandOutputBytes: 64_000,
  }),
  workEstimate: WorkEstimateSchema.optional(),
  executionProfile: ExecutionProfileSchema.optional(),
  budgetEnvelope: BudgetEnvelopeSchema.optional(),
  treatment: TreatmentSchema.optional(),
});

export const UsageSchema = z.object({
  inputTokens: z.number().nonnegative().default(0),
  outputTokens: z.number().nonnegative().default(0),
  totalTokens: z.number().nonnegative().default(0),
  cachedInputTokens: z.number().nonnegative().default(0),
});

export const WorkspaceDiffSchema = z.object({
  added: z.array(z.string()),
  changed: z.array(z.string()),
  removed: z.array(z.string()),
});

export const ArtifactRecordSchema = z.object({
  path: z.string().min(1),
  bytes: z.number().int().nonnegative(),
  sha256: z.string().regex(/^[a-f0-9]{64}$/),
});

export type Budget = z.infer<typeof BudgetSchema>;
export type WorkEstimate = z.infer<typeof WorkEstimateSchema>;
export type ExecutionProfile = z.infer<typeof ExecutionProfileSchema>;
export type BudgetEnvelope = z.infer<typeof BudgetEnvelopeSchema>;
export type WorkspacePolicy = z.infer<typeof WorkspacePolicySchema>;
export type CellInput = z.infer<typeof CellInputSchema>;
export type GeneExpression = z.infer<typeof GeneExpressionSchema>;
export type OutputSchema = z.infer<typeof OutputSchemaSchema>;
export type ArtifactRequirement = z.infer<typeof ArtifactRequirementSchema>;
export type ArtifactRecord = z.infer<typeof ArtifactRecordSchema>;
export type TerminalTool = z.infer<typeof TerminalToolSchema>;
export type CellUsage = z.infer<typeof UsageSchema>;
export type WorkspaceDiff = z.infer<typeof WorkspaceDiffSchema>;

export type CellTerminalStatus =
  | "passed"
  | "failed"
  | "verification_failed"
  | "protocol_error"
  | "capability_mismatch"
  | "budget_exceeded"
  | "cancelled";

export interface TraceEvent {
  at: string;
  type: string;
  data: unknown;
}

export interface CellRunRecord {
  version: typeof WORK_CELL_RECORD_VERSION;
  runId: string;
  cellId: string;
  driver: DriverDescriptor;
  startedAt: string;
  finishedAt: string;
  durationMs: number;
  status: CellTerminalStatus;
  input: CellInput;
  geneExpression?: GeneExpression;
  loadedInterpretations: string[];
  finalText: string;
  output?: unknown;
  artifacts: ArtifactRecord[];
  verification: {
    passed: boolean;
    terminal: TerminalVerification;
    output?: OutputVerification;
    artifacts?: ArtifactVerification;
  };
  workspaceDiff: WorkspaceDiff;
  usage: CellUsage;
  executionObservation: {
    workEstimateId?: string;
    executionProfileId?: string;
    priceRevision?: string;
  };
  estimatedCostUsd?: number;
  estimateBasis?: string;
  trace: TraceEvent[];
  rawSteps: unknown[];
  error?: string;
}

export interface OutputVerification {
  passed: boolean;
  errors: string[];
}

export interface TerminalVerification {
  passed: boolean;
  required: string[];
  called: string[];
}

export interface ArtifactVerification {
  passed: boolean;
  errors: string[];
}

export interface DriverDescriptor {
  adapter: string;
  provider: string;
  model: string;
  pricing?: {
    inputPerMillionUsd: number;
    cachedInputPerMillionUsd?: number;
    outputPerMillionUsd: number;
    source: string;
    revision?: string;
  };
}
