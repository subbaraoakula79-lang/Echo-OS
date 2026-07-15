from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

from api import chat, tasks, memory

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for ECHO OS AI Assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(memory.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": f"{settings.PROJECT_NAME} is online"}
