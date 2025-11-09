
import asyncio
from typing import Dict, List, Optional
from fastapi import WebSocket
from game_room import GameRoom
import math

class Lobby:
    def __init__(self):
        # game_type -> dict of player_id -> websocket
        self.queues: Dict[str, Dict[str, WebSocket]] = {}
        
        self.players = {}
        # Track active tournaments per game type
        self.active_tournaments: Dict[str, 'Tournament'] = {}
        
        # Track individual game rooms
        self.rooms: Dict[str, Dict[str, GameRoom]] = {}

    def join_lobby(self, game_type: str, username: str, websocket: WebSocket):
        """Player joins the lobby for a specific game type"""
        if game_type not in self.queues:
            self.queues[game_type] = {}
            self.players[game_type] = set()
            self.rooms[game_type] = {}
        self.players[game_type].add(username)
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
            self.players[game_type].discard(player_id)
            await self.broadcast_lobby_state(game_type)


        

    async def broadcast_lobby_state(self, game_type: str):
        """Broadcast current lobby state to all players"""
        queue = self.queues.get(game_type, {})
        ready = self.players.get(game_type, set())
        
        message = {
            "type": "lobby_state",
            "players": list(queue.keys()),
           
            "totalCount": len(queue)
        }
        
        for ws in list(queue.values()):
            try:
                await ws.send_json(message)
            except:
                pass

    async def try_start_tournament(self, game_type: str):
        """Check if we have enough players to start a tournament"""
        queue = self.queues.get(game_type, {})
        num_players = len(queue)
        
        print(f"Checking tournament start for {game_type}: {num_players} players in queue")
        
        # Need a power of 2 (2, 4, 8, 16, etc.)
        if num_players < 2:
            return
        
        # Check if it's a power of 2
        if not self._is_power_of_2(num_players):
            return
        
        print(f"Starting tournament for {game_type} with {num_players} players")
        
        # Extract players from queue
        tournament_players = {}
        for player_id in list(queue.keys()):
            tournament_players[player_id] = self.queues[game_type].pop(player_id)
            self.players[game_type].remove(player_id)
        
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
        print('ri')
        players_copy = self.active_players.copy()
        
        player1 = players_copy.pop(0)
        player2 = players_copy.pop(0)
        
        
        
        # Create game rooms for all matches
        game_tasks = []
        
        room_id = f"{self.game_type}_R{self.current_round}"
        
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
        for i in range(1020):  # 60 seconds
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