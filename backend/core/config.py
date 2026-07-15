from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "ECHO OS"
    
    OPENAI_API_KEY: str = ""
    OPENAI_REALTIME_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""
    
    DATABASE_URL: str = "postgresql+asyncpg://echo:echopassword@localhost:5432/echo_os_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
