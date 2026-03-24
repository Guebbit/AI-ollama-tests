# 🛠️ CLI AI — Quick Commands, Scripts & Git Help

Two bash scripts that bring AI to your terminal. Ask questions, get shell
commands, generate commit messages, review code — all from the command line.

---

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `scripts/ai.sh` | General AI assistant — ask anything |
| `scripts/git-ai.sh` | Git workflows — commit, review, PR, explain |

Both scripts hit the Ollama API directly, stream the response token-by-token,
and exit. No server to start, no state to manage.

---

## Installation

```bash
# Make scripts executable
chmod +x scripts/ai.sh scripts/git-ai.sh

# Add global aliases (adjust the path to your project root)
sudo ln -sf "$(pwd)/scripts/ai.sh"     /usr/local/bin/ai
sudo ln -sf "$(pwd)/scripts/git-ai.sh" /usr/local/bin/git-ai
```

Or add to your `~/.bashrc` / `~/.zshrc`:

```bash
alias ai="$(pwd)/scripts/ai.sh"
alias git-ai="$(pwd)/scripts/git-ai.sh"
source ~/.bashrc
```

### Dependencies

```bash
# curl is usually pre-installed; jq is needed for JSON parsing
sudo apt install jq        # Debian/Ubuntu
brew install jq            # macOS
```

---

## `ai` — General Assistant

### Basic Usage

```bash
ai "what does find -name '*.js' do?"

ai "write a bash one-liner to find all TODO comments in .ts files"

ai "explain: what is a closure in JavaScript"   # longer explanation mode
```

### Pipe Input

The script reads from stdin if it's piped — great for combining with other tools:

```bash
# Explain an error message
npm run build 2>&1 | ai "explain this error"

# Summarize a file
cat src/auth.ts | ai "what does this code do?"

# Review a diff
git diff | ai "are there any bugs in these changes?"

# Explain a log file
tail -100 server.log | ai "what went wrong?"
```

### Environment Variables

```bash
# Use a different model for heavier questions
AI_MODEL=qwen3-coder-30b-safe ai "explain how React reconciliation works"

# If Ollama is on a different machine
AI_HOST=http://192.168.1.100:11434 ai "hello"
```

---

## `git-ai` — Git Assistant

### Commands

#### `commit` — Generate a Commit Message

```bash
git add -A
git-ai commit
```

Output example:
```
feat(auth): add JWT refresh token rotation

- Replace static tokens with rotating refresh tokens
- Add Redis-backed token blacklist
- Update middleware to validate token version
```

Follows the [Conventional Commits](https://www.conventionalcommits.org/) spec:
`feat`, `fix`, `refactor`, `docs`, `chore`, `test`, etc.

You can pipe the output directly to git:
```bash
git commit -m "$(git-ai commit)"
```

---

#### `review` — Code Review Before Committing

```bash
git add src/api.ts
git-ai review
```

Output example:
```
Issue 1: Line 42 — missing null check on `user.id` before database query
Issue 2: Line 87 — hardcoded localhost URL, should use an env variable
Looks clean otherwise.
```

Run this before every commit as a quick sanity check.

---

#### `explain` — Understand a Commit

```bash
git-ai explain           # Explain HEAD (last commit)
git-ai explain HEAD~3    # Explain 3 commits ago
git-ai explain abc1234   # Explain a specific SHA
```

Output example:
```
This commit adds JWT authentication to the API. It introduces a new
middleware that validates Bearer tokens on protected routes and rejects
requests with expired or invalid tokens. The user object is attached
to the request context for downstream handlers.
```

---

#### `pr` — Draft a Pull Request Description

```bash
git-ai pr              # Compare against 'main' (default)
git-ai pr develop      # Compare against 'develop'
```

Output example:
```
feat: add JWT authentication system

Changes:
- Add JWT middleware for route protection
- Implement token refresh endpoint
- Add token blacklist with Redis
- Update user model to include token version
- Add integration tests for auth flow
```

Ready to paste into GitHub/GitLab.

---

#### `log` — Summarize Recent History

```bash
git-ai log        # Summarize last 10 commits
git-ai log 20     # Summarize last 20 commits
```

Useful after coming back to a project or onboarding.

---

## The CLI Modelfile

`modelfiles/qwen3:4b/cli` — used by both scripts by default

Key settings:
- **temperature 0.15** — deterministic, no hallucinated commands
- **num_ctx 2048** — small context = fast responses
- **repeat_penalty 1.3** — keeps answers short and non-repetitive
- System prompt: 5 lines max, no markdown, no intros

For heavier analysis (code review, PR descriptions), override with the 30B model:
```bash
AI_MODEL_GIT=qwen3-coder-30b-safe git-ai review
```

---

## How It Works (Under the Hood)

```
 git diff --cached
       │
       ▼
 git-ai.sh builds a prompt
       │
       ▼
 curl → POST http://localhost:11434/api/generate
       │
       ▼
 Ollama streams JSON tokens
       │
       ▼
 jq extracts ".response" field per line
       │
       ▼
 printf to terminal (real-time streaming)
```

The Ollama `/api/generate` endpoint returns one JSON object per line when
streaming is enabled. Each object looks like:
```json
{"model":"qwen3-4b-cli","response":" hello","done":false}
```

We extract `.response` and print it immediately — no waiting for the full output.

---

## Troubleshooting

**`❌ Ollama is not running`**
```bash
docker-compose up -d ollama
# Wait a few seconds, then retry
```

**`❌ jq is required`**
```bash
sudo apt install jq
```

**`No staged changes`** (on `commit` / `review`)
```bash
git add -A    # Stage all changes
git add src/  # Or stage specific files
```

**Output is too verbose**
- The 4B model is already tuned for conciseness
- Add `explain:` prefix to your question for more detail
- Or remove the `explain:` prefix for even shorter answers
