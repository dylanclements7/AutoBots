import React, { useEffect, useState, useRef } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";

export default function App() {
  const [ws, setWs] = useState(null);
  const [phase, setPhase] = useState("lobby");
  const [username, setUsername] = useState("");
  const [inputUsername, setInputUsername] = useState("");
  const [players, setPlayers] = useState([]);
  const [ready, setReady] = useState([]);
  const [pyodide, setPyodide] = useState(null);
  const [pyodideReady, setPyodideReady] = useState(false);
  const [code, setCode] = useState(
`def move(board, my_symbol):
    """
    Return column index (0-6) to drop piece.
    board: 6x7 grid, board[0] is top row
    my_symbol: 'X' or 'O'
    """
    import random
    
    ROWS, COLS = len(board), len(board[0])
    available = [c for c in range(COLS) if board[0][c] == ' ']
    
    if not available:
        return 0
    
    # Prefer center
    center = [c for c in available if 2 <= c <= 4]
    return random.choice(center if center else available)`
  );
  const [board, setBoard] = useState([]);
  const [symbol, setSymbol] = useState("");
  const [output, setOutput] = useState("Waiting...");
  const [gameOver, setGameOver] = useState(false);

  const wsRef = useRef(null);
  const codeRef = useRef(code);
  const symbolRef = useRef("");

  useEffect(() => {
    codeRef.current = code;
  }, [code]);

  useEffect(() => {
    symbolRef.current = symbol;
  }, [symbol]);

  // Load Pyodide
  useEffect(() => {
    const loadPyodide = async () => {
      setOutput("Loading Python...");
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/pyodide/v0.24.0/full/pyodide.js";
      script.onload = async () => {
        try {
          const py = await window.loadPyodide();
          setPyodide(py);
          setPyodideReady(true);
          setOutput("✅ Python loaded!");
        } catch (err) {
          setOutput("❌ Failed to load Python: " + err);
        }
      };
      document.body.appendChild(script);
    };
    loadPyodide();
  }, []);

  // Handle messages
  const handleServerMessage = async (data) => {
    console.log("Received:", data.type);
    
    if (data.type === "lobby_state") {
      setPlayers(data.players);
      setReady(data.ready);
      
    } else if (data.type === "ide_start") {
      setPhase("ide");
      setOutput("Write your bot!");
      
    } else if (data.type === "game_start") {
      setPhase("game");
      setBoard(data.board);
      setSymbol(data.symbol);
      setGameOver(false);
      setOutput(`Game started! You are ${data.symbol}`);
      
    } else if (data.type === "board_update") {
      setBoard(data.board);
      
    } else if (data.type === "your_turn") {
      setBoard(data.board);
      setOutput(`🤖 Your turn! Running bot...`);
      setTimeout(() => runBot(data.board, data.symbol), 100);
      
    } else if (data.type === "game_over") {
      setGameOver(true);
      if (data.board) setBoard(data.board);
      
      let msg = data.winner === "draw" ? "🤝 Draw!" :
                data.winner === username ? "🎉 You won!" :
                data.winner === "forfeit" ? `Game over: ${data.reason}` :
                `😞 You lost. Winner: ${data.winner}`;
      
      setOutput(msg + "\n\nClick 'Back to Lobby'");
      
    } else if (data.type === "error") {
      alert("Error: " + data.message);
    }
  };

  // Run bot
  const runBot = async (currentBoard, currentSymbol) => {
    while (!pyodideReady) {
      await new Promise(r => setTimeout(r, 100));
    }
    
    try {
      setOutput("🤖 Running bot...");
      await pyodide.runPythonAsync(codeRef.current);
      const move = pyodide.runPython(
        `move(${JSON.stringify(currentBoard)}, '${currentSymbol}')`
      );
      
      const col = parseInt(move);
      if (isNaN(col) || col < 0 || col > 6) {
        setOutput(`❌ Invalid: ${move}`);
        wsRef.current.send(JSON.stringify({ type: "move", column: 0 }));
        return;
      }
      
      wsRef.current.send(JSON.stringify({ type: "move", column: col }));
      setOutput(`✅ Played column ${col}`);
      
    } catch (err) {
      setOutput("❌ Error: " + err.toString());
      wsRef.current.send(JSON.stringify({ type: "move", column: 0 }));
    }
  };

  // Username screen
  if (!ws) {
    return (
      <div style={{ padding: 40, maxWidth: 500, margin: "0 auto" }}>
        <h1 style={{ fontSize: 32, marginBottom: 20 }}>🎮 Connect-4 Arena</h1>
        <h2 style={{ fontSize: 20, marginBottom: 20 }}>Enter Username</h2>
        <input
          value={inputUsername}
          onChange={(e) => setInputUsername(e.target.value)}
          placeholder="Your name..."
          style={{
            width: "100%",
            padding: 12,
            fontSize: 16,
            marginBottom: 10,
            border: "2px solid #ccc",
            borderRadius: 4
          }}
          onKeyPress={(e) => {
            if (e.key === "Enter" && inputUsername.trim()) {
              const socket = new WebSocket(`ws://localhost:8000/ws/demo/${inputUsername.trim()}`);
              socket.onmessage = (e) => handleServerMessage(JSON.parse(e.data));
              socket.onopen = () => setUsername(inputUsername.trim());
              socket.onerror = () => alert("Failed to connect!");
              setWs(socket);
              wsRef.current = socket;
            }
          }}
        />
        <button
          onClick={() => {
            if (!inputUsername.trim()) return alert("Enter username");
            const socket = new WebSocket(`ws://localhost:8000/ws/demo/${inputUsername.trim()}`);
            socket.onmessage = (e) => handleServerMessage(JSON.parse(e.data));
            socket.onopen = () => setUsername(inputUsername.trim());
            socket.onerror = () => alert("Failed to connect!");
            setWs(socket);
            wsRef.current = socket;
          }}
          style={{
            width: "100%",
            padding: 12,
            fontSize: 16,
            background: "#2196f3",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
            fontWeight: "bold"
          }}
        >
          Join Game
        </button>
        <div style={{ marginTop: 20, fontSize: 14, color: "#666" }}>
          {pyodideReady ? "✅ Python loaded" : "⏳ Loading Python..."}
        </div>
      </div>
    );
  }

  // Lobby
  if (phase === "lobby") {
    return (
      <div style={{ padding: 40, maxWidth: 600, margin: "0 auto" }}>
        <h1 style={{ fontSize: 32, marginBottom: 20 }}>🎮 Lobby</h1>
        <p style={{ fontSize: 16, marginBottom: 20 }}>
          Connected as <b>{username}</b>
        </p>
        <h3 style={{ fontSize: 20, marginBottom: 10 }}>Players ({players.length}):</h3>
        <ul style={{ listStyle: "none", padding: 0, marginBottom: 20 }}>
          {players.map((p) => (
            <li
              key={p}
              style={{
                padding: 12,
                marginBottom: 8,
                background: "#f5f5f5",
                borderRadius: 4,
                fontSize: 16
              }}
            >
              {p} {ready.includes(p) ? "✅ Ready" : "⏳ Not ready"}
            </li>
          ))}
        </ul>
        <button
          onClick={() => ws.send(JSON.stringify({ type: "ready" }))}
          disabled={ready.includes(username)}
          style={{
            padding: 12,
            fontSize: 16,
            background: ready.includes(username) ? "#4caf50" : "#2196f3",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: ready.includes(username) ? "default" : "pointer",
            fontWeight: "bold",
            width: "100%"
          }}
        >
          {ready.includes(username) ? "✅ Ready!" : "Ready Up"}
        </button>
        <div style={{ marginTop: 20, fontSize: 14, color: "#666" }}>
          {ready.length}/{players.length} ready
          {players.length < 2 && " • Need 2 players"}
        </div>
      </div>
    );
  }

  // IDE
  if (phase === "ide") {
    return (
      <div style={{ padding: 40, maxWidth: 900, margin: "0 auto" }}>
        <h1 style={{ fontSize: 32, marginBottom: 20 }}>💻 Write Your Bot</h1>
        <p style={{ marginBottom: 20, fontSize: 16 }}>
          Create a function that returns column 0-6 to play your move.
        </p>
        <CodeMirror
          value={code}
          height="400px"
          extensions={[python()]}
          onChange={(val) => setCode(val)}
          style={{ border: "2px solid #ccc", borderRadius: 4, marginBottom: 20 }}
        />
        <button
          onClick={() => {
            ws.send(JSON.stringify({ type: "bot_code" }));  // Don't send code!
            // Don't change phase yet - wait for server's game_start message
            setOutput("Bot submitted! Waiting for others...");
          }}
          style={{
            padding: 12,
            fontSize: 16,
            background: "#4caf50",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
            fontWeight: "bold",
            width: "100%"
          }}
        >
          Submit Bot & Start Game
        </button>
      </div>
    );
  }

  // Game
  return (
    <div style={{ padding: 40, maxWidth: 800, margin: "0 auto" }}>
      <h1 style={{ fontSize: 32, marginBottom: 20 }}>
        🎮 Game {gameOver && "- Finished!"}
      </h1>
      
      <div style={{ marginBottom: 20, fontSize: 16 }}>
        <strong>You are:</strong> {symbol} ({symbol === "X" ? "🔴 Red" : "🟡 Yellow"})
      </div>
      
      <div
        style={{
          display: "inline-grid",
          gridTemplateColumns: "repeat(7, 60px)",
          gap: 4,
          background: "#0066cc",
          padding: 12,
          borderRadius: 8,
          marginBottom: 20
        }}
      >
        {board.flat().map((cell, i) => (
          <div
            key={i}
            style={{
              width: 60,
              height: 60,
              borderRadius: "50%",
              background:
                cell === "X" ? "#ff0000" :
                cell === "O" ? "#ffff00" :
                "#ffffff",
              border: "3px solid #003d7a",
              boxShadow: cell !== " " ? "inset 0 3px 6px rgba(0,0,0,0.3)" : "inset 0 2px 4px rgba(0,0,0,0.1)"
            }}
          />
        ))}
      </div>
      
      <div
        style={{
          padding: 12,
          background: "#000",
          color: "#0f0",
          borderRadius: 4,
          fontFamily: "monospace",
          fontSize: 14,
          whiteSpace: "pre-wrap",
          marginBottom: 20,
          minHeight: 60
        }}
      >
        {output}
      </div>
      
      {gameOver && (
        <button
          onClick={() => ws.send(JSON.stringify({ type: "restart" }))}
          style={{
            padding: 12,
            fontSize: 16,
            background: "#2196f3",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
            fontWeight: "bold",
            width: "100%"
          }}
        >
          Back to Lobby
        </button>
      )}
    </div>
  );
}