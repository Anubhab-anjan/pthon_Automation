"""
Safety Guardrails and Execution Policy Manager.
Handles dry-run simulations and user confirmation for destructive operations.
"""

import os
import json
from typing import Dict, Any, Tuple

class SafetyGuardrail:
    """
    Guardrail manager for tool executions.
    """

    def __init__(self, dry_run: bool = False, auto_approve: bool = False):
        self.dry_run = dry_run or (os.getenv("DRY_RUN", "false").lower() == "true")
        self.auto_approve = auto_approve or (os.getenv("AUTO_APPROVE", "false").lower() == "true")

    def check_execution(self, tool_name: str, kwargs: Dict[str, Any], is_destructive: bool) -> Tuple[bool, str]:
        """
        Check whether tool call is allowed to execute.
        Returns: (allow_execution: bool, message: str)
        """
        args_str = json.dumps(kwargs, default=str)

        # 1. Dry Run Check
        if is_destructive and self.dry_run:
            return False, f"[DRY-RUN SIMULATION] Destructive action '{tool_name}' with args {args_str} was simulated and skipped."

        # 2. Interactive Confirmation Check
        if is_destructive and not self.auto_approve:
            warning_msg = f"\n[SAFETY WARNING] The agent wants to execute a potentially destructive operation:\n   Tool: {tool_name}\n   Args: {args_str}"
            try:
                print(warning_msg)
            except Exception:
                pass
            try:
                user_input = input("   Proceed with execution? [y/N]: ").strip().lower()
                if user_input not in ('y', 'yes'):
                    return False, f"Observation: Action '{tool_name}' was CANCELLED by user for safety."
            except (EOFError, KeyboardInterrupt):
                return False, f"Observation: Action '{tool_name}' was CANCELLED (non-interactive stream ended)."

        return True, "Approved"
