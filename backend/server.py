from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from typing import Dict, List
import random, string
from pymongo import MongoClient

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client["clarkathon2025"]
user_data = db["users"]
user_data.insert_one({
    "username": "charlie",
    "rating": 0
})

"""
users.insert_one(user)

# Insert many documents
users.insert_many([
    {"name": "Bob", "age": 30},
    {"name": "Charlie", "age": 28},
])

# Get first matching document
print(users.find_one({"name": "Alice"}))

# Get all users older than 26
for user in users.find({"age": {"$gt": 26}}):
    print(user)
"""




games = [
    "CONNECT4",
    "TICTACTOE"
]

def generate_id(length: int):
   letters = string.ascii_letters + string.digits
   return ''.join(random.choice(letters) for i in range(length))

"""
User requests ID from server
Server generates ID and saves it to database with player name
"""
@app.get("/get_player_id")
def get_player_id(player_name: str):
    new_id = generate_id(10)

    #TODO: save id and name to DB

    return new_id

"""
Waiting room for players 
If enough players ready up, breakdown into appropriate groups and send to game rooms
Each get their own websocket
Get time to code
Once time is up, first player does first move
"""
@app.websocket("/ws/{game_type}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_type: str, player_id: str):
    pass


# TODO: change player name to player id
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

# # --- Mount static files last ---
# app.mount("/", StaticFiles(directory="static", html=True), name="static")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)