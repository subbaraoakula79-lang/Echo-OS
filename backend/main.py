"""
ECHO OS — FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from db.database import init_db, close_db, check_db_health
from core.redis_client import get_redis, close_redis
from services.tools import register_all_tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")

    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")

    # Initialize Redis
    try:
        await get_redis()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️  Redis connection failed: {e}")

    # Register all AI tools
    register_all_tools()
    logger.info("✅ AI tools registered")

    logger.info(f"✅ {settings.PROJECT_NAME} is online")

    yield

    # Shutdown
    await close_redis()
    await close_db()
    logger.info(f"👋 {settings.PROJECT_NAME} shut down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ECHO OS — AI Operating System Backend API",
    version=settings.VERSION,
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Exception Handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# ── Register Routers ──
from api import chat, tasks, memory, auth, email, calendar, devices, search  # noqa: E402

app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(tasks.router, prefix=settings.API_PREFIX)
app.include_router(memory.router, prefix=settings.API_PREFIX)
app.include_router(email.router, prefix=settings.API_PREFIX)
app.include_router(calendar.router, prefix=settings.API_PREFIX)
app.include_router(devices.router, prefix=settings.API_PREFIX)
app.include_router(search.router, prefix=settings.API_PREFIX)


# ── Health Check ──
@app.get("/health")
async def health_check():
    db_ok = await check_db_health()
    try:
        redis = await get_redis()
        redis_ok = await redis.ping()
    except Exception:
        redis_ok = False

    return {
        "status": "healthy" if (db_ok and redis_ok) else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected" if db_ok else "disconnected",
        "redis": "connected" if redis_ok else "disconnected",
    }
