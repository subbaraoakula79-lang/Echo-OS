"""
ECHO OS — Auth API Routes
JWT authentication, registration, and Google OAuth.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.crud.users import get_user_by_email, create_user, update_google_tokens
from db.crud.action_logs import log_action
from core.security import verify_password, create_access_token, create_refresh_token, verify_refresh_token
from core.dependencies import get_current_user
from core.config import settings
from db.models import User
from schemas.models import AuthRegister, AuthLogin, AuthTokens, AuthRefresh, UserOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthTokens, status_code=201)
async def register(req: AuthRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    existing = await get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await create_user(
        db,
        email=req.email,
        display_name=req.display_name,
        password=req.password,
    )

    await log_action(db, user.id, "auth", "register")

    return AuthTokens(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=AuthTokens)
async def login(req: AuthLogin, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    user = await get_user_by_email(db, req.email)
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    await log_action(db, user.id, "auth", "login")

    return AuthTokens(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=AuthTokens)
async def refresh_token(req: AuthRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh an expired access token."""
    payload = verify_refresh_token(req.refresh_token)
    import uuid
    user_id = uuid.UUID(payload["sub"])

    return AuthTokens(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return user


@router.post("/google/callback")
async def google_oauth_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback and create/login user."""
    body = await request.json()
    code = body.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")

    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        import httpx

        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            tokens = token_response.json()

        if "error" in tokens:
            raise HTTPException(status_code=400, detail=tokens["error_description"])

        # Verify ID token
        idinfo = id_token.verify_oauth2_token(
            tokens["id_token"],
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        email = idinfo["email"]
        name = idinfo.get("name", email.split("@")[0])

        # Find or create user
        user = await get_user_by_email(db, email)
        if not user:
            user = await create_user(
                db, email=email, display_name=name,
                google_tokens=tokens,
            )
        else:
            await update_google_tokens(db, user.id, tokens)

        await log_action(db, user.id, "auth", "google_login")

        return AuthTokens(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
