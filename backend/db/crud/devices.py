"""
ECHO OS — Device CRUD Operations
"""

import uuid
from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Device


async def register_device(
    db: AsyncSession,
    user_id: uuid.UUID,
    device_type: str,
    fcm_token: str,
    device_name: Optional[str] = None,
    platform_version: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
) -> Device:
    # Check if device with this FCM token already exists
    existing = await db.execute(
        select(Device).where(Device.fcm_token == fcm_token)
    )
    device = existing.scalar_one_or_none()

    if device:
        device.is_active = True
        device.last_seen = datetime.now(timezone.utc)
        device.device_name = device_name or device.device_name
        device.capabilities = capabilities or device.capabilities
    else:
        device = Device(
            user_id=user_id,
            device_type=device_type,
            device_name=device_name,
            platform_version=platform_version,
            fcm_token=fcm_token,
            capabilities=capabilities or [],
        )
        db.add(device)

    await db.flush()
    await db.refresh(device)
    return device


async def get_user_devices(
    db: AsyncSession,
    user_id: uuid.UUID,
    active_only: bool = True,
) -> List[Device]:
    query = select(Device).where(Device.user_id == user_id)
    if active_only:
        query = query.where(Device.is_active == True)
    query = query.order_by(Device.last_seen.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_android_device(db: AsyncSession, user_id: uuid.UUID) -> Optional[Device]:
    """Get the user's active Android companion device."""
    result = await db.execute(
        select(Device).where(and_(
            Device.user_id == user_id,
            Device.device_type == "android",
            Device.is_active == True,
        )).order_by(Device.last_seen.desc()).limit(1)
    )
    return result.scalar_one_or_none()


async def deactivate_device(db: AsyncSession, device_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    result = await db.execute(
        update(Device)
        .where(and_(Device.id == device_id, Device.user_id == user_id))
        .values(is_active=False)
    )
    await db.flush()
    return result.rowcount > 0


async def update_device_heartbeat(db: AsyncSession, device_id: uuid.UUID) -> None:
    await db.execute(
        update(Device)
        .where(Device.id == device_id)
        .values(last_seen=datetime.now(timezone.utc))
    )
    await db.flush()
