"""
Tool: search_files — Search for files on the local system.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

from core.agent import agent

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "search_files",
    "description": "Search for files on the user's computer by name, extension, or content pattern.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "File name or pattern to search for (e.g., 'report.pdf', '*.txt')."
            },
            "path": {
                "type": "string",
                "description": "Directory to search in. Defaults to user's home directory."
            },
            "extensions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by file extensions (e.g., ['.pdf', '.docx'])."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results (default: 20)."
            }
        },
        "required": ["query"]
    }
}


async def execute(
    query: str,
    path: Optional[str] = None,
    extensions: Optional[List[str]] = None,
    max_results: int = 20,
) -> Dict[str, Any]:
    search_path = Path(path) if path else Path.home()

    if not search_path.exists():
        return {"status": "error", "message": f"Path does not exist: {search_path}"}

    results = []
    query_lower = query.lower()

    try:
        for root, dirs, files in os.walk(search_path):
            # Skip hidden and system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in (
                'node_modules', '__pycache__', '.git', 'venv', '.venv',
                'AppData', 'Library', '$Recycle.Bin',
            )]

            for filename in files:
                if len(results) >= max_results:
                    break

                if query_lower in filename.lower():
                    filepath = Path(root) / filename
                    ext = filepath.suffix.lower()

                    if extensions and ext not in [e.lower() for e in extensions]:
                        continue

                    try:
                        stat = filepath.stat()
                        results.append({
                            "name": filename,
                            "path": str(filepath),
                            "size_kb": round(stat.st_size / 1024, 1),
                            "modified": stat.st_mtime,
                        })
                    except (PermissionError, OSError):
                        continue

            if len(results) >= max_results:
                break

    except PermissionError:
        return {"status": "error", "message": f"Permission denied accessing {search_path}"}

    return {
        "status": "success",
        "query": query,
        "search_path": str(search_path),
        "count": len(results),
        "results": results,
    }


agent.register_tool(TOOL_DEF, execute)
