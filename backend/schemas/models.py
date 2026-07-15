from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    display_name: str
    email: EmailStr
    preferences: Dict[str, Any] = {}

class UserOut(UserBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskOut(TaskBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MemoryCreate(BaseModel):
    content: str
    
class MemoryOut(BaseModel):
    id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MessageCreate(BaseModel):
    role: str
    content: str
    tool_calls: Optional[Dict[str, Any]] = None

class MessageOut(MessageCreate):
    id: UUID
    conversation_id: UUID
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class ConversationCreate(BaseModel):
    title: str = "New Conversation"
    
class ConversationOut(ConversationCreate):
    id: UUID
    user_id: UUID
    started_at: datetime
    last_updated: datetime
    model_config = ConfigDict(from_attributes=True)

class DeviceCreate(BaseModel):
    device_type: str
    fcm_token: str
    
class DeviceOut(DeviceCreate):
    id: UUID
    user_id: UUID
    is_active: bool
    last_seen: datetime
    model_config = ConfigDict(from_attributes=True)
