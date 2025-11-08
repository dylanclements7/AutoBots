import asyncio
from typing import Dict
from fastapi import WebSocket

class GameRoom:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.clients: Dict[str, WebSocket] = {}
        self.game_running = False

    async def connect(self, player_id: str, websocket: WebSocket):
        self.clients[player_id] = websocket
        await self.broadcast({"type": "PLAYER_JOINED", "playerId": player_id})

        if len(self.clients) == 2 and not self.game_running:
            asyncio.create_task(self.run_game())

    async def disconnect(self, player_id: str):
        del self.clients[player_id]
        await self.broadcast({"type": "PLAYER_LEFT", "playerId": player_id})

    async def broadcast(self, message: dict):
        for ws in list(self.clients.values()):
            await ws.send_json(message)

    async def send_to(self, player_id: str, message: dict):
        await self.clients[player_id].send_json(message)

    async def handle_message(self, player_id: str, message: dict):
        # for example: chat messages or ready signals
        await self.broadcast({"from": player_id, **message})

    async def run_game(self):
        self.game_running = True
        await self.broadcast({"type": "GAME_START"})

        players = list(self.clients.keys())
        current = 0

        for turn in range(10):  # replace with real game logic
            await self.broadcast({
                "type": "TURN",
                "turn": turn,
                "playerId": players[current]
            })
            await asyncio.sleep(1)
            current = 1 - current

        await self.broadcast({"type": "GAME_END", "result": "DEMO"})
        self.game_running = False