"""
ECHO OS — Task & Reminder CRUD Operations
"""

import uuid
from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Task, Reminder


# ── Tasks ──

async def create_task(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[datetime] = None,
    tags: Optional[List[str]] = None,
) -> Task:
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        tags=tags or [],
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Task]:
    result = await db.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
    )
    return result.scalar_one_or_none()


async def list_tasks(
    db: AsyncSession,
    user_id: uuid.UUID,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Task]:
    query = select(Task).where(Task.user_id == user_id)
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    query = query.order_by(Task.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_task(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    **kwargs,
) -> Optional[Task]:
    task = await get_task(db, task_id, user_id)
    if not task:
        return None
    for key, value in kwargs.items():
        if hasattr(task, key) and value is not None:
            setattr(task, key, value)
    await db.flush()
    await db.refresh(task)
    return task


async def complete_task(
    db: AsyncSession, task_id: uuid.UUID, user_id: uuid.UUID
) -> Optional[Task]:
    return await update_task(
        db, task_id, user_id,
        status="completed",
        completed_at=datetime.now(timezone.utc),
    )


async def delete_task(db: AsyncSession, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    result = await db.execute(
        delete(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
    )
    await db.flush()
    return result.rowcount > 0


# ── Reminders ──

async def create_reminder(
    db: AsyncSession,
    user_id: uuid.UUID,
    message: str,
    trigger_time: datetime,
    task_id: Optional[uuid.UUID] = None,
    is_recurring: bool = False,
    recurrence_rule: Optional[str] = None,
) -> Reminder:
    reminder = Reminder(
        user_id=user_id,
        task_id=task_id,
        message=message,
        trigger_time=trigger_time,
        is_recurring=is_recurring,
        recurrence_rule=recurrence_rule,
    )
    db.add(reminder)
    await db.flush()
    await db.refresh(reminder)
    return reminder


async def get_pending_reminders(
    db: AsyncSession,
    user_id: Optional[uuid.UUID] = None,
    before: Optional[datetime] = None,
) -> List[Reminder]:
    """Get reminders that are due and not yet triggered."""
    query = select(Reminder).where(Reminder.is_triggered == False)
    if user_id:
        query = query.where(Reminder.user_id == user_id)
    if before:
        query = query.where(Reminder.trigger_time <= before)
    else:
        query = query.where(Reminder.trigger_time <= datetime.now(timezone.utc))
    query = query.order_by(Reminder.trigger_time.asc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def mark_reminder_triggered(db: AsyncSession, reminder_id: uuid.UUID) -> None:
    await db.execute(
        update(Reminder)
        .where(Reminder.id == reminder_id)
        .values(is_triggered=True)
    )
    await db.flush()
