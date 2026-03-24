#!/usr/bin/env bash
# =============================================================================
# ai — Quick AI assistant from the terminal
# =============================================================================
#
# This script sends a prompt to Ollama and streams the response back to your
# terminal. It uses the `qwen3-4b-cli` model by default — a small, fast model
# tuned to give short, terminal-friendly answers.
#
# HOW IT WORKS
# ┌──────────────────────────────────────────────────────────────────┐
# │  You  ──prompt──▶  ai.sh  ──JSON──▶  Ollama API  ──stream──▶  You │
# └──────────────────────────────────────────────────────────────────┘
# Ollama streams back one JSON object per token; we extract the "response"
# field from each and print it immediately, so you see output as it types.
#
# USAGE
#   ai "what does find -name '*.js' do?"
#   ai "write a bash one-liner to count lines in all .ts files"
#   ai "explain:" "what is a closure in JavaScript"   # longer explanation
#   echo "SyntaxError: unexpected token" | ai "what does this error mean?"
#   git diff | ai "summarize these changes in plain English"
#
# DEPENDENCIES
#   curl   — HTTP requests to Ollama
#   jq     — JSON parsing (install with: sudo apt install jq)
#
# ENVIRONMENT VARIABLES
#   AI_MODEL   Model to use (default: qwen3-4b-cli)
#   AI_HOST    Ollama host URL (default: http://localhost:11434)
#
# SETUP
#   chmod +x scripts/ai.sh
#   sudo ln -sf "$(pwd)/scripts/ai.sh" /usr/local/bin/ai   # global alias
# =============================================================================

set -euo pipefail

# --------------- Configuration -----------------------------------------------
MODEL="${AI_MODEL:-qwen3-4b-cli}"
HOST="${AI_HOST:-http://localhost:11434}"
ENDPOINT="$HOST/api/generate"

# --------------- Helpers ------------------------------------------------------

# Verify Ollama is reachable before trying to send a request.
# This gives a human-readable error instead of a cryptic curl failure.
check_ollama() {
    if ! curl -sf "$HOST/api/tags" > /dev/null 2>&1; then
        echo "❌  Ollama is not running at $HOST" >&2
        echo "    Start it with: docker-compose up -d ollama" >&2
        exit 1
    fi
}

# Verify jq is installed (required for JSON handling).
check_deps() {
    if ! command -v jq &> /dev/null; then
        echo "❌  jq is required. Install with: sudo apt install jq" >&2
        exit 1
    fi
}

# Send a prompt to Ollama and stream the response token-by-token.
#
# Ollama's streaming API returns one JSON object per line, like:
#   {"model":"...","response":"Hello","done":false}
#   {"model":"...","response":" world","done":false}
#   {"model":"...","response":"","done":true}
#
# We extract the "response" field from each line and print it immediately.
query() {
    local prompt="$1"

    # jq -n builds a JSON object safely, handling special characters in the prompt.
    local payload
    payload=$(jq -n \
        --arg model "$MODEL" \
        --arg prompt "$prompt" \
        '{model: $model, prompt: $prompt, stream: true}')

    curl -sf -X POST "$ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$payload" | \
        while IFS= read -r line; do
            # Extract just the text token; skip empty lines and done markers
            token=$(printf '%s' "$line" | jq -r '.response // empty')
            printf '%s' "$token"
        done

    echo  # Newline after streamed output
}

# --------------- Main ---------------------------------------------------------

check_deps
check_ollama

PROMPT=""

# If stdin is piped (e.g., `echo "error" | ai "explain"`), read it first.
# This allows composing AI with other Unix tools naturally.
if [ ! -t 0 ]; then
    STDIN=$(cat)
    PROMPT="$STDIN"$'\n\n'
fi

# Append any CLI arguments as the actual question.
if [ "$#" -gt 0 ]; then
    PROMPT+="$*"
fi

if [ -z "$PROMPT" ]; then
    echo "Usage: ai \"your question\""
    echo "       echo 'some text' | ai 'what does this mean?'"
    exit 1
fi

query "$PROMPT"
