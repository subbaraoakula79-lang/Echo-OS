from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from schemas.models import MemoryCreate

router = APIRouter(prefix="/memory", tags=["Memory"])

@router.get("/")
async def get_memories(db: AsyncSession = Depends(get_db)):
    return {"status": "success", "memories": []}

@router.post("/")
async def create_memory(memory: MemoryCreate, db: AsyncSession = Depends(get_db)):
    return {"status": "success", "memory": memory.model_dump()}
