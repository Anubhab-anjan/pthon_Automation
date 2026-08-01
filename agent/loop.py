"""
ReAct Execution Loop Engine.
Implements continuous Goal -> Plan -> Tool Call -> Observe -> Refine -> Complete cycle.
"""

import os
import sys
import json
from typing import Optional, Dict, Any, List

from agent.memory import ShortTermMemory
from agent.tools import registry
from agent.llm import BaseLLMProvider, get_llm_provider
from agent.guardrails import SafetyGuardrail

class AgentLoop:
    """
    Main Autonomous Agent Execution Loop.
    """

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        memory: Optional[ShortTermMemory] = None,
        guardrail: Optional[SafetyGuardrail] = None,
        max_iterations: int = 15,
        verbose: bool = True
    ):
        self.llm = llm_provider or get_llm_provider()
        self.memory = memory or ShortTermMemory()
        self.guardrail = guardrail or SafetyGuardrail()
        self.max_iterations = max_iterations
        self.verbose = verbose

    def _log(self, prefix: str, message: str, color_code: str = "\033[94m"):
        """Print formatted step log to standard output safely."""
        if not self.verbose:
            return
        
        # Strip color codes on Windows legacy CP1252 if stdout encoding is not utf-8
        is_win_legacy = sys.platform == "win32" and getattr(sys.stdout, "encoding", "").lower() != "utf-8"
        if is_win_legacy:
            text = f"\n{prefix} {message}".encode("ascii", errors="replace").decode("ascii")
            print(text)
        else:
            reset_code = "\033[0m"
            formatted_str = f"\n{color_code}{prefix}{reset_code} {message}"
            try:
                print(formatted_str)
            except Exception:
                print(f"\n{prefix} {message}".encode("ascii", errors="replace").decode("ascii"))

    def run_task(self, goal: str) -> str:
        """
        Execute a single user task request in an observation loop.
        """
        self.memory.reset(new_goal=goal)
        self._log("[TASK STARTED]", f"Goal: {goal}", color_code="\033[95m")

        tools_schema = registry.get_gemini_declarations()

        for step in range(1, self.max_iterations + 1):
            self._log(f"[STEP {step}/{self.max_iterations}]", "Generating next action...", color_code="\033[90m")

            messages = self.memory.get_messages()

            try:
                response = self.llm.generate(messages=messages, tools_schema=tools_schema)
            except Exception as e:
                err_msg = f"LLM Generation Error: {str(e)}"
                self._log("[ERROR]", err_msg, color_code="\033[91m")
                return f"Task failed due to LLM error: {str(e)}"

            # Print Assistant Thought / Plan if provided
            if response.thought:
                self._log("[PLAN / REASONING]", response.thought, color_code="\033[96m")

            # Check if LLM requested tool calls
            if response.has_tool_calls():
                for tool_call in response.tool_calls:
                    call_id = tool_call["id"]
                    tool_name = tool_call["name"]
                    kwargs = tool_call["arguments"]

                    args_str = json.dumps(kwargs, default=str)
                    self._log(f"[TOOL CALL: {tool_name}]", f"Arguments: {args_str}", color_code="\033[93m")

                    # Check guardrails
                    is_destructive = registry.is_destructive(tool_name)
                    allowed, msg = self.guardrail.check_execution(tool_name, kwargs, is_destructive)

                    if allowed:
                        # Invoke Tool
                        observation = registry.invoke(tool_name, kwargs)
                    else:
                        observation = msg

                    # Truncate long observation outputs for console display
                    obs_display = observation if len(observation) <= 400 else observation[:400] + "... [truncated]"
                    self._log(f"[OBSERVATION: {tool_name}]", obs_display, color_code="\033[92m")

                    # Update short-term memory
                    self.memory.add_assistant_tool_call(
                        call_id=call_id,
                        tool_name=tool_name,
                        arguments=kwargs,
                        thought=response.thought
                    )
                    self.memory.add_observation(
                        call_id=call_id,
                        tool_name=tool_name,
                        result=observation
                    )
            else:
                # No tool calls made; agent reached final answer
                final_text = response.final_answer or response.thought or "Task completed."
                self.memory.add_assistant_final(final_text)
                self._log("[COMPLETED]", final_text, color_code="\033[92m")
                return final_text

        # Reached max iterations without finishing
        max_msg = f"Task exceeded maximum iterations ({self.max_iterations})."
        self._log("[LIMIT REACHED]", max_msg, color_code="\033[91m")
        return max_msg
