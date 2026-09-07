"""
ECHO OS — Search API Routes
Web search and local file search endpoints.
"""

from fastapi import APIRouter, Depends
from core.dependencies import get_current_user
from db.models import User
from schemas.models import WebSearchRequest, FileSearchRequest
from services.search import web_search, research_mode
from services.tools.search_files import execute as search_files_exec

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/web")
async def search_web(
    req: WebSearchRequest,
    user: User = Depends(get_current_user),
):
    """Search the web via Serper API."""
    results = await web_search(req.query, num_results=req.num_results)
    return {"status": "success", "data": results}


@router.post("/web/research")
async def research(
    req: WebSearchRequest,
    user: User = Depends(get_current_user),
):
    """Multi-query research mode for comprehensive results."""
    results = await research_mode(req.query)
    return {"status": "success", "data": results}


@router.post("/files")
async def search_local_files(
    req: FileSearchRequest,
    user: User = Depends(get_current_user),
):
    """Search for files on the local system."""
    results = await search_files_exec(
        query=req.query,
        path=req.path,
        extensions=req.extensions,
    )
    return results
