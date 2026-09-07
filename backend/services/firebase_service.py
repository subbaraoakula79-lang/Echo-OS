"""
ECHO OS — Firebase Service
FCM push notifications and device messaging.
"""

import logging
from typing import Optional, Dict, Any

from core.config import settings

logger = logging.getLogger(__name__)

_firebase_initialized = False


def _init_firebase():
    """Initialize Firebase Admin SDK."""
    global _firebase_initialized
    if _firebase_initialized:
        return True

    if not all([settings.FIREBASE_PROJECT_ID, settings.FIREBASE_CLIENT_EMAIL, settings.FIREBASE_PRIVATE_KEY]):
        logger.warning("Firebase credentials not configured")
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n") if settings.FIREBASE_PRIVATE_KEY else "",
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "token_uri": "https://oauth2.googleapis.com/token",
        })
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase Admin SDK initialized")
        return True
    except Exception as e:
        logger.error(f"Firebase init error: {e}")
        return False


async def send_push_notification(
    fcm_token: str,
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Send a push notification via FCM."""
    if not _init_firebase():
        return {"status": "error", "message": "Firebase not configured"}

    try:
        from firebase_admin import messaging

        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=fcm_token,
        )
        response = messaging.send(message)
        return {"status": "success", "message_id": response}
    except Exception as e:
        logger.error(f"FCM send error: {e}")
        return {"status": "error", "message": str(e)}


async def send_device_command(
    fcm_token: str,
    command: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """Send a command to an Android companion device via FCM data message."""
    if not _init_firebase():
        return {"status": "error", "message": "Firebase not configured"}

    try:
        from firebase_admin import messaging

        data = {
            "command": command,
            "payload": str(payload),  # FCM data must be string values
        }
        message = messaging.Message(
            data=data,
            token=fcm_token,
            android=messaging.AndroidConfig(priority="high"),
        )
        response = messaging.send(message)
        return {"status": "success", "message_id": response}
    except Exception as e:
        logger.error(f"Device command error: {e}")
        return {"status": "error", "message": str(e)}
