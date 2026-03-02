# 🧩 Model Weights

## What is a Weight?

A neural network = giant math function

- **Input:** tokens (text, code, etc.)
- **Output:** predictions (next token)

Network structure:

- Neurons connected in layers
- Each connection has:

**Weight** → strength of connection
**Bias** → baseline offset

➡️ All weights together = what the model learned

For LLMs: **billions of numbers stored in memory**



## Why Weights Matter

Weights = the model’s knowledge

- Change weights → change knowledge (fine-tuning)
- Quantization → store weights in fewer bits
  → less VRAM
  → slightly less precision



### Example Sizes

| Model | # Weights | VRAM FP16 |
|------|-----------|-----------|
Llama 7B | ~7B | ~14 GB
Llama 13B | ~13B | ~26 GB
Llama 30B | ~30B | ~60 GB



## Analogy

Neural network = system of springs & levers

- Each weight = spring tension
- Springs control how input becomes output
- You only change springs when training



---

# 📦 LLM Sizes & Quantization

## VRAM Usage (Approx.)

| Model | FP16 VRAM | Quantized | Safe on 24 GB |
|------|------------|-----------|----------------|
7B | ~6–8 GB | Q4_0 / Q4_1 | ✅ 2–3 models
8B | ~8–10 GB | Q4_0 | ✅ 2 models
13B | ~13–15 GB | Q4 | ✅ 1 model
30B | ~30–35 GB | Q4–Q6 | ⚠ Tight fit
70B | ~70 GB | Q4–Q8 | ❌ Needs multi-GPU



## Quantization Explained

Reduces memory by using fewer bits per weight:

- **Q4** → 4-bit
  - Fast
  - Low VRAM
  - Slight accuracy loss

- **Q5 / Q6** → better accuracy, more VRAM



### Rule of Thumb (24 GB GPU)

**Safe**
- 7B–13B Q4

**Risky**
- 30B Q4 (near VRAM limit)

**Max**
- One 13B–30B model at a time



---

# 🔤 Tokens

## What is a Token?

- ≈ 1 word (or 0.75 words)
- Rare words split into parts

LLMs have a **context window**
= max tokens per request



### Context Examples

| Model | Context | Words |
|------|---------|-------|
13B models | 32k | ~24k words
70B models | 32k–64k | ~24k–48k words



### `max_tokens`

Controls how much the model generates

👉 Keep around **512–1024**
to avoid VRAM spikes



---

# 🛠️ Training Locally

## Levels of “Training”

### 1) Fine-tuning / LoRA

- Adjust behavior without retraining
- Adds small adapter layers

Good for:
- Custom style
- Custom knowledge

Low GPU usage



### 2) RAG (Retrieval-Augmented Generation)

- No weight changes
- Inject documents at query time

Best for:
- Private data
- Local files
- Knowledge bases



### 3) Full Training

- Requires massive compute
- Not realistic on a single consumer GPU




### 4) 📁 Files

#### Modelfile
- Defines **model behavior**
- Like **BIOS settings for an AI**

#### Makefile
- Automates commands
- Used by the `make` tool





---

# ⚡ TL;DR

**Weights = knowledge**
**Quantization = compression**
**Tokens = text units**
**LoRA/RAG = practical customization**