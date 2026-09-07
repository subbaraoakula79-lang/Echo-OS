"""
Tool: create_task — Create a new task for the user.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from core.agent import agent

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "create_task",
    "description": "Create a new task or to-do item for the user. Use when they ask to remember, track, or schedule something.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title/name of the task."
            },
            "description": {
                "type": "string",
                "description": "Optional detailed description."
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "urgent"],
                "description": "Priority level. Default: medium."
            },
            "due_date": {
                "type": "string",
                "description": "Due date in ISO 8601 format (e.g., 2024-12-25T20:00:00). Optional."
            }
        },
        "required": ["title"]
    }
}


async def execute(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: Optional[str] = None,
) -> Dict[str, Any]:
    # Actual DB operation happens in the API layer via context
    # Tool returns structured data for the agent to confirm
    result = {
        "status": "success",
        "message": f"Task '{title}' created successfully.",
        "task": {
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
        }
    }

    if due_date:
        try:
            dt = datetime.fromisoformat(due_date)
            result["task"]["due_date_formatted"] = dt.strftime("%B %d, %Y at %I:%M %p")
        except ValueError:
            pass

    logger.info(f"Task created: {title}")
    return result


agent.register_tool(TOOL_DEF, execute)
