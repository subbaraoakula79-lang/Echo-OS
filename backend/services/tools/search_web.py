"""
Tool: search_web — Search the internet using Serper API.
"""

import logging
from typing import Dict, Any

import httpx

from core.agent import agent
from core.config import settings

logger = logging.getLogger(__name__)

TOOL_DEF = {
    "name": "search_web",
    "description": "Search the internet for current information. Use this when the user asks about recent events, facts, or needs information you don't have.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up on the internet."
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return (default: 5, max: 10).",
                "default": 5
            }
        },
        "required": ["query"]
    }
}


async def execute(query: str, num_results: int = 5) -> Dict[str, Any]:
    if not settings.SERPER_API_KEY:
        return {"status": "error", "message": "Serper API key not configured. Unable to search the web."}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": settings.SERPER_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"q": query, "num": min(num_results, 10)},
            )
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("organic", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            })

        answer_box = data.get("answerBox", {})
        knowledge_graph = data.get("knowledgeGraph", {})

        return {
            "status": "success",
            "query": query,
            "answer_box": answer_box.get("answer") or answer_box.get("snippet"),
            "knowledge_graph": knowledge_graph.get("description"),
            "results": results,
        }
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return {"status": "error", "message": str(e)}


agent.register_tool(TOOL_DEF, execute)
