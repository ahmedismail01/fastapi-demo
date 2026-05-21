from fastapi import Depends, WebSocket, WebSocketDisconnect, APIRouter
from core.socket import manager
from core.dependencies import get_current_user
from core.security import verify_access_token

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params["token"]
    user_id = verify_access_token(token)["id"]

    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
