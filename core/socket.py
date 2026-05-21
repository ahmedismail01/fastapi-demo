from fastapi import WebSocket
from typing import Dict
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    def get_connection(self, user_id: str):
        return self.active_connections.get(user_id)

    async def send_personal_message(self, user_id: str, data):
        websocket = self.active_connections.get(user_id)
        message = json.dumps(data)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, data: dict):
        for websocket in self.active_connections.values():
            await websocket.send_text(json.dumps(data))

    async def notify_followers(
            self,
            user_id: str,
            message: str,
            followers: list[str]
    ):
        for follower_id in followers:
            await self.send_personal_message(
                follower_id,
                message
            )

    async def send_message_to_followers(self, type, data, author: str, followers):
        data.update({"type": type, "author": author})
        for following in followers:
            await self.send_personal_message(following.follower_id, data)


manager = ConnectionManager()
