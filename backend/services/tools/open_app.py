"""
Tool: open_app — Open a system application.
"""

import logging
import platform
import subprocess
from typing import Dict, Any

from core.agent import agent

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "open_app",
    "description": "Open a desktop application on the user's computer. Works on Windows, macOS, and Linux.",
    "parameters": {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name of the application to open (e.g., 'Chrome', 'Notepad', 'Calculator', 'VS Code')."
            }
        },
        "required": ["app_name"]
    }
}

# Common app mappings per OS
APP_MAP = {
    "windows": {
        "chrome": "start chrome",
        "google chrome": "start chrome",
        "firefox": "start firefox",
        "notepad": "start notepad",
        "calculator": "start calc",
        "calc": "start calc",
        "file explorer": "start explorer",
        "explorer": "start explorer",
        "terminal": "start wt",
        "cmd": "start cmd",
        "powershell": "start powershell",
        "vs code": "code",
        "vscode": "code",
        "visual studio code": "code",
        "spotify": "start spotify:",
        "settings": "start ms-settings:",
        "task manager": "start taskmgr",
        "paint": "start mspaint",
        "word": "start winword",
        "excel": "start excel",
        "outlook": "start outlook",
    },
    "darwin": {
        "chrome": "open -a 'Google Chrome'",
        "safari": "open -a Safari",
        "finder": "open -a Finder",
        "terminal": "open -a Terminal",
        "vs code": "open -a 'Visual Studio Code'",
        "spotify": "open -a Spotify",
        "calculator": "open -a Calculator",
        "notes": "open -a Notes",
    },
    "linux": {
        "chrome": "google-chrome &",
        "firefox": "firefox &",
        "terminal": "x-terminal-emulator &",
        "files": "nautilus &",
        "vs code": "code &",
        "calculator": "gnome-calculator &",
    },
}


async def execute(app_name: str) -> Dict[str, Any]:
    system = platform.system().lower()
    if system == "windows":
        os_key = "windows"
    elif system == "darwin":
        os_key = "darwin"
    else:
        os_key = "linux"

    app_lower = app_name.lower().strip()
    command = APP_MAP.get(os_key, {}).get(app_lower)

    if not command:
        # Try to open generically
        if os_key == "windows":
            command = f"start {app_name}"
        elif os_key == "darwin":
            command = f"open -a '{app_name}'"
        else:
            command = f"{app_name} &"

    try:
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {
            "status": "success",
            "message": f"Opening {app_name}...",
        }
    except Exception as e:
        logger.error(f"Failed to open {app_name}: {e}")
        return {
            "status": "error",
            "message": f"Could not open {app_name}: {str(e)}",
        }


agent.register_tool(TOOL_DEF, execute)
