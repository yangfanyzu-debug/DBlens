from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies.auth import get_current_user
from app.schemas.ai import AiChatRequest
from app.services.ai_assistant import stream_chat_events

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat/stream")
async def stream_chat(request: AiChatRequest, _current_user=Depends(get_current_user)):
    return StreamingResponse(
        stream_chat_events(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
