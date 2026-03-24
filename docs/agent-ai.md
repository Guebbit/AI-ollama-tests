# 🤖 Agent AI — Multi-Step Task Automation

The agent takes a high-level goal and breaks it into concrete, numbered steps —
then works through them one by one, keeping the full context of everything it
has done so far.

Think of it as your ADHD-friendly project manager: you describe the *what*,
it figures out the *how*, and shows you exactly where it is at every step.

---

## How It Works

```
You  ──task──▶  PLAN phase
                  │
                  ▼ (numbered steps)
               EXECUTE phase  ◀── loops through steps ──▶  output per step
                  │
                  ▼
               DONE — summary of what was accomplished
```

Each step builds on the previous ones. The model receives the full conversation
history at every step, so it always knows what has already been done.

---

## Setup

```bash
# Python 3.8+ is required (no extra packages needed — uses stdlib only)
python3 --version

# Make it executable
chmod +x scripts/agent.py

# Optional: global alias
sudo ln -sf "$(pwd)/scripts/agent.py" /usr/local/bin/agent
```

---

## Usage

### Basic

```bash
python3 scripts/agent.py "refactor the auth module to use JWT"
python3 scripts/agent.py "write unit tests for UserService"
python3 scripts/agent.py "set up ESLint and Prettier for this project"
```

### Interactive Mode

Run without arguments to get prompted:

```bash
python3 scripts/agent.py
# > What do you want to accomplish? set up CI/CD for a Node.js app
```

### Options

```bash
# Use a specific model
python3 scripts/agent.py --model qwen3-coder-30b-safe "add TypeScript to this project"

# Limit the number of steps (default: 8)
python3 scripts/agent.py --steps 5 "migrate database schema"

# Use a remote Ollama instance
python3 scripts/agent.py --host http://192.168.1.100:11434 "fix the auth bug"
```

---

## Example Session

```
$ python3 scripts/agent.py "add input validation to the Express API"

============================================================
🎯  TASK: add input validation to the Express API
============================================================

📋  PLANNING...

PLAN
1. Identify all Express route handlers that accept user input
2. Choose a validation library (zod or express-validator)
3. Install the library and add it to package.json
4. Add validation schemas for each route's expected input
5. Add error handler middleware for validation failures
6. Test each endpoint with invalid input to verify

✅  6 steps identified

------------------------------------------------------------
🔧  STEP 1/6: Identify all Express route handlers that accept user input
------------------------------------------------------------
CMD: grep -rn "req.body\|req.params\|req.query" src/routes/

Found handlers in:
- src/routes/auth.ts (lines 12, 34, 67)
- src/routes/users.ts (lines 8, 23)
- src/routes/products.ts (lines 15, 44, 89)

------------------------------------------------------------
🔧  STEP 2/6: Choose a validation library
------------------------------------------------------------
Recommended: zod — TypeScript-first, excellent inference, composable schemas.

...

============================================================
✨  DONE — Summary
============================================================
Added zod validation to all Express routes. Created validation schemas
in src/schemas/. Added error handler middleware in src/middleware/validation.ts.
Next: run the test suite to catch any type mismatches.
```

---

## Understanding the Output

Each step is clearly marked so you always know where you are:

| Prefix | Meaning |
|--------|---------|
| `CMD: <command>` | A shell command you should run |
| `FILE: <path>` | A file the agent wants to create or modify |
| `ASK: <question>` | The agent needs your input before continuing |
| Plain text | An explanation or analysis |

The agent does **not** execute commands automatically — it describes what to do
and you execute the steps. This keeps you in control while eliminating the
mental overhead of figuring out the steps yourself.

---

## The Agent Modelfile

`modelfiles/qwen3-coder:30b/agent` — structured planner + executor

Key settings:
- **temperature 0.3** — enough creativity to plan well, grounded enough to stay correct
- **num_ctx 16384** — large context so it tracks the full task history
- **repeat_penalty 1.2** — prevents the model from re-listing steps it already covered

System prompt enforces the PLAN → EXECUTE → VERIFY → DONE structure so the
output is always scannable.

---

## Tips for ADHD Workflows

**Be specific in your task description**
```bash
# ❌ Too vague
python3 scripts/agent.py "fix the bug"

# ✅ Clear and actionable
python3 scripts/agent.py "fix the 404 error on /api/users/:id when user doesn't exist"
```

**Limit steps for quick tasks**
```bash
python3 scripts/agent.py --steps 3 "add a README badge for CI status"
```

**Chain with git-ai when done**
```bash
# After the agent finishes, commit with an AI-generated message
git add -A && git-ai commit
```

**Use for onboarding new codebases**
```bash
python3 scripts/agent.py "explore this codebase and explain the architecture"
```

---

## How Context Works (Why It Remembers Things)

LLMs are stateless — each API call starts fresh. The agent simulates memory
by passing the *entire conversation history* to every request:

```
Turn 1:  [user: plan request]         → model returns: plan
Turn 2:  [user: plan], [ai: plan],    → model returns: step 1 result
         [user: execute step 1]
Turn 3:  [user: plan], [ai: plan],    → model returns: step 2 result
         [user: step 1], [ai: result],
         [user: execute step 2]
...
```

This is why context window size matters (`num_ctx 16384`). If the task gets
very long and hits the limit, earlier context is truncated. Keep tasks focused
to stay within the window.

---

## Troubleshooting

**`❌ Ollama is not running`**
```bash
docker-compose up -d ollama
```

**Plan parsing fails**
- The model sometimes formats plans differently. Try rephrasing your task
  more concretely: "list the steps to ..." instead of vague requests.

**Steps take too long**
- The 30B model is powerful but slower. For simpler tasks, switch to 4B:
  ```bash
  python3 scripts/agent.py --model qwen3-4b-balanced "your task"
  ```

**Model hallucinates file paths**
- The agent works best on tasks where file structure can be inferred from
  context. Add file paths to your task description:
  ```bash
  python3 scripts/agent.py "add tests to src/services/auth.ts"
  ```
