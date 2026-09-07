"""
ECHO OS — User CRUD Operations
"""

import uuid
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from core.security import hash_password


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    email: str,
    display_name: str,
    password: Optional[str] = None,
    role: str = "user",
    google_tokens: Optional[dict] = None,
) -> User:
    user = User(
        email=email,
        display_name=display_name,
        hashed_password=hash_password(password) if password else None,
        role=role,
        google_tokens=google_tokens,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user_preferences(
    db: AsyncSession, user_id: uuid.UUID, preferences: dict
) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if user:
        current = user.preferences or {}
        current.update(preferences)
        user.preferences = current
        await db.flush()
        await db.refresh(user)
    return user


async def update_google_tokens(
    db: AsyncSession, user_id: uuid.UUID, tokens: dict
) -> None:
    await db.execute(
        update(User).where(User.id == user_id).values(google_tokens=tokens)
    )
    await db.flush()


async def deactivate_user(db: AsyncSession, user_id: uuid.UUID) -> None:
    await db.execute(
        update(User).where(User.id == user_id).values(is_active=False)
    )
    await db.flush()
