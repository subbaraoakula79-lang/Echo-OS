"""
ECHO OS — Memory CRUD Operations
Handles semantic memory storage and vector search with fallback.
"""

import uuid
from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Memory


async def create_memory(
    db: AsyncSession,
    user_id: uuid.UUID,
    content: str,
    category: str = "general",
    importance: float = 0.5,
    embedding: Optional[List[float]] = None,
    metadata: Optional[dict] = None,
) -> Memory:
    memory = Memory(
        user_id=user_id,
        content=content,
        category=category,
        importance=importance,
        embedding=embedding,
        metadata_=metadata or {},
    )
    db.add(memory)
    await db.flush()
    await db.refresh(memory)
    return memory


async def get_memories(
    db: AsyncSession,
    user_id: uuid.UUID,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Memory]:
    query = select(Memory).where(
        and_(Memory.user_id == user_id, Memory.is_active == True)
    )
    if category:
        query = query.where(Memory.category == category)
    query = query.order_by(Memory.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def search_memories_by_embedding(
    db: AsyncSession,
    user_id: uuid.UUID,
    query_embedding: List[float],
    limit: int = 10,
    similarity_threshold: float = 0.3,
) -> List[Memory]:
    """Semantic search with pgvector or timestamp fallback."""
    try:
        query = (
            select(Memory)
            .where(
                and_(
                    Memory.user_id == user_id,
                    Memory.is_active == True,
                    Memory.embedding.isnot(None),
                )
            )
            .order_by(Memory.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    except Exception:
        # Fallback for non-pgvector engines (e.g. SQLite)
        query = (
            select(Memory)
            .where(and_(Memory.user_id == user_id, Memory.is_active == True))
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())


async def delete_memory(db: AsyncSession, memory_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    result = await db.execute(
        update(Memory)
        .where(and_(Memory.id == memory_id, Memory.user_id == user_id))
        .values(is_active=False)
    )
    await db.flush()
    return result.rowcount > 0


async def touch_memory(db: AsyncSession, memory_id: uuid.UUID) -> None:
    """Update the accessed_at timestamp when a memory is retrieved."""
    await db.execute(
        update(Memory)
        .where(Memory.id == memory_id)
        .values(accessed_at=datetime.now(timezone.utc))
    )
    await db.flush()
