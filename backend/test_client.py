import asyncio
import websockets
import json
async def test_player(username, delay=0):
    await asyncio.sleep(delay)
    
    uri = f"ws://localhost:8000/ws/tictactoe/{username}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"[{username}] Connected")
            
            # First, try to receive the lobby state
            try:
                initial_msg = await asyncio.wait_for(websocket.recv(), timeout=2)
                print(f"[{username}] Initial message: {json.loads(initial_msg).get('type')}")
            except asyncio.TimeoutError:
                print(f"[{username}] No initial message received")
            
            # Wait a bit then ready up
            await asyncio.sleep(1)
            print(f"[{username}] Sending ready...")
            await websocket.send(json.dumps({"type": "ready"}))
            print(f"[{username}] Sent ready")
            
            current_room_id = None
            
            # Listen for messages
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                msg_type = data.get("type")
                
                print(f"[{username}] Received: {msg_type}")
                
                if msg_type == "match_starting":
                    current_room_id = data.get("roomId")
                    print(f"[{username}] Match starting in room {current_room_id}")
                
                elif msg_type == "ide_start":
                    # Submit bot code immediately
                    print(f"[{username}] IDE phase started, submitting bot...")
                    await asyncio.sleep(0.5)
                    await websocket.send(json.dumps({
                        "type": "bot_code",
                        "roomId": current_room_id,
                        "code": "dummy code"
                    }))
                    print(f"[{username}] Submitted bot code")
                
                elif msg_type == "game_start":
                    print(f"[{username}] Game starting!")
                
                elif msg_type == "your_turn":
                    game_state = data.get("gameState")
                    
                    # Make a simple move (first available column)
                    for col in range(7):
                        if game_state[0][col] == " ":
                            await websocket.send(json.dumps({
                                "type": "move",
                                "move": col
                            }))
                            print(f"[{username}] Played column {col}")
                            break
                
                elif msg_type == "board_update":
                    print(f"[{username}] Board updated")
                
                elif msg_type == "game_over":
                    winner = data.get("winner")
                    reason = data.get("reason")

                    
                
                elif msg_type == "tournament_complete":
                    champion = data.get("champion")
                    print(f"[{username}] Tournament complete! Champion: {champion}")
                    break
                
    except websockets.exceptions.ConnectionClosedOK as e:
        print(f"[{username}] Connection closed OK")
    except Exception as e:
        print(f"[{username}] Error: {type(e).__name__}: {e}")

async def main():
    # Test with 2 players
    await asyncio.gather(
        test_player("Alice"),
        test_player("Bob", delay=0.5)
    )

if __name__ == "__main__":
    asyncio.run(main())