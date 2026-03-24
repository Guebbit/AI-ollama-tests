# 🖊️ Editor AI — Autocomplete + Chat in Your IDE

Your IDE becomes your coding partner. This guide sets up **Continue.dev** to
use your local Ollama models for autocomplete and chat — no cloud, no API keys,
no subscription.

Continue.dev supports **VS Code**, **WebStorm**, **PhpStorm**, **IntelliJ IDEA**,
**PyCharm**, **GoLand**, and all other JetBrains IDEs using the same config file.

---

## What You Get

| Feature | Model Used |
|---------|-----------|
| Inline autocomplete (Tab to accept) | `qwen3-coder-30b-editor` |
| Chat panel (ask anything) | `qwen3-coder-30b-safe` |
| Edit selected code in place | `qwen3-coder-30b-safe` |
| Codebase semantic search | `nomic-embed-text` |
| Quick questions (fast) | `qwen3-4b-balanced` |

---

## Step 1 — Make Sure the Models Are Running

Before configuring your IDE, start the Docker stack and wait for the models to load:

```bash
docker-compose up -d

# Wait for model-loader to finish (check logs)
docker-compose logs -f model-loader
```

Verify the models are available:
```bash
curl http://localhost:11434/api/tags | jq '.models[].name'
# Should include: qwen3-coder-30b-editor, qwen3-coder-30b-safe, qwen3-4b-balanced
```

---

## Step 2 — Copy the Config (All IDEs)

Continue stores its config at `~/.continue/config.json`. This single file is
shared by **all IDEs** — set it up once, and it works everywhere.

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

## Step 3 — Install Continue in Your IDE

### VS Code

1. Open VS Code
2. Press `Ctrl+Shift+X` (Extensions panel)
3. Search for **Continue**
4. Click **Install**

Or install via the command line:
```bash
code --install-extension continue.continue
```

After installing, reload VS Code. The Continue icon appears in the left sidebar.

---

### WebStorm / PhpStorm / IntelliJ IDEA / PyCharm / GoLand

All JetBrains IDEs use the same plugin from the JetBrains Marketplace.

**Method A — From inside the IDE:**

1. Open **Settings** (`Ctrl+Alt+S` / `Cmd+,` on macOS)
2. Go to **Plugins** → **Marketplace** tab
3. Search for **Continue**
4. Click **Install**, then **Restart IDE**

**Method B — From the browser:**

1. Open [plugins.jetbrains.com](https://plugins.jetbrains.com/plugin/22707-continue)
2. Click **Install to IDE**
3. Select your running JetBrains IDE from the popup

After restarting, the **Continue** panel appears in the right sidebar (or via
**View → Tool Windows → Continue**).

---

## Step 4 — (Optional) Set Up Codebase Search

To use `@Codebase` in chat (semantic search over your whole project), pull the
embedding model:

```bash
docker exec -it $(docker-compose ps -q ollama) ollama pull nomic-embed-text
```

Then in your IDE's Continue panel, type `@Codebase` in chat to index and search
your project semantically.

---

## How to Use It — Daily Workflow

### Autocomplete

Just start typing — Continue shows a ghost suggestion inline.

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
- **Next suggestion:** `Alt+]` (VS Code) / `Alt+[` or `Alt+]` (JetBrains)

---

### Chat

Select code, open the chat panel, and ask:

```
> What does this function do?
> Refactor this to use async/await
> Add error handling to this
> Write unit tests for this
```

---

### Edit in Place

Select code → use the inline edit shortcut → describe the change:

```
> Extract this into a separate function
> Convert to TypeScript
> Add JSDoc comments
```

---

### Context References

In chat, prefix with `@` to attach context:

```
@file src/auth.ts   — explain how authentication works
@folder src/api     — what endpoints are exposed?
@terminal           — explain this error
@problems           — fix these TypeScript errors
@codebase           — search the whole repo semantically
```

---

## Keyboard Shortcuts

### VS Code

| Action | Windows / Linux | macOS |
|--------|-----------------|-------|
| Open chat panel | `Ctrl+L` | `Cmd+L` |
| Open Continue sidebar | `Ctrl+Shift+L` | `Cmd+Shift+L` |
| Edit selected code inline | `Ctrl+I` | `Cmd+I` |
| Accept autocomplete | `Tab` | `Tab` |
| Dismiss autocomplete | `Escape` | `Escape` |
| Next autocomplete suggestion | `Alt+]` | `Option+]` |

### JetBrains IDEs (WebStorm, PhpStorm, IntelliJ, etc.)

| Action | Windows / Linux | macOS |
|--------|-----------------|-------|
| Open chat panel | `Alt+Shift+J` | `Option+Shift+J` |
| Edit selected code inline | `Ctrl+I` | `Cmd+I` |
| Accept autocomplete | `Tab` | `Tab` |
| Dismiss autocomplete | `Escape` | `Escape` |
| Toggle Continue panel | **View → Tool Windows → Continue** | same |

> **Note:** JetBrains shortcuts can be customized in **Settings → Keymap →
> search "Continue"**.

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
- The 30B model needs a GPU with enough VRAM. Swap to the lighter model by
  editing `~/.continue/config.json` and changing `tabAutocompleteModel.model`
  to `qwen3-4b-balanced`

**"Model not found" error**
- Run `docker-compose up -d` and wait for `model-loader` to finish
- Check: `docker-compose logs model-loader`

**Continue panel not visible in JetBrains**
- Go to **View → Tool Windows → Continue**
- Or check **Settings → Plugins** to confirm the plugin is enabled

**Chat shows wrong model**
- Click the model picker at the bottom of the Continue panel to switch

**Config not loading in JetBrains**
- Confirm `~/.continue/config.json` exists and is valid JSON (comments with
  `//` are supported by Continue but not standard JSON parsers)
- Restart the IDE after editing the config
