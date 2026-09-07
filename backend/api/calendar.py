"""
ECHO OS — Calendar API Routes
Google Calendar integration for event management.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from core.dependencies import get_current_user
from db.models import User
from schemas.models import CalendarEventCreate, CalendarEventUpdate
from services import google_services

router = APIRouter(prefix="/calendar", tags=["Calendar"])


def _get_tokens(user: User) -> dict:
    if not user.google_tokens:
        raise HTTPException(status_code=400, detail="Google account not linked")
    return user.google_tokens


@router.get("/events")
async def list_events(
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 20,
    user: User = Depends(get_current_user),
):
    """List upcoming calendar events."""
    tokens = _get_tokens(user)
    events = await google_services.list_calendar_events(
        tokens, time_min=time_min, time_max=time_max, max_results=max_results
    )
    return {"status": "success", "count": len(events), "events": events}


@router.post("/events")
async def create_event(
    req: CalendarEventCreate,
    user: User = Depends(get_current_user),
):
    """Create a new calendar event."""
    tokens = _get_tokens(user)
    result = await google_services.create_calendar_event(
        tokens,
        title=req.title,
        start_time=req.start_time.isoformat(),
        end_time=req.end_time.isoformat(),
        description=req.description or "",
        location=req.location or "",
        attendees=req.attendees,
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.patch("/events/{event_id}")
async def update_event(
    event_id: str,
    req: CalendarEventUpdate,
    user: User = Depends(get_current_user),
):
    """Update an existing calendar event."""
    tokens = _get_tokens(user)
    updates = {}
    if req.title:
        updates["title"] = req.title
    if req.description:
        updates["description"] = req.description
    if req.location:
        updates["location"] = req.location
    if req.start_time:
        updates["start_time"] = req.start_time.isoformat()
    if req.end_time:
        updates["end_time"] = req.end_time.isoformat()

    result = await google_services.update_calendar_event(tokens, event_id, **updates)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.delete("/events/{event_id}")
async def remove_event(
    event_id: str,
    user: User = Depends(get_current_user),
):
    """Delete a calendar event."""
    tokens = _get_tokens(user)
    result = await google_services.delete_calendar_event(tokens, event_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
