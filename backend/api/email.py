"""
ECHO OS — Email API Routes
Gmail integration for inbox, drafts, search, and sending.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from core.dependencies import get_current_user
from db.models import User
from schemas.models import EmailDraft, EmailSearch
from services import google_services

router = APIRouter(prefix="/email", tags=["Email"])


def _get_tokens(user: User) -> dict:
    if not user.google_tokens:
        raise HTTPException(status_code=400, detail="Google account not linked. Please authenticate with Google first.")
    return user.google_tokens


@router.get("/inbox")
async def get_inbox(
    max_results: int = 10,
    user: User = Depends(get_current_user),
):
    """Fetch and summarize the user's inbox."""
    tokens = _get_tokens(user)
    messages = await google_services.get_inbox(tokens, max_results=max_results)
    return {"status": "success", "count": len(messages), "messages": messages}


@router.post("/draft")
async def create_draft(
    req: EmailDraft,
    user: User = Depends(get_current_user),
):
    """Create an email draft."""
    tokens = _get_tokens(user)
    result = await google_services.create_draft(tokens, to=req.to, subject=req.subject, body=req.body)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/send")
async def send_email(
    req: EmailDraft,
    user: User = Depends(get_current_user),
):
    """Send an email directly."""
    tokens = _get_tokens(user)
    result = await google_services.send_email(
        tokens, to=req.to, subject=req.subject, body=req.body, cc=req.cc
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/search")
async def search_emails(
    req: EmailSearch,
    user: User = Depends(get_current_user),
):
    """Search emails with Gmail query syntax."""
    tokens = _get_tokens(user)
    results = await google_services.search_emails(tokens, query=req.query, max_results=req.max_results)
    return {"status": "success", "count": len(results), "results": results}
