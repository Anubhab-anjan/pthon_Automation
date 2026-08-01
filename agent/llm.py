"""
Abstract LLM Client Provider Layer.
Supports Google Gemini (via google.generativeai and google.genai), OpenAI (via openai), and Mock/Demo provider.
Returns standardized responses with thought reasoning and tool calls.
"""

import os
import sys
import json
import uuid
from typing import List, Dict, Any, Optional

_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_path = os.path.join(_root_dir, ".env")
try:
    from dotenv import load_dotenv
    load_dotenv(_env_path, override=True)
except ImportError:
    pass

def get_config_var(key_name: str, default_val: str = "") -> str:
    val = os.getenv(key_name, "").strip()
    if not val and os.path.exists(_env_path):
        try:
            with open(_env_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key_name}="):
                        val = line.split("=", 1)[1].strip()
                        break
        except Exception:
            pass
    return val or default_val

class LLMResponse:
    """Standardized response structure from LLM generation."""
    def __init__(
        self,
        thought: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        final_answer: Optional[str] = None
    ):
        self.thought = thought or ""
        self.tool_calls = tool_calls or []
        self.final_answer = final_answer or ""

    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class BaseLLMProvider:
    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools_schema: List[Dict[str, Any]]
    ) -> LLMResponse:
        raise NotImplementedError


class MockProvider(BaseLLMProvider):
    """
    Mock LLM Provider for demonstration, testing, and offline CLI loops without requiring API keys.
    """

    def __init__(self, model_name: str = "mock-agent-v1"):
        self.model_name = model_name
        self.step_count = 0

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools_schema: List[Dict[str, Any]]
    ) -> LLMResponse:
        self.step_count += 1
        
        # Get last user goal and last tool observation
        last_user = ""
        has_tool_observation = False
        for m in reversed(messages):
            if m.get("role") == "user" and not last_user:
                last_user = m.get("content", "").lower()
            if m.get("role") == "tool":
                has_tool_observation = True
                break

        # If we already executed a tool, finish task
        if has_tool_observation:
            return LLMResponse(
                thought="I have received the observation from the executed tool and verified the result.",
                final_answer="[MOCK ENGINE] Task completed successfully based on tool execution result."
            )

        # Decide tool call based on task query keyword
        call_id = f"call_{uuid.uuid4().hex[:8]}"

        if any(w in last_user for w in ["system", "info", "os", "platform", "version"]):
            return LLMResponse(
                thought="Analyzing user request for system information. Invoking get_system_info tool.",
                tool_calls=[{
                    "id": call_id,
                    "name": "get_system_info",
                    "arguments": {}
                }]
            )
        elif any(w in last_user for w in ["organize", "pdf", "extension", "categorize", "clean"]):
            return LLMResponse(
                thought="User requested file organization by extension. Invoking organize_files_by_extension tool.",
                tool_calls=[{
                    "id": call_id,
                    "name": "organize_files_by_extension",
                    "arguments": {"folder_path": "."}
                }]
            )
        elif any(w in last_user for w in ["image", "photo", "edit", "batch"]):
            return LLMResponse(
                thought="User requested image batch editing. Invoking batch_edit_images tool.",
                tool_calls=[{
                    "id": call_id,
                    "name": "batch_edit_images",
                    "arguments": {"input_dir": "./imgs", "output_dir": "./editedImgs"}
                }]
            )
        elif any(w in last_user for w in ["search", "google", "web", "find"]):
            return LLMResponse(
                thought="User requested web search. Invoking search_web tool.",
                tool_calls=[{
                    "id": call_id,
                    "name": "search_web",
                    "arguments": {"query": last_user.replace("Task Goal:", "").strip()}
                }]
            )
        else:
            # Default to list_directory
            return LLMResponse(
                thought="Analyzing directory contents to fulfill user request. Invoking list_directory tool.",
                tool_calls=[{
                    "id": call_id,
                    "name": "list_directory",
                    "arguments": {"path": "."}
                }]
            )


class GeminiProvider(BaseLLMProvider):
    """Provider for Google Gemini API via google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = (api_key or get_config_var("GEMINI_API_KEY")).strip()
        self.model_name = (model_name or get_config_var("GEMINI_MODEL", "gemini-2.5-flash")).strip()
        
        if not self.api_key:
            raise ValueError(f"GEMINI_API_KEY environment variable is missing or empty.")

        try:
            from google import genai
            from google.genai import types
            self.genai = genai
            self.types = types
            self.client = genai.Client(api_key=self.api_key)
        except Exception:
            try:
                import sys
                extra_path = "C:/Users/anubh/AppData/Local/Python/pythoncore-3.14-64/Lib/site-packages"
                if extra_path not in sys.path:
                    sys.path.append(extra_path)
                from google import genai
                from google.genai import types
                self.genai = genai
                self.types = types
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                raise ImportError(f"google-genai package is not installed: {str(e)}")

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools_schema: List[Dict[str, Any]]
    ) -> LLMResponse:
        return self._generate_new(messages, tools_schema)

    def _generate_legacy(
        self,
        messages: List[Dict[str, Any]],
        tools_schema: List[Dict[str, Any]]
    ) -> LLMResponse:
        model = self.genai.GenerativeModel(self.model_name)
        prompt_lines = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                prompt_lines.append(f"System: {content}")
            elif role == "user":
                prompt_lines.append(f"User: {content}")
            elif role == "assistant":
                prompt_lines.append(f"Assistant: {content}")
            elif role == "tool":
                prompt_lines.append(f"Observation ({msg.get('name')}): {content}")

        prompt_lines.append("\nPlease evaluate the goal, decide the next logical step, or provide the final answer summary.")
        
        try:
            response = model.generate_content("\n".join(prompt_lines))
            text = response.text if hasattr(response, "text") and response.text else "Task processed."
            return LLMResponse(thought=text, final_answer=text)
        except Exception as e:
            return LLMResponse(thought=f"Error during Gemini generation: {str(e)}", final_answer=f"Gemini API Error: {str(e)}")

    def _generate_new(
        self,
        messages: List[Dict[str, Any]],
        tools_schema: List[Dict[str, Any]]
    ) -> LLMResponse:
        system_instruction = None
        contents = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = content
            elif role == "user":
                contents.append(self.types.Content(
                    role="user",
                    parts=[self.types.Part.from_text(text=content)]
                ))
            elif role == "assistant":
                parts = []
                if content:
                    parts.append(self.types.Part.from_text(text=content))
                if "tool_calls" in msg:
                    for tc in msg["tool_calls"]:
                        fn = tc.get("function", {})
                        parts.append(self.types.Part.from_function_call(
                            name=fn.get("name"),
                            args=fn.get("arguments", {})
                        ))
                if parts:
                    contents.append(self.types.Content(role="model", parts=parts))
            elif role == "tool":
                call_name = msg.get("name")
                tool_content = msg.get("content", "")
                contents.append(self.types.Content(
                    role="user",
                    parts=[self.types.Part.from_function_response(
                        name=call_name,
                        response={"result": tool_content}
                    )]
                ))

        # Format function declarations
        fn_declarations = []
        for tool_def in tools_schema:
            fn_declarations.append(self.types.FunctionDeclaration(
                name=tool_def["name"],
                description=tool_def["description"],
                parameters=tool_def.get("parameters")
            ))

        config = self.types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[self.types.Tool(function_declarations=fn_declarations)] if fn_declarations else None,
            temperature=0.2,
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config
        )

        thought_parts = []
        tool_calls = []

        if response.function_calls:
            for fc in response.function_calls:
                call_id = f"call_{uuid.uuid4().hex[:8]}"
                tool_calls.append({
                    "id": call_id,
                    "name": fc.name,
                    "arguments": dict(fc.args) if fc.args else {}
                })
        
        if response.text:
            thought_parts.append(response.text)

        thought_text = "\n".join(thought_parts).strip()

        if tool_calls:
            return LLMResponse(thought=thought_text, tool_calls=tool_calls)
        else:
            return LLMResponse(thought=thought_text, final_answer=thought_text)


class OpenAIProvider(BaseLLMProvider):
    """Provider for OpenAI API via openai SDK."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is missing.")

        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package is not installed. Install via `pip install openai`.")

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools_schema: List[Dict[str, Any]]
    ) -> LLMResponse:
        # Convert schema to OpenAI format if needed
        openai_tools = []
        for t in tools_schema:
            openai_tools.append({
                "type": "function",
                "function": t
            })

        formatted_messages = []
        for m in messages:
            # Map tool role to assistant or tool format
            if m.get("role") == "tool":
                formatted_messages.append({
                    "role": "tool",
                    "tool_call_id": m.get("tool_call_id", "call_default"),
                    "content": m.get("content", "")
                })
            else:
                formatted_messages.append(m)

        kwargs = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": 0.2
        }
        if openai_tools:
            kwargs["tools"] = openai_tools

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        msg = choice.message

        thought = msg.content or ""
        tool_calls = []

        if msg.tool_calls:
            for tc in msg.tool_calls:
                fn_args = json.loads(tc.function.arguments or "{}")
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": fn_args
                })

        if tool_calls:
            return LLMResponse(thought=thought, tool_calls=tool_calls)
        else:
            return LLMResponse(thought=thought, final_answer=thought)


def get_llm_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> BaseLLMProvider:
    """Factory function to instantiate configured LLM Provider."""
    provider = (provider_name or os.getenv("LLM_PROVIDER", "gemini")).lower()

    if provider in ("mock", "demo"):
        return MockProvider()

    if provider == "gemini":
        try:
            return GeminiProvider(api_key=api_key, model_name=model_name)
        except (ValueError, ImportError) as e:
            # If no API key set or import fails, check if OpenAI is available or fallback gracefully to Mock with warning
            if os.getenv("OPENAI_API_KEY"):
                print("Notice: GEMINI_API_KEY missing or error, switching to OPENAI_API_KEY.")
                return OpenAIProvider(model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
            else:
                print(f"\n[*] NOTICE: Gemini initialization notice ({str(e)}).")
                print("   Running agent in DEMO/MOCK mode for offline testing.")
                print("   To use real LLM intelligence, verify your GEMINI_API_KEY in your .env file.\n")
                return MockProvider()
    elif provider == "openai":
        try:
            return OpenAIProvider(api_key=api_key, model_name=model_name)
        except ValueError:
            print("\n[*] NOTICE: No OPENAI_API_KEY found.")
            print("   Running agent in DEMO/MOCK mode for offline testing.")
            print("   To use real LLM intelligence, add OPENAI_API_KEY to your .env file.\n")
            return MockProvider()
    else:
        raise ValueError(f"Unsupported provider: '{provider}'. Choose 'gemini', 'openai', or 'mock'.")
