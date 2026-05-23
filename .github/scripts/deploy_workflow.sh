#!/usr/bin/env bash
# Fan out the director-agent workflow, scripts, and skills to a project repo
# via a pull request on a feature branch. Never pushes to the default branch.
#
# Usage:
#   .github/scripts/deploy_workflow.sh <github_repo> [director_id]
#
# Example:
#   .github/scripts/deploy_workflow.sh dapp-controls/dCAD dcad
#
# What it does:
#   1. Detects the target repo's default branch (main vs master).
#   2. Clones it to a temp dir, creates a branch off the default.
#   3. Copies the workflow + scripts + .claude/skills/ into the clone.
#   4. Writes a tiny CLAUDE.md redirect ONLY if the target has no CLAUDE.md.
#   5. Commits, pushes the branch, opens a PR against the default branch.
#   6. Sets ANTHROPIC_API_KEY as an Actions secret (and reminds you about the SA).
#   7. Prints the dcli command to stamp github_repo on the director's Firestore record.
#
# Prerequisites:
#   - gh CLI authenticated with repo + workflow + secrets scope
#   - Run from the root of the director-pattern repo
#   - gcloud authenticated to dapp-controls-internal

set -euo pipefail

TARGET_REPO="${1:?Usage: deploy_workflow.sh <owner/repo> [director_id]}"
DIRECTOR_ID="${2:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Refuse to deploy if the root copies of agent_cli.py / firestore_db.py diverged from
# .github/scripts/. The vendored .github/scripts/ copies are what the cloud workflow uses;
# the root copies are what the local `dcli` shim uses. They MUST stay byte-identical.
for f in agent_cli.py firestore_db.py; do
  if ! cmp -s "$REPO_ROOT/$f" "$REPO_ROOT/.github/scripts/$f"; then
    echo "ERROR: $f differs between repo root and .github/scripts/." >&2
    echo "Run: cp $REPO_ROOT/$f $REPO_ROOT/.github/scripts/$f && git add and commit." >&2
    exit 1
  fi
done

# ── Detect target default branch ───────────────────────────────────────────────

DEFAULT_BRANCH=$(gh api "repos/$TARGET_REPO" --jq '.default_branch')
echo "Target: $TARGET_REPO (default branch: $DEFAULT_BRANCH)"

if [ -z "$DEFAULT_BRANCH" ] || [ "$DEFAULT_BRANCH" = "null" ]; then
  echo "ERROR: could not detect default branch for $TARGET_REPO" >&2
  exit 1
fi

# ── Clone to a temp dir ────────────────────────────────────────────────────────

WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

CLONE_DIR="$WORK_DIR/repo"
echo "Cloning $TARGET_REPO into $CLONE_DIR ..."
gh repo clone "$TARGET_REPO" "$CLONE_DIR" -- --depth=1 --branch="$DEFAULT_BRANCH" --quiet

cd "$CLONE_DIR"

BRANCH_NAME="chore/adopt-director-agent-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$BRANCH_NAME"

# ── Copy workflow + scripts ────────────────────────────────────────────────────

WORKFLOW_FILES=(
  ".github/workflows/director-agent.yml"
  ".github/scripts/fetch_context.py"
  ".github/scripts/post_reply.py"
  ".github/scripts/prepare_drafter_brief.py"
  ".github/scripts/post_drafter_steps.py"
  ".github/scripts/agent_cli.py"
  ".github/scripts/firestore_db.py"
)

for f in "${WORKFLOW_FILES[@]}"; do
  mkdir -p "$(dirname "$f")"
  cp "$REPO_ROOT/$f" "$f"
  echo "  staged: $f"
done

# ── Copy skills ────────────────────────────────────────────────────────────────

SKILL_FILES=(
  ".claude/skills/write-adr/SKILL.md"
  ".claude/skills/execute-adr/SKILL.md"
)

for f in "${SKILL_FILES[@]}"; do
  mkdir -p "$(dirname "$f")"
  cp "$REPO_ROOT/$f" "$f"
  echo "  staged: $f"
done

# Many consumer repos gitignore `.claude/` (Claude Code worktree state).
# Narrow it to `.claude/worktrees/` so skills are trackable. If the pattern
# isn't present, leave .gitignore alone.
if [ -f .gitignore ] && grep -qE '^\.claude/?\s*$' .gitignore; then
  # Use a portable sed in-place edit (works on GNU sed and BSD sed).
  python3 -c "
import re, sys
p = '.gitignore'
src = open(p).read()
new = re.sub(r'(?m)^\.claude/?\s*$', '.claude/worktrees/', src)
if new != src:
    open(p, 'w').write(new)
    print('  updated: .gitignore (.claude/ -> .claude/worktrees/)')
"
fi

# ── CLAUDE.md: write a redirect ONLY if target has none ────────────────────────

if [ ! -f "CLAUDE.md" ]; then
  cat > CLAUDE.md <<'CLAUDEMD_EOF'
# CLAUDE.md

This repo's developer documentation lives in [README.md](README.md). Read it first — it covers project purpose, build/load instructions, command catalog, project layout, and dependencies.

## Tooling preferences for agents

- Prefer `Read`, `Glob`, `Grep` over `Bash(cat|ls|find|grep)` — cheaper and structured.
- Make independent tool calls in **parallel** within a single message. Reading three files serially is three turns; reading them in one batch is one.
- For ADR drafting, use the `write-adr` skill. For ADR implementation, use the `execute-adr` skill. The skills encode the procedure and stop conditions — don't re-derive them.
- ADRs live under `docs/decisions/NNNN-slug.md`. Numbering is reserved atomically by the workflow's `prepare_drafter_brief.py` — never pick the next number by reading the folder.
CLAUDEMD_EOF
  echo "  staged: CLAUDE.md (redirect — none existed)"
else
  echo "  skipped: CLAUDE.md (target already has one)"
fi

# ── Commit, push, PR ───────────────────────────────────────────────────────────

git add -A
# Force-add skills in case .gitignore still excludes them on this run.
git add -f .claude/skills/ 2>/dev/null || true
if git diff --cached --quiet; then
  echo "Nothing to commit — target is already up to date."
  exit 0
fi

git -c user.email="agent-control@dapp-controls.com" \
    -c user.name="dAPP Controls Agent" \
    commit -m "chore: adopt director-agent workflow + ADR skills

Fans out from director-pattern:
- .github/workflows/director-agent.yml (Sonnet drafter, max-turns 10)
- .github/scripts/* (workflow runtime scripts)
- .claude/skills/write-adr/ (drafter procedure + stop conditions)
- .claude/skills/execute-adr/ (coder procedure + stop conditions)
- CLAUDE.md (redirect to README, only if missing)"

git push -u origin "$BRANCH_NAME" --quiet

PR_URL=$(gh pr create \
  --repo "$TARGET_REPO" \
  --base "$DEFAULT_BRANCH" \
  --head "$BRANCH_NAME" \
  --title "chore: adopt director-agent workflow + ADR skills" \
  --body "Fans out the updated director-agent workflow, runtime scripts, and ADR skills from \`dapp-controls/director-pattern\`. See that repo's PR #14 for full rationale and expected impact (20-turn ~\$1.50 runs → 5-8 turn ~\$0.15 runs).

## Changes

- \`.github/workflows/director-agent.yml\` — drafter switched from Opus to Sonnet, both heads at \`--max-turns 10\`, allowlist trimmed (\`Bash(cat *)\`/\`Bash(ls *)\` removed), prompts point at skills.
- \`.github/scripts/*\` — refreshed to current canonical versions in director-pattern.
- \`.claude/skills/write-adr/\` — drafter procedure, parallel-read pattern, stop conditions, expected 3-5 turns.
- \`.claude/skills/execute-adr/\` — coder procedure, scope discipline, board-update calls, expected 6-10 turns.
$( [ -f CLAUDE.md ] && grep -q 'redirect to README' CLAUDE.md 2>/dev/null && echo "- \`CLAUDE.md\` — one-page redirect to README + tooling preferences for agents (this repo had no CLAUDE.md before)." )

## Test plan

- [ ] Dispatch a drafter run (\"write an ADR for X\") via Cowork; confirm draft PR opens with the ADR file and turn count under 10.
- [ ] Dispatch a coder run (\"execute ADR N\") against an existing ADR; confirm implementation PR opens and board records story/task/mark-accepted.

Companion: dapp-controls/director-pattern#14")

echo "Opened PR: $PR_URL"

# ── Set GitHub Actions secrets ─────────────────────────────────────────────────

echo "Setting GitHub Actions secrets ..."

ANTHROPIC_KEY=$(gcloud secrets versions access latest \
  --secret=ANTHROPIC_API_KEY --project=dapp-controls-internal 2>/dev/null || echo "")

if [ -n "$ANTHROPIC_KEY" ]; then
  gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_KEY" --repo "$TARGET_REPO"
  echo "  set: ANTHROPIC_API_KEY"
else
  echo "  WARNING: could not fetch ANTHROPIC_API_KEY from gcloud — set manually"
fi

echo "  note: FIREBASE_SERVICE_ACCOUNT_JSON must be copied manually — GitHub does not expose secret values."
echo "  Run if needed: gcloud iam service-accounts keys create /tmp/sa.json --iam-account=agent-control@dapp-controls-internal.iam.gserviceaccount.com --project=dapp-controls-internal"
echo "                 gh secret set FIREBASE_SERVICE_ACCOUNT_JSON --body \"\$(cat /tmp/sa.json)\" --repo $TARGET_REPO"
echo "                 rm /tmp/sa.json"

# ── Print dcli stamp command ───────────────────────────────────────────────────

echo ""
echo "Done. PR: $PR_URL"
echo ""
echo "When ready, stamp the director's Firestore record:"
if [ -n "$DIRECTOR_ID" ]; then
  echo "  python agent_cli.py edit-director --director $DIRECTOR_ID --github-repo $TARGET_REPO"
fi
