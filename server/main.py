from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

lobbies = {
    "demo": {
        "players": {},  # username -> websocket
        "turn_order": [],  # list of usernames
        "board": [[" "]*7 for _ in range(6)],
        "current_turn": 0
    }
}

@app.websocket("/ws/demo/{username}")
async def websocket_demo(websocket: WebSocket, username: str):
    await websocket.accept()
    lobby = lobbies["demo"]

    # Register player if not already
    if username not in lobby["players"]:
        lobby["players"][username] = websocket
        lobby["turn_order"].append(username)

    # Send initial info
    await websocket.send_json({
        "type": "info",
        "symbol": "X" if lobby["turn_order"].index(username) == 0 else "O",
        "board": lobby["board"],
        "message": f"Joined lobby demo as {username}"
    })

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "move":
                # Check if it's this player's turn
                if lobby["turn_order"][lobby["current_turn"]] != username:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Not your turn!"
                    })
                    continue

                col = data["column"]
                board = lobby["board"]

                # Drop piece in the first empty row from bottom
                for row in reversed(board):
                    if row[col] == " ":
                        row[col] = "X" if lobby["turn_order"].index(username) == 0 else "O"
                        break

                # Advance turn
                lobby["current_turn"] = (lobby["current_turn"] + 1) % len(lobby["turn_order"])

                # Broadcast updated board to all players
                for player_ws in lobby["players"].values():
                    await player_ws.send_json({
                        "type": "update",
                        "board": board,
                        "winner": None
                    })

    except WebSocketDisconnect:
        # Remove player on disconnect
        lobby["players"].pop(username, None)
        if username in lobby["turn_order"]:
            lobby["turn_order"].remove(username)
