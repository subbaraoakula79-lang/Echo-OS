"""
ECHO OS — Search Service
Serper web search with research mode.
"""

import logging
from typing import Dict, Any, List, Optional

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


async def web_search(query: str, num_results: int = 10) -> Dict[str, Any]:
    """Standard web search via Serper API."""
    if not settings.SERPER_API_KEY:
        return {"error": "Serper API key not configured"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": settings.SERPER_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"q": query, "num": num_results},
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Serper search error: {e}")
        return {"error": str(e)}


async def news_search(query: str, num_results: int = 10) -> Dict[str, Any]:
    """Search recent news via Serper API."""
    if not settings.SERPER_API_KEY:
        return {"error": "Serper API key not configured"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://google.serper.dev/news",
                headers={
                    "X-API-KEY": settings.SERPER_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"q": query, "num": num_results},
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Serper news search error: {e}")
        return {"error": str(e)}


async def research_mode(
    topic: str,
    sub_queries: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Multi-query research mode: generate sub-queries and aggregate results."""
    queries = sub_queries or [
        topic,
        f"{topic} latest news",
        f"{topic} overview",
    ]

    all_results = []
    for q in queries[:5]:  # Max 5 sub-queries
        result = await web_search(q, num_results=5)
        if "error" not in result:
            for item in result.get("organic", []):
                all_results.append({
                    "query": q,
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })

    return {
        "topic": topic,
        "queries_executed": len(queries),
        "total_results": len(all_results),
        "results": all_results,
    }
