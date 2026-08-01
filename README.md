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

## 💻 Step-by-Step Setup Guide for your Laptop

Follow these steps to set up and run the Autonomous AI Agent on your Windows, macOS, or Linux laptop.

### 📋 Prerequisites
1. **Python 3.10+** installed on your laptop ([Download Python](https://www.python.org/downloads/)).
2. **Git** installed ([Download Git](https://git-scm.com/downloads)).
3. A **Google Gemini API Key** ([Get Free Gemini API Key](https://aistudio.google.com/app/apikey)).

---

### Step 1: Clone the Repository

Open your terminal (Command Prompt / PowerShell on Windows, or Terminal on macOS/Linux) and run:

```bash
git clone https://github.com/Anubhab-anjan/pthon_Automation.git
cd pthon_Automation
```

---

### Step 2: Create & Activate a Virtual Environment

It is recommended to use a virtual environment to keep dependencies clean:

#### 🪟 Windows (Command Prompt / PowerShell)
```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### 🍎 macOS / 🐧 Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Step 3: Install Required Dependencies

Install the lightweight required packages:

```bash
pip install -r requirements.txt
```

---

### Step 4: Configure Your API Key

Create a `.env` configuration file from the template:

#### 🪟 Windows (CMD / PowerShell)
```cmd
copy .env.example .env
```

#### 🍎 macOS / 🐧 Linux
```bash
cp .env.example .env
```

Open the newly created `.env` file in VS Code, Notepad, or any text editor, and add your Gemini API key:

```ini
GEMINI_API_KEY=your_actual_gemini_api_key_here
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash
```

*(Note: If you don't add an API key, the agent will automatically launch in **Offline DEMO/MOCK Mode** so you can still test tool execution loops!)*

---

### Step 5: Launch the AI Agent!

Start the interactive CLI agent loop:

```bash
python main.py
```

You will see the agent startup banner:

```text
=================================================================
[+] AUTONOMOUS CLI AI AGENT  (ReAct Loop Engine)
=================================================================
  * Provider       : GEMINI
  * Model          : gemini-2.5-flash
  * Dry-Run Mode   : DISABLED
  * Safety Approval: INTERACTIVE CONFIRMATION
  * Available Tools: 16 loaded
=================================================================

[+] Agent Ready. Type your request (or 'exit' to quit):

 > 
```

Now type any goal! For example:
- `open instagram`
- `organize all PDF files in my Downloads folder`
- `download YouTube video https://www.youtube.com/watch?v=...`
- `batch edit images in ./imgs`
- `search web for Python 3.12 release notes`
- `get system info`

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
| | `open_web_url` | Opens web URLs or apps (e.g. Instagram, Google) in default system browser |
| | `get_system_info` | Inspects OS platform, Python version, working directory, and user environment |
| **Web** | `fetch_webpage_content` | Extracts plain text from web page URLs |
| | `search_web` | Searches DuckDuckGo for real-time web results |

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

# Use Mock/Demo mode (offline test mode)
python main.py --provider mock

# Customize maximum ReAct loop steps per task (default: 15)
python main.py --max-steps 10
```

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
│   ├── os_tools.py       # Shell command execution & browser URL tools
│   └── web_tools.py      # Web fetching & DuckDuckGo search tools
├── main.py               # Interactive CLI terminal loop entry point
├── .env.example          # Environment key & configuration template
├── .gitignore            # Git exclusion rules (safely hides your .env key)
├── requirements.txt      # Lightweight dependencies
└── README.md             # Documentation
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
