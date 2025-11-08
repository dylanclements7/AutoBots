from managers.game_room import GameRoom

class RoomManager:
    def __init__(self):
        self.rooms = {}  # room_id -> GameRoom

    def get_or_create_room(self, room_id: str) -> GameRoom:
        if room_id not in self.rooms:
            self.rooms[room_id] = GameRoom(room_id)
        return self.rooms[room_id]

room_manager = RoomManager()