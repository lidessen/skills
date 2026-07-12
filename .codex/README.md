# Codex hook binding

This directory is a **local Codex projection** of the portable
intervention-reconciliation contract in
[Decision 024](../design/decisions/024-platform-neutral-intervention-reconciliation.md).
It is not part of the portable method and must be checked against current Codex
documentation when it changes.

## Effective guarantee

**Shadow / assist only.** `UserPromptSubmit` records a privacy-preserving
prompt observation and injects a reminder for the agent to compare a Principal
message with its active task. It does not decide that a correction occurred,
block writes, or accept work.

State is session-local under `~/.codex/intervention-reconciliation/`. It stores
the prompt hash and byte count, never prompt text. The generic state CLI and
receipt format live in [`scripts/intervention-reconciliation.py`](../scripts/intervention-reconciliation.py).

## Enable and verify in a fresh Codex session

1. Start Codex in this repository and use `/hooks` to inspect and trust the
   project hook. Do not use a trust-bypass flag: hook review is part of the
   binding's safety boundary.
2. Send an ordinary task message. It should create an observation but no
   correction receipt.
3. Send a material correction. The agent must compare it with the active task;
   if it changes a target, hard boundary, concept relation, authority, or
   acceptance condition, it records a receipt before claiming a mutation
   implements the correction.
4. Inspect the resulting state:

   ```sh
   INTERVENTION_RECONCILIATION_STATE_DIR="$HOME/.codex/intervention-reconciliation" \
     python3 scripts/intervention-reconciliation.py status --cwd "$PWD"
   ```

   The state root used by the Codex adapter is
   `~/.codex/intervention-reconciliation`; the command above selects it for the
   generic CLI.

The current lifecycle names, command-handler limitation, and project-hook
trust model come from the [Codex Hooks guide](https://learn.chatgpt.com/docs/hooks)
and [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference),
checked on 2026-07-12. Re-check those sources before adding a mutation gate or
stop continuation.
