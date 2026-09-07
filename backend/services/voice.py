"""
ECHO OS — Voice Service
ElevenLabs TTS integration for natural speech synthesis.
"""

import logging
from typing import AsyncGenerator, Optional

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


async def text_to_speech_stream(
    text: str,
    voice_id: Optional[str] = None,
) -> AsyncGenerator[bytes, None]:
    """Stream audio bytes from ElevenLabs TTS."""
    if not settings.ELEVENLABS_API_KEY:
        logger.warning("ELEVENLABS_API_KEY not set")
        return

    vid = voice_id or settings.ELEVENLABS_VOICE_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/stream"

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            async with client.stream(
                "POST",
                url,
                headers={
                    "xi-api-key": settings.ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "model_id": settings.ELEVENLABS_MODEL_ID,
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                        "style": 0.3,
                        "use_speaker_boost": True,
                    },
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    yield chunk
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")


async def text_to_speech(text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
    """Get complete audio bytes (non-streaming) from ElevenLabs."""
    audio_chunks = []
    async for chunk in text_to_speech_stream(text, voice_id):
        audio_chunks.append(chunk)

    if audio_chunks:
        return b"".join(audio_chunks)
    return None
