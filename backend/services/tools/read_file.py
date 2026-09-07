"""
Tool: read_file — Read contents of a file.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from core.agent import agent

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "read_file",
    "description": "Read the contents of a file from the user's system. Limited to text files under 100KB.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Full path to the file to read."
            }
        },
        "required": ["file_path"]
    }
}

MAX_FILE_SIZE = 100 * 1024  # 100KB


async def execute(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)

    if not path.exists():
        return {"status": "error", "message": f"File not found: {file_path}"}

    if not path.is_file():
        return {"status": "error", "message": f"Not a file: {file_path}"}

    if path.stat().st_size > MAX_FILE_SIZE:
        return {
            "status": "error",
            "message": f"File too large ({path.stat().st_size / 1024:.1f}KB). Maximum is 100KB.",
        }

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return {
            "status": "success",
            "file_path": file_path,
            "content": content,
            "size_bytes": len(content.encode("utf-8")),
            "lines": content.count("\n") + 1,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


agent.register_tool(TOOL_DEF, execute)
