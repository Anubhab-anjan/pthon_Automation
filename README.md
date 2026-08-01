# 🤖 Autonomous CLI AI Agent (Pure Python)

A lightweight, autonomous, CLI-driven AI agent in **pure Python** inspired by OpenClaw and AutoGPT ReAct execution loops.

`pthon_Automation` has been refactored into a full-featured agent system that accepts goals from the terminal, formulates multi-step execution plans, dynamically invokes automation tools in an observation loop, and continues listening for your next request.

---

## 🌟 Key Features

- **Pure Python Implementation:** Built with standard library and minimal lightweight dependencies (`google-genai` / `openai`, `pillow`, `yt-dlp`). Zero heavy framework overhead (no LangChain/AutoGen/CrewAI).
- **ReAct Execution Engine:** Implements the continuous loop:
  `Task Goal ➔ Plan ➔ Tool Call ➔ Execute ➔ Observe ➔ Refine ➔ Complete ➔ Next Task`
- **Dynamic Tool Registry:** Decorate any type-annotated Python function with `@tool` to automatically generate function declarations for the LLM.
- **Multi-Provider LLM Layer:** Primary support for **Google Gemini** (`gemini-2.5-flash`), with built-in support for **OpenAI** (`gpt-4o-mini`).
- **Safety & Guardrails:** Built-in dry-run simulation mode (`--dry-run`) and interactive confirmation prompts before executing destructive actions (file deletion, mass moves/renames, shell commands).
- **Short-Term Context Memory:** Tracks conversation history, tool calls, and system observations per task session, with clean reset between tasks.

---

## 🏗️ Core Architecture

```
pthon_Automation/
├── agent/
│   ├── __init__.py
│   ├── loop.py           # ReAct action-observation loop controller
│   ├── tools.py          # Tool registry decorator (@tool) & schema generator
│   ├── memory.py         # Short-term execution memory & context tracking
│   ├── llm.py            # Gemini & OpenAI provider abstraction layer
│   └── guardrails.py     # Dry-run policy & interactive safety manager
├── tools/
│   ├── __init__.py       # Auto-registers tool modules
│   ├── file_tools.py     # File organization, move, copy, read, write tools
│   ├── media_tools.py    # Refactored Image Editor & YouTube Downloader tools
│   ├── os_tools.py       # Shell command execution & system info tools
│   └── web_tools.py      # Web fetching & DuckDuckGo search tools
├── main.py               # Interactive CLI terminal loop entry point
├── .env.example          # Environment key & configuration template
├── requirements.txt      # Lightweight dependencies
└── README.md             # Documentation
```

---

## 🛠️ Included Automation Tools

| Category | Tool | Description |
| :--- | :--- | :--- |
| **Files** | `organize_files_by_extension` | Automatically categorizes files into subfolders (`PDFs/`, `Images/`, `Documents/`, etc.) |
| | `list_directory` | Lists contents, types, and sizes in a directory |
| | `create_directory` | Creates single or nested directories |
| | `move_file` | Moves files or directories (Safety check required) |
| | `copy_file` | Copies files to target destinations |
| | `delete_file` | Removes files or empty folders (Safety check required) |
| | `read_file_content` | Reads raw text content from files |
| | `write_file_content` | Writes/overwrites content to files (Safety check required) |
| **Media** | `batch_edit_images` | Batch sharpens, rotates, adjusts contrast, and converts images to grayscale |
| | `download_youtube_video` | Downloads YouTube videos at highest resolution via `yt-dlp` / `pytube` |
| | `get_youtube_video_info` | Retrieves video title, view count, uploader, and duration |
| **System** | `execute_shell_command` | Executes arbitrary terminal shell commands (Safety check required) |
| | `get_system_info` | Inspects OS platform, Python version, working directory, and user environment |
| **Web** | `fetch_webpage_content` | Extracts plain text from web page URLs |
| | `search_web` | Searches DuckDuckGo for real-time web results |

---

## 🚀 Quick Start

### 1. Installation & Setup

Clone the repository and install the lightweight requirements:

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash
```

### 3. Launch Interactive CLI Agent

Run `main.py` to start the CLI session:

```bash
python main.py
```

Sample CLI output:

```text
=================================================================
🤖  AUTONOMOUS CLI AI AGENT  (ReAct Loop Engine)
=================================================================
  • Provider       : GEMINI
  • Model          : gemini-2.5-flash
  • Dry-Run Mode   : DISABLED
  • Safety Approval: INTERACTIVE CONFIRMATION
  • Available Tools: 15 loaded
=================================================================

🤖 Agent Ready. Type your request (or 'exit' to quit):

 > Organize all PDF files in my Downloads folder into a "PDFs" directory.
```

---

## 🛡️ Safety & CLI Options

You can pass command-line flags to customize safety behavior and model selection:

```bash
# Enable dry-run mode (simulates destructive tools like delete, move, or shell execution without running them)
python main.py --dry-run

# Enable auto-approve mode (skips interactive [y/N] safety confirmations)
python main.py --auto-approve

# Use OpenAI instead of Gemini
python main.py --provider openai --model gpt-4o-mini

# Customize maximum ReAct loop steps per task (default: 15)
python main.py --max-steps 10
```

---

## ➕ Adding Your Own Custom Tools

Creating new tools is as simple as defining a Python function with type hints, a docstring, and the `@tool` decorator:

```python
from agent.tools import tool

@tool(is_destructive=False)
def calculate_file_hash(filepath: str) -> str:
    """
    Calculate SHA256 hash of a local file.

    Args:
        filepath: Path to target file.
    """
    import hashlib
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()
```

Save the tool in `tools/` and it will automatically be loaded and made available to the LLM agent on startup!
