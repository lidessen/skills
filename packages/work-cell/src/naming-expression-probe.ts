import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, isAbsolute, resolve } from "node:path";
import { createDeepSeek, type DeepSeekLanguageModelOptions } from "@ai-sdk/deepseek";
import { generateText, Output } from "ai";
import { z } from "zod";
import type { CandidateArtifact, CandidateFieldRecord } from "./candidate-field";
import type { CellUsage } from "./contracts";

(globalThis as typeof globalThis & { AI_SDK_LOG_WARNINGS?: boolean }).AI_SDK_LOG_WARNINGS = false;

const ProbeManifestSchema = z.object({
  id: z.string().min(1),
  root: z.string().min(1),
  outputDir: z.string().min(1),
  sources: z.array(z.object({
    path: z.string().min(1),
    maxChars: z.number().int().positive(),
  })).min(1),
  namingExpressionProbe: z.object({
    candidateCount: z.number().int().min(3).max(12),
    materialPerOperator: z.number().int().min(1).max(4),
    randomSeed: z.string().min(1),
    estimatedTokens: z.number().int().positive(),
    aestheticEvidence: z.array(z.string().min(1)).min(1).max(12),
  }),
});

const CandidateEnvelopeSchema = z.object({
  record: z.custom<CandidateFieldRecord>((value) => {
    const record = value as Partial<CandidateFieldRecord> | null;
    return record?.version === "work-cell.candidate-field.v1" && Array.isArray(record.artifacts);
  }),
});

const NamingCandidateSchema = z.object({
  name: z.string().min(1).max(80),
  spokenForm: z.string().min(1).max(120),
  formationPath: z.string().min(1).max(400),
  plainRelation: z.string().min(1).max(500),
  risk: z.string().min(1).max(300),
  materialIndexes: z.array(z.number().int().positive()).max(3),
});

const NamingSetSchema = z.object({
  candidates: z.array(NamingCandidateSchema).min(3).max(12),
  setRejectionSignal: z.string().min(1).max(500),
});

export interface NamingExpressionResult extends z.infer<typeof NamingSetSchema> {}

export function selectProjectionMaterial(
  artifacts: CandidateArtifact[],
  perOperator: number,
  randomSeed: string,
): CandidateArtifact[] {
  const grouped = new Map<string, CandidateArtifact[]>();
  for (const artifact of artifacts) {
    const entries = grouped.get(artifact.operatorId) ?? [];
    entries.push(artifact);
    grouped.set(artifact.operatorId, entries);
  }
  return [...grouped.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .flatMap(([operatorId, entries]) => entries
      .toSorted((left, right) => seededRank(randomSeed, operatorId, left.id).localeCompare(seededRank(randomSeed, operatorId, right.id)))
      .slice(0, perOperator));
}

if (import.meta.main) {
  await main(process.argv.slice(2)).catch((error: unknown) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 2;
  });
}

async function main(args: string[]): Promise<void> {
  const candidateArg = args[0];
  const manifestArg = args[1];
  if (!candidateArg || !manifestArg) {
    throw new Error("usage: bun src/naming-expression-probe.ts <candidate-field.json> <manifest.json>");
  }
  if (!process.env.DEEPSEEK_API_KEY) throw new Error("DEEPSEEK_API_KEY is required for a live naming-expression probe");

  const candidatePath = resolve(candidateArg);
  const candidateContent = await readFile(candidatePath, "utf8");
  const candidateRecord = CandidateEnvelopeSchema.parse(JSON.parse(candidateContent)).record;
  const manifestPath = resolve(manifestArg);
  const manifest = ProbeManifestSchema.parse(JSON.parse(await readFile(manifestPath, "utf8")));
  const root = isAbsolute(manifest.root) ? manifest.root : resolve(dirname(manifestPath), manifest.root);
  const snapshotParts: string[] = [];
  const sourceEvidence: Array<{ path: string; sha256: string; includedChars: number }> = [];
  for (const source of manifest.sources) {
    const path = resolve(root, source.path);
    const content = await readFile(path, "utf8");
    const excerpt = content.slice(0, source.maxChars);
    snapshotParts.push(`## ${source.path}\n\n${excerpt}`);
    sourceEvidence.push({
      path: source.path,
      sha256: createHash("sha256").update(content).digest("hex"),
      includedChars: excerpt.length,
    });
  }

  const material = selectProjectionMaterial(
    candidateRecord.artifacts,
    manifest.namingExpressionProbe.materialPerOperator,
    manifest.namingExpressionProbe.randomSeed,
  );
  if (material.length === 0) throw new Error("candidate field contains no projection material");
  const snapshot = snapshotParts.join("\n\n");
  const modelId = "deepseek-v4-flash";
  const provider = createDeepSeek({ apiKey: process.env.DEEPSEEK_API_KEY });
  const model = provider(modelId);
  const startedAt = new Date();
  const [direct, projected] = await Promise.all([
    generateNamingSet({
      model,
      snapshot,
      count: manifest.namingExpressionProbe.candidateCount,
      aestheticEvidence: manifest.namingExpressionProbe.aestheticEvidence,
    }),
    generateNamingSet({
      model,
      snapshot,
      count: manifest.namingExpressionProbe.candidateCount,
      aestheticEvidence: manifest.namingExpressionProbe.aestheticEvidence,
      material,
    }),
  ]);
  assertNamingSet(direct.output, manifest.namingExpressionProbe.candidateCount, 0);
  assertNamingSet(projected.output, manifest.namingExpressionProbe.candidateCount, material.length);
  const finishedAt = new Date();
  const runId = randomUUID();
  const usage = addUsage(direct.usage, projected.usage);
  const outputRoot = resolve(root, manifest.outputDir, manifest.id);
  await mkdir(outputRoot, { recursive: true });
  const output = resolve(outputRoot, `naming-expression-${runId}.json`);
  const directIsA = seededRank(manifest.namingExpressionProbe.randomSeed, runId, "blind") < "8";
  const packet = resolve(outputRoot, `naming-expression-${runId}-blind.md`);
  const key = resolve(outputRoot, `naming-expression-${runId}-key.json`);
  const envelope = {
    version: "work-cell.naming-expression-probe.v1",
    runId,
    startedAt: startedAt.toISOString(),
    finishedAt: finishedAt.toISOString(),
    durationMs: finishedAt.getTime() - startedAt.getTime(),
    driver: { provider: "deepseek", model: modelId },
    sourceEvidence,
    candidateField: {
      path: candidatePath,
      sha256: createHash("sha256").update(candidateContent).digest("hex"),
      runId: candidateRecord.runId,
      materialArtifactIds: material.map((artifact) => artifact.id),
      materialByOperator: Object.fromEntries([...new Set(material.map((artifact) => artifact.operatorId))].sort().map((operatorId) => [
        operatorId,
        material.filter((artifact) => artifact.operatorId === operatorId).map((artifact) => artifact.id),
      ])),
    },
    treatment: {
      direct: direct.output,
      projected: projected.output,
    },
    usageByTreatment: { direct: direct.usage, projected: projected.usage },
    usage,
    estimateAudit: {
      estimatedTokens: manifest.namingExpressionProbe.estimatedTokens,
      actualTokens: usage.totalTokens,
      relativeError: Math.abs(usage.totalTokens - manifest.namingExpressionProbe.estimatedTokens) / manifest.namingExpressionProbe.estimatedTokens,
    },
  };
  await Promise.all([
    writeFile(output, `${JSON.stringify(envelope, null, 2)}\n`, "utf8"),
    writeFile(packet, renderBlindPacket(directIsA ? direct.output : projected.output, directIsA ? projected.output : direct.output), "utf8"),
    writeFile(key, `${JSON.stringify({ runId, A: directIsA ? "direct" : "projected", B: directIsA ? "projected" : "direct" }, null, 2)}\n`, "utf8"),
  ]);
  console.log(JSON.stringify({
    output,
    packet,
    key,
    durationMs: envelope.durationMs,
    materialArtifacts: material.length,
    materialOperators: new Set(material.map((artifact) => artifact.operatorId)).size,
    usage,
    estimateAudit: envelope.estimateAudit,
  }, null, 2));
}

async function generateNamingSet(input: {
  model: ReturnType<ReturnType<typeof createDeepSeek>>;
  snapshot: string;
  count: number;
  aestheticEvidence: string[];
  material?: CandidateArtifact[];
}): Promise<{ output: NamingExpressionResult; usage: CellUsage }> {
  const hasMaterial = input.material !== undefined;
  const result = await generateText({
    model: input.model,
    system: [
      "You name one actual long-lived open-source project for people who must be able to say, remember, discuss, and continue it.",
      "Creativity is a true relation made memorable, not maximal distance from ordinary language. Generate freely first; use naturalness as a later selection judgment, never as a command to stay literal, safe, or generic.",
      "A name may be borrowed, transformed, translated, compressed, inverted, invented, culturally rooted, or found through a private association. No language, length, cultural register, or formation path is preferred in advance.",
      "A person should be able to speak the name before hearing its story. The story may deepen the name but must not rescue an awkward surface.",
      "Treat the Principal's aesthetic evidence as observations, not templates. Do not imitate the examples' language, length, historical form, spelling, or mechanism.",
      "Reject a set that merely attaches Common, Open, Shared, Public, Civic, AI, Agent, Forge, Loom, Workshop, or another mission noun to six generic objects. The candidates must arise through materially different formation paths.",
      hasMaterial
        ? "Private scratch material follows. Digest it silently, use only relations that become natural in the project, and discard all of it if it produces affectation. Never quote, expose, summarize, or defend the scratch material."
        : "No private associative scratch material is available. Set every materialIndexes field to an empty array.",
      `Return exactly ${input.count} genuinely different usable candidates. Explain each relation and risk in one plain sentence. Do not recommend or adopt a winner.`,
    ].join("\n"),
    prompt: [
      "## Project source",
      input.snapshot,
      "## Concrete naming problem",
      "Find a durable project name for this whole project. Recover the relation before the word. The project seeks to make advanced AI production capability governable, inspectable, replaceable, and broadly usable rather than captured by a few firms. Its name must survive implementation changes and leave room for the project to grow. Existing examples and rejected names are evidence, never templates.",
      "## Principal aesthetic evidence",
      JSON.stringify(input.aestheticEvidence),
      ...(hasMaterial ? [
        "## Private associative scratch material",
        JSON.stringify(input.material!.map((artifact, index) => ({ index: index + 1, content: artifact.content }))),
        "materialIndexes may cite zero to three scratch indexes that actually changed a candidate; an empty list is valid and preferable to forced influence.",
      ] : []),
    ].join("\n\n"),
    output: Output.object({ schema: NamingSetSchema }),
    maxOutputTokens: 2_800,
    temperature: 0.78,
    topP: 0.92,
    providerOptions: {
      deepseek: { thinking: { type: "disabled" } } satisfies DeepSeekLanguageModelOptions,
    },
  });
  return { output: result.output, usage: normalizeUsage(result.totalUsage, result.providerMetadata) };
}

function assertNamingSet(value: NamingExpressionResult, count: number, materialCount: number): void {
  if (value.candidates.length !== count) throw new Error(`naming treatment must return exactly ${count} candidates`);
  const names = value.candidates.map((candidate) => candidate.name.trim().toLocaleLowerCase());
  if (new Set(names).size !== names.length) throw new Error("naming treatment returned duplicate candidate names");
  for (const candidate of value.candidates) {
    if (materialCount === 0 && candidate.materialIndexes.length > 0) {
      throw new Error(`direct baseline claimed unavailable material for ${candidate.name}`);
    }
    const invalid = candidate.materialIndexes.filter((index) => index > materialCount);
    if (invalid.length > 0) throw new Error(`${candidate.name} cited unavailable material indexes: ${invalid.join(", ")}`);
  }
}

function renderBlindPacket(a: NamingExpressionResult, b: NamingExpressionResult): string {
  return [
    "# Naming expression comparison",
    "",
    "Judge the two sets as usable project naming work. You may choose A, B, both, or neither; relative preference is not required when both fail.",
    "",
    renderSet("A", a),
    renderSet("B", b),
    "Reply with `A`, `B`, `both`, or `neither`, followed by any individual names worth continuing. Treatment and private material are intentionally hidden.",
    "",
  ].join("\n");
}

function renderSet(label: string, value: NamingExpressionResult): string {
  return [
    `## Set ${label}`,
    "",
    ...value.candidates.flatMap((candidate) => [
      `### ${candidate.name}`,
      "",
      `Spoken: ${candidate.spokenForm}`,
      "",
      `Formation: ${candidate.formationPath}`,
      "",
      candidate.plainRelation,
      "",
      `Risk: ${candidate.risk}`,
      "",
    ]),
  ].join("\n");
}

function seededRank(seed: string, group: string, id: string): string {
  return createHash("sha256").update(`${seed}:${group}:${id}`).digest("hex");
}

function normalizeUsage(usage: unknown, metadata: unknown): CellUsage {
  const record = asRecord(usage);
  const provider = asRecord(asRecord(metadata).deepseek);
  const inputTokens = numberValue(record.inputTokens) || numberValue(record.promptTokens);
  const outputTokens = numberValue(record.outputTokens) || numberValue(record.completionTokens);
  return {
    inputTokens,
    outputTokens,
    totalTokens: numberValue(record.totalTokens) || inputTokens + outputTokens,
    cachedInputTokens: numberValue(record.cachedInputTokens) || numberValue(provider.promptCacheHitTokens),
  };
}

function addUsage(left: CellUsage, right: CellUsage): CellUsage {
  return {
    inputTokens: left.inputTokens + right.inputTokens,
    outputTokens: left.outputTokens + right.outputTokens,
    totalTokens: left.totalTokens + right.totalTokens,
    cachedInputTokens: left.cachedInputTokens + right.cachedInputTokens,
  };
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" ? value as Record<string, unknown> : {};
}

function numberValue(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}
