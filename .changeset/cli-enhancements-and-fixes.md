---
"agent-worker": minor
---

CLI enhancements and stability improvements:

**Observability & Developer Experience:**
- **Enhanced CLI Observability**: Improved help text and better debugging experience
- **JSON Output Support**: Added JSON output support for better programmatic usage and integration
- **Dual Display Modes**: Normal (timeline) vs debug (standard log) for better workflow output visibility
- **Adaptive Layout**: Enhanced workflow output with smart formatting including dot indicators with `HH:MM:SS` timestamps
- **Improved Debug Output**: Better formatting for tool calls with unified format and text labels
- **Inbox Seen State**: Added inbox seen state and tool call logging in debug output
- **System Logs in Channel**: System log messages now appear in channel and `peek` output

**New Providers & Capabilities:**
- **Minimax CN Provider**: Added `minimax_cn` provider with dedicated `MINIMAX_CN_API_KEY` environment variable support
- **Scheduled Wakeup**: Agent sessions can now be scheduled to wake up at specific times using cron expressions
- **Project-local Context**: Support for project-local context directories via `--context-dir` flag

**Performance Improvements:**
- **Incremental Channel Reads**: Optimized channel reading with incremental sync via `StorageBackend.readFrom`

**Bug Fixes:**

_Runtime Isolation:_
- Fixed cross-run message leakage with `markRunStart()` preventing messages from previous runs
- Fixed channel watcher replaying previous run entries incorrectly
- Eliminated duplicate `DONE`/`ERROR` logs by having runners return data while controller logs once

_Display Issues:_
- Removed 500-character truncation limit on agent messages for full output visibility
- Fixed syntax error in template string escaping for esbuild (`${{ }}`)

_Compatibility & SDK Integration:_
- Renamed `parameters` to `inputSchema` to align with AI SDK v6
- Fixed SDK/mock runners to use actual MCP tool schemas instead of synthetic ones
- Null-safe `onStepFinish` callback in SDK runner
- Suppressed AI SDK warnings in normal mode, showing errors only

_Configuration & Validation:_
- Fixed default context directory to use global `~/.agent-worker/contexts/`
- Added upfront validation for cron field parsing with improved error messages
- Addressed review findings for feedback tool reliability

**Error Messaging:**
- Better error messages with `statusCode`, `url`, and `body` extraction from AI SDK errors
