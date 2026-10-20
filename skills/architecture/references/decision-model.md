# Structure decision model

Read this reference when the task requires deciding whether material belongs together, should be split, or needs a stronger boundary.

## Start with the object, not the container

An object may be a concept, source unit, package, build target, artifact, process, state owner, or public contract. A folder is only one possible view of those objects. Before proposing a move or split, answer:

1. What responsibility or decision does this object own?
2. What does it deliberately not own?
3. Who consumes it, through which entrypoint or interface?
4. Which changes should happen together, and which should not?
5. Which invariant, transaction, resource, or failure behavior must remain local?
6. What is public, private, generated, or only a build-time view?
7. Who reviews, versions, publishes, deploys, and recovers it?

If these answers are missing, record the unknown instead of inventing a package boundary.

## Six relations to inspect separately

| Relation                | Evidence                                               | Decision it can support               | What it cannot prove alone     |
| ----------------------- | ------------------------------------------------------ | ------------------------------------- | ------------------------------ |
| Semantic responsibility | domain rules, invariants, change reasons               | grouping or splitting concepts        | independent package or process |
| Dependency/API          | imports, exports, visibility, protocol, registry       | direction and public surface          | independent deployment         |
| Build/version           | manifest, module/crate/package, target, workspace      | build, cache, version or release unit | runtime isolation              |
| Runtime/delivery        | entrypoint, binary, container, process supervisor      | process and deployment boundary       | source ownership               |
| State/resource          | database, queue, transaction, lease, cache, filesystem | ownership and failure coupling        | public API stability           |
| Ownership/release       | owner files, review rules, compatibility and rollout   | governance and responsibility         | implementation truth           |

The same directory may contain multiple objects from different relations. Conversely, one semantic feature may intentionally span source directories, a schema file, generated code, a test fixture, and a release configuration.

## Grouping signals

Keep units together when most of these are true:

- They change for the same reason and are reviewed together.
- They share an invariant, transaction, lifecycle, or resource owner.
- They have the same primary consumers and compatibility horizon.
- Splitting would create a protocol or coordination layer with no independent value.
- Their build, test, failure, deployment, and rollback boundaries are the same.

Co-location does not require exposing every symbol. A single package can have a stable facade and private implementation; a single process can contain several internal components.

## Splitting signals

Split only when the difference is real and useful:

- A consumer needs one side without the other.
- The sides change, compile, test, release, or scale independently.
- They have different platform or dependency constraints.
- They need different failure, security, resource, or recovery boundaries.
- They have different owners or compatibility promises.
- A protocol or schema already exists and is the canonical boundary.

Do not split merely because a file is long, two languages appear, a folder has many children, or a future consumer is imagined without evidence.

## Boundary ladder

Choose the lowest level that can enforce the required difference:

| Level                        | Use when                                                                        | Evidence to check                                       |
| ---------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------- |
| File or subdirectory         | material is one responsibility but benefits from navigation                     | imports, local cohesion, discoverability                |
| Private/internal unit        | implementation must be hidden from unrelated consumers                          | language/build visibility rules, facade                 |
| Package/crate/module         | dependency, build, version, or consumer boundary is real                        | manifest, import path, build and test target            |
| Library/package distribution | external reuse and compatibility are intentional                                | public API, release metadata, install behavior          |
| Binary/process               | independent lifecycle, resources, failure, or deployment matters                | entrypoint, protocol, supervisor, artifact and rollback |
| Repository                   | governance, access, release cadence, or source-of-truth boundary is independent | ownership, CI, versioning, publication and migration    |

An extra layer has a cost: names, APIs, coordination, testing, versioning, and failure modes. State why the current lower level cannot express or enforce the requirement before escalating.

## Boundary tests

For every proposed unit, write short answers to:

- Include: what belongs here and why?
- Exclude: what looks nearby but must stay outside?
- Nearest neighbor: which other unit is easiest to confuse with it?
- Counterexample: what request would make the proposed boundary wrong?
- Consumer: who is allowed to depend on it, and through what surface?
- Change: what can change without changing this unit's contract?

If the answers are only directory names, the boundary is not yet specified.

## Naming rules

Name by responsibility and stable relationship:

- `protocol`, `client`, `server`, `adapter`, `runtime`, and `cli` are useful when the role is materially different.
- An environment suffix such as `browser`, `node`, `native`, or `wasm` should correspond to a real build or runtime constraint.
- A concept name should not silently promise package publication, process independence, or public API stability.
- `common`, `shared`, `utils`, `misc`, and `core` require a concrete contract and exclusion rule or should be decomposed.

Names are part of the interface. A rename that changes imports, persistence keys, plugin IDs, URLs, generated paths, or user commands is a contract change even when the implementation is unchanged.
