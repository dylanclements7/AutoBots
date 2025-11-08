from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

lobbies = {
    "demo": {
        "players": {},  # username -> websocket
        "ready": set(),
        "bot_codes": {},  # username -> code (stored but not used by server)
        "board": [[" " for _ in range(7)] for _ in range(6)],
        "turn_order": [],  # list of usernames
        "current_turn": 0,
        "state": "lobby",  # "lobby" | "ide" | "playing" | "finished"
        "pending_moves": {},  # username -> asyncio.Queue for moves
    }
}


def check_winner(board) -> Optional[str]:
    """Check for a winner in Connect 4. Returns 'X', 'O', 'draw', or None"""
    rows, cols = 6, 7
    
    # Check horizontal
    for r in range(rows):
        for c in range(cols - 3):
            if board[r][c] != " " and all(board[r][c+i] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check vertical
    for r in range(rows - 3):
        for c in range(cols):
            if board[r][c] != " " and all(board[r+i][c] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check diagonal (down-right)
    for r in range(rows - 3):
        for c in range(cols - 3):
            if board[r][c] != " " and all(board[r+i][c+i] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check diagonal (down-left)
    for r in range(rows - 3):
        for c in range(3, cols):
            if board[r][c] != " " and all(board[r+i][c-i] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check for draw
    if all(board[0][c] != " " for c in range(cols)):
        return "draw"
    
    return None


def is_valid_move(board, col: int) -> bool:
    """Check if a column has space"""
    if col < 0 or col >= 7:
        return False
    return board[0][col] == " "


def make_move(board, col: int, symbol: str) -> bool:
    """Make a move and return success"""
    if not is_valid_move(board, col):
        return False
    
    # Drop piece
    for row in reversed(board):
        if row[col] == " ":
            row[col] = symbol
            break
    
    return True


async def broadcast(lobby_name, message, exclude=None):
    """Send message to all players in the lobby."""
    lobby = lobbies[lobby_name]
    for username, ws in lobby["players"].items():
        if exclude and username == exclude:
            continue
        try:
            await ws.send_json(message)
        except:
            pass


async def run_game(lobby_name):
    """Main game loop that requests moves from players"""
    lobby = lobbies[lobby_name]
    players = lobby["turn_order"]
    
    if len(players) < 2:
        print("Not enough players to start game.")
        return
    
    # Reset board
    board = [[" " for _ in range(7)] for _ in range(6)]
    lobby["board"] = board
    lobby["current_turn"] = 0
    lobby["state"] = "playing"
    
    # Send game start with player assignments
    for i, username in enumerate(players):
        symbol = "X" if i == 0 else "O"
        ws = lobby["players"][username]
        await ws.send_json({
            "type": "game_start",
            "board": board,
            "symbol": symbol,
            "players": players
        })
    
    print(f"Game started with players: {players}")
    
    # Game loop
    while lobby["state"] == "playing":
        current_player = players[lobby["current_turn"]]
        symbol = "X" if lobby["current_turn"] == 0 else "O"
        ws = lobby["players"].get(current_player)
        
        if not ws:
            print(f"Player {current_player} not found!")
            break
        
        try:
            # Request move from current player
            await ws.send_json({
                "type": "your_turn",
                "board": board,
                "symbol": symbol,
            })
            
            print(f"Waiting for move from {current_player} ({symbol})")
            
            # Wait for move from queue
            queue = lobby["pending_moves"].get(current_player)
            if not queue:
                print(f"No queue for {current_player}")
                break
                
            col = await asyncio.wait_for(queue.get(), timeout=15)
            
            print(f"{current_player} played column {col}")
            
            # Validate and make move
            if not make_move(board, col, symbol):
                print(f"Invalid move from {current_player}: column {col}")
                # End game, other player wins
                other_player = players[1 - lobby["current_turn"]]
                await broadcast(lobby_name, {
                    "type": "game_over",
                    "winner": other_player,
                    "reason": f"{current_player} made invalid move",
                    "board": board
                })
                lobby["state"] = "finished"
                break
            
            # Broadcast board update
            await broadcast(lobby_name, {
                "type": "board_update",
                "board": board
            })
            
            # Check for winner
            winner_symbol = check_winner(board)
            if winner_symbol:
                lobby["state"] = "finished"
                if winner_symbol == "draw":
                    await broadcast(lobby_name, {
                        "type": "game_over",
                        "winner": "draw",
                        "reason": "Board full",
                        "board": board
                    })
                else:
                    winner_player = players[0] if winner_symbol == "X" else players[1]
                    await broadcast(lobby_name, {
                        "type": "game_over",
                        "winner": winner_player,
                        "reason": "Connected 4",
                        "board": board
                    })
                break
            
            # Next turn
            lobby["current_turn"] = (lobby["current_turn"] + 1) % 2
            await asyncio.sleep(0.3)  # Small delay between turns
            
        except asyncio.TimeoutError:
            print(f"{current_player} took too long!")
            other_player = players[1 - lobby["current_turn"]]
            await broadcast(lobby_name, {
                "type": "game_over",
                "winner": other_player,
                "reason": f"{current_player} timeout",
                "board": board
            })
            lobby["state"] = "finished"
            break
        except Exception as e:
            print(f"Error in game loop: {e}")
            break
    
    print("Game ended")


@app.websocket("/ws/demo/{username}")
async def websocket_demo(websocket: WebSocket, username: str):
    await websocket.accept()
    lobby_name = "demo"
    lobby = lobbies[lobby_name]
    
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
    
    print(f"{username} connected. Total players: {len(lobby['players'])}")
    
    # Send lobby state
    await broadcast(
        lobby_name,
        {
            "type": "lobby_state",
            "players": list(lobby["players"].keys()),
            "ready": list(lobby["ready"]),
        },
    )
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "ready":
                lobby["ready"].add(username)
                print(f"{username} is ready. Ready: {len(lobby['ready'])}/{len(lobby['players'])}")
                
                await broadcast(
                    lobby_name,
                    {
                        "type": "lobby_state",
                        "players": list(lobby["players"].keys()),
                        "ready": list(lobby["ready"]),
                    },
                )
                
                # When all players ready -> start IDE phase
                if len(lobby["ready"]) == len(lobby["players"]) and len(lobby["players"]) >= 2:
                    lobby["state"] = "ide"
                    print("Starting IDE phase")
                    await broadcast(lobby_name, {"type": "ide_start"})
            
            elif msg_type == "bot_code":
                lobby["bot_codes"][username] = data["code"]
                print(f"{username} submitted bot code. Total: {len(lobby['bot_codes'])}/{len(lobby['players'])}")
                
                # When all players submitted code -> start game
                if len(lobby["bot_codes"]) == len(lobby["players"]) and len(lobby["players"]) >= 2:
                    print("All bots submitted, starting game!")
                    asyncio.create_task(run_game(lobby_name))
            
            elif msg_type == "move":
                # Put move in queue for game loop
                col = data.get("column")
                if col is not None:
                    await lobby["pending_moves"][username].put(col)
                    print(f"Queued move from {username}: column {col}")
            
            elif msg_type == "restart":
                print(f"{username} requested restart")
                lobby["board"] = [[" " for _ in range(7)] for _ in range(6)]
                lobby["ready"].clear()
                lobby["bot_codes"].clear()
                lobby["current_turn"] = 0
                lobby["state"] = "lobby"
                
                await broadcast(
                    lobby_name,
                    {
                        "type": "lobby_state",
                        "players": list(lobby["players"].keys()),
                        "ready": list(lobby["ready"]),
                    },
                )
    
    except WebSocketDisconnect:
        print(f"{username} disconnected")
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
            lobby_name,
            {
                "type": "lobby_state",
                "players": list(lobby["players"].keys()),
                "ready": list(lobby["ready"]),
            },
        )
        
        # If game was playing, end it
        if lobby["state"] == "playing":
            lobby["state"] = "finished"
            await broadcast(lobby_name, {
                "type": "game_over",
                "winner": "forfeit",
                "reason": f"{username} disconnected",
                "board": lobby["board"]
            })