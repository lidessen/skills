#!/bin/bash
# Pull Issue states from GitHub/GitLab into context.md
set -e

MEMORY_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.memory"
CONTEXT_FILE="$MEMORY_DIR/context.md"

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

gh_issue_info() {
  local num="${1#\#}"
  gh issue view "$num" --json number,title,state,assignees -q \
    '"- #\(.number) \(.title) - \(.state | ascii_downcase)\(if .assignees | length > 0 then " @" + (.assignees[0].login) else "" end)"' 2>/dev/null || echo "- #$num (fetch failed)"
}

glab_issue_info() {
  local num="${1#\#}"
  glab issue view "$num" -F json 2>/dev/null | jq -r \
    '"- #\(.iid) \(.title) - \(.state)\(if .assignee then " @" + .assignee.username else "" end)"' || echo "- #$num (fetch failed)"
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

# Extract active issues from frontmatter
ACTIVE=$(grep "^active_issues:" "$CONTEXT_FILE" | sed 's/active_issues: *\[\(.*\)\]/\1/' | tr -d '"' | tr -d "'" | tr ',' '\n' | tr -d ' ')

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "Syncing from $REMOTE..."

# Build new Active Work section
ACTIVE_WORK="## Active Work
<!-- Last sync: $TIMESTAMP -->"

for issue in $ACTIVE; do
  [ -z "$issue" ] && continue

  case "$REMOTE" in
    github)
      info=$(gh_issue_info "$issue")
      ;;
    gitlab)
      info=$(glab_issue_info "$issue")
      ;;
  esac
  ACTIVE_WORK="$ACTIVE_WORK
$info"
  echo "  $info"
done

# Update synced timestamp in frontmatter
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/^synced:.*/synced: $TIMESTAMP/" "$CONTEXT_FILE"
else
  sed -i "s/^synced:.*/synced: $TIMESTAMP/" "$CONTEXT_FILE"
fi

echo ""
echo "Active Work section to update in context.md:"
echo "$ACTIVE_WORK"
echo ""
echo "Sync complete - update context.md manually or use agent"
