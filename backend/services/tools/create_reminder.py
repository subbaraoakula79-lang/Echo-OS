"""
Tool: create_reminder — Schedule a reminder for the user.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from core.agent import agent

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "create_reminder",
    "description": "Set a reminder for the user at a specific date and time. Use when they say 'remind me' or 'don't let me forget'.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The reminder message to deliver."
            },
            "trigger_time": {
                "type": "string",
                "description": "When to trigger the reminder, in ISO 8601 format."
            },
            "is_recurring": {
                "type": "boolean",
                "description": "Whether this reminder repeats. Default: false."
            }
        },
        "required": ["message", "trigger_time"]
    }
}


async def execute(
    message: str,
    trigger_time: str,
    is_recurring: bool = False,
) -> Dict[str, Any]:
    try:
        dt = datetime.fromisoformat(trigger_time)
        formatted = dt.strftime("%B %d, %Y at %I:%M %p")

        return {
            "status": "success",
            "message": f"Reminder set: '{message}' for {formatted}.",
            "reminder": {
                "message": message,
                "trigger_time": trigger_time,
                "formatted_time": formatted,
                "is_recurring": is_recurring,
            }
        }
    except ValueError:
        return {
            "status": "error",
            "message": f"Invalid time format: {trigger_time}. Use ISO 8601 format."
        }


agent.register_tool(TOOL_DEF, execute)
