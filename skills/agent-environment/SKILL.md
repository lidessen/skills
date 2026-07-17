---
name: agent-environment
description: >-
  Set up, audit, reconcile, verify, or migrate a person's user-level
  coding-agent environment across devices and tools such as Codex, Cursor, and
  Claude Code.
  Use for "set up my agents on this machine", "migrate my AI coding setup",
  "新设备配置 Codex/Cursor/Claude Code", "update my global agent workflow",
  "同步我的 agent skills and rules", or
  when personal instructions, skills, plugins, MCP servers, hooks, permissions,
  tool installation, and authentication prerequisites must be reconstructed or
  evolved safely. Do not use for project-local agent workflow design, fleet
  policy, copying sessions/caches, or ordinary dotfiles unrelated to agent work.
---

# Agent Environment

## Principle expression

**Primary:** P12
**Supporting:** P14, P16, P15

## Scope

Own one recurring judgment: **what minimum user-level workflow source lets this
person reconstruct and evolve the intended coding-agent capabilities and
working agreements across tools and devices, and how can each projection be
reconciled and verified without copying secrets, opaque state, or accidental
machine history?**

This Skill owns inventory classification, portable workflow-source formation,
three-way reconciliation, migration receipts, and ordinary-entry verification.
It does not own project instructions, provider accounts, secret storage, tool
implementation, organization policy, or the acceptance of a personal working
agreement. Use an existing dotfiles or configuration manager as the carrier
when one is already trusted; do not replace it with a new framework.

Read [concepts](references/concepts.md) when `desired source`, `projection`,
`secret prerequisite`, `local state`, or `override` are being conflated. Read
[current tool surfaces](references/tool-surfaces.md) only for tools in scope,
and re-check their official documentation before writing because vendor
surfaces change.

## Principle source

Use a host Sequence and matching interpretations when the host declares them.
Otherwise use this Skill's read-only fallback in `references/sequence.md`.
Read only P12, P14, P16, and P15.

## Dispatch

- With `audit`, read and follow `commands/audit.md`.
- With `setup`, read and follow `commands/setup.md`.
- With `reconcile`, read and follow `commands/reconcile.md`.
- With `migrate`, read and follow `commands/migrate.md`.
- With `verify`, read and follow `commands/verify.md`.
- With no argument, begin with a read-only audit. Do not infer authority to
  change user-level files from a request to inspect or recommend.

## Start

```text
Person, source device, and target device:
Tools and ordinary entry paths in scope:
Required capabilities and working agreements:
Existing portable source or dotfiles carrier:
Last applied source revision and receipt, if any:
Configuration that must remain machine-local:
Secret/authentication prerequisites, named but not read:
Target OS, shell, and trust constraints:
Human approval and rollback boundary:
Observation that would show successful reconstruction:
```

If the user has not authorized writes, stop after inventory and a proposed
reconciliation. Never print, copy, commit, or ask a model to summarize secret
values, authentication databases, session transcripts, caches, or machine
identifiers.

## Core method

1. **Recover intended work before files.** Name the tools, recurring actions,
   personal working agreements, capabilities, and verification observations.
   Do not treat every file under a vendor home directory as desired state.
2. **Inventory through supported surfaces.** Inspect installation provenance,
   versions, user instructions, skills/plugins, MCP and hook declarations,
   permission policy, and authentication *status*. Record paths and presence;
   redact values. Use official status or diagnostics commands when available.
3. **Classify every item.** Assign `desired source`, `tool projection`, `secret
   prerequisite`, `machine-local state`, `local override`, or `unknown`. Unknown
   and conflicting items block automatic copying; they do not become portable
   merely because they are readable.
4. **Select the smallest carrier.** Reuse an accepted dotfiles/configuration
   source when present. Otherwise prepare a small user-controlled,
   version-controlled profile from
   [the profile template](assets/environment-profile.md). Store workflow intent,
   source locators, install provenance, non-secret modules, projection mappings,
   exclusions, and verification—not vendor caches or an export of `$HOME`.
5. **Plan per tool from current documentation.** Read only the relevant section
   of [tool surfaces](references/tool-surfaces.md), then verify the current
   official path and precedence. Prefer a supported import, installer, settings
   command, or structural merge over editing undocumented application stores.
   If current documentation, runtime help, or diagnostics are unavailable, name
   the lookup/manual action; never invent an exact command or configuration key.
   Every exact command or key in a plan or receipt must carry the official page,
   inspected `--help`, or runtime diagnostic that admitted it in this activation.
   Words such as `example`, `equivalent`, or `likely` do not bypass this gate.
6. **Reconcile source evolution, not files alone.** For ongoing updates, compare
   the last applied source/projection, the target's current state, and the new
   approved source. Map changed workflow intent to affected tools before
   editing. A tool-local change is a target observation or candidate source
   change; it does not flow upstream without human adoption.
7. **Apply without taking ownership.** Back up or checkpoint each managed
   target; merge structured configuration by key; use clearly delimited blocks
   only for text projections; preserve unmanaged content byte-for-byte when the
   carrier promises that boundary. Do not replace a whole user configuration to
   make one setting match.
8. **Rehydrate secrets separately.** Retain only the credential's purpose,
   provider, required scope, preferred secure store, and status check. On the
   target device, use the tool's supported login or secret-manager path and let
   the human complete interactive authorization.
9. **Verify through ordinary entry paths.** Check parse/discovery, then run one
   harmless behavior or capability probe per tool. A copied file is not proof
   that the runtime loaded it. Preserve local overrides and one deliberately
   excluded history/cache item as boundary evidence.
10. **Return a reconciliation receipt.** Report applied, preserved, deferred,
   unsupported, and failed items; source revision; target/tool versions;
   rollback locations; manual authorization still required; and observations
   that should reopen the profile. The receipt is evidence, not a new source.
   Classify every mechanical action as `verified` or `lookup-required`; omit the
   command/key entirely for `lookup-required` actions.

## Ownership and routing

| Need | Owner |
|---|---|
| Personal cross-device agent workflow setup, evolution, and migration | this Skill |
| Agent behavior inside one repository | project `AGENTS.md`, `CLAUDE.md`, rules, or `improve-agent-workflow` |
| General shell/editor/package dotfiles | existing dotfiles or configuration-management method |
| Install or update portable agent skills | current skills installer or the tool's supported package path |
| Secret value, login, account, or provider authorization | human plus supported credential store/login flow |
| Organization-wide enforced policy | organization administrator and managed configuration |
| Tool-specific current configuration semantics | vendor documentation and runtime diagnostics |

## Boundaries

- Do not make one vendor's hidden directory the cross-tool source of truth.
- Do not migrate chats, sessions, memories, caches, telemetry, indexes, UI
  layout, or device identifiers by default. Promote a specific item only after
  the user names the future decision it must support and its privacy boundary.
- Do not translate every setting across tools. Preserve common intent where a
  faithful projection exists; otherwise retain an explicit tool-specific
  commitment or `unsupported` result.
- Do not make a generated tool configuration bidirectionally authoritative.
  Adopt a tool-local improvement into the workflow source explicitly, then
  project it outward in a later reconciliation.
- Do not bake current vendor paths or keys into universal doctrine. Re-check
  the linked official source during execution and record the observed version.
- Do not claim setup complete while authentication, an ordinary-entry probe,
  or an unresolved conflict remains hidden.
- Do not require Codex, Cursor, Claude Code, a particular OS, a dotfiles
  manager, or this repository after the Skill is installed.

## Completion standard

An environment setup, update, or migration is ready only when the portable
workflow source and its human owner are explicit, every in-scope item has a
state classification, source and target drift are distinguished, secrets and
local state remain outside the portable source, existing target content has a
rollback path, each tool passes an ordinary-entry verification or is visibly
deferred, and the receipt states residual manual work. A profile that cannot be
updated without copying opaque vendor state or overwriting target differences
is not yet a portable environment.
