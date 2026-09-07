"""
ECHO OS — Chat API Routes
Handles text chat, streaming, and WebSocket voice connections.
"""

import json
import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.crud.conversations import (
    create_conversation, get_conversation, add_message,
    get_recent_messages_for_context, list_conversations,
)
from db.crud.memories import search_memories_by_embedding
from core.agent import agent
from core.dependencies import get_current_user, get_current_user_optional
from core.memory_engine import generate_embedding, build_memory_context, extract_preferences
from core.config import settings
from db.models import User
from schemas.models import ChatRequest, ChatResponse, ConversationOut, ConversationCreate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/completions", response_model=ChatResponse)
async def chat_completions(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a message and get a complete response with tool execution."""
    # Get or create conversation
    conversation_id = req.conversation_id
    if not conversation_id:
        conv = await create_conversation(db, user.id, title=req.message[:50])
        conversation_id = conv.id
    else:
        conv = await get_conversation(db, conversation_id, user.id)
        if not conv:
            conv = await create_conversation(db, user.id, title=req.message[:50])
            conversation_id = conv.id

    # Save user message
    await add_message(db, conversation_id, role="user", content=req.message)

    # Get conversation history for context
    history = await get_recent_messages_for_context(db, conversation_id, limit=20)

    # Semantic memory retrieval
    memory_context = ""
    try:
        query_embedding = await generate_embedding(req.message)
        if query_embedding:
            memories = await search_memories_by_embedding(
                db, user.id, query_embedding, limit=5
            )
            memory_context = build_memory_context(memories)
    except Exception as e:
        logger.warning(f"Memory retrieval failed: {e}")

    # Get agent response
    response = await agent.get_response(
        user_message=req.message,
        conversation_history=history[:-1],  # Exclude the just-added user message
        memory_context=memory_context,
    )

    # Save assistant response
    await add_message(
        db, conversation_id,
        role="assistant",
        content=response.get("content", ""),
        tool_calls=response.get("tool_calls"),
    )

    # Auto-extract and store preferences
    preferences = extract_preferences(req.message)
    if preferences:
        from db.crud.memories import create_memory
        for pref in preferences:
            embedding = await generate_embedding(pref["content"])
            await create_memory(
                db, user.id,
                content=pref["content"],
                category="preference",
                embedding=embedding,
            )

    return ChatResponse(
        message=response.get("content", ""),
        conversation_id=conversation_id,
        tool_results=response.get("tool_results"),
    )


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Stream a response using Server-Sent Events."""
    conversation_id = req.conversation_id
    if not conversation_id:
        conv = await create_conversation(db, user.id, title=req.message[:50])
        conversation_id = conv.id

    await add_message(db, conversation_id, role="user", content=req.message)
    history = await get_recent_messages_for_context(db, conversation_id, limit=20)

    async def generate():
        full_content = ""
        async for token in agent.stream_response(
            user_message=req.message,
            conversation_history=history[:-1],
        ):
            full_content += token
            yield f"data: {json.dumps({'token': token})}\n\n"

        # Save complete response
        await add_message(db, conversation_id, role="assistant", content=full_content)
        yield f"data: {json.dumps({'done': True, 'conversation_id': str(conversation_id)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/conversations", response_model=list[ConversationOut])
async def get_conversations(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List user's conversations."""
    return await list_conversations(db, user.id, limit=limit, offset=offset)


@router.post("/conversations", response_model=ConversationOut)
async def create_new_conversation(
    req: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new conversation."""
    return await create_conversation(db, user.id, title=req.title)


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: uuid.UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get messages for a conversation."""
    conv = await get_conversation(db, conversation_id, user.id)
    if not conv:
        return {"status": "error", "message": "Conversation not found"}
    messages = await get_recent_messages_for_context(db, conversation_id, limit=limit)
    return {"status": "success", "messages": messages}


@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time voice interaction."""
    await websocket.accept()
    logger.info("Voice WebSocket connected")

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "audio_chunk":
                # Forward to OpenAI Realtime API (placeholder for proxy)
                await websocket.send_json({
                    "type": "processing",
                    "message": "Audio received, processing...",
                })

            elif msg.get("type") == "text":
                # Process text command
                response = await agent.get_response(
                    user_message=msg.get("content", ""),
                )
                await websocket.send_json({
                    "type": "response",
                    "content": response.get("content", ""),
                    "tool_results": response.get("tool_results"),
                })

                # Generate TTS audio
                if response.get("content"):
                    from services.voice import text_to_speech
                    audio = await text_to_speech(response["content"])
                    if audio:
                        import base64
                        await websocket.send_json({
                            "type": "audio",
                            "data": base64.b64encode(audio).decode(),
                            "format": "mp3",
                        })

            elif msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info("Voice WebSocket disconnected")
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
