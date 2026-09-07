"""
ECHO OS — Action Log CRUD
Audit trail for all sensitive operations.
"""

import uuid
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ActionLog


async def log_action(
    db: AsyncSession,
    user_id: uuid.UUID,
    action_type: str,
    action_name: Optional[str] = None,
    status: str = "success",
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> ActionLog:
    log = ActionLog(
        user_id=user_id,
        action_type=action_type,
        action_name=action_name,
        status=status,
        details=details or {},
        ip_address=ip_address,
    )
    db.add(log)
    await db.flush()
    return log


async def get_action_logs(
    db: AsyncSession,
    user_id: uuid.UUID,
    action_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[ActionLog]:
    query = select(ActionLog).where(ActionLog.user_id == user_id)
    if action_type:
        query = query.where(ActionLog.action_type == action_type)
    query = query.order_by(ActionLog.timestamp.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())
