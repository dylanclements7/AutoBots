from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from typing import Dict, List

app = FastAPI()

# --- WebSocket route first ---
rooms: Dict[str, List[Dict]] = {}

@app.websocket("/ws/{room_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, player_name: str):
    await websocket.accept()
    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append({"name": player_name, "ws": websocket})
    await broadcast(room_id, f"✅ {player_name} joined the room!")
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(room_id, f"{player_name}: {data}")
    except WebSocketDisconnect:
        rooms[room_id] = [p for p in rooms[room_id] if p["ws"] != websocket]
        await broadcast(room_id, f"❌ {player_name} left the room")

async def broadcast(room_id: str, message: str):
    for player in rooms.get(room_id, []):
        try:
            await player["ws"].send_text(message)
        except:
            pass

# --- Mount static files last ---
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)