from core.agent import agent
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Search Web Tool
search_web_def = {
    "name": "search_web",
    "description": "Searches the internet for information.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query."}
        },
        "required": ["query"]
    }
}

async def search_web_exec(query: str) -> Dict[str, Any]:
    logger.info(f"Executing web search: {query}")
    # In a full implementation, this hits the Serper API
    return {"status": "success", "results": f"Mock results for '{query}': Example finding."}

agent.register_tool(search_web_def, search_web_exec)

# Create Task Tool
create_task_def = {
    "name": "create_task",
    "description": "Creates a new task for the user.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"}
        },
        "required": ["title"]
    }
}

async def create_task_exec(title: str, description: str = "") -> Dict[str, Any]:
    logger.info(f"Creating task: {title}")
    # In a full implementation, this saves to PostgreSQL
    return {"status": "success", "message": f"Task '{title}' has been successfully scheduled."}

agent.register_tool(create_task_def, create_task_exec)
