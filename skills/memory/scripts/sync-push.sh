#!/bin/bash
# Push memory summary to tracking Issue (append mode)
set -e

MEMORY_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.memory"
CONTEXT_FILE="$MEMORY_DIR/context.md"

# Marker comments for agent-managed section
START_MARKER="<!-- AGENT-MEMORY-START -->"
END_MARKER="<!-- AGENT-MEMORY-END -->"

detect_remote() {
  if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
    if git remote get-url origin 2>/dev/null | grep -qE "github|gh"; then
      echo "github"
      return
    fi
  fi
  if command -v glab &>/dev/null && glab auth status &>/dev/null 2>&1; then
    if git remote get-url origin 2>/dev/null | grep -q "gitlab"; then
      echo "gitlab"
      return
    fi
  fi
  echo "none"
}

if [ ! -f "$CONTEXT_FILE" ]; then
  echo "No context.md found. Run init.sh first."
  exit 1
fi

REMOTE=$(detect_remote)
if [ "$REMOTE" = "none" ]; then
  echo "No remote CLI available, skipping sync"
  exit 0
fi

# Extract tracking issue from frontmatter
TRACKING=$(grep "^tracking:" "$CONTEXT_FILE" | sed 's/tracking: *"\{0,1\}\([^"]*\)"\{0,1\}/\1/' | tr -d '#' | tr -d ' ')

if [ -z "$TRACKING" ]; then
  echo "No tracking issue configured in context.md"
  echo "To setup: create a tracking Issue and add 'tracking: \"#N\"' to frontmatter"
  exit 0
fi

# Validate tracking is numeric
if ! [[ "$TRACKING" =~ ^[0-9]+$ ]]; then
  echo "Invalid tracking issue format: $TRACKING (expected numeric)"
  exit 1
fi

echo "Syncing to $REMOTE tracking issue #$TRACKING..."

# Generate summary from context.md (extract content after frontmatter)
SUMMARY=$(awk '/^---$/{if(++c==2)found=1;next}found' "$CONTEXT_FILE")
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Build the agent-managed section
AGENT_SECTION="$START_MARKER
## Agent Memory Sync
_Last updated: $TIMESTAMP_

$SUMMARY
$END_MARKER"

# Get current issue body
case "$REMOTE" in
  github)
    CURRENT_BODY=$(gh issue view "$TRACKING" --json body -q '.body' 2>/dev/null || echo "")
    ;;
  gitlab)
    CURRENT_BODY=$(glab issue view "$TRACKING" -F json 2>/dev/null | jq -r '.description // ""' || echo "")
    ;;
esac

# Check if agent section exists
if echo "$CURRENT_BODY" | grep -q "$START_MARKER"; then
  # Replace existing agent section
  NEW_BODY=$(echo "$CURRENT_BODY" | awk -v new="$AGENT_SECTION" '
    /<!-- AGENT-MEMORY-START -->/{skip=1; print new; next}
    /<!-- AGENT-MEMORY-END -->/{skip=0; next}
    !skip{print}
  ')
else
  # Append agent section
  NEW_BODY="$CURRENT_BODY

$AGENT_SECTION"
fi

# Update the issue
case "$REMOTE" in
  github)
    echo "$NEW_BODY" | gh issue edit "$TRACKING" --body-file -
    echo "Updated GitHub issue #$TRACKING"
    ;;
  gitlab)
    echo "$NEW_BODY" | glab issue update "$TRACKING" --description "$(cat)"
    echo "Updated GitLab issue #$TRACKING"
    ;;
esac

# Update synced timestamp in context.md
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/^synced:.*/synced: $TIMESTAMP/" "$CONTEXT_FILE"
else
  sed -i "s/^synced:.*/synced: $TIMESTAMP/" "$CONTEXT_FILE"
fi

echo "Sync complete"
