"""
ECHO OS — SQLAlchemy ORM Models
All database tables for the ECHO OS system with dual PostgreSQL & SQLite support.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Float, Index, JSON, Uuid,
)
from sqlalchemy.orm import relationship

from db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ── User ──

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(320), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Null for OAuth-only users
    avatar_url = Column(String(512), nullable=True)
    role = Column(String(20), default="user", nullable=False)  # user, admin
    preferences = Column(JSON, default=dict)
    google_tokens = Column(JSON, nullable=True)  # OAuth tokens for Gmail/Calendar
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    action_logs = relationship("ActionLog", back_populates="user", cascade="all, delete-orphan")


# ── Memory (Semantic) ──

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), default="general")  # preference, fact, note, context
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    embedding = Column(JSON, nullable=True)  # Vector list / JSON for embeddings
    metadata_ = Column("metadata", JSON, default=dict)  # Extra context
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    accessed_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="memories")

    __table_args__ = (
        Index("ix_memories_user_category", "user_id", "category"),
    )


# ── Conversation ──

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="New Conversation")
    summary = Column(Text, nullable=True)
    is_archived = Column(Boolean, default=False)
    started_at = Column(DateTime(timezone=True), default=utc_now)
    last_updated = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan",
                            order_by="Message.timestamp")


# ── Message ──

class Message(Base):
    __tablename__ = "messages"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(Uuid(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=True)
    tool_calls = Column(JSON, nullable=True)  # Tool call requests from assistant
    tool_call_id = Column(String(100), nullable=True)  # For tool response messages
    tool_name = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now)

    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_ts", "conversation_id", "timestamp"),
    )


# ── Task ──

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    priority = Column(String(10), default="medium")  # low, medium, high, urgent
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="tasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_tasks_user_status", "user_id", "status"),
    )


# ── Reminder ──

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Uuid(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    message = Column(Text, nullable=False)
    trigger_time = Column(DateTime(timezone=True), nullable=False)
    is_triggered = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(100), nullable=True)  # cron-style
    created_at = Column(DateTime(timezone=True), default=utc_now)

    task = relationship("Task", back_populates="reminders")

    __table_args__ = (
        Index("ix_reminders_trigger", "is_triggered", "trigger_time"),
    )


# ── Calendar Event ──

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    external_event_id = Column(String(255), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    attendees = Column(JSON, default=list)
    is_all_day = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)


# ── Device ──

class Device(Base):
    __tablename__ = "devices"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_name = Column(String(255), nullable=True)
    device_type = Column(String(50), nullable=False)  # android, web, desktop
    platform_version = Column(String(50), nullable=True)
    fcm_token = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    capabilities = Column(JSON, default=list)  # ["call", "sms", "notifications"]
    last_seen = Column(DateTime(timezone=True), default=utc_now)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="devices")


# ── Permission ──

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resource = Column(String(100), nullable=False)  # email, calendar, phone, sms
    is_granted = Column(Boolean, default=False)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_permissions_user_resource", "user_id", "resource", unique=True),
    )


# ── Action Log ──

class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(100), nullable=False)  # tool_call, auth, data_access, etc.
    action_name = Column(String(255), nullable=True)  # Specific tool or action name
    status = Column(String(20), default="success")  # success, failed, pending
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="action_logs")

    __table_args__ = (
        Index("ix_action_logs_user_ts", "user_id", "timestamp"),
    )
