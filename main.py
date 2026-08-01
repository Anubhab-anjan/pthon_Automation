"""
Autonomous CLI AI Agent - Main Interactive Loop Entry Point.
Inspired by OpenClaw & AutoGPT ReAct execution loops.
"""

import sys
import os
import argparse

# Configure stdout error replacement on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(errors="replace")


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Load .env file from project root
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT_DIR, ".env"), override=True)
except ImportError:
    pass

from agent.tools import registry
import tools  # Auto-registers all tools

from agent.memory import ShortTermMemory
from agent.llm import get_llm_provider
from agent.guardrails import SafetyGuardrail
from agent.loop import AgentLoop

def safe_print(text: str):
    """Print text safely across all terminal encodings."""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = text.encode("ascii", errors="replace").decode("ascii")
        print(clean_text)

def print_banner(provider_name: str, model_name: str, dry_run: bool, auto_approve: bool):
    safe_print("\n" + "=" * 65)
    safe_print("[+] AUTONOMOUS CLI AI AGENT  (ReAct Loop Engine)")
    safe_print("=" * 65)
    safe_print(f"  * Provider       : {provider_name.upper()}")
    safe_print(f"  * Model          : {model_name}")
    safe_print(f"  * Dry-Run Mode   : {'ENABLED (Simulating destructive actions)' if dry_run else 'DISABLED'}")
    safe_print(f"  * Safety Approval: {'AUTO-APPROVE' if auto_approve else 'INTERACTIVE CONFIRMATION'}")
    safe_print(f"  * Available Tools: {len(registry.list_tools())} loaded")
    safe_print("=" * 65)


def parse_args():
    parser = argparse.ArgumentParser(description="Autonomous Pure Python CLI AI Agent")
    parser.add_argument(
        "-p", "--provider",
        type=str,
        default=os.getenv("LLM_PROVIDER", "gemini"),
        choices=["gemini", "openai", "mock"],
        help="LLM Provider ('gemini', 'openai', or 'mock')"
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=None,
        help="LLM model name (overrides default for provider)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=os.getenv("DRY_RUN", "false").lower() == "true",
        help="Enable dry-run simulation mode for destructive operations"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        default=os.getenv("AUTO_APPROVE", "false").lower() == "true",
        help="Skip interactive confirmation prompts for destructive tool calls"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=int(os.getenv("MAX_ITERATIONS", "15")),
        help="Maximum ReAct loop iterations per user task goal"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Determine default model name if not specified
    model_name = args.model
    if not model_name:
        if args.provider.lower() == "gemini":
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        else:
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    print_banner(
        provider_name=args.provider,
        model_name=model_name,
        dry_run=args.dry_run,
        auto_approve=args.auto_approve
    )

    try:
        llm_provider = get_llm_provider(
            provider_name=args.provider,
            model_name=model_name
        )
    except Exception as e:
        safe_print(f"\n[!] Configuration Error: {str(e)}")
        safe_print("Please check your .env file or environment variables for valid API keys.")
        safe_print("See .env.example for configuration details.\n")
        sys.exit(1)

    guardrail = SafetyGuardrail(
        dry_run=args.dry_run,
        auto_approve=args.auto_approve
    )

    agent_loop = AgentLoop(
        llm_provider=llm_provider,
        guardrail=guardrail,
        max_iterations=args.max_steps
    )

    safe_print("\n[+] Agent Ready. Type your request (or 'exit' to quit):\n")

    while True:
        try:
            user_input = input(" > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "q"):
                safe_print("\n[*] Goodbye! Agent shutting down.\n")
                break

            # Execute task in observation loop
            agent_loop.run_task(goal=user_input)
            print("\n" + "-" * 65 + "\n")

        except (KeyboardInterrupt, EOFError):
            safe_print("\n\n[*] Agent session terminated by user.")
            break


if __name__ == "__main__":
    main()
