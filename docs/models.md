# Ollama Models — Usage Guide (Size‑Agnostic)

> Note: Parameter counts are listed only as available variants, not as a quality indicator.

---

## dolphin-llama3

**Variants:** 8B, 70B
**Preferred use:** High-quality chat, creative writing, roleplay, complex reasoning
**Strong suits:** Instruction following, deep explanations, expressive outputs
**Features:** Uncensored, supports long context, good for dialogue simulations
**Description:** Dolphin uncensored fine-tune of Llama 3 family, focused on expressive and reliable conversation.

---

## mixtral

**Variants:** 8x7B (MoE), other MoE derivatives
**Preferred use:** General assistant, multilingual reasoning, analysis
**Strong suits:** Mixture-of-Experts efficiency, large context reasoning
**Features:** Supports multiple languages, good for analytical tasks
**Description:** High-performance MoE model optimized for complex prompts and broad knowledge use.

---

## llama2-uncensored

**Variants:** 7B, 13B, 70B
**Preferred use:** Experimental, open-ended chat
**Strong suits:** Unfiltered responses, lightweight
**Features:** Minimal safety restrictions
**Description:** Llama 2 uncensored fine-tune for open-ended conversation and testing experimental prompts.

---

## phi4-mini

**Variants:** ~3.8B class (mini line)
**Preferred use:** Lightweight assistant, edge device deployment
**Strong suits:** Fast, efficient, solid reasoning for size
**Features:** Low memory usage, quick response times
**Description:** Compact model for general-purpose lightweight tasks.

---

## dolphin-phi

**Variants:** ~2.7B class
**Preferred use:** Tiny fast assistant
**Strong suits:** Ultra-lightweight, relaxed alignment
**Features:** Uncensored, extremely fast
**Description:** Dolphin tuning applied to Phi models, optimized for speed and minimal alignment constraints.

---

## phi3

**Variants:** Mini (~3.8B), Small, Medium
**Preferred use:** General tasks, basic coding
**Strong suits:** High efficiency per size, reliable formatting
**Features:** Lightweight, good reasoning, small memory footprint
**Description:** Efficient small model for everyday use and coding basics.

---

## llava-llama3

**Variants:** 8B class
**Preferred use:** Vision + language tasks
**Strong suits:** Image captioning, visual Q&A, diagram understanding
**Features:** Multimodal input (image + text)
**Description:** LLaVA fine-tuned on Llama 3 for vision-language tasks.

---

## deepseek-coder-v2

**Variants:** 1.3B, 6.7B, 16B, 33B
**Preferred use:** Programming, code generation, refactoring
**Strong suits:** Multi-language coding, debugging, long context
**Features:** IDE integration-friendly, repository analysis
**Description:** Specialized coding model optimized for professional software development tasks.

---

## llama3.1

**Variants:** 8B, 70B
**Preferred use:** Balanced general assistant
**Strong suits:** Reliable, strong reasoning
**Features:** Safe, general-purpose tasks
**Description:** Everyday assistant with good performance across multiple domains.

---

## qwen3-coder

**Variants:** 7B, 14B, 30B
**Preferred use:** Advanced coding, agents, tool use
**Strong suits:** Strong reasoning, planning, multilingual coding
**Features:** Tool usage, code generation, debugging
**Description:** Powerful coding assistant for multi-step programming and agent applications.

---

## deepseek-r1

**Variants:** ~7B, 14B, 32B+
**Preferred use:** Reasoning, math, step-by-step problem solving
**Strong suits:** Analytical, chain-of-thought style reasoning
**Features:** Focused on logical reasoning, structured problem solving
**Description:** Optimized for reasoning-heavy tasks.

---

## qwen3

**Variants:** 4B, larger dense and MoE variants
**Preferred use:** Lightweight general assistant
**Strong suits:** Multilingual, fast, instruction following
**Features:** Lightweight deployment, responsive interactions
**Description:** Small and fast general-purpose assistant for everyday tasks.

---

# Similar Model Families

## Phi family

* dolphin-phi → smallest, least aligned
* phi3 → stronger baseline
* phi4-mini → efficiency-focused

## Llama family

* llama3.1 → balanced general use
* dolphin-llama3 → uncensored expressive variant

## Coding specialists

* deepseek-coder-v2 → efficient dedicated coder
* qwen3-coder → advanced coding + agent tasks

## Reasoning specialists

* deepseek-r1 → analytical and math-heavy tasks

---

*End of documentation*
