# Hybrid repository and architecture review

Read this reference when more than one language, build system, runtime, artifact type, or repository participates in one product.

## Draw separate graphs

For each important unit, map the following rather than one combined tree:

| Graph             | Questions                                                                                                                                    |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Source            | Which files are authoritative source, generated output, vendor, mirror, fixture, or documentation?                                           |
| Dependency/API    | Who imports or calls it? What visibility, protocol, schema, or registration rule constrains the edge?                                        |
| Build             | Which target compiles, generates, links, packages, or tests it? Which target is only an aggregate/phony target?                              |
| Runtime/delivery  | Which library, binary, process, container, installer, or distribution contains it? Can it start, stop, upgrade, and roll back independently? |
| State/resource    | Which process owns data, queues, leases, files, credentials, transactions, and recovery?                                                     |
| Ownership/release | Who reviews the source, schema, generator, generated output, release configuration, and deployment?                                          |

An implementation library can be independently compiled but statically linked into one process. A plugin can be dynamically discovered but share the host's lifecycle. A repository can contain several artifacts without providing independent release governance.

## Source of truth and generated outputs

For every generated or mirrored object, record:

```text
authoritative input → generator/version → generated output → consumer/build target → verification
```

Check whether output is committed, reproducible, ignored, published to another repository, or regenerated in CI. Never treat an automatically published mirror, `generated/`, `out/`, or vendor copy as authoritative without source evidence.

Schema and IDL need extra care:

- Give the schema one owner and one canonical location.
- Keep compatibility and versioning rules with the schema, not only with one generated language.
- Put language bindings and protocol adapters at the edge.
- Verify that generated code is consumed by the intended build targets and that stale output cannot silently become the API.

## Platform and language boundaries

Organize platform code around the actual build/release matrix. For each platform, answer:

- Which source and target are selected?
- Which artifact is produced?
- Which API or ABI is exposed?
- Is the platform code a library, binding, tool, or part of one host process?
- Who tests and releases that combination?

Names such as `linux`, `android`, `node`, `browser`, `native`, or `wasm` are useful only when a build condition, target, runtime, or artifact makes the distinction real. Do not duplicate a core abstraction merely to mirror the platform directory.

## Plugin, extension, application, and process

Classify each term by its enforced behavior:

- A package/crate is an import or build unit.
- A plugin/extension is an attachable implementation only if discovery, registration, lifecycle, and compatibility are defined.
- An application/CLI is an entrypoint and composition surface; it may still be one part of a larger process.
- A process/service has its own lifecycle, resource ownership, failure behavior, and deployment artifact.
- A distribution is a selected combination of components and configuration; it need not map one-to-one to a source directory.

Do not infer a process boundary from `plugin`, `extension`, `contrib`, `app`, `server`, or `components`. Check whether the unit is separately launched, addressed, upgraded, and recovered.

## Repository split decision

Keep a mixed project together when atomic changes, shared CI, shared schema, synchronized releases, or cross-language refactors are important. Split repositories when source ownership, access, release cadence, compatibility, or dependency isolation are independently governed and the coordination cost is acceptable.

Before splitting, check:

- Can a stable protocol/schema replace direct source coupling?
- Can a consumer build and test against a versioned artifact?
- Who owns migrations, generated code, compatibility, security, and rollback?
- Does a split make local development, atomic fixes, and failure diagnosis materially worse?
- Is the proposed new repository actually a source of truth rather than a publish mirror?

## Patterns observed in large projects

- LLVM distinguishes projects, runtimes, build targets, and distribution components through CMake and installation configuration.
- Chromium uses GN targets, visibility, dependency rules, process layers, generated Mojo bindings, and OWNERS; `components/` is not automatically a product or service.
- Kubernetes distinguishes source, `cmd` binaries, Go modules, staging publication, generated APIs, and container artifacts.
- Envoy separates API, implementation, server executable, extensions, mobile library, and distribution combinations; extensions are often linked into one host.
- OpenTelemetry separates specification/proto, language implementations, Collector components, and generated distributions; receiver/exporter directories are plugin types, not deployment units.

These patterns support the graph model; they are not templates to copy. Scale, build tooling, release cadence, and ownership must be independently justified.
