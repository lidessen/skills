# Set Up an Agent Environment

Establish an authorized user-level coding-agent environment on one device.

1. Recover required working agreements, capabilities, tools, installation
   preferences, trust boundaries, and acceptance observations. If the request
   only names products, ask or infer conservatively; do not import every feature
   from another machine.
2. Audit the current device without reading secrets or opaque application
   stores. Reuse a trusted dotfiles/configuration source if it already owns the
   relevant files. Otherwise copy `assets/environment-profile.md` into a
   user-approved version-controlled location and fill only the sections needed
   now. Keep device-specific receipts outside the shared desired source.
3. Separate portable source, tool projections, secret prerequisites,
   machine-local state, and local overrides. Obtain human confirmation of the
   profile before destructive replacement or before promoting an existing
   machine artifact into portable source.
4. Read the in-scope sections of `references/tool-surfaces.md` and verify the
   current vendor documentation. Use supported installers, import flows,
   settings commands, and global skill installation where they preserve the
   intended boundary.
5. Before each write, retain a rollback copy or version-control checkpoint.
   Merge structured configuration by key and text projections by an explicit
   owned block. Preserve unrelated target content. Stop on ambiguous duplicate
   owners, invalid syntax, or a target changed since inspection.
6. Name authentication and secret requirements in the profile without values.
   Let the human complete supported login or secret-manager steps; record only
   status and scope after completion.
7. Verify each tool through its ordinary entry path, including one distinctive
   instruction or capability and one preserved/excluded boundary. Record
   unsupported and deferred items rather than weakening acceptance silently.
8. Write a migration/setup receipt alongside the chosen profile or return it in
   chat when no durable carrier was authorized. Include source revision,
   observed versions, applied and preserved items, rollback paths, manual work,
   and reopening signals.

Setup is incomplete when a file exists but the runtime has not loaded it, or
when an interactive authorization remains necessary but is not visible in the
receipt.
