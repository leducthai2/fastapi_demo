import requests
from typing import Annotated, Dict, List
import json
from enum import Enum
from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)
from models.models import Item
import uvicorn
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from config.setting import settings

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                var itemId = document.getElementById("itemId")
                var token = document.getElementById("token")
                ws = new WebSocket("ws://localhost:8000/items/" + itemId.value + "/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault()
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

app = FastAPI()

# Store active WebSocket connections for different rooms
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message: str, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse(html)

async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@app.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    item_id: str,
    q: int | None = None,
    cookie_or_token: Annotated[str, Depends(get_cookie_or_token)],
):
    await manager.connect(websocket, item_id)
    await manager.broadcast(f"A new user joined room {item_id}!", item_id)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(
                f"Session cookie or query token value is: {cookie_or_token}",
                item_id
            )
            if q is not None:
                await manager.broadcast(f"Query parameter q is: {q}", item_id)
            await manager.broadcast(f"Message text was: {data}", item_id)
    except WebSocketException:
        manager.disconnect(websocket, item_id)
        await manager.broadcast(f"A user left room {item_id}.", item_id)


@app.post("/chat/gemini")
async def send_prompt(prompt_item: Item):
    prompt = prompt_item.text

    genai.configure(api_key=settings.gemini_key)

    model = genai.GenerativeModel(settings.gemini_version)
    response = model.generate_content(prompt)
    return {"response": response.text}


if __name__ == "__main__":
   uvicorn.run("gemini_api:app", host="0.0.0.0", port=8000, reload=True)

