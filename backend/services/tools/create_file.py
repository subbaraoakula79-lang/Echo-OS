"""
Tool: create_file — Create a new file with content.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from core.agent import agent

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "create_file",
    "description": "Create a new file with optional content. Requires user confirmation for overwriting existing files.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Full path for the new file."
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file."
            }
        },
        "required": ["file_path"]
    }
}


async def execute(file_path: str, content: str = "") -> Dict[str, Any]:
    path = Path(file_path)

    if path.exists():
        return {
            "status": "confirmation_required",
            "message": f"File already exists at {file_path}. Confirm overwrite?",
        }

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "message": f"File created: {file_path}",
            "size_bytes": len(content.encode("utf-8")),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


agent.register_tool(TOOL_DEF, execute)
