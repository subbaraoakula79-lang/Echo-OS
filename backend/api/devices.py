"""
ECHO OS — Devices API Routes
Register, manage, and send commands to connected devices.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.crud.devices import (
    register_device, get_user_devices, deactivate_device, get_android_device,
)
from db.crud.action_logs import log_action
from core.dependencies import get_current_user
from db.models import User
from schemas.models import DeviceCreate, DeviceOut, DeviceCommand
from services.firebase_service import send_device_command

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("/", response_model=list[DeviceOut])
async def list_devices(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all registered devices."""
    return await get_user_devices(db, user.id)


@router.post("/register", response_model=DeviceOut, status_code=201)
async def register_new_device(
    req: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Register a new device (Android companion, etc.)."""
    device = await register_device(
        db, user.id,
        device_type=req.device_type,
        fcm_token=req.fcm_token,
        device_name=req.device_name,
        platform_version=req.platform_version,
        capabilities=req.capabilities,
    )
    await log_action(db, user.id, "device", "register", details={"device_type": req.device_type})
    return device


@router.post("/{device_id}/command")
async def send_command(
    device_id: uuid.UUID,
    req: DeviceCommand,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a command to a registered device via FCM."""
    devices = await get_user_devices(db, user.id)
    device = next((d for d in devices if d.id == device_id), None)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if not device.fcm_token:
        raise HTTPException(status_code=400, detail="Device has no FCM token")

    result = await send_device_command(device.fcm_token, req.command, req.payload)
    await log_action(
        db, user.id, "device_command", req.command,
        details={"device_id": str(device_id), "payload": req.payload},
    )
    return result


@router.delete("/{device_id}")
async def remove_device(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Deactivate a device."""
    deactivated = await deactivate_device(db, device_id, user.id)
    if not deactivated:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"status": "success", "message": "Device deactivated"}
