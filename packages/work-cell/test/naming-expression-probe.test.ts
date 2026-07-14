import { expect, test } from "bun:test";
import type { CandidateArtifact } from "../src/candidate-field";
import { selectProjectionMaterial } from "../src/naming-expression-probe";

test("projection material preserves every available operator instead of inheriting archive selection bias", () => {
  const artifacts = [
    ...artifactsFor("plain", 4),
    ...artifactsFor("remote", 4),
    ...artifactsFor("weathering", 4),
  ];

  const first = selectProjectionMaterial(artifacts, 2, "stable-seed");
  const replay = selectProjectionMaterial(artifacts.toReversed(), 2, "stable-seed");

  expect(first.map((artifact) => artifact.id)).toEqual(replay.map((artifact) => artifact.id));
  expect(Object.fromEntries(["plain", "remote", "weathering"].map((operatorId) => [
    operatorId,
    first.filter((artifact) => artifact.operatorId === operatorId).length,
  ]))).toEqual({ plain: 2, remote: 2, weathering: 2 });
});

function artifactsFor(operatorId: string, count: number): CandidateArtifact[] {
  return Array.from({ length: count }, (_, index) => ({
    id: `${operatorId}-${index + 1}`,
    content: `${operatorId} material ${index + 1}`,
    phase: operatorId === "weathering" ? "mutate" : "emit",
    operatorId,
    sourceNodeIds: [],
    parentCandidateIds: [],
    seedTitleIds: [],
    participationTitleIds: [],
    seedActivations: [],
  }));
}
