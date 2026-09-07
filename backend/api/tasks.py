from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from schemas.models import TaskCreate

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/")
async def get_tasks(db: AsyncSession = Depends(get_db)):
    # Standard DB execution would go here
    return {"status": "success", "tasks": []}

@router.post("/")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    return {"status": "success", "task": task.model_dump()}
    