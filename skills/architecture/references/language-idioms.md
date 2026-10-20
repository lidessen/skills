# Language and ecosystem idioms

Read only when the current repository uses the relevant language or package/build system. These are boundary clues, not templates. Verify the current project's manifests and build configuration before applying them.

## Node.js and TypeScript

- `package.json` fields such as `exports`, `imports`, `bin`, `files`, and `types` can define public imports, internal aliases, CLI entrypoints, and published content more precisely than directory names.
- TypeScript project references express logical subprojects through build dependencies and declaration boundaries. A `packages/` directory without references, manifests, or consumers is only a naming convention.
- In Next.js, route groups and private folders can organize route source without changing the URL or exposing a route. A folder can therefore be organizational rather than an API boundary.
- Node.js itself separates public library surfaces, `lib/internal`, native `src`, vendored dependencies, tests, tools, and docs. The public/internal distinction is supported by exports and documentation, not by `internal` alone.

Useful primary references: [TypeScript project references](https://www.typescriptlang.org/docs/handbook/project-references), [Next.js project structure](https://nextjs.org/docs/app/getting-started/project-structure), [Node.js collaborator guide](https://github.com/nodejs/node/blob/main/doc/contributing/collaborator-guide.md).

## Go

- A Go module is a versioned collection of packages; a package is a directory-level import unit; a binary or service is a runtime/delivery unit. Keep these relations separate.
- `cmd/` conventionally holds executable entrypoints. The reusable behavior normally lives in packages, often under `internal/` when external imports must be compiler-restricted.
- `internal/` has language-enforced import rules. `pkg/` has no equivalent special enforcement; treat it as a project convention that requires evidence.
- `go.work` and `replace` can support development composition without proving a production deployment or repository boundary.
- Split a module when external reuse, versioning, dependency isolation, or release ownership justifies it—not merely because a directory is large.

Useful primary references: [Organizing a Go module](https://go.dev/doc/modules/layout), [Go Modules Reference](https://go.dev/ref/mod).

## Rust

- Cargo packages and crates have concrete targets: library, binary, integration test, example, benchmark, build script, or proc-macro. Check `Cargo.toml` and target declarations rather than inferring from `src/`.
- A workspace shares build/dependency coordination across packages. Workspace membership is not by itself a public API, independent process, or release promise.
- Features, target-specific dependencies, proc-macros, generated code, and platform modules often form real build boundaries even when the final artifact is one binary.
- Crate extraction is justified by API reuse, dependency/build isolation, platform constraints, release ownership, or a separately testable contract. Do not optimize for crate count.

Useful primary references: [Cargo project layout](https://doc.rust-lang.org/cargo/guide/project-layout.html), [Cargo workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html).

## Python

- `src` layout separates importable source from the checkout and makes installed-package behavior easier to test; flat layout reduces friction for direct checkout execution. Packaging metadata and development workflow decide which tradeoff is appropriate.
- A public facade, re-export, documented import path, entry point, and deprecation policy together define API stability. A leading underscore or `internal` directory is only a signal.
- Plugins and applications need an actual discovery or registration mechanism, lifecycle, scope, and compatibility contract. A `plugins/` directory alone is not a plugin system.
- Django distinguishes framework package, project, reusable application, and management command. FastAPI's `APIRouter` organizes routes within one application; it does not imply a service or distribution boundary.
- CPython shows that a runtime feature may span Python source, native implementation, tests, docs, and platform build files. Feature alignment can be more useful than forcing everything into one package tree.

Useful primary references: [src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/), [pytest integration practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html), [FastAPI bigger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/), [CPython structure](https://github.com/python/cpython/blob/main/InternalDocs/structure.md).

## Cross-language cautions

- Ruff combines Rust implementation crates with Python distribution metadata; the Python import package, Rust workspace, wheel, and CLI are different objects.
- A protocol/schema can be the stable cross-language boundary while implementations remain in one repository or several repositories.
- Generated bindings are outputs of a source/build relation, not automatically public API or source of truth.
- A language-specific convention is transferable only when the current toolchain enforces the same relation. Do not copy names such as `cmd`, `internal`, `crates`, `src`, or `packages` as decoration.
