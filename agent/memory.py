"""
Short-Term Execution Memory Manager for Agent Loop Context.
Tracks system prompts, conversation history, tool calls, and observations.
"""

from typing import List, Dict, Any, Optional

class ShortTermMemory:
    """
    Manages short-term execution context for a single user task session.
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are an autonomous Python CLI AI Agent. "
        "Your task is to solve user requests by breaking them down into step-by-step reasoning "
        "and invoking the available tools. "
        "Always evaluate observations from tool calls carefully. "
        "If a tool call succeeds, proceed to the next logical step or provide your final answer. "
        "If a tool call fails, analyze the error observation and try an alternative approach or tool. "
        "When the user's task is fully completed, provide a clear, concise final answer summary."
    )

    def __init__(self, system_prompt: Optional[str] = None):
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.messages: List[Dict[str, Any]] = []
        self.current_goal: Optional[str] = None
        self.reset()

    def reset(self, new_goal: Optional[str] = None):
        """Reset memory context for a new user task goal."""
        self.current_goal = new_goal
        self.messages = []
        if self.system_prompt:
            self.messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        if new_goal:
            self.messages.append({
                "role": "user",
                "content": f"Task Goal: {new_goal}"
            })

    def add_user_message(self, content: str):
        """Add a user message to memory."""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_thought(self, content: str):
        """Add reasoning / plan text from the assistant."""
        self.messages.append({"role": "assistant", "content": content})

    def add_assistant_tool_call(self, call_id: str, tool_name: str, arguments: Dict[str, Any], thought: Optional[str] = None):
        """Add assistant tool invocation to memory."""
        msg: Dict[str, Any] = {
            "role": "assistant",
            "tool_calls": [{
                "id": call_id,
                "function": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }]
        }
        if thought:
            msg["content"] = thought
        self.messages.append(msg)

    def add_observation(self, call_id: str, tool_name: str, result: str):
        """Add tool execution observation result."""
        self.messages.append({
            "role": "tool",
            "tool_call_id": call_id,
            "name": tool_name,
            "content": result
        })

    def add_assistant_final(self, content: str):
        """Add final completion response from assistant."""
        self.messages.append({"role": "assistant", "content": content})

    def get_messages(self) -> List[Dict[str, Any]]:
        """Return the current context messages array."""
        return self.messages

    def get_history_summary(self) -> str:
        """Return formatted string history for display/logging."""
        lines = []
        for idx, msg in enumerate(self.messages, 1):
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            tool_calls = msg.get("tool_calls", None)
            if tool_calls:
                lines.append(f"[{idx}] {role} CALLS: {tool_calls}")
            else:
                lines.append(f"[{idx}] {role}: {content}")
        return "\n".join(lines)
