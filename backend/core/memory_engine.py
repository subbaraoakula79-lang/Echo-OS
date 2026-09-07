"""
ECHO OS — Memory Engine
Embedding generation and semantic memory search using OpenAI + pgvector.
"""

import logging
import re
from typing import List, Optional, Dict, Any

from openai import AsyncOpenAI

from core.config import settings

logger = logging.getLogger(__name__)

_client: Optional[AsyncOpenAI] = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


async def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate an embedding vector for the given text."""
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set, skipping embedding generation")
        return None
    try:
        client = _get_client()
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
            dimensions=settings.OPENAI_EMBEDDING_DIMENSIONS,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return None


async def generate_embeddings_batch(texts: List[str]) -> List[Optional[List[float]]]:
    """Generate embeddings for multiple texts in a single API call."""
    if not settings.OPENAI_API_KEY or not texts:
        return [None] * len(texts)
    try:
        client = _get_client()
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=texts,
            dimensions=settings.OPENAI_EMBEDDING_DIMENSIONS,
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        logger.error(f"Batch embedding generation failed: {e}")
        return [None] * len(texts)


# ── Preference Extraction ──

PREFERENCE_PATTERNS = [
    r"(?:i\s+(?:like|love|prefer|enjoy|want|use|always))\s+(.+)",
    r"(?:my\s+(?:name|favorite|preferred))\s+(?:is|are)\s+(.+)",
    r"(?:call\s+me)\s+(.+)",
    r"(?:i\s+(?:am|'m))\s+(.+)",
    r"(?:remember\s+(?:that|this))\s*:?\s*(.+)",
]


def extract_preferences(message: str) -> List[Dict[str, str]]:
    """Extract potential user preferences from a message for memory storage."""
    preferences = []
    lower = message.lower().strip()

    for pattern in PREFERENCE_PATTERNS:
        matches = re.findall(pattern, lower, re.IGNORECASE)
        for match in matches:
            preferences.append({
                "content": match.strip(),
                "category": "preference",
                "source": message,
            })

    return preferences


def build_memory_context(memories: List[Any], max_tokens: int = 1000) -> str:
    """Build a formatted memory context string for the system prompt."""
    if not memories:
        return ""

    context_parts = []
    estimated_tokens = 0

    for memory in memories:
        content = getattr(memory, "content", str(memory))
        category = getattr(memory, "category", "general")
        entry = f"[{category}] {content}"
        entry_tokens = len(entry.split()) * 1.3  # rough estimate

        if estimated_tokens + entry_tokens > max_tokens:
            break

        context_parts.append(entry)
        estimated_tokens += entry_tokens

    return "\n".join(context_parts)
