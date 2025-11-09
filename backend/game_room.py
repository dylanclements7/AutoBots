import asyncio
from typing import Dict, Optional
from fastapi import WebSocket
import importlib
import copy

class GameRoom:
    def __init__(self, game_type: str, room_id: str, players: Dict[str, WebSocket]):
        """
        game_type: the type of game (connect_four, tic_tac_toe, etc.)
        room_id: unique room identifier
        players: dict of {player_id: websocket} assigned to this room
        """
        self.game_type = game_type
        self.room_id = room_id
        self.clients = players
        self.game_running = False
        
        # Load game module dynamically
        try:
            self.game_module = importlib.import_module(f"game_files.{game_type}")
        except Exception as e:
            print(f"ERROR: Could not load game module 'game_files.{game_type}': {e}")
            raise
        
        # Initialize game state from module
        starting_state = self.game_module.starting_game_state
        if hasattr(starting_state, 'copy'):
            self.game_state = starting_state.copy()
        else:
            # Deep copy for nested lists
            self.game_state = copy.deepcopy(starting_state)
        
        # Player management
        self.turn_order = list(players.keys())
        self.current_turn = 0
        self.pending_moves: Dict[str, asyncio.Queue] = {
            player_id: asyncio.Queue() for player_id in players.keys()
        }
        
        # Bot code storage (not executed server-side, just tracked)
        self.bot_codes: Dict[str, bool] = {}
        
        # Player symbols (X, O, etc.)
        self.player_symbols = {}
        self._assign_symbols()
        
        # Winner tracking
        self.winner = None
        
    def _assign_symbols(self):
        """Assign symbols to players based on game requirements"""
        symbols = getattr(self.game_module, 'player_symbols', ['X', 'O'])
        for i, player_id in enumerate(self.turn_order):
            self.player_symbols[player_id] = symbols[i % len(symbols)]
    
    async def broadcast(self, message: dict, exclude: Optional[str] = None):
        """Send message to all players in the room"""
        for player_id, ws in self.clients.items():
            if exclude and player_id == exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to {player_id}: {e}")
    
    async def send_to(self, player_id: str, message: dict):
        """Send message to specific player"""
        try:
            await self.clients[player_id].send_json(message)
        except Exception as e:
            print(f"Error sending to {player_id}: {e}")
    
    async def handle_bot_submission(self, player_id: str):
        """Handle when a player submits their bot code"""
        self.bot_codes[player_id] = True
        print(f"{player_id} submitted bot code. Total: {len(self.bot_codes)}/{len(self.clients)}")
        
        # Start game when all bots submitted
        if len(self.bot_codes) == len(self.clients):
            print(f"All bots submitted for room {self.room_id}, starting game!")
            asyncio.create_task(self.run_game())
    
    async def handle_move(self, player_id: str, move_data: dict):
        """Queue a move from a player"""
        move = move_data.get("move")
        if move is not None:
            await self.pending_moves[player_id].put(move)
            print(f"Queued move from {player_id} in room {self.room_id}: {move}")
    
    async def run_game(self):
        """Main game loop - requests moves from players and validates them"""
        if self.game_running:
            return
        
        self.game_running = True
        
        # Reset game state - FIXED: use deep copy
        self.game_state = copy.deepcopy(self.game_module.starting_game_state)
        self.current_turn = 0
        
        # Send game start with player assignments
        for player_id in self.turn_order:
            await self.send_to(player_id, {
                "type": "game_start",
                "roomId": self.room_id,
                "gameState": self.game_state,
                "symbol": self.player_symbols[player_id],
                "players": self.turn_order,
                "yourTurn": player_id == self.turn_order[0]
            })
        
        print(f"Game started in room {self.room_id} with players: {self.turn_order}")
        
        # Main game loop
        while self.game_running:
            current_player = self.turn_order[self.current_turn]
            symbol = self.player_symbols[current_player]
            
            try:
                # Request move from current player
                await self.send_to(current_player, {
                    "type": "your_turn",
                    "gameState": self.game_state,
                    "symbol": symbol,
                })
                
                print(f"Waiting for move from {current_player} ({symbol})")
                
                # Wait for move from queue (with timeout)
                move = await asyncio.wait_for(
                    self.pending_moves[current_player].get(),
                    timeout=15.0
                )
                
                print(f"{current_player} played move: {move}")
                
                filepath = "/game_files"+self.game_type+".py"

                with open(filepath, 'r') as f:
                    code = f.read()

                error, self.game_state = makeMove(code, self.game_state, move, symbol)

                

                # Broadcast board update
                await self.broadcast({
                    "type": "board_update",
                    "gameState": self.game_state,
                    "lastMove": {"player": current_player, "move": move}
                })
                
                # Check for winner
                winner_result = checkWinner(code, self.game_state)
                if winner_result:
                    await self._end_game_winner(winner_result)
                    break
                
                # Next turn
                self.current_turn = (self.current_turn + 1) % len(self.turn_order)
                await asyncio.sleep(0.3)  # Small delay between turns
                
            except asyncio.TimeoutError:
                print(f"{current_player} took too long!")
                await self._end_game_timeout(current_player)
                break
            except Exception as e:
                print(f"Error in game loop for room {self.room_id}: {e}")
                await self.broadcast({
                    "type": "game_error",
                    "error": str(e)
                })
                break
        
        print(f"Game ended in room {self.room_id}")
        self.game_running = False
    
    async def _end_game_invalid_move(self, offending_player: str):
        """End game due to invalid move"""
        # Other player(s) win
        other_players = [p for p in self.turn_order if p != offending_player]
        winner = other_players[0] if len(other_players) == 1 else None
        self.winner = winner
        
        await self.broadcast({
            "type": "game_over",
            "roomId": self.room_id,
            "winner": winner,
            "reason": f"{offending_player} made invalid move",
            "gameState": self.game_state
        })
        self.game_running = False
    
    async def _end_game_timeout(self, offending_player: str):
        """End game due to timeout"""
        other_players = [p for p in self.turn_order if p != offending_player]
        winner = other_players[0] if len(other_players) == 1 else None
        self.winner = winner
        
        await self.broadcast({
            "type": "game_over",
            "roomId": self.room_id,
            "winner": winner,
            "reason": f"{offending_player} timeout",
            "gameState": self.game_state
        })
        self.game_running = False
    
    async def _end_game_winner(self, winner_result):
        """End game with a winner or draw"""
        if winner_result == "draw":
            self.winner = "draw"  # ADD THIS LINE
            await self.broadcast({
                "type": "game_over",
                "roomId": self.room_id,
                "winner": "draw",
                "reason": "Game drawn",
                "gameState": self.game_state
            })
        else:
            # winner_result is the symbol, find the player
            winner_player = None
            for player_id, symbol in self.player_symbols.items():
                if symbol == winner_result:
                    winner_player = player_id
                    break
            
            self.winner = winner_player  # MOVE THIS OUTSIDE THE LOOP
            
            await self.broadcast({
                "type": "game_over",
                "roomId": self.room_id,
                "winner": winner_player,
                "reason": "Victory",
                "gameState": self.game_state
            })
        
        self.game_running = False
    
    async def handle_disconnect(self, player_id: str):
        """Handle player disconnection"""
        print(f"{player_id} disconnected from room {self.room_id}")
        
        if self.game_running:
            # End game, other player wins
            other_players = [p for p in self.turn_order if p != player_id]
            winner = other_players[0] if len(other_players) == 1 else None
            self.winner = winner
            
            await self.broadcast({
                "type": "game_over",
                "roomId": self.room_id,
                "winner": winner,
                "reason": f"{player_id} disconnected",
                "gameState": self.game_state
            }, exclude=player_id)
            
            self.game_running = False

def makeMove(code: str, board, move, symbol):
    url = "https://emkc.org/api/v2/piston/execute"
    payload = {
        "language": "python3",
        "version": "3.10.0",
        "source": code + "\n"+ f"makeMove({board}, {move}, {symbol})"  # directly pass code as string
    }

    response = requests.post(url, json=payload)
    data = response.json()

    output = data.get("run", {}).get("output", "")
    return output.strip()

def checkWinner(code: str, board):
    url = "https://emkc.org/api/v2/piston/execute"
    payload = {
        "language": "python3",
        "version": "3.10.0",
        "source": code + "\n"+ f"makeMove({board})"  # directly pass code as string
    }

    response = requests.post(url, json=payload)
    data = response.json()

    output = data.get("run", {}).get("output", "")
    return output.strip()

# import asyncio
# from typing import Dict
# from fastapi import WebSocket

# class GameRoom:
#     def __init__(self, game_type: str, room_id: str):
#         self.game_type = game_type
#         self.room_id = room_id
#         self.clients: Dict[str, WebSocket] = {}
#         self.game_running = False

#     async def connect(self, player_id: str, websocket: WebSocket):
#         self.clients[player_id] = websocket
#         await self.broadcast({"type": "PLAYER_JOINED", "playerId": player_id})

#         if len(self.clients) == 2 and not self.game_running:
#             asyncio.create_task(self.run_game())

#     async def disconnect(self, player_id: str):
#         del self.clients[player_id]
#         await self.broadcast({"type": "PLAYER_LEFT", "playerId": player_id})

#     async def broadcast(self, message: dict):
#         for ws in list(self.clients.values()):
#             await ws.send_json(message)

#     async def send_to(self, player_id: str, message: dict):
#         await self.clients[player_id].send_json(message)

#     async def handle_message(self, player_id: str, message: dict):
#         # for example: chat messages or ready signals
#         await self.broadcast({"from": player_id, **message})

#     async def run_game(self):
#         self.game_running = True
#         await self.broadcast({"type": "GAME_START"})

#         players = list(self.clients.keys())
#         current = 0

#         for turn in range(10):  # replace with real game logic
#             await self.broadcast({
#                 "type": "TURN",
#                 "turn": turn,
#                 "playerId": players[current]
#             })
#             await asyncio.sleep(1)
#             current = 1 - current

#         await self.broadcast({"type": "GAME_END", "result": "DEMO"})
#         self.game_running = False




# import asyncio
# from typing import Dict
# from fastapi import WebSocket
# from game_files import *

# class GameRoom:
#     def __init__(self, game_type: str, room_id: str, players: Dict[str, WebSocket]):
#         """
#         game_type: the type of game (connect4, tictactoe, etc.)
#         room_id: unique room identifier
#         players: dict of {player_id: websocket} assigned to this room
#         """
#         self.game_type = game_type
#         self.room_id = room_id
#         self.clients = players
#         self.game_running = False
#         self.game_state = game_type.starting_game_state.copy()
#         self.turn_order = []
#         self.current_turn = 0

#     async def broadcast(self, message: dict):
#         for ws in list(self.clients.values()):
#             await ws.send_json(message)

#     async def run_game(self):
#         self.game_running = True
#         await self.broadcast({"type": "GAME_START", "roomId": self.room_id})

#         players = list(self.clients.keys())
#         current = 0

#         # Example: simple demo game loop
#         for turn in range(10):
#             await self.broadcast({
#                 "type": "TURN",
#                 "turn": turn,
#                 "playerId": players[current]
#             })
#             await asyncio.sleep(1)
#             current = 1 - current

#         await self.broadcast({"type": "GAME_END", "roomId": self.room_id, "result": "DEMO"})
#         self.game_running = False
