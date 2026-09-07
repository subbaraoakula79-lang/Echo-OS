"""
ECHO OS — Central Configuration
Loads all environment variables with sensible defaults for local development.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


class Settings(BaseSettings):
    # ── Project ──
    PROJECT_NAME: str = "ECHO OS"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "app://echo-os"]

    # ── Authentication ──
    JWT_SECRET_KEY: str = "echo-os-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""

    # ── Database ──
    DATABASE_URL: str = "postgresql+asyncpg://echo:echopassword@localhost:5432/echo_os_db"
    DATABASE_ECHO: bool = False

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Celery ──
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── OpenAI ──
    OPENAI_API_KEY: str = ""
    OPENAI_REALTIME_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSIONS: int = 1536

    # ── ElevenLabs ──
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Default: Rachel
    ELEVENLABS_MODEL_ID: str = "eleven_turbo_v2_5"

    # ── Serper (Web Search) ──
    SERPER_API_KEY: str = ""

    # ── Google OAuth & APIs ──
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    GOOGLE_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    # ── Firebase ──
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None

    # ── Voice ──
    WAKE_WORD: str = "hey echo"

    # ── System Prompt ──
    SYSTEM_PROMPT: str = (
        "You are ECHO, an intelligent personal operating system inspired by JARVIS.\n"
        "You help the user manage tasks, information, communication and productivity.\n\n"
        "Rules:\n"
        "- Be concise and direct.\n"
        "- Confirm sensitive actions (sending emails, making calls, deleting data) before executing.\n"
        "- Never perform destructive actions without explicit approval.\n"
        "- Remember user preferences and past context.\n"
        "- Use available tools whenever they can help fulfill the user's request.\n"
        "- Explain actions clearly after executing them.\n"
        "- When uncertain, ask for clarification.\n"
        "- Format responses cleanly with markdown when helpful.\n"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
