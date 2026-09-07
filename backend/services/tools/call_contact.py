"""
Tool: call_contact — Make a phone call through the Android companion app.
"""

import logging
from typing import Dict, Any

from core.agent import agent

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "call_contact",
    "description": "Initiate a phone call to a contact through the user's Android companion device. ALWAYS confirm with the user before calling.",
    "parameters": {
        "type": "object",
        "properties": {
            "contact_name": {
                "type": "string",
                "description": "Name of the contact to call."
            },
            "phone_number": {
                "type": "string",
                "description": "Phone number to call. Required if contact is not in the phone's contacts."
            }
        },
        "required": ["contact_name"]
    }
}


async def execute(contact_name: str, phone_number: str = "") -> Dict[str, Any]:
    # This sends a FCM push to the Android companion app
    return {
        "status": "confirmation_required",
        "message": f"Ready to call {contact_name}" + (f" at {phone_number}" if phone_number else "") + ". Shall I proceed?",
        "action": {
            "type": "call",
            "contact_name": contact_name,
            "phone_number": phone_number,
        }
    }


agent.register_tool(TOOL_DEF, execute)
