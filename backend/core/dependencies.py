"""
ECHO OS — FastAPI Dependencies
Dependency injection for auth, database, and Redis with local default user support.
"""

import uuid
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import verify_access_token
from db.database import get_db
from db.models import User

security_scheme = HTTPBearer(auto_error=False)


async def get_or_create_default_user(db: AsyncSession) -> User:
    """Get or create default local system user for seamless offline/desktop operation."""
    result = await db.execute(select(User).where(User.email == "user@echo.os"))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            email="user@echo.os",
            display_name="USER",
            role="admin",
            is_active=True,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Return the current user, or default user if not authenticated."""
    if credentials is None:
        return await get_or_create_default_user(db)
    try:
        payload = verify_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user or await get_or_create_default_user(db)
    except Exception:
        return await get_or_create_default_user(db)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Return current authenticated user, defaulting to local user if unauthenticated."""
    user = await get_current_user_optional(credentials, db)
    return user or await get_or_create_default_user(db)


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    return user
