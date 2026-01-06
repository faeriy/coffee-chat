from typing import List

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Waiting till websocket accepts connection and append to the active connections"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Close the websocket connection"""
        self.active_connections.remove(websocket)

    async def send_personal_message(self, websocket: WebSocket, message: str) -> None:
        """Send text to the websocket"""
        await websocket.send_text(message)

    async def broadcast(self, message: str) -> None:
        """Broadcast the message to all of the active connections"""
        for connection in self.active_connections:
            connection.send_text(message)


connection_manager: ConnectionManager = ConnectionManager()


@app.websocket("ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int) -> None:
    await connection_manager.connect()

    try:
        while True:
            data: str = await websocket.receive_text()
            await connection_manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket=websocket)
        await connection_manager.broadcast(f"Client #{client_id} left the chat")
