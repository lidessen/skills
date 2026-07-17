# Verify an Agent Environment

Check whether the declared personal agent environment actually reaches each
tool and preserves its safety boundaries.

1. Fix the portable profile revision, target device, tool versions, ordinary
   entry paths, and expected observations. Verification does not modify the
   profile or accept its own findings.
2. Parse or use each tool's supported diagnostic surface to check configuration,
   instruction, skill/plugin, MCP/hook, permission, and authentication status.
   Redact values and do not infer successful loading from path presence alone.
3. Run one harmless ordinary-entry probe per tool that exercises a distinctive
   portable instruction or capability. Prefer built-in inspection commands;
   otherwise use a bounded prompt whose expected evidence is named in advance.
4. Run boundary probes: one target-local override remains effective, one
   excluded cache/session/memory item was not copied, and one unsupported
   cross-tool setting remains visible rather than silently translated.
5. Compare observations with the profile and reconciliation ledger. Classify
   every requirement as `supported`, `repair`, `manual`, `unsupported`, or
   `not-tested`; include the source and runtime evidence for that disposition.
6. Return the smallest repair for failed items and the event that should reopen
   verification, such as a tool upgrade, profile revision, device replacement,
   changed credential scope, or lost discovery path.

Do not report full success from syntax checks alone. At least one actual
instruction/capability observation and one preservation/exclusion observation
must come from the target environment.
