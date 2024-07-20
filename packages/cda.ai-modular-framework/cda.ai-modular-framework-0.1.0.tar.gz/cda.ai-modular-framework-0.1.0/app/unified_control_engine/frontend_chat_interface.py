from fastapi import APIRouter, WebSocket
import json

class FrontendChatbotInterface:
    def __init__(self):
        self.router = APIRouter()

    async def websocket_endpoint(self, websocket: WebSocket):
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            response = self.handle_message(data)
            await websocket.send_text(response)

    def handle_message(self, message: str) -> str:
        response = {"message": f"Received: {message}"}
        return json.dumps(response)

    def setup_routes(self):
        self.router.websocket("/ws")(self.websocket_endpoint)