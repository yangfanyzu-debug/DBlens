from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ws.manager import ws_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{query_id}")
async def websocket_endpoint(websocket: WebSocket, query_id: str):
    print(f"[WS] Client connected: {query_id}")
    await ws_manager.connect(query_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            print(f"[WS] Received from client: {data}")
            if data.get("type") == "kill":
                from app.services.query_executor import kill_query
                await kill_query(data.get("query_id", query_id))
    except WebSocketDisconnect:
        print(f"[WS] Client disconnected: {query_id}")
        ws_manager.disconnect(query_id)
