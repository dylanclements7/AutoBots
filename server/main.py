from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Optional, Dict, Any
import importlib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global lobbies structure: lobby_id -> lobby_state
lobbies: Dict[str, Dict[str, Any]] = {}

# Game registry - maps game_type to module
GAMES = {
    "connect4": "server.games.connect4",
    # "tictactoe": "games.tictactoe",
    # "chess": "games.chess",
}


def get_game_module(game_type: str):
    """Dynamically import and return game module"""
    if game_type not in GAMES:
        raise ValueError(f"Unknown game type: {game_type}")
    return importlib.import_module(GAMES[game_type])


def create_lobby(lobby_id: str, game_type: str):
    """Create a new lobby for a specific game type"""
    game_module = get_game_module(game_type)
    
    lobbies[lobby_id] = {
        "game_type": game_type,
        "players": {},  # username -> websocket
        "ready": set(),
        "bot_codes": {},  # username -> True (just tracking submission)
        "board": game_module.create_initial_board(),
        "turn_order": [],
        "current_turn": 0,
        "state": "lobby",  # "lobby" | "ide" | "playing" | "finished"
        "pending_moves": {},  # username -> asyncio.Queue
        "game_data": {},  # Game-specific data
    }
    return lobbies[lobby_id]


async def broadcast(lobby_id: str, message: dict, exclude: Optional[str] = None):
    """Send message to all players in a lobby"""
    lobby = lobbies.get(lobby_id)
    if not lobby:
        return
    
    for username, ws in lobby["players"].items():
        if exclude and username == exclude:
            continue
        try:
            await ws.send_json(message)
        except:
            pass


async def run_game(lobby_id: str):
    """Main game loop - delegates to game-specific logic"""
    lobby = lobbies.get(lobby_id)
    if not lobby:
        return
    
    game_module = get_game_module(lobby["game_type"])
    players = lobby["turn_order"]
    
    if len(players) < game_module.MIN_PLAYERS:
        print(f"Not enough players. Need {game_module.MIN_PLAYERS}, have {len(players)}")
        return
    
    # Reset board
    lobby["board"] = game_module.create_initial_board()
    lobby["current_turn"] = 0
    lobby["state"] = "playing"
    
    # Send game start with player assignments
    for i, username in enumerate(players):
        symbol = game_module.get_player_symbol(i)
        ws = lobby["players"][username]
        await ws.send_json({
            "type": "game_start",
            "board": lobby["board"],
            "symbol": symbol,
            "players": players,
            "game_type": lobby["game_type"]
        })
    
    print(f"Game '{lobby['game_type']}' started with players: {players}")
    
    # Game loop
    while lobby["state"] == "playing":
        current_player = players[lobby["current_turn"]]
        symbol = game_module.get_player_symbol(lobby["current_turn"])
        ws = lobby["players"].get(current_player)
        
        if not ws:
            print(f"Player {current_player} not found!")
            break
        
        try:
            # Request move from current player
            await ws.send_json({
                "type": "your_turn",
                "board": lobby["board"],
                "symbol": symbol,
            })
            
            print(f"Waiting for move from {current_player} ({symbol})")
            
            # Wait for move from queue
            queue = lobby["pending_moves"].get(current_player)
            if not queue:
                print(f"No queue for {current_player}")
                break
            
            move = await asyncio.wait_for(queue.get(), timeout=15)
            print(f"{current_player} sent move: {move}")
            
            # Validate and make move using game-specific logic
            is_valid, error_msg = game_module.validate_move(lobby["board"], move, symbol)
            
            if not is_valid:
                print(f"Invalid move from {current_player}: {error_msg}")
                other_player = players[1 - lobby["current_turn"]]
                await broadcast(lobby_id, {
                    "type": "game_over",
                    "winner": other_player,
                    "reason": f"{current_player} made invalid move: {error_msg}",
                    "board": lobby["board"]
                })
                lobby["state"] = "finished"
                break
            
            # Apply the move
            game_module.apply_move(lobby["board"], move, symbol)
            
            # Broadcast board update
            await broadcast(lobby_id, {
                "type": "board_update",
                "board": lobby["board"]
            })
            
            # Check for winner
            winner = game_module.check_winner(lobby["board"])
            if winner:
                lobby["state"] = "finished"
                if winner == "draw":
                    await broadcast(lobby_id, {
                        "type": "game_over",
                        "winner": "draw",
                        "reason": "Game ended in a draw",
                        "board": lobby["board"]
                    })
                else:
                    # Find which player has this symbol
                    winner_player = None
                    for i, player in enumerate(players):
                        if game_module.get_player_symbol(i) == winner:
                            winner_player = player
                            break
                    
                    await broadcast(lobby_id, {
                        "type": "game_over",
                        "winner": winner_player,
                        "reason": f"{winner_player} wins!",
                        "board": lobby["board"]
                    })
                break
            
            # Next turn
            lobby["current_turn"] = (lobby["current_turn"] + 1) % len(players)
            await asyncio.sleep(0.3)
            
        except asyncio.TimeoutError:
            print(f"{current_player} took too long!")
            other_player = players[1 - lobby["current_turn"]]
            await broadcast(lobby_id, {
                "type": "game_over",
                "winner": other_player,
                "reason": f"{current_player} timeout",
                "board": lobby["board"]
            })
            lobby["state"] = "finished"
            break
        except Exception as e:
            print(f"Error in game loop: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("Game ended")


@app.websocket("/ws/{lobby_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, lobby_id: str, username: str):
    await websocket.accept()
    
    # Create lobby if it doesn't exist (default to connect4)
    # In production, you'd pass game_type as a query param
    if lobby_id not in lobbies:
        create_lobby(lobby_id, "connect4")
    
    lobby = lobbies[lobby_id]
    
    # Check if username taken
    if username in lobby["players"]:
        await websocket.send_json({
            "type": "error",
            "message": "Username already taken"
        })
        await websocket.close()
        return
    
    # Register player
    lobby["players"][username] = websocket
    if username not in lobby["turn_order"]:
        lobby["turn_order"].append(username)
    lobby["pending_moves"][username] = asyncio.Queue()
    
    print(f"{username} connected to {lobby_id}. Total players: {len(lobby['players'])}")
    
    # Send lobby state
    await broadcast(
        lobby_id,
        {
            "type": "lobby_state",
            "players": list(lobby["players"].keys()),
            "ready": list(lobby["ready"]),
            "game_type": lobby["game_type"]
        },
    )
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "ready":
                lobby["ready"].add(username)
                print(f"{username} is ready in {lobby_id}")
                
                await broadcast(
                    lobby_id,
                    {
                        "type": "lobby_state",
                        "players": list(lobby["players"].keys()),
                        "ready": list(lobby["ready"]),
                    },
                )
                
                game_module = get_game_module(lobby["game_type"])
                min_players = game_module.MIN_PLAYERS
                
                # When all players ready -> start IDE phase
                if len(lobby["ready"]) == len(lobby["players"]) and len(lobby["players"]) >= min_players:
                    lobby["state"] = "ide"
                    print(f"Starting IDE phase for {lobby_id}")
                    await broadcast(lobby_id, {"type": "ide_start"})
            
            elif msg_type == "bot_code":
                lobby["bot_codes"][username] = True  # Just mark submitted
                print(f"{username} submitted bot. Total: {len(lobby['bot_codes'])}/{len(lobby['players'])}")
                
                # When all players submitted -> start game
                if len(lobby["bot_codes"]) == len(lobby["players"]) and len(lobby["players"]) >= 2:
                    print(f"All bots submitted for {lobby_id}, starting game!")
                    asyncio.create_task(run_game(lobby_id))
            
            elif msg_type == "move":
                # Move format depends on game (could be column, coordinate, etc.)
                move = data.get("move")
                if move is not None:
                    await lobby["pending_moves"][username].put(move)
                    print(f"Queued move from {username}: {move}")
            
            elif msg_type == "restart":
                print(f"{username} requested restart in {lobby_id}")
                game_module = get_game_module(lobby["game_type"])
                lobby["board"] = game_module.create_initial_board()
                lobby["ready"].clear()
                lobby["bot_codes"].clear()
                lobby["current_turn"] = 0
                lobby["state"] = "lobby"
                
                await broadcast(
                    lobby_id,
                    {
                        "type": "lobby_state",
                        "players": list(lobby["players"].keys()),
                        "ready": list(lobby["ready"]),
                    },
                )
    
    except WebSocketDisconnect:
        print(f"{username} disconnected from {lobby_id}")
    finally:
        # Clean up player
        lobby["players"].pop(username, None)
        lobby["ready"].discard(username)
        lobby["bot_codes"].pop(username, None)
        lobby["pending_moves"].pop(username, None)
        if username in lobby["turn_order"]:
            lobby["turn_order"].remove(username)
        
        # Notify remaining players
        await broadcast(
            lobby_id,
            {
                "type": "lobby_state",
                "players": list(lobby["players"].keys()),
                "ready": list(lobby["ready"]),
            },
        )
        
        # If game was playing, end it
        if lobby["state"] == "playing":
            lobby["state"] = "finished"
            await broadcast(lobby_id, {
                "type": "game_over",
                "winner": "forfeit",
                "reason": f"{username} disconnected",
                "board": lobby["board"]
            })
        
        # Clean up empty lobbies
        if len(lobby["players"]) == 0:
            print(f"Lobby {lobby_id} is empty, removing...")
            lobbies.pop(lobby_id, None)


@app.get("/")
async def root():
    return {
        "available_games": list(GAMES.keys()),
        "active_lobbies": len(lobbies),
        "lobbies": {
            lobby_id: {
                "game_type": lobby["game_type"],
                "players": len(lobby["players"]),
                "state": lobby["state"]
            }
            for lobby_id, lobby in lobbies.items()
        }
    }