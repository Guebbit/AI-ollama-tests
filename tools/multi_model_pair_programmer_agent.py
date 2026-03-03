#!/usr/bin/env python3
"""Run a local multi-model pair-programming session against an Ollama endpoint."""

# Import argparse to expose a simple CLI for running the local agent.
import argparse
# Import json to encode/decode HTTP request payloads to Ollama.
import json
# Import os to inspect repository paths and build file snapshots.
import os
# Import textwrap to format long prompts in a readable way.
import textwrap
# Import urllib modules from the standard library to avoid extra dependencies.
from urllib import error, request


# Keep common directories out of repository snapshots to stay focused and fast.
EXCLUDED_DIRS = {".git", "node_modules", "dist", "__pycache__", ".idea", ".venv", "venv"}


# Define role-focused prompts so models can collaborate like a pair-programming team.
SYSTEM_PROMPTS = {
    "planner": (
        "You are a senior software architect. Build a minimal, safe, testable execution plan "
        "for the requested project task. Prefer small steps and explicit validation commands."
    ),
    "coder": (
        "You are a senior software engineer. Produce practical implementation instructions and "
        "code blocks that can be applied with minimal changes and verified with existing tests."
    ),
    "reviewer": (
        "You are a strict code reviewer. Identify correctness, maintainability, and security gaps. "
        "Return concrete fixes and missing test cases."
    ),
}


# Declare model preferences per role so the agent can auto-pick locally available models.
MODEL_PREFERENCES = {
    "planner": ["deepseek-r1", "qwen3", "llama3.1"],
    "coder": ["qwen3-coder", "deepseek-coder-v2", "llama3.1"],
    "reviewer": ["deepseek-r1", "qwen3", "llama3.1"],
}


# Read local models from Ollama so we can route each role to an available model automatically.
def list_local_models(endpoint: str) -> list[str]:
    """Return local Ollama model names from /api/tags."""
    # Build the endpoint URL once to keep HTTP logic simple and explicit.
    url = f"{endpoint.rstrip('/')}/api/tags"
    # Make a GET request to the local Ollama API with a short timeout.
    with request.urlopen(url, timeout=20) as response:
        # Parse the API response body as JSON.
        payload = json.loads(response.read().decode("utf-8"))
    # Return only model names and ignore malformed records defensively.
    return [item["name"] for item in payload.get("models", []) if "name" in item]


# Pick the first preferred model found locally, then fall back to the first available model.
def choose_model(role: str, available_models: list[str], explicit_model: str | None) -> str:
    """Resolve the model name used by a role."""
    # Respect an explicit model override from CLI if provided.
    if explicit_model:
        # Return the explicit model name directly for fully manual control.
        return explicit_model
    # Scan the role preference list and return the first locally available match.
    for preferred in MODEL_PREFERENCES[role]:
        # Accept exact names and tagged variants like qwen3-coder:14b.
        for local_model in available_models:
            # Use startswith so preference names match size-tagged models.
            if local_model.startswith(preferred):
                # Return the first match to keep selection deterministic.
                return local_model
    # Fall back to the first installed model if no preference was found.
    if available_models:
        # Return a safe fallback so the agent still runs on custom local model sets.
        return available_models[0]
    # Raise a clear error if no local models are installed.
    raise RuntimeError("No local Ollama models found. Run `ollama pull <model>` first.")


# Build a compact repository snapshot so models can reason over project context without huge prompts.
def build_repo_snapshot(repo_path: str, max_files: int) -> str:
    """Return a compact repository tree snapshot."""
    # Initialize a list that will hold relative file paths.
    files: list[str] = []
    # Walk the repository tree recursively.
    for root, dirnames, filenames in os.walk(repo_path):
        # Filter excluded directories in-place to prune recursion early.
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        # Append files to the snapshot list while preserving relative paths.
        for filename in filenames:
            # Join root and filename into an absolute file path.
            absolute_path = os.path.join(root, filename)
            # Convert each absolute path to a repository-relative path.
            relative_path = os.path.relpath(absolute_path, repo_path)
            # Add the relative path to the file list.
            files.append(relative_path)
            # Stop collecting once we hit the requested cap.
            if len(files) >= max_files:
                # Return immediately to keep prompt size bounded.
                return "\n".join(sorted(files))
    # Return all collected file paths sorted for deterministic output.
    return "\n".join(sorted(files))


# Send one non-streaming chat request to Ollama and return the assistant content.
def chat_once(endpoint: str, model: str, system_prompt: str, user_prompt: str) -> str:
    """Call /api/chat once and return model text content."""
    # Build the chat API URL using the configured endpoint.
    url = f"{endpoint.rstrip('/')}/api/chat"
    # Build a deterministic, non-streaming chat payload.
    body = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    # Encode the payload to UTF-8 JSON bytes for HTTP transmission.
    encoded_body = json.dumps(body).encode("utf-8")
    # Build an HTTP POST request with the JSON content type.
    http_request = request.Request(
        url,
        data=encoded_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    # Execute the request and parse the returned message content.
    with request.urlopen(http_request, timeout=120) as response:
        # Decode the full response body as JSON.
        payload = json.loads(response.read().decode("utf-8"))
    # Extract and return assistant text, defaulting safely to an empty string.
    return payload.get("message", {}).get("content", "")


# Orchestrate planner, coder, and reviewer turns to produce a final actionable implementation brief.
def run_session(args: argparse.Namespace) -> str:
    """Run one multi-model session and return markdown output."""
    # Discover locally available models from the configured Ollama endpoint.
    available_models = list_local_models(args.endpoint)
    # Resolve the planner model from CLI override or local preferences.
    planner_model = choose_model("planner", available_models, args.planner_model)
    # Resolve the coder model from CLI override or local preferences.
    coder_model = choose_model("coder", available_models, args.coder_model)
    # Resolve the reviewer model from CLI override or local preferences.
    reviewer_model = choose_model("reviewer", available_models, args.reviewer_model)

    # Collect a compact file tree snapshot to provide project context.
    repo_snapshot = build_repo_snapshot(args.repo_path, args.max_files)
    # Build shared context text reused across all role prompts.
    shared_context = textwrap.dedent(
        f"""
        User goal:
        {args.goal}

        Repository path:
        {args.repo_path}

        Repository file snapshot (first {args.max_files} files):
        {repo_snapshot or '(empty repository snapshot)'}
        """
    ).strip()

    # Ask the planner to produce a step-by-step minimal implementation strategy.
    planner_output = chat_once(
        args.endpoint,
        planner_model,
        SYSTEM_PROMPTS["planner"],
        shared_context + "\n\nReturn an execution plan with validations and rollback considerations.",
    )

    # Ask the coder to draft concrete changes based on the planner output.
    coder_output = chat_once(
        args.endpoint,
        coder_model,
        SYSTEM_PROMPTS["coder"],
        shared_context
        + "\n\nPlanner output:\n"
        + planner_output
        + "\n\nReturn concrete file-level changes and command-level validation steps.",
    )

    # Ask the reviewer to identify risks and propose focused corrections.
    reviewer_output = chat_once(
        args.endpoint,
        reviewer_model,
        SYSTEM_PROMPTS["reviewer"],
        shared_context
        + "\n\nPlanner output:\n"
        + planner_output
        + "\n\nCoder output:\n"
        + coder_output
        + "\n\nReturn prioritized review comments and fixes.",
    )

    # Ask the coder for a final revised implementation brief after review feedback.
    final_output = chat_once(
        args.endpoint,
        coder_model,
        SYSTEM_PROMPTS["coder"],
        shared_context
        + "\n\nPlanner output:\n"
        + planner_output
        + "\n\nReviewer feedback:\n"
        + reviewer_output
        + "\n\nProduce a final actionable implementation brief with exact steps and commands.",
    )

    # Build a markdown report that preserves each role turn for transparency and customization.
    report = textwrap.dedent(
        f"""
        # Multi-Model Pair Programming Session

        - Planner model: `{planner_model}`
        - Coder model: `{coder_model}`
        - Reviewer model: `{reviewer_model}`
        - Repository: `{args.repo_path}`

        ## Goal
        {args.goal}

        ## Planner Output
        {planner_output}

        ## Coder Output (Draft)
        {coder_output}

        ## Reviewer Output
        {reviewer_output}

        ## Final Implementation Brief
        {final_output}
        """
    ).strip() + "\n"
    # Return the markdown report to the caller for file output.
    return report


# Parse CLI arguments so the agent can run on fresh projects and existing repositories.
def build_argument_parser() -> argparse.ArgumentParser:
    """Create and return the CLI parser."""
    # Create the parser with a short help description.
    parser = argparse.ArgumentParser(description="Run a local multi-model pair-programming session.")
    # Add the high-level project goal argument.
    parser.add_argument("--goal", required=True, help="Project goal or coding task to execute.")
    # Add the repository path argument (defaults to current working directory).
    parser.add_argument("--repo-path", default=os.getcwd(), help="Repository path to analyze.")
    # Add the Ollama endpoint argument with docker-compose default host port.
    parser.add_argument("--endpoint", default="http://localhost:9191", help="Ollama HTTP endpoint.")
    # Add optional explicit planner model override.
    parser.add_argument("--planner-model", default=None, help="Optional explicit planner model.")
    # Add optional explicit coder model override.
    parser.add_argument("--coder-model", default=None, help="Optional explicit coder model.")
    # Add optional explicit reviewer model override.
    parser.add_argument("--reviewer-model", default=None, help="Optional explicit reviewer model.")
    # Add a snapshot size cap to avoid oversized prompts.
    parser.add_argument("--max-files", type=int, default=300, help="Max repository files to include.")
    # Add output markdown file path for saved session transcripts.
    parser.add_argument(
        "--output",
        default="multi-model-pair-programming-session.md",
        help="Markdown output path for the generated session.",
    )
    # Return the configured parser to the caller.
    return parser


# Execute the CLI flow and emit clear runtime errors for connectivity issues.
def main() -> int:
    """CLI entrypoint."""
    # Build and parse CLI arguments.
    args = build_argument_parser().parse_args()
    # Resolve repository path to an absolute path for reproducible outputs.
    args.repo_path = os.path.abspath(args.repo_path)
    try:
        # Run the multi-model session and get the markdown result.
        report = run_session(args)
        # Write the generated report to the requested output path.
        with open(args.output, "w", encoding="utf-8") as file_handle:
            # Persist the full session transcript for future review/customization.
            file_handle.write(report)
        # Print a success message with the output path for fast discovery.
        print(f"Session completed successfully. Output written to: {args.output}")
        # Return zero to indicate success.
        return 0
    except error.URLError as exc:
        # Print a clear connection error to help users fix endpoint issues quickly.
        print(f"Could not reach Ollama endpoint '{args.endpoint}': {exc}")
        # Return non-zero to signal failure to callers and automation.
        return 1
    except RuntimeError as exc:
        # Print functional runtime errors such as missing local models.
        print(str(exc))
        # Return non-zero to signal functional failure.
        return 1


# Run the CLI only when this script is executed directly.
if __name__ == "__main__":
    # Exit with the main function status code for shell compatibility.
    raise SystemExit(main())
