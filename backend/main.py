from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from pymongo import MongoClient
from lobby import Lobby
import asyncio
from fastapi.responses import HTMLResponse

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
games_collection = db["games"]

# Supported games
games = [
    "connect4",
    "tictactoe"
]

gameData = {
    "connect4": {
        "title": "Connect 4",
        "html":"""
    <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connect 4 Board</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #1a1a2e;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        
        .container {
            text-align: center;
        }
        
        .board {
            display: inline-grid;
            grid-template-columns: repeat(7, 70px);
            gap: 8px;
            background: #0066cc;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }
        
        .cell {
            width: 70px;
            height: 70px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: inset 0 3px 8px rgba(0, 0, 0, 0.2);
        }
        
        .cell.X {
            background: #ff4444;
            box-shadow: inset 0 3px 8px rgba(0, 0, 0, 0.4);
            animation: drop 0.4s ease-out;
        }
        
        .cell.O {
            background: #ffeb3b;
            box-shadow: inset 0 3px 8px rgba(0, 0, 0, 0.4);
            animation: drop 0.4s ease-out;
        }
        
        @keyframes drop {
            0% {
                transform: translateY(-500px);
                opacity: 0;
            }
            60% {
                transform: translateY(10px);
            }
            100% {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        .status {
            margin-top: 20px;
            color: white;
            font-size: 20px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
        }
        
        .player-info {
            margin-bottom: 20px;
            color: white;
            font-size: 18px;
        }
        
        .turn-indicator {
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-left: 10px;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="player-info">
            <span id="playerSymbol">Waiting...</span>
            <span id="turnIndicator" class="turn-indicator" style="display: none;"></span>
        </div>
        <div class="board" id="board"></div>
        <div class="status" id="status">Connecting...</div>
    </div>

    <script>
        const boardEl = document.getElementById('board');
        const statusEl = document.getElementById('status');
        const playerSymbolEl = document.getElementById('playerSymbol');
        const turnIndicatorEl = document.getElementById('turnIndicator');
        
        let mySymbol = '';
        let currentBoard = [];
        
        // Initialize empty board
        function initBoard() {
            boardEl.innerHTML = '';
            for (let row = 0; row < 6; row++) {
                for (let col = 0; col < 7; col++) {
                    const cell = document.createElement('div');
                    cell.className = 'cell';
                    cell.dataset.row = row;
                    cell.dataset.col = col;
                    boardEl.appendChild(cell);
                }
            }
        }
        
        // Update board display
        function updateBoard(board) {
            currentBoard = board;
            const cells = boardEl.querySelectorAll('.cell');
            
            board.forEach((row, rowIdx) => {
                row.forEach((cell, colIdx) => {
                    const cellIdx = rowIdx * 7 + colIdx;
                    const cellEl = cells[cellIdx];
                    
                    // Remove old classes
                    cellEl.classList.remove('X', 'O');
                    
                    // Add new class if occupied
                    if (cell === 'X') {
                        cellEl.classList.add('X');
                    } else if (cell === 'O') {
                        cellEl.classList.add('O');
                    }
                });
            });
        }
        
        // Listen for messages from parent window
        window.addEventListener('message', (event) => {
            const data = event.data;
            
            if (data.type === 'game_start') {
                mySymbol = data.symbol;
                playerSymbolEl.textContent = `You are: ${mySymbol} (${mySymbol === 'X' ? '🔴 Red' : '🟡 Yellow'})`;
                updateBoard(data.board);
                statusEl.textContent = 'Game started!';
            } 
            else if (data.type === 'board_update') {
                updateBoard(data.gameState || data.board);
                statusEl.textContent = 'Board updated';
            }
            else if (data.type === 'your_turn') {
                updateBoard(data.gameState || data.board);
                statusEl.textContent = '🤖 Your turn! Running bot...';
                turnIndicatorEl.style.display = 'inline-block';
                turnIndicatorEl.style.background = mySymbol === 'X' ? '#ff4444' : '#ffeb3b';
            }
            else if (data.type === 'waiting') {
                statusEl.textContent = "⏳ Opponent's turn...";
                turnIndicatorEl.style.display = 'none';
            }
            else if (data.type === 'game_over') {
                if (data.board) updateBoard(data.board);
                
                let msg = '';
                if (data.winner === 'draw') {
                    msg = '🤝 Game ended in a draw!';
                } else if (data.winner === mySymbol) {
                    msg = '🎉 You won!';
                } else {
                    msg = `😞 You lost. Winner: ${data.winner}`;
                }
                
                statusEl.textContent = msg;
                turnIndicatorEl.style.display = 'none';
            }
            else if (data.type === 'status') {
                statusEl.textContent = data.message;
            }
        });
        
        // Initialize
        initBoard();
        
        // Tell parent we're ready
        window.parent.postMessage({ type: 'board_ready' }, '*');
    </script>
</body>
</html>
""", 
        "description":"Connect 4 is a two-player strategy board game where players take turns dropping colored discs into a vertical grid. The objective is to be the first to form a horizontal, vertical, or diagonal line of four discs of the same color."
    },
    "tictactoe": {
        "title": "Tic-Tac-Toe",
        "html":"""
    <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tic-Tac-Toe Board</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        
        .container {
            text-align: center;
        }
        
        .board {
            display: inline-grid;
            grid-template-columns: repeat(3, 120px);
            gap: 10px;
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .cell {
            width: 120px;
            height: 120px;
            background: white;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 60px;
            font-weight: bold;
            cursor: default;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .cell.X {
            color: #e74c3c;
            animation: appear 0.4s ease-out;
        }
        
        .cell.O {
            color: #3498db;
            animation: appear 0.4s ease-out;
        }
        
        .cell.X::before {
            content: '✕';
            position: absolute;
            font-size: 80px;
        }
        
        .cell.O::before {
            content: '○';
            position: absolute;
            font-size: 80px;
        }
        
        .cell.winning {
            background: #f1c40f;
            animation: win-pulse 0.6s ease-in-out infinite;
        }
        
        @keyframes appear {
            0% {
                transform: scale(0) rotate(-180deg);
                opacity: 0;
            }
            60% {
                transform: scale(1.2) rotate(10deg);
            }
            100% {
                transform: scale(1) rotate(0deg);
                opacity: 1;
            }
        }
        
        @keyframes win-pulse {
            0%, 100% {
                transform: scale(1);
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            }
            50% {
                transform: scale(1.05);
                box-shadow: 0 6px 20px rgba(241, 196, 15, 0.6);
            }
        }
        
        .status {
            margin-top: 25px;
            color: white;
            font-size: 22px;
            padding: 15px 25px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            backdrop-filter: blur(10px);
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .player-info {
            margin-bottom: 25px;
            color: white;
            font-size: 20px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .turn-indicator {
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-left: 10px;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        
        .grid-line {
            position: absolute;
            background: rgba(255, 255, 255, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="player-info">
            <span id="playerSymbol">Waiting...</span>
            <span id="turnIndicator" class="turn-indicator" style="display: none;"></span>
        </div>
        <div class="board" id="board"></div>
        <div class="status" id="status">Connecting...</div>
    </div>

    <script>
        const boardEl = document.getElementById('board');
        const statusEl = document.getElementById('status');
        const playerSymbolEl = document.getElementById('playerSymbol');
        const turnIndicatorEl = document.getElementById('turnIndicator');
        
        let mySymbol = '';
        let currentBoard = [];
        let winningCells = [];
        
        // Initialize empty board
        function initBoard() {
            boardEl.innerHTML = '';
            for (let row = 0; row < 3; row++) {
                for (let col = 0; col < 3; col++) {
                    const cell = document.createElement('div');
                    cell.className = 'cell';
                    cell.dataset.row = row;
                    cell.dataset.col = col;
                    boardEl.appendChild(cell);
                }
            }
        }
        
        // Find winning line
        function findWinningLine(board) {
            // Check rows
            for (let r = 0; r < 3; r++) {
                if (board[r][0] !== ' ' && board[r][0] === board[r][1] && board[r][1] === board[r][2]) {
                    return [[r, 0], [r, 1], [r, 2]];
                }
            }
            
            // Check columns
            for (let c = 0; c < 3; c++) {
                if (board[0][c] !== ' ' && board[0][c] === board[1][c] && board[1][c] === board[2][c]) {
                    return [[0, c], [1, c], [2, c]];
                }
            }
            
            // Check diagonals
            if (board[0][0] !== ' ' && board[0][0] === board[1][1] && board[1][1] === board[2][2]) {
                return [[0, 0], [1, 1], [2, 2]];
            }
            if (board[0][2] !== ' ' && board[0][2] === board[1][1] && board[1][1] === board[2][0]) {
                return [[0, 2], [1, 1], [2, 0]];
            }
            
            return null;
        }
        
        // Update board display
        function updateBoard(board, highlightWin = false) {
            currentBoard = board;
            const cells = boardEl.querySelectorAll('.cell');
            
            // Find winning line if game is over
            const winLine = highlightWin ? findWinningLine(board) : null;
            
            board.forEach((row, rowIdx) => {
                row.forEach((cell, colIdx) => {
                    const cellIdx = rowIdx * 3 + colIdx;
                    const cellEl = cells[cellIdx];
                    
                    // Remove old classes
                    cellEl.classList.remove('X', 'O', 'winning');
                    
                    // Add new class if occupied
                    if (cell === 'X') {
                        cellEl.classList.add('X');
                    } else if (cell === 'O') {
                        cellEl.classList.add('O');
                    }
                    
                    // Highlight winning cells
                    if (winLine) {
                        for (let [r, c] of winLine) {
                            if (r === rowIdx && c === colIdx) {
                                cellEl.classList.add('winning');
                            }
                        }
                    }
                });
            });
        }
        
        // Listen for messages from parent window
        window.addEventListener('message', (event) => {
            const data = event.data;
            
            if (data.type === 'game_start') {
                mySymbol = data.symbol;
                playerSymbolEl.textContent = `You are: ${mySymbol} (${mySymbol === 'X' ? '✕ Red' : '○ Blue'})`;
                updateBoard(data.board || data.gameState);
                statusEl.textContent = 'Game started!';
            } 
            else if (data.type === 'board_update') {
                updateBoard(data.gameState || data.board);
                statusEl.textContent = 'Board updated';
            }
            else if (data.type === 'your_turn') {
                updateBoard(data.gameState || data.board);
                statusEl.textContent = '🤖 Your turn! Running bot...';
                turnIndicatorEl.style.display = 'inline-block';
                turnIndicatorEl.style.background = mySymbol === 'X' ? '#e74c3c' : '#3498db';
            }
            else if (data.type === 'waiting') {
                statusEl.textContent = "⏳ Opponent's turn...";
                turnIndicatorEl.style.display = 'none';
            }
            else if (data.type === 'game_over') {
                const board = data.board || data.gameState;
                if (board) updateBoard(board, true); // Highlight winning line
                
                let msg = '';
                if (data.winner === 'draw') {
                    msg = '🤝 Game ended in a draw!';
                } else if (data.winner === mySymbol) {
                    msg = '🎉 You won!';
                } else {
                    msg = `😞 You lost. Winner: ${data.winner}`;
                }
                
                statusEl.textContent = msg;
                turnIndicatorEl.style.display = 'none';
            }
            else if (data.type === 'status') {
                statusEl.textContent = data.message;
            }
        });
        
        // Initialize
        initBoard();
        
        // Tell parent we're ready
        window.parent.postMessage({ type: 'board_ready' }, '*');
    </script>
</body>
</html>
""", 
        "description":"Tic-tac-toe is a two-player strategy board game where players take turns dropping colored discs into a vertical grid. The objective is to be the first to form a horizontal, vertical, or diagonal line of four discs of the same color."
    }
}


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
    
<<<<<<< HEAD
    # Join lobby (not async anymore)
=======
>>>>>>> newpistonproblems
    success = lobby.join_lobby(game_type, username, websocket)
    if not success:
        await websocket.send_json({
            "type": "error",
            "message": "Username already taken"
        })
        await websocket.close()
        return
<<<<<<< HEAD
    #check if a tournament can start
    tournament = await lobby.try_start_tournament(game_type)
    if tournament:
        await websocket.send_json({
            "type": "tournament_started",
            "tournament": tournament
        })
        await websocket.close()
        return

=======
    
    
>>>>>>> newpistonproblems
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
    return {"games": games, "gameData": gameData}


@app.get("/api/lobby/{game_type}/status")
async def get_lobby_status(game_type: str):
    """
    Get current lobby status for a game type
    """
    if game_type not in games:
        raise HTTPException(status_code=404, detail="Game type not found")
    
    queue = lobby.queues.get(game_type, {})
    
    
    return {
        "game_type": game_type,
        "total_players": len(queue),
        "players": list(queue.keys()),
        
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
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    