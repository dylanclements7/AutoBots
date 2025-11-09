from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
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

client = MongoClient("mongodb://localhost:27017/")
db = client["clarkathon2025"]
games_collection = db["games"]
user_data = db["users"]
games_collection.insert_one({
    "title": "connect4",
    "objective": "Build a connect four bot that can outsmart your opponent",
    "game_summary": "Connect 4 is a two-player strategy board game where players take turns dropping colored discs into a vertical grid. The objective is to be the first to form a horizontal, vertical, or diagonal line of four discs of the same color.",
    "win_condition": "First player to connect four of their symbols in a row (horizontally, vertically, or diagonally) wins. If the board fills up without a winner, the game ends in a draw.",
    "task": "Create a bot that can play Connect 4 by implementing strategies to block your opponent and create opportunities to win.",
    "bot_input_format": "Your bot will receive the current game board as a 2D array, where empty cells are represented by ' ', your pieces by 'X', and your opponent's pieces by 'O'.",
    "bot_output_format": "Your bot should output the column index (0-6) where it wants to drop its piece.",
    "state_format": {"board": [[" " for _ in range(7)] for _ in range(6)], "current_player": "X"},
    "player_symbols": ["X", "O"],
    "difficulty": "Medium",
    "code": r'''
from typing import Optional

def is_valid_move(board, col: int) -> bool:
    """Check if a column has space"""
    if col < 0 or col >= 7:
        return False
    return board[0][col] == " "


def make_move(board, col: int, symbol: str):
    """Make a move and return success"""
    if not is_valid_move(board, col):
        return (True, board)
    
    # Drop piece
    for row in reversed(board):
        if row[col] == " ":
            row[col] = symbol
            break
    
    return (False, board)

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
''',
    "html": """<!DOCTYPE html>
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
"""
})

games_collection.insert_one({
    "title": "tictactoe",
    "objective": "Build a Tic Tac Toe bot that can outsmart your opponent",
    "game_summary": "Tic Tac Toe is a classic two-player game played on a 3x3 grid. Players take turns placing their symbols (X or O) in empty cells, aiming to align three of their symbols horizontally, vertically, or diagonally to win the game.",
    "win_condition": "The first player to align three of their symbols in a row (horizontally, vertically, or diagonally) wins. If all cells are filled without a winner, the game ends in a draw.",
    "task": "Create a bot that can play Tic Tac Toe by implementing strategies to block your opponent and create opportunities to win.",
    "bot_input_format": "Your bot will receive the current game board as a 2D array, where empty cells are represented by ' ', your pieces by 'X', and your opponent's pieces by 'O'.",
    "bot_output_format": "Your bot should output the cell index (0-8) where it wants to place its symbol, with indices mapped left→right, top→bottom.",
    "state_format": {"board": [[" " for _ in range(3)] for _ in range(3)], "current_player": "X"},
    "player_symbols": ["X", "O"],
    "difficulty": "Easy",
    "code": r'''
from typing import Optional

def is_valid_move(board, pos: int) -> bool:
    """
    Check if a move is valid.
    For Tic Tac Toe, pos is 0-8 representing cells left→right, top→bottom.
    """
    if pos < 0 or pos > 8:
        return False
    
    row, col = divmod(pos, 3)
    return board[row][col] == " "


def make_move(board, pos: int, symbol: str):
    """Place the symbol if the move is valid. Return True if move made."""
    if not is_valid_move(board, pos):
        return (True, board)
    
    row, col = divmod(pos, 3)
    board[row][col] = symbol
    return (False, board)


def check_winner(board) -> Optional[str]:
    """Check for a winner. Returns 'X', 'O', 'draw', or None"""
    lines = []

    # Rows & Columns
    for i in range(3):
        lines.append(board[i])                      # row i
        lines.append([board[0][i], board[1][i], board[2][i]])  # col i

    # Diagonals
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])

    # Check winners
    for line in lines:
        if line[0] != " " and line.count(line[0]) == 3:
            return line[0]

    # Check for draw (all cells filled)
    if all(board[r][c] != " " for r in range(3) for c in range(3)):
        return "draw"

    return None
''',
    "html": """<!DOCTYPE html>
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
"""
})

@app.websocket("/ws/{game_type}/{username}")
async def join_lobby(websocket: WebSocket, game_type: str, username: str):
    """
    Main WebSocket endpoint for game lobby and gameplay
    """
    await websocket.accept()
    
    # Validate game type (using title as identifier since name field doesn't exist yet)
    game = games_collection.find_one({"title": game_type})
    if not game:
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
    #check if a tournament can start
    tournament = await lobby.try_start_tournament(game_type)
    if tournament:
        await websocket.send_json({
            "type": "tournament_started",
            "tournament": tournament
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
    Return list of available games from database
    """
    games = list(games_collection.find({}, {
        "_id": 0,  # Exclude MongoDB's _id field
        "name": 1,
        "title": 1,
        "difficulty": 1,
        "game_summary": 1,
        "objective": 1,
        "player_symbols": 1
    }))
    
    # Also return the full game data for detailed views
    game_data = list(games_collection.find({}, {"_id": 0}))
    
    return {
        "games": games,  # List of game summaries
        "gameData": game_data  # Full game details
    }


@app.get("/api/lobby/{game_type}/status")
async def get_lobby_status(game_type: str):
    """
    Get current lobby status for a game type
    """
    print([game for game in games_collection.find({}, {"name": 1})])
    games = [game["title"] for game in games_collection.find({}, {"name": 1})]
    print('GAMES', games)
    if game_type not in games:
        raise HTTPException(status_code=404, detail="Game type not found")
    
    queue = lobby.queues.get(game_type, {})
    
    
    return {
        "game_type": game_type,
        "total_players": len(queue),
        "players": list(queue.keys()),
        
    }

class GameModel(BaseModel):
    title: str
    objective: str
    game_summary: str
    win_condition: str
    task: str
    bot_input_format: str
    bot_output_format: str
    state_format: Dict[str, Any]
    player_symbols: List[str]
    difficulty: str
    code: str
    html: str
    
@app.post("/add_game_to_db")
async def add_game_to_db(game: GameModel):
    # Auto-generate name from title (lowercase, no spaces)
    name = game.title.lower().replace(" ", "")
    
    # Check if a game with this name already exists
    if games_collection.find_one({"name": name}):
        raise HTTPException(status_code=400, detail="A game with this title already exists.")
    
    # Insert into MongoDB with auto-generated name
    game_dict = game.dict()
    game_dict["name"] = name
    games_collection.insert_one(game_dict)

    return {"message": "Game added successfully!", "title": game.title, "name": name}


# Optional: Serve static files for frontend
# app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)