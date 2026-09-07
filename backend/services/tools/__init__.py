"""
ECHO OS — Tool Registry
Auto-discovery and registration of all tools with the ECHO Agent.
"""

import logging
from core.agent import agent

logger = logging.getLogger(__name__)


def register_all_tools():
    """Import all tool modules to trigger their registration."""
    from services.tools import (  # noqa: F401
        search_web,
        create_task,
        create_reminder,
        open_app,
        search_files,
        create_file,
        read_file,
        send_email,
        create_calendar_event,
        call_contact,
        send_sms,
    )
    logger.info(f"Registered {len(agent.tools)} tools with ECHO Agent")
