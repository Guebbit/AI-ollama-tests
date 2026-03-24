#!/usr/bin/env bash
# =============================================================================
# git-ai — AI-powered Git assistant
# =============================================================================
#
# Wraps common git workflows with AI so you spend less time writing boilerplate
# and more time shipping. All commands read from your actual git repo state and
# pass the relevant diff/log to the AI model.
#
# COMMANDS
#   git-ai commit    Generate a conventional commit message from staged changes
#   git-ai review    Review staged changes for bugs or issues
#   git-ai explain   Explain what the last commit (or a given SHA) does
#   git-ai pr        Draft a Pull Request description from recent commits
#   git-ai log       Summarize recent git history in plain English
#
# EXAMPLES
#   git add -A && git-ai commit     # Stage everything, then generate message
#   git-ai review                   # Get a code review before you commit
#   git-ai explain HEAD~3           # Explain a specific commit
#   git-ai pr main                  # PR description against the main branch
#   git-ai log 20                   # Summarize last 20 commits
#
# DEPENDENCIES
#   curl, jq  — same as ai.sh
#
# ENVIRONMENT VARIABLES
#   AI_MODEL_GIT   Model to use (default: qwen3-4b-cli)
#   AI_HOST        Ollama host URL (default: http://localhost:11434)
#
# SETUP
#   chmod +x scripts/git-ai.sh
#   sudo ln -sf "$(pwd)/scripts/git-ai.sh" /usr/local/bin/git-ai
# =============================================================================

set -euo pipefail

MODEL="${AI_MODEL_GIT:-qwen3-4b-cli}"
HOST="${AI_HOST:-http://localhost:11434}"
ENDPOINT="$HOST/api/generate"

# --------------- Helpers ------------------------------------------------------

check_ollama() {
    if ! curl -sf "$HOST/api/tags" > /dev/null 2>&1; then
        echo "❌  Ollama is not running at $HOST" >&2
        echo "    Start it with: docker-compose up -d ollama" >&2
        exit 1
    fi
}

check_deps() {
    if ! command -v jq &> /dev/null; then
        echo "❌  jq is required. Install with: sudo apt install jq" >&2
        exit 1
    fi
}

check_git() {
    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        echo "❌  Not inside a git repository" >&2
        exit 1
    fi
}

# Send a prompt to the model and stream back the response.
query() {
    local prompt="$1"

    local payload
    payload=$(jq -n \
        --arg model "$MODEL" \
        --arg prompt "$prompt" \
        '{model: $model, prompt: $prompt, stream: true}')

    curl -sf -X POST "$ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$payload" | \
        while IFS= read -r line; do
            token=$(printf '%s' "$line" | jq -r '.response // empty')
            printf '%s' "$token"
        done

    echo
}

# --------------- Commands -----------------------------------------------------

# Generate a commit message following the Conventional Commits spec:
#   https://www.conventionalcommits.org/
#
# The model sees the full staged diff (same as `git diff --cached`).
# It outputs only the commit message — you can copy-paste or pipe it.
cmd_commit() {
    local diff
    diff=$(git diff --cached)

    if [ -z "$diff" ]; then
        echo "No staged changes. Stage files first with: git add <files>"
        exit 1
    fi

    echo "⏳  Generating commit message..."
    echo ""
    query "Write a git commit message in Conventional Commits format for the diff below.
Output ONLY the commit message — no explanation, no markdown, just the message.
Keep the subject line under 72 characters.

$diff"
}

# Review staged changes before committing.
# Useful as a quick sanity check: obvious bugs, forgotten debug logs, etc.
cmd_review() {
    local diff
    diff=$(git diff --cached)

    if [ -z "$diff" ]; then
        echo "No staged changes. Stage files first with: git add <files>"
        exit 1
    fi

    echo "🔍  Reviewing staged changes..."
    echo ""
    query "You are a code reviewer. Review this git diff for bugs, security issues,
or obvious mistakes. List only real problems — skip style nitpicks unless severe.
Be concise. If everything looks fine, say so in one sentence.

$diff"
}

# Explain what a commit does in plain English.
# Defaults to HEAD; accepts any git ref as argument.
cmd_explain() {
    local commit="${1:-HEAD}"
    local diff
    diff=$(git show "$commit" --stat --patch 2>/dev/null) || {
        echo "❌  Could not find commit: $commit"
        exit 1
    }

    echo "💬  Explaining commit $commit..."
    echo ""
    query "Explain what this git commit does in 2-3 sentences of plain English.
Focus on the intent and impact, not the syntax of the diff.

$diff"
}

# Draft a Pull Request description based on commits between HEAD and a base branch.
# Shows a title + bullet points of changes — ready to paste into GitHub/GitLab.
cmd_pr() {
    local base="${1:-main}"
    local commits
    local diff_stat

    # Try to get commits relative to base branch; fall back to last 10 commits.
    commits=$(git log "$base"..HEAD --oneline 2>/dev/null) || \
    commits=$(git log --oneline -10)

    diff_stat=$(git diff "$base" --stat 2>/dev/null) || \
    diff_stat=$(git diff --stat HEAD~5 2>/dev/null) || \
    diff_stat="(could not compute diff stat)"

    if [ -z "$commits" ]; then
        echo "No commits found between $base and HEAD."
        exit 1
    fi

    echo "📝  Drafting PR description vs $base..."
    echo ""
    query "Write a Pull Request description for these changes.
Format: one-line title, then bullet points of what changed.
Be concise — this is for developers who will review the code.

Commits:
$commits

File changes:
$diff_stat"
}

# Summarize recent git history in plain English.
# Useful for onboarding or remembering what you were working on.
cmd_log() {
    local n="${1:-10}"
    local log
    log=$(git log --oneline -"$n")

    echo "📜  Summarizing last $n commits..."
    echo ""
    query "Summarize this git history in plain English.
One sentence per logical group of changes. Skip merge commits.
Output should read like a changelog.

$log"
}

# --------------- Main ---------------------------------------------------------

check_deps
check_ollama
check_git

COMMAND="${1:-help}"
shift 2>/dev/null || true

case "$COMMAND" in
    commit)   cmd_commit ;;
    review)   cmd_review ;;
    explain)  cmd_explain "$@" ;;
    pr)       cmd_pr "$@" ;;
    log)      cmd_log "$@" ;;
    help|*)
        echo "git-ai — AI-powered Git assistant"
        echo ""
        echo "Commands:"
        echo "  commit           Generate commit message from staged changes"
        echo "  review           Review staged changes for bugs/issues"
        echo "  explain [sha]    Explain a commit in plain English (default: HEAD)"
        echo "  pr [base]        Draft PR description (default base: main)"
        echo "  log [n]          Summarize last n commits (default: 10)"
        echo ""
        echo "Examples:"
        echo "  git add -A && git-ai commit"
        echo "  git-ai review"
        echo "  git-ai explain HEAD~2"
        echo "  git-ai pr develop"
        echo "  git-ai log 20"
        ;;
esac
