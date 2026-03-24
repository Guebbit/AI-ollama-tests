# 🖊️ Editor AI — Autocomplete + Chat in VS Code

Your IDE becomes your coding partner. This guide sets up **Continue.dev** to
use your local Ollama models for autocomplete and chat — no cloud, no API keys,
no subscription.

---

## What You Get

| Feature | Shortcut | Model Used |
|---------|----------|-----------|
| Inline autocomplete | `Tab` to accept | `qwen3-coder-30b-editor` |
| Chat panel (ask anything) | `Ctrl+L` / `Cmd+L` | `qwen3-coder-30b-safe` |
| Edit selected code | `Ctrl+I` / `Cmd+I` | `qwen3-coder-30b-safe` |
| Codebase search | `@Codebase` in chat | `nomic-embed-text` |
| Quick question | Chat with 4B model | `qwen3-4b-balanced` |

---

## Step 1 — Install the Extension

1. Open VS Code
2. Press `Ctrl+Shift+X` (Extensions)
3. Search for **Continue**
4. Click **Install**

Or install via CLI:
```bash
code --install-extension continue.continue
```

---

## Step 2 — Copy the Config

Continue stores its config at `~/.continue/config.json` on your system.

```bash
# Copy the project config to your home directory
cp .continue/config.json ~/.continue/config.json
```

Or symlink it so edits in the repo automatically take effect:
```bash
mkdir -p ~/.continue
ln -sf "$(pwd)/.continue/config.json" ~/.continue/config.json
```

---

## Step 3 — Make Sure the Models Are Running

The Docker stack must be running, and the custom models must be created:

```bash
docker-compose up -d

# Wait for model-loader to finish (check logs)
docker-compose logs -f model-loader
```

Verify the models exist:
```bash
curl http://localhost:11434/api/tags | jq '.models[].name'
# Should include: qwen3-coder-30b-editor, qwen3-coder-30b-safe, qwen3-4b-balanced
```

---

## Step 4 — (Optional) Set Up Codebase Search

To use `@Codebase` in chat (semantic search over your whole project):

```bash
# Pull the embedding model
docker exec -it <ollama-container> ollama pull nomic-embed-text
```

Then in VS Code:
1. Open Continue sidebar (`Ctrl+Shift+L`)
2. Click the settings icon
3. Enable "Use embeddings"
4. Type `@Codebase` in chat to index and search your project

---

## How to Use It — Daily Workflow

### Autocomplete

Just start typing — Continue shows a grey ghost suggestion inline.

```javascript
// Type this:
function calculateTax(price,

// Continue suggests:
function calculateTax(price, rate) {
  return price * rate;
}
```

- **Accept:** `Tab`
- **Dismiss:** `Escape`
- **Next suggestion:** `Alt+]`

### Chat (Ctrl+L)

Select code, press `Ctrl+L`, and ask:

```
> What does this function do?
> Refactor this to use async/await
> Add error handling to this
> Write unit tests for this
```

### Edit in Place (Ctrl+I)

Select code → `Ctrl+I` → describe the change:

```
> Extract this into a separate function
> Convert to TypeScript
> Add JSDoc comments
```

### Context References

In chat, prefix with `@` to attach context:

```
@file src/auth.ts  — explain how authentication works
@folder src/api    — what endpoints are exposed?
@terminal          — explain this error
@problems          — fix these TypeScript errors
```

---

## Keyboard Shortcuts Cheat Sheet

```
Ctrl+L       Open chat panel
Ctrl+Shift+L Open Continue sidebar
Ctrl+I       Edit selected code inline
Tab          Accept autocomplete suggestion
Escape       Dismiss autocomplete / Close chat
Alt+]        Cycle to next autocomplete suggestion
```

---

## The Editor Modelfile

`modelfiles/qwen3-coder:30b/editor` — used for autocomplete

Key settings:
- **temperature 0.1** — very deterministic, no "creative" surprises in your code
- **num_ctx 16384** — sees enough surrounding context to make smart completions
- **top_k 20** — picks from only the most likely tokens (fast + accurate)
- System prompt tells it to output raw code only (no markdown wrapping)

---

## Troubleshooting

**Autocomplete is slow or not appearing**
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- The 30B model needs a GPU with enough VRAM. Try swapping to `qwen3-4b-cli`
  in the `tabAutocompleteModel` section of `~/.continue/config.json`

**"Model not found" error**
- Run `docker-compose up -d` and wait for `model-loader` to finish
- Check: `docker-compose logs model-loader`

**Chat is showing the wrong model**
- Click the model picker at the bottom of the Continue panel to switch
