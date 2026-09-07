"""
Tool: create_calendar_event — Create a Google Calendar event.
"""

import logging
from typing import Dict, Any, Optional, List

from core.agent import agent

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "create_calendar_event",
    "description": "Create an event on the user's Google Calendar.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Event title/name."
            },
            "start_time": {
                "type": "string",
                "description": "Start time in ISO 8601 format."
            },
            "end_time": {
                "type": "string",
                "description": "End time in ISO 8601 format."
            },
            "description": {
                "type": "string",
                "description": "Optional event description."
            },
            "location": {
                "type": "string",
                "description": "Optional event location."
            },
            "attendees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of attendee email addresses."
            }
        },
        "required": ["title", "start_time", "end_time"]
    }
}


async def execute(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    attendees: Optional[List[str]] = None,
) -> Dict[str, Any]:
    from datetime import datetime

    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        return {
            "status": "success",
            "message": f"Calendar event '{title}' created for {start_dt.strftime('%B %d, %Y at %I:%M %p')}.",
            "event": {
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                "description": description,
                "location": location,
                "attendees": attendees or [],
                "duration_minutes": int((end_dt - start_dt).total_seconds() / 60),
            }
        }
    except ValueError as e:
        return {"status": "error", "message": f"Invalid date format: {e}"}


agent.register_tool(TOOL_DEF, execute)
