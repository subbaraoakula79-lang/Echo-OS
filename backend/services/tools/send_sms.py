"""
Tool: send_sms — Send an SMS through the Android companion app.
"""

import logging
from typing import Dict, Any

from core.agent import agent

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "send_sms",
    "description": "Send a text message (SMS) through the user's Android phone. ALWAYS confirm message content and recipient before sending.",
    "parameters": {
        "type": "object",
        "properties": {
            "contact_name": {
                "type": "string",
                "description": "Name of the recipient."
            },
            "phone_number": {
                "type": "string",
                "description": "Recipient's phone number."
            },
            "message": {
                "type": "string",
                "description": "The text message to send."
            }
        },
        "required": ["contact_name", "message"]
    }
}


async def execute(contact_name: str, message: str, phone_number: str = "") -> Dict[str, Any]:
    return {
        "status": "confirmation_required",
        "message": f"Ready to send SMS to {contact_name}: \"{message}\". Shall I send it?",
        "action": {
            "type": "sms",
            "contact_name": contact_name,
            "phone_number": phone_number,
            "message": message,
        }
    }


agent.register_tool(TOOL_DEF, execute)
