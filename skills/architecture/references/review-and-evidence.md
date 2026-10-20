# Review, change, and evidence

Read this reference when the task requires a written architecture review, an actual reorganization, or a claim that a structure works in practice.

## Choose the mode

### Review only

Inspect the smallest set of files and configurations that can change the decision. Return findings, alternatives, evidence, unknowns, and reopen conditions. Do not move files or rewrite imports unless requested.

### Reorganization requested

Define the target boundary first, then make the smallest complete change: source, imports, manifests, build/codegen, tests, documentation, registration, and release references that belong to the same contract. Preserve unrelated uncommitted work and do not delete data or an uncertain endpoint to make the tree cleaner.

### Runtime or delivery claim

A structural review may identify a hypothesis, but it does not prove startup, packaging, isolation, recovery, or user acceptance. Use the project's runtime and integration checks for those claims and report the structural and runtime evidence separately.

## Evidence ladder

| Level                   | What to inspect                                                                                            | What it supports                                        |
| ----------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Source evidence         | imports, exports, manifests, build files, codegen, entrypoints, ownership docs                             | current structural facts                                |
| Mechanical verification | formatter, linter, typecheck, unit/integration tests, build, package/install                               | conformance and repeatable mechanics                    |
| Runtime observation     | clean import/install, CLI/service start, protocol call, process tree, failure/restart, artifact inspection | actual behavior in the exercised path                   |
| Boundary support        | independent consumer/build/release/failure/ownership scenario                                              | whether the proposed boundary is useful and enforceable |
| User acceptance         | maintainers can locate, modify, test, release, and explain the result                                      | practical success                                       |

Do not upgrade a lower level into a higher one. A passing formatter does not prove a correct package boundary; a successful unit test does not prove an independent service; a generated directory does not prove source ownership.

## Change scenarios

Use scenarios that can falsify the proposal:

1. Add another feature in the same concept.
2. Replace one implementation without changing consumers.
3. Add a second consumer or language binding.
4. Build or publish only one target/platform.
5. Restart or fail one part while another continues.
6. Change a schema, generated output, or public name.
7. Review, version, roll back, or migrate the unit independently.

For each scenario, state what should remain local, what crosses the boundary, and what evidence would show that the proposal is wrong.

## Compact report format

```md
结构问题：<one concrete question and scope>
当前事实：<source, dependency, build, runtime, state, ownership evidence>
决定：<keep, move, split, merge, rename, or defer>
边界：<owns / excludes / consumers / enforced surface>
建议结构：<tree or relation view, with non-boundary folders marked>
验证：<mechanical, runtime, boundary, and acceptance evidence separately>
未知与重开条件：<what was not checked and what would change the decision>
```

If multiple options remain valid, compare their change cost, dependency direction, build/release cost, runtime isolation, ownership clarity, and migration risk. Do not hide an unresolved choice behind a confident folder tree.
