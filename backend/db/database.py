"""
ECHO OS — Database Engine
Async SQLAlchemy engine, session factory, and lifecycle management with automatic fallback.
"""

import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from core.config import settings

logger = logging.getLogger(__name__)

# Primary Engine
try:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
except Exception as e:
    logger.warning(f"Could not create PostgreSQL engine: {e}. Falling back to SQLite.")
    engine = create_async_engine(
        "sqlite+aiosqlite:///./echo_os.db",
        echo=settings.DATABASE_ECHO,
    )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


async def get_db():
    """FastAPI dependency: yield an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize database: create tables and extensions with fallback support."""
    global engine, AsyncSessionLocal

    try:
        async with engine.begin() as conn:
            if "postgresql" in str(engine.url):
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    logger.info("pgvector extension enabled")
                except Exception as e:
                    logger.warning(f"Could not enable pgvector extension: {e}")

            from db import models  # noqa: F401
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

    except Exception as e:
        logger.warning(f"PostgreSQL connection failed: {e}. Switching to SQLite fallback...")
        engine = create_async_engine("sqlite+aiosqlite:///./echo_os.db")
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with engine.begin() as conn:
            from db import models  # noqa: F401
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite fallback database initialized successfully: ./echo_os.db")


async def close_db() -> None:
    """Dispose the engine connection pool."""
    await engine.dispose()
    logger.info("Database connection pool closed")


async def check_db_health() -> bool:
    """Quick health check for the database connection."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
