"""
ECHO OS — Conversation & Message CRUD Operations
"""

import uuid
from typing import Optional, List

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Conversation, Message


# ── Conversations ──

async def create_conversation(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str = "New Conversation",
) -> Conversation:
    conv = Conversation(user_id=user_id, title=title)
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return conv


async def get_conversation(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Optional[Conversation]:
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(and_(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        ))
    )
    return result.scalar_one_or_none()


async def list_conversations(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    include_archived: bool = False,
) -> List[Conversation]:
    query = select(Conversation).where(Conversation.user_id == user_id)
    if not include_archived:
        query = query.where(Conversation.is_archived == False)
    query = query.order_by(Conversation.last_updated.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def archive_conversation(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    result = await db.execute(
        update(Conversation)
        .where(and_(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        ))
        .values(is_archived=True)
    )
    await db.flush()
    return result.rowcount > 0


# ── Messages ──

async def add_message(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    role: str,
    content: Optional[str] = None,
    tool_calls: Optional[dict] = None,
    tool_call_id: Optional[str] = None,
    tool_name: Optional[str] = None,
    tokens_used: Optional[int] = None,
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_call_id=tool_call_id,
        tool_name=tool_name,
        tokens_used=tokens_used,
    )
    db.add(msg)
    await db.flush()
    await db.refresh(msg)
    return msg


async def get_messages(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    limit: int = 100,
    before_id: Optional[uuid.UUID] = None,
) -> List[Message]:
    query = select(Message).where(Message.conversation_id == conversation_id)
    if before_id:
        # Get the timestamp of the reference message for cursor-based pagination
        ref = await db.execute(select(Message.timestamp).where(Message.id == before_id))
        ref_ts = ref.scalar_one_or_none()
        if ref_ts:
            query = query.where(Message.timestamp < ref_ts)
    query = query.order_by(Message.timestamp.asc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_recent_messages_for_context(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    limit: int = 20,
) -> List[dict]:
    """Get recent messages formatted for the AI agent context window."""
    messages = await get_messages(db, conversation_id, limit=limit)
    context = []
    for msg in messages:
        entry = {"role": msg.role, "content": msg.content or ""}
        if msg.tool_calls:
            entry["tool_calls"] = msg.tool_calls
        if msg.tool_call_id:
            entry["tool_call_id"] = msg.tool_call_id
        if msg.tool_name:
            entry["name"] = msg.tool_name
        context.append(entry)
    return context
