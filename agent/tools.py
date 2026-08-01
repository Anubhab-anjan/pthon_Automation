"""
Tool Registry and Schema Conversion Engine.
Converts Python functions with type hints and docstrings into LLM-usable tool schemas.
"""

import inspect
import json
import functools
import traceback
from typing import Callable, Dict, Any, List, Optional, get_type_hints

class ToolRegistry:
    """
    Registry for functions exposed as tools to the LLM agent.
    """

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._destructive_tools: set = set()

    def register(self, func: Optional[Callable] = None, *, name: Optional[str] = None, is_destructive: bool = False):
        """
        Decorator or method to register a python function as an agent tool.
        """
        def decorator(f: Callable) -> Callable:
            tool_name = name or f.__name__
            self._tools[tool_name] = f
            self._schemas[tool_name] = self._generate_schema(f, tool_name)
            if is_destructive:
                self._destructive_tools.add(tool_name)
            return f

        if func is None:
            return decorator
        return decorator(func)

    def is_destructive(self, tool_name: str) -> bool:
        """Check if a tool is flagged as potentially destructive."""
        return tool_name in self._destructive_tools

    def get_tool(self, tool_name: str) -> Optional[Callable]:
        """Get function by tool name."""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """List names of all registered tools."""
        return list(self._tools.keys())

    def get_openai_schemas(self) -> List[Dict[str, Any]]:
        """Get list of tool schemas in OpenAI function calling format."""
        schemas = []
        for name, schema in self._schemas.items():
            schemas.append({
                "type": "function",
                "function": schema
            })
        return schemas

    def get_gemini_declarations(self) -> List[Dict[str, Any]]:
        """Get list of function declarations for Gemini SDK."""
        declarations = []
        for name, schema in self._schemas.items():
            declarations.append(schema)
        return declarations

    def invoke(self, tool_name: str, kwargs: Dict[str, Any]) -> str:
        """
        Execute a registered tool by name with arguments.
        Returns a standardized string observation.
        """
        if tool_name not in self._tools:
            return f"Error: Tool '{tool_name}' is not registered. Available tools: {', '.join(self.list_tools())}"

        func = self._tools[tool_name]
        try:
            # Clean up kwargs if LLM passed nested structures or json string
            cleaned_kwargs = {}
            for k, v in kwargs.items():
                if isinstance(v, str) and (v.startswith("{") or v.startswith("[")):
                    try:
                        cleaned_kwargs[k] = json.loads(v)
                    except Exception:
                        cleaned_kwargs[k] = v
                else:
                    cleaned_kwargs[k] = v

            result = func(**cleaned_kwargs)
            if result is None:
                return f"Tool '{tool_name}' executed successfully with no return output."
            elif isinstance(result, (dict, list)):
                return json.dumps(result, indent=2, default=str)
            else:
                return str(result)
        except Exception as e:
            tb = traceback.format_exc()
            return f"Error executing tool '{tool_name}' with args {kwargs}:\n{str(e)}\n\nTraceback:\n{tb}"

    def _py_type_to_json_type(self, py_type: Any) -> str:
        """Map Python types to JSON Schema types."""
        if py_type in (int,):
            return "integer"
        elif py_type in (float,):
            return "number"
        elif py_type in (bool,):
            return "boolean"
        elif py_type in (list, tuple, List):
            return "array"
        elif py_type in (dict, Dict):
            return "object"
        else:
            return "string"

    def _generate_schema(self, func: Callable, tool_name: str) -> Dict[str, Any]:
        """Generate JSON schema description for a given function."""
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or f"Tool function {tool_name}"
        
        type_hints = {}
        try:
            type_hints = get_type_hints(func)
        except Exception:
            pass

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue

            param_type = type_hints.get(param_name, param.annotation)
            json_type = self._py_type_to_json_type(param_type)

            param_desc = f"Argument {param_name}"

            properties[param_name] = {
                "type": json_type,
                "description": param_desc
            }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "name": tool_name,
            "description": doc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

# Global tool registry instance
registry = ToolRegistry()

def tool(func: Optional[Callable] = None, *, name: Optional[str] = None, is_destructive: bool = False):
    """
    Decorator to register a function as a tool.
    Usage:
        @tool
        def my_tool(x: int) -> int: ...

        @tool(is_destructive=True)
        def delete_file(path: str) -> str: ...
    """
    return registry.register(func, name=name, is_destructive=is_destructive)
