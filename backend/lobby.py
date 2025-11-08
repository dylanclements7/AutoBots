# from managers.game_room import GameRoom
# import random, string

# def generate_id(length: int):
#    letters = string.ascii_letters + string.digits
#    return ''.join(random.choice(letters) for i in range(length))

# class RoomManager:
#     def __init__(self):
#         self.rooms = {
#         "CONNECT4": {},
#         "TICTACTOE": {}
#         }  # game_type -> GameRoom

#         # self.room_id = max()

#     def find_room(self, game_type: str) -> GameRoom:
#         game_rooms = self.rooms[game_type]
#         # check if there is an open room
#         for room in game_rooms:
#             if not room.game_running and len(room.clients) < 2:
#                 return room
        
#         # no open rooms exist
#         new_id = generate_id()

#         # if game_rooms:                existing_ids = list(map(int, game_rooms.keys()))
#         #     new_id = str(max(existing_ids) + 1)        #     

#         new_room = GameRoom(game_type, new_id)
#         game_rooms[new_id] = new_room
#         return (new_room, new_id)

#     # TODO: Remove game room when game finished   


# room_manager = RoomManager()

# import asyncio
# from typing import Dict, List
# from fastapi import WebSocket
# from game_room import GameRoom

# class Lobby:
#     def __init__(self):
#         # game_type -> dict of player_id -> websocket
#         self.queues: Dict[str, Dict[str, WebSocket]] = {}
#         # game_type -> number of players per game
#         self.players_per_game: Dict[str, int] = {
#             "CONNECT4": 2,
#             "TICTACTOE": 2
#         }
#         # Keep track of game rooms
#         self.rooms: Dict[str, Dict[str, GameRoom]] = {}

#     async def join_lobby(self, game_type: str, username: str, websocket: WebSocket):
#         if game_type not in self.queues:
#             self.queues[game_type] = {}
#             self.rooms[game_type] = {}

#         self.queues[game_type][username] = websocket
#         await self.broadcast_lobby(game_type, {"type": "PLAYER_JOINED_LOBBY", "playerId": username})

#         await self.try_start_game(game_type)

#     async def leave_lobby(self, game_type: str, player_id: str):
#         if player_id in self.queues.get(game_type, {}):
#             del self.queues[game_type][player_id]
#             await self.broadcast_lobby(game_type, {"type": "PLAYER_LEFT_LOBBY", "playerId": player_id})

#     async def broadcast_lobby(self, game_type: str, message: dict):
#         for ws in list(self.queues.get(game_type, {}).values()):
#             await ws.send_json(message)

#     async def try_start_game(self, game_type: str):
#         """
#         Check if enough players are ready in the lobby to start a game.
#         If so, remove them from the queue and start a new GameRoom.
#         """
#         queue = self.queues[game_type]
#         num_needed = self.players_per_game[game_type]

#         while len(queue) >= num_needed:
#             # Pop the first N players from the queue
#             selected_players: Dict[str, WebSocket] = {}
#             for _ in range(num_needed):
#                 player_id, ws = queue.popitem()
#                 selected_players[player_id] = ws

#             # Generate a room ID
#             room_id = str(len(self.rooms[game_type]) + 1)

#             # Create and store GameRoom
#             game_room = GameRoom(game_type, room_id, selected_players)
#             self.rooms[game_type][room_id] = game_room

#             # Start the game asynchronously
#             asyncio.create_task(game_room.run_game())

#             # Notify players
#             for pid in selected_players.keys():
#                 await selected_players[pid].send_json({
#                     "type": "GAME_STARTING",
#                     "roomId": room_id,
#                     "players": list(selected_players.keys())
#                 })

import asyncio
from typing import Dict, List, Optional
from fastapi import WebSocket
from game_room import GameRoom
import math

class Lobby:
    def __init__(self):
        # game_type -> dict of player_id -> websocket
        self.queues: Dict[str, Dict[str, WebSocket]] = {}
        
        # game_type -> set of ready players
        self.ready_players: Dict[str, set] = {}
        
        # Track active tournaments per game type
        self.active_tournaments: Dict[str, 'Tournament'] = {}
        
        # Track individual game rooms
        self.rooms: Dict[str, Dict[str, GameRoom]] = {}

    def join_lobby(self, game_type: str, username: str, websocket: WebSocket):
        """Player joins the lobby for a specific game type"""
        if game_type not in self.queues:
            self.queues[game_type] = {}
            self.ready_players[game_type] = set()
            self.rooms[game_type] = {}

        # Check if username is already in lobby
        if username in self.queues[game_type]:
            return False  # Don't use await here

        self.queues[game_type][username] = websocket
        
        # Broadcast is async, so we need to handle this differently
        return True

    async def leave_lobby(self, game_type: str, player_id: str):
        """Player leaves the lobby"""
        if player_id in self.queues.get(game_type, {}):
            del self.queues[game_type][player_id]
            self.ready_players[game_type].discard(player_id)
            await self.broadcast_lobby_state(game_type)

    async def player_ready(self, game_type: str, player_id: str):
        """Mark a player as ready"""
        if player_id not in self.queues.get(game_type, {}):
            return
        
        self.ready_players[game_type].add(player_id)
        print(f"{player_id} is ready. Ready: {len(self.ready_players[game_type])}/{len(self.queues[game_type])}")
        
        await self.broadcast_lobby_state(game_type)
        
        # Check if we can start a tournament
        await self.try_start_tournament(game_type)

    async def player_unready(self, game_type: str, player_id: str):
        """Mark a player as not ready"""
        self.ready_players[game_type].discard(player_id)
        await self.broadcast_lobby_state(game_type)

    async def broadcast_lobby_state(self, game_type: str):
        """Broadcast current lobby state to all players"""
        queue = self.queues.get(game_type, {})
        ready = self.ready_players.get(game_type, set())
        
        message = {
            "type": "lobby_state",
            "players": list(queue.keys()),
            "ready": list(ready),
            "readyCount": len(ready),
            "totalCount": len(queue)
        }
        
        for ws in list(queue.values()):
            try:
                await ws.send_json(message)
            except:
                pass

    async def try_start_tournament(self, game_type: str):
        """Check if we have enough ready players to start a tournament"""
        ready = self.ready_players[game_type]
        
        # Need a power of 2 (2, 4, 8, 16, etc.)
        if len(ready) < 2:
            return
        
        # Check if it's a power of 2
        if not self._is_power_of_2(len(ready)):
            return
        
        # All ready players must still be in the queue
        valid_ready = [p for p in ready if p in self.queues[game_type]]
        if len(valid_ready) != len(ready):
            # Clean up invalid ready players
            self.ready_players[game_type] = set(valid_ready)
            return
        
        print(f"Starting tournament for {game_type} with {len(ready)} players")
        
        # Extract players from queue
        tournament_players = {}
        for player_id in list(ready):
            tournament_players[player_id] = self.queues[game_type].pop(player_id)
            self.ready_players[game_type].remove(player_id)
        
        # Create and start tournament
        tournament = Tournament(game_type, tournament_players, self)
        self.active_tournaments[game_type] = tournament
        asyncio.create_task(tournament.run())
        
        # Update lobby state for remaining players
        await self.broadcast_lobby_state(game_type)

    def _is_power_of_2(self, n: int) -> bool:
        """Check if n is a power of 2"""
        return n > 0 and (n & (n - 1)) == 0

    async def handle_bot_submission(self, game_type: str, room_id: str, player_id: str):
        """Forward bot submission to the appropriate game room"""
        if game_type in self.rooms and room_id in self.rooms[game_type]:
            await self.rooms[game_type][room_id].handle_bot_submission(player_id)

    async def handle_move(self, game_type: str, room_id: str, player_id: str, move_data: dict):
        """Forward move to the appropriate game room"""
        if game_type in self.rooms and room_id in self.rooms[game_type]:
            await self.rooms[game_type][room_id].handle_move(player_id, move_data)

    def register_room(self, game_type: str, room_id: str, game_room: GameRoom):
        """Register a game room"""
        if game_type not in self.rooms:
            self.rooms[game_type] = {}
        self.rooms[game_type][room_id] = game_room


class Tournament:
    def __init__(self, game_type: str, players: Dict[str, WebSocket], lobby: Lobby):
        self.game_type = game_type
        self.players = players  # All players in tournament
        self.lobby = lobby
        self.current_round = 1
        self.total_rounds = int(math.log2(len(players)))
        self.active_players = list(players.keys())  # Players still in tournament
        self.round_results: Dict[int, List[str]] = {}  # round -> list of winners

    async def run(self):
        """Run the entire tournament"""
        print(f"Tournament started with {len(self.players)} players, {self.total_rounds} rounds")
        
        # Notify all players tournament is starting
        await self.broadcast({
            "type": "tournament_start",
            "totalPlayers": len(self.players),
            "totalRounds": self.total_rounds,
            "players": self.active_players
        })
        
        # Run each round
        while self.current_round <= self.total_rounds:
            print(f"Starting round {self.current_round}/{self.total_rounds}")
            
            await self.broadcast({
                "type": "round_start",
                "round": self.current_round,
                "totalRounds": self.total_rounds,
                "activePlayers": self.active_players
            })
            
            winners = await self.run_round()
            self.round_results[self.current_round] = winners
            self.active_players = winners
            
            await self.broadcast({
                "type": "round_end",
                "round": self.current_round,
                "winners": winners
            })
            
            self.current_round += 1
            
            # Wait between rounds
            if self.current_round <= self.total_rounds:
                await asyncio.sleep(3)
        
        # Tournament complete
        champion = self.active_players[0] if self.active_players else None
        print(f"Tournament complete! Champion: {champion}")
        
        await self.broadcast({
            "type": "tournament_complete",
            "champion": champion,
            "results": self.round_results
        })

    async def run_round(self) -> List[str]:
        """Run a single round of matches and return winners"""
        # Pair up players for this round
        matches = []
        players_copy = self.active_players.copy()
        
        while len(players_copy) >= 2:
            player1 = players_copy.pop(0)
            player2 = players_copy.pop(0)
            matches.append((player1, player2))
        
        print(f"Round {self.current_round} matches: {matches}")
        
        # Create game rooms for all matches
        game_tasks = []
        for match_idx, (player1, player2) in enumerate(matches):
            room_id = f"{self.game_type}_R{self.current_round}_M{match_idx+1}"
            
            match_players = {
                player1: self.players[player1],
                player2: self.players[player2]
            }
            
            game_room = GameRoom(self.game_type, room_id, match_players)
            self.lobby.register_room(self.game_type, room_id, game_room)
            
            print(f"Created game room {room_id} for {player1} vs {player2}")
            
            # Notify players their match is starting
            for player_id in [player1, player2]:
                try:
                    await self.players[player_id].send_json({
                        "type": "match_starting",
                        "roomId": room_id,
                        "round": self.current_round,
                        "opponent": player2 if player_id == player1 else player1
                    })
                    print(f"Sent match_starting to {player_id}")
                except Exception as e:
                    print(f"Error sending match_starting to {player_id}: {e}")
            
            # Small delay to ensure match_starting is received
            await asyncio.sleep(0.1)
            
            # Send IDE start message to both players
            try:
                await game_room.broadcast({
                    "type": "ide_start",
                    "roomId": room_id
                })
                print(f"Sent ide_start for room {room_id}")
            except Exception as e:
                print(f"Error sending ide_start: {e}")
            
            # Start waiting for this match
            game_tasks.append(self._wait_for_match(game_room))
        
        # Wait for all matches in this round to complete
        winners = []
        results = await asyncio.gather(*game_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, str) and result in self.players:
                winners.append(result)
            elif isinstance(result, Exception):
                print(f"Match error: {result}")
        
        return winners
    
    async def _wait_for_match(self, game_room: GameRoom) -> Optional[str]:
        """Wait for a match to complete and return the winner"""
        print(f"Waiting for match in room {game_room.room_id}")
        
        # Wait for both players to submit bot code (60 second timeout)
        for i in range(120):  # 60 seconds
            if len(game_room.bot_codes) >= len(game_room.clients):
                break
            await asyncio.sleep(0.5)
        
        if len(game_room.bot_codes) < len(game_room.clients):
            print(f"Timeout waiting for bot submissions in room {game_room.room_id}")
            return list(game_room.clients.keys())[0]
        
        print(f"All bots submitted for room {game_room.room_id}")
        
        # Wait for game to finish (2 minute timeout)
        for i in range(240):  # 120 seconds
            if game_room.winner is not None:  # CHANGED: check winner directly
                break
            await asyncio.sleep(0.5)
        
        print(f"Match complete. Winner: {game_room.winner}")
        return game_room.winner

    async def broadcast(self, message: dict):
        """Send message to all tournament players"""
        for ws in self.players.values():
            try:
                await ws.send_json(message)
            except:
                pass