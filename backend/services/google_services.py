"""
ECHO OS — Google Services
Gmail and Google Calendar API integration.
"""

import logging
import base64
from typing import Optional, List, Dict, Any
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from core.config import settings

logger = logging.getLogger(__name__)


def _get_credentials(tokens: dict) -> Optional[Credentials]:
    """Build Google OAuth credentials from stored tokens."""
    if not tokens:
        return None
    try:
        creds = Credentials(
            token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=settings.GOOGLE_SCOPES,
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception as e:
        logger.error(f"Google credentials error: {e}")
        return None


# ══════════════════════════════════════════
# GMAIL
# ══════════════════════════════════════════


async def get_inbox(tokens: dict, max_results: int = 10) -> List[Dict[str, Any]]:
    """Fetch recent inbox messages."""
    creds = _get_credentials(tokens)
    if not creds:
        return []
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me", maxResults=max_results, labelIds=["INBOX"]
        ).execute()

        messages = []
        for msg_ref in results.get("messages", []):
            msg = service.users().messages().get(
                userId="me", id=msg_ref["id"], format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"],
            ).execute()

            headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            messages.append({
                "id": msg["id"],
                "from": headers.get("From", ""),
                "to": [headers.get("To", "")],
                "subject": headers.get("Subject", ""),
                "snippet": msg.get("snippet", ""),
                "date": headers.get("Date", ""),
            })
        return messages
    except Exception as e:
        logger.error(f"Gmail inbox error: {e}")
        return []


async def send_email(
    tokens: dict,
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Send an email via Gmail API."""
    creds = _get_credentials(tokens)
    if not creds:
        return {"error": "Not authenticated with Google"}
    try:
        service = build("gmail", "v1", credentials=creds)
        message = MIMEText(body)
        message["To"] = ", ".join(to)
        message["Subject"] = subject
        if cc:
            message["Cc"] = ", ".join(cc)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        return {"status": "success", "message_id": result.get("id")}
    except Exception as e:
        logger.error(f"Gmail send error: {e}")
        return {"error": str(e)}


async def create_draft(
    tokens: dict,
    to: List[str],
    subject: str,
    body: str,
) -> Dict[str, Any]:
    """Create a Gmail draft."""
    creds = _get_credentials(tokens)
    if not creds:
        return {"error": "Not authenticated with Google"}
    try:
        service = build("gmail", "v1", credentials=creds)
        message = MIMEText(body)
        message["To"] = ", ".join(to)
        message["Subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = service.users().drafts().create(
            userId="me", body={"message": {"raw": raw}}
        ).execute()
        return {"status": "success", "draft_id": result.get("id")}
    except Exception as e:
        logger.error(f"Gmail draft error: {e}")
        return {"error": str(e)}


async def search_emails(tokens: dict, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search emails with Gmail query syntax."""
    creds = _get_credentials(tokens)
    if not creds:
        return []
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        ).execute()

        messages = []
        for msg_ref in results.get("messages", []):
            msg = service.users().messages().get(
                userId="me", id=msg_ref["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()
            headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            messages.append({
                "id": msg["id"],
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "snippet": msg.get("snippet", ""),
                "date": headers.get("Date", ""),
            })
        return messages
    except Exception as e:
        logger.error(f"Gmail search error: {e}")
        return []


# ══════════════════════════════════════════
# GOOGLE CALENDAR
# ══════════════════════════════════════════


async def list_calendar_events(
    tokens: dict,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """List upcoming calendar events."""
    creds = _get_credentials(tokens)
    if not creds:
        return []
    try:
        service = build("calendar", "v3", credentials=creds)
        kwargs: Dict[str, Any] = {
            "calendarId": "primary",
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }
        if time_min:
            kwargs["timeMin"] = time_min
        if time_max:
            kwargs["timeMax"] = time_max

        results = service.events().list(**kwargs).execute()
        events = []
        for event in results.get("items", []):
            events.append({
                "id": event["id"],
                "title": event.get("summary", "Untitled"),
                "description": event.get("description", ""),
                "location": event.get("location", ""),
                "start": event["start"].get("dateTime", event["start"].get("date")),
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "attendees": [a.get("email") for a in event.get("attendees", [])],
            })
        return events
    except Exception as e:
        logger.error(f"Calendar list error: {e}")
        return []


async def create_calendar_event(
    tokens: dict,
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    attendees: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a new Google Calendar event."""
    creds = _get_credentials(tokens)
    if not creds:
        return {"error": "Not authenticated with Google"}
    try:
        service = build("calendar", "v3", credentials=creds)
        event = {
            "summary": title,
            "description": description,
            "location": location,
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"},
        }
        if attendees:
            event["attendees"] = [{"email": a} for a in attendees]

        result = service.events().insert(calendarId="primary", body=event).execute()
        return {"status": "success", "event_id": result.get("id"), "link": result.get("htmlLink")}
    except Exception as e:
        logger.error(f"Calendar create error: {e}")
        return {"error": str(e)}


async def update_calendar_event(
    tokens: dict,
    event_id: str,
    **updates,
) -> Dict[str, Any]:
    """Update an existing calendar event."""
    creds = _get_credentials(tokens)
    if not creds:
        return {"error": "Not authenticated with Google"}
    try:
        service = build("calendar", "v3", credentials=creds)
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        if "title" in updates:
            event["summary"] = updates["title"]
        if "description" in updates:
            event["description"] = updates["description"]
        if "location" in updates:
            event["location"] = updates["location"]
        if "start_time" in updates:
            event["start"]["dateTime"] = updates["start_time"]
        if "end_time" in updates:
            event["end"]["dateTime"] = updates["end_time"]

        result = service.events().update(
            calendarId="primary", eventId=event_id, body=event
        ).execute()
        return {"status": "success", "event_id": result.get("id")}
    except Exception as e:
        logger.error(f"Calendar update error: {e}")
        return {"error": str(e)}


async def delete_calendar_event(tokens: dict, event_id: str) -> Dict[str, Any]:
    """Delete a calendar event."""
    creds = _get_credentials(tokens)
    if not creds:
        return {"error": "Not authenticated with Google"}
    try:
        service = build("calendar", "v3", credentials=creds)
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {"status": "success", "message": "Event deleted"}
    except Exception as e:
        logger.error(f"Calendar delete error: {e}")
        return {"error": str(e)}
