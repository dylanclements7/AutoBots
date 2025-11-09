import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState, ReactNode, useRef } from "react";

type LobbyState = {
  players: string[];
  ready: string[];
  readyCount: number;
  totalCount: number;
};

type GameMessage = {
  type: string;
  [key: string]: any;
};

type WebSocketContextType = {
  socket: WebSocket | null;
  isConnected: boolean;
  lobbyState: LobbyState | null;
  matchState: number | null;
  roomId: string | null;
  gameMessage: GameMessage | null;
  connect: (gameType: string, username: string) => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  setMatchState: (state: number | null) => void;
};


const WebSocketContext = createContext<WebSocketContextType | null>(null);

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lobbyState, setLobbyState] = useState<LobbyState | null>(null);
  const [matchState, setMatchState] = useState<number| null>(null);
  const [roomId, setRoomId] = useState<string | null>(null);
  const [gameMessage, setGameMessage] = useState<GameMessage | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const router = useRouter();

  const connect = (gameType: string, username: string) => {
    // Don't reconnect if already connected to same game
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      console.log("WebSocket already connected");
      return;
    }

    const url = `ws://localhost:8000/ws/${gameType}/${username}`;
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      console.log("WebSocket connected to", url);
    };

    ws.onmessage = (event: MessageEvent) => {
      try {
        const message = JSON.parse(event.data);
        console.log("WebSocket message:", message);

        if (message.type === "lobby_state") {
          setLobbyState({
            players: message.players || [],
            ready: message.ready || [],
            readyCount: message.readyCount || 0,
            totalCount: message.totalCount || 0
          });
        }
        if (message.type === "tournament_start") {
          router.push(`/game/${gameType}`);
        }
        if (message.type === "match_starting") {
          setMatchState(0);
          setRoomId(message.roomId);
        }
        if (message.type === "ide_start") {
          setMatchState(1);
          setRoomId(message.roomId);
        }
        if (message.type === "game_start") {
          setMatchState(2);
          setGameMessage(message);
        }
        if (message.type === "your_turn") {
          setGameMessage(message);
        }
        if (message.type === "board_update") {
          setGameMessage(message);
        }
        if (message.type === "game_over") {
          setGameMessage(message);
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log("WebSocket disconnected");
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    socketRef.current = ws;
    setSocket(ws);
  };

  const disconnect = () => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
      setSocket(null);
      setIsConnected(false);
    }
  };

  const sendMessage = (message: any) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    } else {
      console.error("WebSocket is not connected");
    }
  };

  return (
    <WebSocketContext.Provider value={{ socket, isConnected, lobbyState, matchState, roomId, gameMessage, connect, disconnect, sendMessage, setMatchState }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocket must be used within WebSocketProvider");
  }
  return context;
}


