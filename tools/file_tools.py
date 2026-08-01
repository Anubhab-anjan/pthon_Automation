"""
File System & Folder Management Automation Tools.
"""

import os
import shutil
from typing import Dict, List, Optional
from agent.tools import tool

@tool
def list_directory(path: str = ".") -> str:
    """
    List contents of a directory including file names, types (file vs directory), and sizes.

    Args:
        path: Path to the target directory. Defaults to current directory standard "."

    Returns:
        Formatted summary of items in directory.
    """
    if not os.path.exists(path):
        return f"Error: Path '{path}' does not exist."

    if not os.path.isdir(path):
        return f"Error: Path '{path}' is a file, not a directory."

    items = os.listdir(path)
    if not items:
        return f"Directory '{path}' is empty."

    lines = [f"Directory contents of '{os.path.abspath(path)}':"]
    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            lines.append(f"  [DIR]  {item}")
        else:
            size = os.path.getsize(full_path)
            lines.append(f"  [FILE] {item} ({size} bytes)")

    return "\n".join(lines)


@tool
def create_directory(path: str) -> str:
    """
    Create a new directory (and any necessary parent subdirectories).

    Args:
        path: Absolute or relative directory path to create.
    """
    try:
        os.makedirs(path, exist_ok=True)
        return f"Successfully created directory '{os.path.abspath(path)}'."
    except Exception as e:
        return f"Failed to create directory '{path}': {str(e)}"


@tool(is_destructive=True)
def move_file(source: str, destination: str) -> str:
    """
    Move a file or folder from source path to destination path.

    Args:
        source: Source file or folder path.
        destination: Target file path or directory.
    """
    if not os.path.exists(source):
        return f"Error: Source '{source}' does not exist."

    try:
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        shutil.move(source, destination)
        return f"Successfully moved '{source}' to '{destination}'."
    except Exception as e:
        return f"Failed to move '{source}' to '{destination}': {str(e)}"


@tool
def copy_file(source: str, destination: str) -> str:
    """
    Copy a file from source to destination.

    Args:
        source: Source file path.
        destination: Destination file or folder path.
    """
    if not os.path.exists(source):
        return f"Error: Source file '{source}' does not exist."

    try:
        if os.path.isdir(destination):
            dest_file = os.path.join(destination, os.path.basename(source))
        else:
            dest_file = destination
            dest_dir = os.path.dirname(dest_file)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)

        shutil.copy2(source, dest_file)
        return f"Successfully copied '{source}' to '{dest_file}'."
    except Exception as e:
        return f"Failed to copy file: {str(e)}"


@tool(is_destructive=True)
def delete_file(path: str) -> str:
    """
    Delete a file or empty directory.

    Args:
        path: File or empty directory path to remove.
    """
    if not os.path.exists(path):
        return f"Error: Path '{path}' does not exist."

    try:
        if os.path.isdir(path):
            os.rmdir(path)
            return f"Successfully removed directory '{path}'."
        else:
            os.remove(path)
            return f"Successfully deleted file '{path}'."
    except Exception as e:
        return f"Failed to delete '{path}': {str(e)}"


@tool
def read_file_content(path: str) -> str:
    """
    Read text content from a local file.

    Args:
        path: Path to the target text file.
    """
    if not os.path.exists(path):
        return f"Error: File '{path}' does not exist."

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content if content else "(File is empty)"
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"


@tool(is_destructive=True)
def write_file_content(path: str, content: str) -> str:
    """
    Write or overwrite text content to a file.

    Args:
        path: Path to target file.
        content: Text content string to write.
    """
    try:
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{path}'."
    except Exception as e:
        return f"Failed to write file '{path}': {str(e)}"


@tool(is_destructive=True)
def organize_files_by_extension(folder_path: str = ".") -> str:
    """
    Organize all files in a folder into subdirectories categorized by file extension.
    For example: .pdf files -> PDFs/, .jpg/.png -> Images/, .py -> Code/, etc.

    Args:
        folder_path: Path to folder to organize. Defaults to current directory ".".
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return f"Error: Invalid directory '{folder_path}'."

    extension_map = {
        "PDFs": [".pdf"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "Documents": [".doc", ".docx", ".txt", ".rtf", ".odt", ".csv", ".xlsx"],
        "Audio": [".mp3", ".wav", ".flac", ".m4a"],
        "Videos": [".mp4", ".mkv", ".mov", ".avi"],
        "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
        "Code": [".py", ".js", ".html", ".css", ".json", ".md", ".sh", ".bat"]
    }

    moved_counts: Dict[str, int] = {}
    total_moved = 0

    protected_files = {'main.py', 'requirements.txt', 'README.md', '.env', '.env.example', '.gitignore', 'ImageEditor.py', 'ytdownloader.py'}

    for filename in os.listdir(folder_path):
        if filename in protected_files:
            continue
        full_path = os.path.join(folder_path, filename)
        if os.path.isdir(full_path):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            category = "Others"
        else:
            category = "Others"
            for cat, exts in extension_map.items():
                if ext in exts:
                    category = cat
                    break

        target_dir = os.path.join(folder_path, category)
        os.makedirs(target_dir, exist_ok=True)
        dest_path = os.path.join(target_dir, filename)

        try:
            shutil.move(full_path, dest_path)
            moved_counts[category] = moved_counts.get(category, 0) + 1
            total_moved += 1
        except Exception as e:
            pass

    if total_moved == 0:
        return f"No files were moved in '{folder_path}'."

    summary = [f"Successfully organized {total_moved} files in '{folder_path}':"]
    for cat, count in moved_counts.items():
        summary.append(f"  - {cat}: {count} files")
    return "\n".join(summary)
