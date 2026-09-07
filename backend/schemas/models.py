"""
ECHO OS — Pydantic Schemas
Request/Response models for all API endpoints.
"""

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ══════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════

class AuthRegister(BaseModel):
    email: EmailStr
    display_name: str
    password: str = Field(min_length=8)


class AuthLogin(BaseModel):
    email: EmailStr
    password: str


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthRefresh(BaseModel):
    refresh_token: str


# ══════════════════════════════════════════
# USER
# ══════════════════════════════════════════

class UserBase(BaseModel):
    display_name: str
    email: EmailStr
    preferences: Dict[str, Any] = {}


class UserOut(UserBase):
    id: UUID
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserPreferencesUpdate(BaseModel):
    preferences: Dict[str, Any]


# ══════════════════════════════════════════
# CHAT / MESSAGES
# ══════════════════════════════════════════

class MessageCreate(BaseModel):
    content: str
    conversation_id: Optional[UUID] = None


class MessageOut(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: Optional[str] = None
    tool_calls: Optional[Dict[str, Any]] = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: UUID
    tool_results: Optional[List[Dict[str, Any]]] = None


class ConversationCreate(BaseModel):
    title: str = "New Conversation"


class ConversationOut(BaseModel):
    id: UUID
    title: str
    summary: Optional[str] = None
    is_archived: bool
    started_at: datetime
    last_updated: datetime
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════
# MEMORY
# ══════════════════════════════════════════

class MemoryCreate(BaseModel):
    content: str
    category: str = "general"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class MemoryOut(BaseModel):
    id: UUID
    content: str
    category: str
    importance: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MemorySearch(BaseModel):
    query: str
    limit: int = Field(default=10, le=50)
    category: Optional[str] = None


# ══════════════════════════════════════════
# TASKS
# ══════════════════════════════════════════

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None
    tags: List[str] = []


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class TaskOut(TaskBase):
    id: UUID
    user_id: UUID
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ReminderCreate(BaseModel):
    message: str
    trigger_time: datetime
    task_id: Optional[UUID] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None


class ReminderOut(BaseModel):
    id: UUID
    message: str
    trigger_time: datetime
    is_triggered: bool
    is_recurring: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════
# EMAIL
# ══════════════════════════════════════════

class EmailDraft(BaseModel):
    to: List[str]
    subject: str
    body: str
    cc: Optional[List[str]] = None


class EmailOut(BaseModel):
    id: str
    from_: Optional[str] = Field(None, alias="from")
    to: List[str]
    subject: str
    snippet: str
    date: str


class EmailSearch(BaseModel):
    query: str
    max_results: int = 10


# ══════════════════════════════════════════
# CALENDAR
# ══════════════════════════════════════════

class CalendarEventCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[str] = []
    is_all_day: bool = False


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    location: Optional[str] = None


class CalendarEventOut(BaseModel):
    id: UUID
    external_event_id: Optional[str] = None
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[Any] = []
    is_all_day: bool
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════
# DEVICES
# ══════════════════════════════════════════

class DeviceCreate(BaseModel):
    device_type: str
    device_name: Optional[str] = None
    fcm_token: str
    platform_version: Optional[str] = None
    capabilities: List[str] = []


class DeviceOut(BaseModel):
    id: UUID
    device_type: str
    device_name: Optional[str] = None
    is_active: bool
    capabilities: List[str]
    last_seen: datetime
    model_config = ConfigDict(from_attributes=True)


class DeviceCommand(BaseModel):
    command: str  # call, sms, open_app, notification
    payload: Dict[str, Any]


# ══════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════

class WebSearchRequest(BaseModel):
    query: str
    num_results: int = 10


class FileSearchRequest(BaseModel):
    query: str
    path: Optional[str] = None
    extensions: Optional[List[str]] = None


# ══════════════════════════════════════════
# GENERIC
# ══════════════════════════════════════════

class StatusResponse(BaseModel):
    status: str
    message: str = ""
    data: Optional[Any] = None
