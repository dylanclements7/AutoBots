import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState, ReactNode, useRef } from "react";

type LobbyState = {
  players: string[];
  ready: string[];
  readyCount: number;
  totalCount: number;
};

type WebSocketContextType = {
  socket: WebSocket | null;
  isConnected: boolean;
  lobbyState: LobbyState | null;
  matchState: number | null;
  roomId: string | null;
  connect: (gameType: string, username: string) => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  setMatchState: (state: number | null) => void;
  code: string;
  setCode: (code: string) => void;
};

async function runCode(code: string, pyodide: any, vals: any[], setOutput: (output: string) => void){
    
    //load function
    await pyodide.runPythonAsync(code);
    //call game function
    const out = await pyodide.runPythonAsync("game(" + vals.join(", ") + ")")
    setOutput(out?.toString());
}


const WebSocketContext = createContext<WebSocketContextType | null>(null);

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lobbyState, setLobbyState] = useState<LobbyState | null>(null);
  const [matchState, setMatchState] = useState<number| null>(null);
  const [roomId, setRoomId] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const router = useRouter();
  const [code, setCode] = useState<string>("");

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
          //to python 
          runCode(code,pyodideRef.current,testCases, setTestCases);
          
          const state = message.state;
          const pyState= pyodide.toPy(state)
          runCode(code,pyodideRef.current,pyState, setTestCases);
          
        
        }if (message.type === "your_turn") {
          
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
    <WebSocketContext.Provider value={{ socket, isConnected, lobbyState, matchState, roomId, connect, disconnect, sendMessage, setMatchState }}>
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


