"""
Operating System & Terminal Command Automation Tools.
"""

import os
import sys
import platform
import subprocess
from agent.tools import tool

@tool(is_destructive=True)
def execute_shell_command(command: str) -> str:
    """
    Execute an arbitrary shell/terminal command on the host OS.
    Use with caution.

    Args:
        command: The shell command string to run (e.g. 'dir', 'python --version', 'git status').

    Returns:
        Combined stdout and stderr from command execution.
    """
    try:
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        output = []
        if process.stdout:
            output.append(f"STDOUT:\n{process.stdout.strip()}")
        if process.stderr:
            output.append(f"STDERR:\n{process.stderr.strip()}")

        result_str = "\n".join(output) if output else "(Command executed with no output)"
        return f"Exit Code: {process.returncode}\n{result_str}"
    except subprocess.TimeoutExpired:
        return f"Error: Command '{command}' timed out after 60 seconds."
    except Exception as e:
        return f"Error executing command '{command}': {str(e)}"


@tool
def get_system_info() -> str:
    """
    Get host operating system details, platform, python version, and working directory.
    """
    info = [
        f"Operating System: {platform.system()} {platform.release()} ({platform.version()})",
        f"Architecture: {platform.machine()}",
        f"Python Version: {sys.version.split()[0]}",
        f"Current Working Directory: {os.getcwd()}",
        f"User Environment Home: {os.path.expanduser('~')}"
    ]
    return "\n".join(info)


@tool
def open_web_url(url: str) -> str:
    """
    Open a web URL or social site (e.g., Instagram, YouTube, Google) in the default system web browser.

    Args:
        url: Web URL or domain name to open in browser (e.g. 'https://instagram.com' or 'instagram.com').
    """
    import webbrowser
    target_url = url if url.startswith(("http://", "https://")) else f"https://{url}"
    try:
        webbrowser.open(target_url)
        return f"Successfully launched system web browser for '{target_url}'."
    except Exception as e:
        return f"Failed to open URL '{target_url}': {str(e)}"
