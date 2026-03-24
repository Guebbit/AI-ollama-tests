#!/usr/bin/env python3
# Allow built-in generics (list[dict]) as type hints on Python 3.8 and 3.9.
from __future__ import annotations
"""
agent.py — Multi-step AI agent powered by Ollama
=================================================

This script turns a high-level task description into a structured, multi-step
execution plan. The AI model acts as an *agent*: it plans, executes step by
step, and keeps a running log of what was done.

HOW IT WORKS
============

    You ─── task ───▶  PLAN phase    ─── steps list ───▶
                       EXECUTE phase  ─── one step at a time ───▶ output
                       DONE           ─── summary

The agent uses Ollama's streaming API. Each "turn" builds on the previous
context so the model always knows the full task history.

USAGE
=====
    python3 scripts/agent.py "refactor the auth module to use JWT"
    python3 scripts/agent.py "write unit tests for UserService"
    python3 scripts/agent.py --model qwen3-coder-30b-agent "set up CI/CD pipeline"
    python3 scripts/agent.py --steps 5 "migrate database schema"

INTERACTIVE MODE (no arguments)
    python3 scripts/agent.py

DEPENDENCIES
============
    Python 3.8+, requests  (pip install requests)

ENVIRONMENT VARIABLES
=====================
    AI_MODEL_AGENT   Model name (default: qwen3-coder-30b-agent)
    AI_HOST          Ollama host (default: http://localhost:11434)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

# ── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_MODEL = os.environ.get("AI_MODEL_AGENT", "qwen3-coder-30b-agent")
DEFAULT_HOST  = os.environ.get("AI_HOST", "http://localhost:11434")

# ── Ollama API ─────────────────────────────────────────────────────────────────

def check_ollama(host: str) -> None:
    """Verify Ollama is running before we try to send any requests."""
    try:
        urllib.request.urlopen(f"{host}/api/tags", timeout=5)
    except (urllib.error.URLError, OSError):
        print(f"❌  Ollama is not running at {host}", file=sys.stderr)
        print("    Start it with: docker-compose up -d ollama", file=sys.stderr)
        sys.exit(1)


def stream_response(host: str, model: str, prompt: str, context: list[dict]) -> str:
    """
    Send a prompt to Ollama using the /api/chat endpoint and stream the reply.

    The `context` list is a standard OpenAI-style message list:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]

    Streaming: Ollama sends one JSON object per line. We print tokens as they
    arrive so the user sees output in real time (important for ADHD — no blank
    staring at a spinner).

    Returns the full accumulated response text.
    """
    messages = context + [{"role": "user", "content": prompt}]

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{host}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    full_response = ""

    try:
        with urllib.request.urlopen(req) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue

                obj = json.loads(line)
                token = obj.get("message", {}).get("content", "")

                if token:
                    print(token, end="", flush=True)
                    full_response += token

                if obj.get("done"):
                    break

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"\n❌  Ollama API error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

    print()  # Newline after streamed output
    return full_response


# ── Agent Logic ────────────────────────────────────────────────────────────────

PLAN_PROMPT = """\
I need to complete this task:

{task}

First, write a numbered PLAN of steps (maximum {max_steps} steps).
Each step should be concrete and actionable.
Format exactly like this — nothing else:

PLAN
1. <step description>
2. <step description>
...

Do not execute anything yet. Just output the plan."""


EXECUTE_PROMPT = """\
Execute step {step_num}: {step_description}

Guidelines:
- If this step needs a shell command, prefix it with  CMD: <command>
- If this step changes a file, prefix it with        FILE: <path>
- If this step needs user input, prefix it with       ASK: <question>
- Otherwise, explain what you did or would do

Keep it short and focused on this single step."""


DONE_PROMPT = """\
All steps are complete. Write a short DONE summary:
- What was accomplished
- Any files changed (if applicable)
- Any next steps the user should take

Keep it to 5 lines max."""


def parse_plan(plan_text: str) -> list[str]:
    """
    Extract the numbered list of steps from the model's PLAN output.

    Looks for lines that start with a number followed by a period or parenthesis,
    e.g.: "1. Do this thing"  or  "1) Do this thing"
    """
    steps = []
    for line in plan_text.splitlines():
        line = line.strip()
        # Match lines like "1. ..." or "1) ..."
        if line and line[0].isdigit() and len(line) > 2 and line[1] in ".):":
            # Strip the leading number and separator
            step_text = line[2:].strip()
            if step_text:
                steps.append(step_text)
    return steps


def run_agent(task: str, model: str, host: str, max_steps: int = 8) -> None:
    """
    Run the full agent loop for a given task.

    Phase 1 — PLAN:    Ask the model to break the task into steps.
    Phase 2 — EXECUTE: Loop through each step, passing context forward.
    Phase 3 — DONE:    Ask the model to write a completion summary.
    """
    # Conversation history passed to every API call so the model has full context.
    # This is how "memory" works in a stateless LLM — we resend everything.
    context: list[dict] = []

    # ── Phase 1: Plan ─────────────────────────────────────────────────────────
    print("=" * 60)
    print(f"🎯  TASK: {task}")
    print("=" * 60)
    print()
    print("📋  PLANNING...")
    print()

    plan_prompt = PLAN_PROMPT.format(task=task, max_steps=max_steps)
    plan_text = stream_response(host, model, plan_prompt, context)

    # Add the plan exchange to context so the model remembers it
    context.append({"role": "user",      "content": plan_prompt})
    context.append({"role": "assistant", "content": plan_text})

    # Parse the steps from the model's output
    steps = parse_plan(plan_text)

    if not steps:
        print()
        print("⚠️   Could not parse a numbered plan from the model's response.")
        print("    Try rephrasing your task more concretely.")
        sys.exit(1)

    print()
    print(f"✅  {len(steps)} steps identified")
    print()

    # ── Phase 2: Execute each step ────────────────────────────────────────────
    for i, step in enumerate(steps, start=1):
        print("-" * 60)
        print(f"🔧  STEP {i}/{len(steps)}: {step}")
        print("-" * 60)

        execute_prompt = EXECUTE_PROMPT.format(
            step_num=i,
            step_description=step,
        )

        step_result = stream_response(host, model, execute_prompt, context)

        # Each step's Q&A is appended so subsequent steps have full context
        context.append({"role": "user",      "content": execute_prompt})
        context.append({"role": "assistant", "content": step_result})

        print()

    # ── Phase 3: Done ─────────────────────────────────────────────────────────
    print("=" * 60)
    print("✨  DONE — Summary")
    print("=" * 60)

    stream_response(host, model, DONE_PROMPT, context)
    print()


# ── Entry Point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-step AI agent powered by Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "task",
        nargs="*",
        help="Task description (interactive prompt if omitted)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Ollama model name (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Ollama API host (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=8,
        metavar="N",
        help="Maximum number of steps in the plan (default: 8)",
    )

    args = parser.parse_args()

    # Accept task from CLI args or interactive prompt
    if args.task:
        task = " ".join(args.task)
    else:
        print("🤖  Multi-step AI Agent")
        print("    Powered by Ollama —", args.model)
        print()
        task = input("📌  What do you want to accomplish? ").strip()
        if not task:
            print("No task provided. Exiting.")
            sys.exit(0)

    check_ollama(args.host)
    run_agent(task, args.model, args.host, max_steps=args.steps)


if __name__ == "__main__":
    main()
