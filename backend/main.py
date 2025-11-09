from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from pymongo import MongoClient
from lobby import Lobby
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize lobby system
lobby = Lobby()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["clarkathon2025"]
user_data = db["users"]

# Supported games
games = [
    "connect4",
    "tictactoe"
]


# @app.post("/sign_up")
# def sign_up(username: str, password_hash: str):
#     """
#     Handle user authentication/registration
#     """
#     existing_user = user_data.find_one({"username": username})
    
#     if existing_user:
#         # Username exists, check password
#         if existing_user["password_hash"] == password_hash:
#             return {"username": username, "rating": existing_user.get("rating", 0)}
#         else:
#             raise HTTPException(status_code=400, detail="Username taken or password incorrect")
    
#     # Username does not exist, create new user
#     user_data.insert_one({
#         "username": username,
#         "password_hash": password_hash,
#         "rating": 0
#     })
    
#     return {"username": username, "rating": 0}

@app.websocket("/ws/{game_type}/{username}")
async def join_lobby(websocket: WebSocket, game_type: str, username: str):
    """
    Main WebSocket endpoint for game lobby and gameplay
    """
    await websocket.accept()
    
    # Validate game type
    if game_type not in games:
        await websocket.send_json({
            "type": "error",
            "message": f"Invalid game type: {game_type}"
        })
        await websocket.close()
        return
    
    # Join lobby (not async anymore)
    success = lobby.join_lobby(game_type, username, websocket)
    if not success:
        await websocket.send_json({
            "type": "error",
            "message": "Username already taken"
        })
        await websocket.close()
        return
    # Now broadcast the updated lobby state
    await lobby.broadcast_lobby_state(game_type)
    
    print(f"{username} connected to {game_type} lobby")
    
    # Track current room for this player
    current_room_id = None
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "ready":
                # Player marks themselves as ready
                await lobby.player_ready(game_type, username)
            
            elif msg_type == "unready":
                # Player marks themselves as not ready
                await lobby.player_unready(game_type, username)
            
            elif msg_type == "bot_code":
                # Player submits their bot code
                room_id = data.get("roomId")
                if room_id:
                    current_room_id = room_id
                    await lobby.handle_bot_submission(game_type, room_id, username)
                else:
                    print(f"Warning: {username} sent bot_code without roomId")
            
            elif msg_type == "move":
                # Player makes a move in their game
                room_id = data.get("roomId") or current_room_id
                if room_id:
                    await lobby.handle_move(game_type, room_id, username, data)
                else:
                    print(f"Warning: {username} sent move without roomId")
            
            elif msg_type == "chat":
                # Optional: handle chat messages in lobby
                message = data.get("message", "")
                await lobby.broadcast_lobby_state(game_type)  # Could add chat broadcast
            
            elif msg_type == "leave_lobby":
                # Player leaves lobby
                await lobby.leave_lobby(game_type, username)
                break
    
    except WebSocketDisconnect:
        print(f"{username} disconnected from {game_type}")
    except Exception as e:
        print(f"Error for {username} in {game_type}: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up on disconnect
        await lobby.leave_lobby(game_type, username)
        
        # If player was in a game room, handle disconnect
        if current_room_id and game_type in lobby.rooms:
            game_room = lobby.rooms[game_type].get(current_room_id)
            if game_room:
                await game_room.handle_disconnect(username)


@app.get("/api/games")
async def get_games():
    """
    Return list of available games
    """
    return {"games": games}


@app.get("/api/lobby/{game_type}/status")
async def get_lobby_status(game_type: str):
    """
    Get current lobby status for a game type
    """
    if game_type not in games:
        raise HTTPException(status_code=404, detail="Game type not found")
    
    queue = lobby.queues.get(game_type, {})
    ready = lobby.ready_players.get(game_type, set())
    
    return {
        "game_type": game_type,
        "total_players": len(queue),
        "ready_players": len(ready),
        "players": list(queue.keys()),
        "ready_list": list(ready)
    }


@app.get("/api/user/{username}/stats")
async def get_user_stats(username: str):
    """
    Get user statistics from database
    """
    user = user_data.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user["username"],
        "rating": user.get("rating", 0),
        "wins": user.get("wins", 0),
        "losses": user.get("losses", 0),
        "games_played": user.get("games_played", 0)
    }


@app.post("/api/user/{username}/update_stats")
async def update_user_stats(username: str, win: bool):
    """
    Update user stats after a game
    """
    user = user_data.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate new rating (simple ELO-like system)
    current_rating = user.get("rating", 0)
    rating_change = 25 if win else -15
    new_rating = max(0, current_rating + rating_change)
    
    # Update stats
    user_data.update_one(
        {"username": username},
        {
            "$set": {"rating": new_rating},
            "$inc": {
                "games_played": 1,
                "wins" if win else "losses": 1
            }
        }
    )
    
    return {
        "username": username,
        "new_rating": new_rating,
        "rating_change": rating_change
    }


@app.on_event("startup")
async def startup_event():
    """
    Initialize any startup tasks
    """
    print("Server starting up...")
    print(f"Available games: {games}")
    
    # Ensure indexes on user collection
    user_data.create_index("username", unique=True)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up on shutdown
    """
    print("Server shutting down...")
    client.close()


# Optional: Serve static files for frontend
# app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)