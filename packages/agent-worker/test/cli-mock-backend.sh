#!/bin/bash
# CLI integration test with mock AI backend
#
# Tests the full CLI workflow execution:
#   agent-worker run workflow.yaml --debug
#
# Uses `backend: mock` which runs MockLanguageModelV3 + real MCP tools.
# No real LLM API calls needed.

set -euo pipefail

# ==================== Setup ====================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FIXTURE="$SCRIPT_DIR/fixtures/mock-workflow.yaml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
DIM='\033[2m'
NC='\033[0m'

PASS=0
FAIL=0
OUTPUT_DIR=$(mktemp -d)
trap "rm -rf $OUTPUT_DIR" EXIT

pass() {
  echo -e "  ${GREEN}✓${NC} $1"
  PASS=$((PASS + 1))
}

fail() {
  echo -e "  ${RED}✗${NC} $1"
  if [ -n "${2:-}" ]; then
    echo -e "    ${DIM}$2${NC}"
  fi
  FAIL=$((FAIL + 1))
}

# ==================== Test 1: Workflow completes with mock backend ====================

echo ""
echo "Test 1: Workflow execution with mock backend"
echo "─────────────────────────────────────────────"

OUTPUT="$OUTPUT_DIR/test1.txt"

cd "$PACKAGE_DIR"
if timeout 60 npx tsx src/cli/index.ts run "$FIXTURE" --debug > "$OUTPUT" 2>&1; then
  pass "Exit code 0"
else
  EXIT_CODE=$?
  fail "Exit code $EXIT_CODE" "$(tail -5 "$OUTPUT" 2>/dev/null)"
fi

# Check workflow reached completion (idle detection)
if grep -qi "workflow complete\|all agents idle" "$OUTPUT" 2>/dev/null; then
  pass "Workflow reached idle/complete state"
else
  fail "Workflow did not reach idle state" "$(grep -i 'idle\|complete\|error' "$OUTPUT" 2>/dev/null | tail -3)"
fi

# Check MCP connection established for both agents
if grep -q "MCP connected" "$OUTPUT" 2>/dev/null; then
  pass "Mock backend connected to MCP server"
else
  fail "No MCP connection logs found"
fi

# Check both agents were invoked
if grep -q "\[alice\]" "$OUTPUT" 2>/dev/null; then
  pass "Agent alice was invoked"
else
  fail "Agent alice was not invoked"
fi

if grep -q "\[bob\]" "$OUTPUT" 2>/dev/null; then
  pass "Agent bob was invoked"
else
  fail "Agent bob was not invoked"
fi

# Check MCP tool calls (channel_send) were executed
if grep -qi "channel_send\|Processed:" "$OUTPUT" 2>/dev/null; then
  pass "MCP channel_send tool was called"
else
  fail "No channel_send tool call detected"
fi

# Check prompts contained inbox messages
if grep -q "Inbox.*message" "$OUTPUT" 2>/dev/null; then
  pass "Agents received inbox messages in prompt"
else
  fail "No inbox messages in agent prompts"
fi

# ==================== Test 2: Verbose mode output ====================

echo ""
echo "Test 2: Verbose mode output"
echo "───────────────────────────"

OUTPUT="$OUTPUT_DIR/test2.txt"

if timeout 60 npx tsx src/cli/index.ts run "$FIXTURE" --verbose > "$OUTPUT" 2>&1; then
  pass "Exit code 0 (verbose)"
else
  fail "Exit code non-zero (verbose)"
fi

# Channel messages should be visible in non-debug mode
if grep -q "alice\|bob" "$OUTPUT" 2>/dev/null; then
  pass "Agent activity visible in verbose output"
else
  fail "No agent activity in verbose output"
fi

# ==================== Test 3: Default mode (no flags) ====================

echo ""
echo "Test 3: Default mode (no flags)"
echo "────────────────────────────────"

OUTPUT="$OUTPUT_DIR/test3.txt"

if timeout 60 npx tsx src/cli/index.ts run "$FIXTURE" > "$OUTPUT" 2>&1; then
  pass "Exit code 0 (default mode)"
else
  fail "Exit code non-zero (default mode)"
fi

# Should show workflow name
if grep -q "mock-test\|Running workflow" "$OUTPUT" 2>/dev/null; then
  pass "Workflow header displayed"
else
  fail "No workflow header in output"
fi

# ==================== Summary ====================

echo ""
echo "════════════════════════════════"
TOTAL=$((PASS + FAIL))
echo -e "  Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC} / $TOTAL total"

if [ $FAIL -gt 0 ]; then
  echo ""
  echo -e "  ${YELLOW}Debug output saved to: $OUTPUT_DIR/${NC}"
  # Don't delete output dir on failure
  trap - EXIT
  exit 1
else
  echo -e "  ${GREEN}All tests passed!${NC}"
fi
echo "════════════════════════════════"
echo ""
