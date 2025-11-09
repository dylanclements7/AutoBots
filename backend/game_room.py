import asyncio
from typing import Dict, Optional
from fastapi import WebSocket
import importlib
import copy
import requests
import json
import ast
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["clarkathon2025"]
game_data = db["games"]



class GameRoom:
    def __init__(self, game_type: str, room_id: str, players: Dict[str, WebSocket]):
        """
        game_type: the type of game (connect4, tictactoe, etc.)
        room_id: unique room identifier
        players: dict of {player_id: websocket} assigned to this room
        """
        self.game_type = game_type
        self.room_id = room_id
        self.clients = players
        self.game_running = False
        self.game = game_data.find_one({ "title": f"{game_type}" })
        
        # MongoDB returns these as native Python types - no json.loads needed
        symbols = self.game['player_symbols']  # Already a list like ['X', 'O']
        self.starting_state = self.game['state_format']  # Already parsed
        
        # Check if state_format is a dict with 'board' key, or just the board itself
        if isinstance(self.starting_state, dict) and 'board' in self.starting_state:
            self.state_is_dict = True
            self.starting_board = self.starting_state['board']
        else:
            self.state_is_dict = False
            self.starting_board = self.starting_state
        
        # Initialize board and game_state
        if self.state_is_dict:
            self.game_state = copy.deepcopy(self.starting_state)
            self.board = copy.deepcopy(self.starting_board)
        else:
            self.board = copy.deepcopy(self.starting_board)
            self.game_state = self.board
        
        # Player management
        self.turn_order = list(players.keys())
        self.current_turn = 0
        self.pending_moves: Dict[str, asyncio.Queue] = {
            player_id: asyncio.Queue() for player_id in players.keys()
        }
        
        # Bot code storage (not executed server-side, just tracked)
        self.bot_codes: Dict[str, bool] = {}
        
        # Player symbols (X, O, etc.) - will be a dict mapping player_id to symbol
        self.player_symbols = {}  # Initialize as empty dict
        self.available_symbols = symbols  # Store the list of available symbols
        self._assign_symbols()
        
        # Winner tracking
        self.winner = None
        
    def _assign_symbols(self):
        """Assign symbols to players based on game requirements"""
        # Use the available_symbols list to assign to each player
        for i, player_id in enumerate(self.turn_order):
            self.player_symbols[player_id] = self.available_symbols[i % len(self.available_symbols)]
    
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
        
        # Reset game state - use deep copy to avoid mutation
        if self.state_is_dict:
            self.game_state = copy.deepcopy(self.starting_state)
            self.board = copy.deepcopy(self.starting_board)
        else:
            self.board = copy.deepcopy(self.starting_board)
            self.game_state = self.board
        
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
                
                # Get code directly from MongoDB - it's already a string
                code = self.game['code']

                # Pass only the board to the game functions, not the full state dict
                error, new_board = makeMove(code, self.board, move, symbol)

                if error:
                    # Handle invalid move
                    await self._end_game_invalid_move(current_player)
                    break

                # Update the board
                self.board = new_board
                
                # Update game_state (either just the board or the dict with board)
                if self.state_is_dict:
                    self.game_state['board'] = new_board
                else:
                    self.game_state = new_board

                await self.broadcast({
                    "type": "board_update",
                    "gameState": self.game_state,
                    "lastMove": {"player": current_player, "move": move}
                })
                
                winner_result = checkWinner(code, self.board)
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
            self.winner = "draw"
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
            
            self.winner = winner_player
            
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
    """Execute make_move function via Piston API"""
    # Convert board to proper JSON string
    board_json = json.dumps(board)

    source = code + f"\nresult = make_move({board_json}, {move}, '{symbol}')\nprint(result)"

    url = "https://emkc.org/api/v2/piston/execute"
    payload = {
        "language": "python",
        "version": "3.10.0",
        "files": [{
            "content": source
        }]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    output = data.get("run", {}).get("output", "").strip()

    try:
        result = eval(output)  # Safely parse the tuple
        return result  # Returns (error, board)
    except:
        print(f"Error parsing output: {output}")
        return (True, board)  # Return error if parsing fails


def checkWinner(code: str, board):
    """Execute check_winner function via Piston API"""
    # Convert board to proper JSON string
    board_json = json.dumps(board)

    source = code + f"\nresult = check_winner({board_json})\nprint(result)"

    url = "https://emkc.org/api/v2/piston/execute"
    payload = {
        "language": "python",
        "version": "3.10.0",
        "files": [{
            "content": source
        }]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    output = data.get("run", {}).get("output", "").strip()

    if output in ["'X'", "'O'", "'draw'"]:
        return output.strip("'")
    elif output == "None":
        return None
    else:
        return output if output else None