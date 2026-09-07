"""
ECHO OS — Memory API Routes
Store, search, and manage semantic memories.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.crud.memories import (
    create_memory, get_memories, search_memories_by_embedding, delete_memory,
)
from core.dependencies import get_current_user
from core.memory_engine import generate_embedding
from db.models import User
from schemas.models import MemoryCreate, MemoryOut, MemorySearch

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.get("/", response_model=list[MemoryOut])
async def list_memories(
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List stored memories with optional category filter."""
    return await get_memories(db, user.id, category=category, limit=limit, offset=offset)


@router.post("/", response_model=MemoryOut, status_code=201)
async def store_memory(
    req: MemoryCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Store a new memory with embedding for semantic search."""
    embedding = await generate_embedding(req.content)
    return await create_memory(
        db, user.id,
        content=req.content,
        category=req.category,
        importance=req.importance,
        embedding=embedding,
    )


@router.post("/search", response_model=list[MemoryOut])
async def search_memories(
    req: MemorySearch,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Semantic search across stored memories."""
    query_embedding = await generate_embedding(req.query)
    if not query_embedding:
        return await get_memories(db, user.id, limit=req.limit)

    return await search_memories_by_embedding(
        db, user.id, query_embedding, limit=req.limit
    )


@router.delete("/{memory_id}")
async def remove_memory(
    memory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Soft-delete a memory."""
    deleted = await delete_memory(db, memory_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "success", "message": "Memory removed"}
