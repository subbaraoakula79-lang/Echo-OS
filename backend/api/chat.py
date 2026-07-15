from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from schemas.models import MessageCreate
from core.agent import agent
import services.tools  # Ensure tools are registered

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/completions")
async def chat_completions(req: MessageCreate, db: AsyncSession = Depends(get_db)):
    msg_list = [{"role": req.role, "content": req.content}]
    response = await agent.get_response(msg_list)
    
    # Store message in DB (mocked for now)
    
    return {"status": "success", "message": response}

@router.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Placeholder for OpenAI Realtime Voice integration
            await websocket.send_text(f"Echo Voice Server received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected from voice server")
