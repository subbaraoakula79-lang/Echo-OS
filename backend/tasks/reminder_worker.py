"""
ECHO OS — Reminder Worker
Celery task that checks for due reminders and sends notifications.
"""

import asyncio
import logging
from datetime import datetime, timezone

from celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.reminder_worker.check_due_reminders")
def check_due_reminders():
    """Check for due reminders and trigger notifications."""
    asyncio.run(_check_reminders_async())


async def _check_reminders_async():
    """Async implementation of reminder checking."""
    from db.database import AsyncSessionLocal
    from db.crud.tasks import get_pending_reminders, mark_reminder_triggered
    from db.crud.devices import get_user_devices
    from services.firebase_service import send_push_notification

    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        try:
            reminders = await get_pending_reminders(db, before=now)

            for reminder in reminders:
                logger.info(f"Triggering reminder: {reminder.message}")

                # Send push notification to all user devices
                devices = await get_user_devices(db, reminder.user_id)
                for device in devices:
                    if device.fcm_token:
                        await send_push_notification(
                            fcm_token=device.fcm_token,
                            title="⏰ ECHO Reminder",
                            body=reminder.message,
                            data={"type": "reminder", "reminder_id": str(reminder.id)},
                        )

                await mark_reminder_triggered(db, reminder.id)

            await db.commit()

            if reminders:
                logger.info(f"Triggered {len(reminders)} reminder(s)")
        except Exception as e:
            logger.error(f"Reminder check failed: {e}")
            await db.rollback()
