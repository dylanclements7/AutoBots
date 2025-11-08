from managers.game_room import GameRoom
import random, string

def generate_id(length: int):
   letters = string.ascii_letters + string.digits
   return ''.join(random.choice(letters) for i in range(length))

class RoomManager:
    def __init__(self):
        self.rooms = {
        "CONNECT4": {},
        "TICTACTOE": {}
        }  # game_type -> GameRoom

        # self.room_id = max()

    def find_room(self, game_type: str) -> GameRoom:
        game_rooms = self.rooms[game_type]
        # check if there is an open room
        for room in game_rooms:
            if not room.game_running and len(room.clients) < 2:
                return room
        
        # no open rooms exist
        new_id = generate_id()

        # if game_rooms:                existing_ids = list(map(int, game_rooms.keys()))
        #     new_id = str(max(existing_ids) + 1)        #     

        new_room = GameRoom(game_type, new_id)
        game_rooms[new_id] = new_room
        return (new_room, new_id)

    # TODO: Remove game room when game finished   


room_manager = RoomManager()