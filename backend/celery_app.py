"""
ECHO OS — Celery Application
Background task worker for reminders and scheduled operations.
"""

from celery import Celery
from core.config import settings

celery_app = Celery(
    "echo_os",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "check-reminders": {
            "task": "tasks.reminder_worker.check_due_reminders",
            "schedule": 60.0,  # Check every 60 seconds
        },
    },
)

celery_app.autodiscover_tasks(["tasks"])
