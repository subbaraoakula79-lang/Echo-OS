"""
Tool: send_email — Draft and send emails via Gmail API.
"""

import logging
from typing import Dict, Any, Optional, List

from core.agent import agent

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "send_email",
    "description": "Draft or send an email using the user's Gmail account. ALWAYS ask for confirmation before sending.",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of recipient email addresses."
            },
            "subject": {
                "type": "string",
                "description": "Email subject line."
            },
            "body": {
                "type": "string",
                "description": "Email body content."
            },
            "cc": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional CC recipients."
            },
            "draft_only": {
                "type": "boolean",
                "description": "If true, save as draft instead of sending. Default: true.",
            }
        },
        "required": ["to", "subject", "body"]
    }
}


async def execute(
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    draft_only: bool = True,
) -> Dict[str, Any]:
    # This will integrate with google_services.py for actual sending
    action = "drafted" if draft_only else "queued for sending"

    return {
        "status": "success",
        "message": f"Email {action} successfully.",
        "email": {
            "to": to,
            "cc": cc or [],
            "subject": subject,
            "body_preview": body[:200] + "..." if len(body) > 200 else body,
            "is_draft": draft_only,
        },
        "confirmation_required": not draft_only,
    }


agent.register_tool(TOOL_DEF, execute)
