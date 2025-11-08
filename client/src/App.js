import React, { useEffect, useState, useRef } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";

export default function App() {
  const [pyodide, setPyodide] = useState(null);
  const [output, setOutput] = useState("");
  const [symbol, setSymbol] = useState("");
  const [board, setBoard] = useState([]);
  const [winner, setWinner] = useState(null);
  const [code, setCode] = useState(
    `def move(board, my_symbol):
    import js, random
    if not board or not board[0]:
        return 0
    ROWS, COLS = len(board), len(board[0])
    available = [c for c in range(COLS) if board[0][c] == ' ']
    choice = random.choice(available)
    js.console.log("Available:", available, "Choice:", choice)
    return choice`
  );

  const wsRef = useRef(null);

  // Load Pyodide from CDN
  useEffect(() => {
    const loadPyodide = async () => {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/pyodide/v0.24.0/full/pyodide.js";
      script.onload = async () => {
        const py = await window.loadPyodide();
        setPyodide(py);
        console.log("Pyodide loaded from CDN!");
      };
      document.body.appendChild(script);
    };
    loadPyodide();
  }, []);

  // Connect to WebSocket with unique username
  useEffect(() => {
    const username = "User" + Math.floor(Math.random() * 10000);
    wsRef.current = new WebSocket(`ws://localhost:8000/ws/demo/${username}`);

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "info") {
        setSymbol(data.symbol);
        setBoard(data.board);
        setOutput(data.message);
      } else if (data.type === "update") {
        setBoard(data.board);
      } else if (data.type === "error") {
        setOutput(data.message);
      }
    };

    return () => wsRef.current.close();
  }, []);

  // Run bot locally and send move
  async function runBot() {
    if (!pyodide) return;
    if (!board || board.length === 0 || !symbol) {
      console.warn("Board not initialized yet!");
      return;
    }
    try {
      await pyodide.runPythonAsync(code);
      const move = pyodide.runPython(
        `move(${JSON.stringify(board)}, '${symbol}')`
      );
      wsRef.current.send(JSON.stringify({ type: "move", column: move }));
      setOutput(`You played column ${move}`);
    } catch (err) {
      setOutput("Error: " + err);
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Connect-4 Arena</h1>

      <CodeMirror
        value={code}
        height="300px"
        extensions={[python()]}
        onChange={(value) => setCode(value)}
      />

      <button
        onClick={runBot}
        disabled={!!winner || !board.length || !symbol}
        style={{ marginTop: 10 }}
      >
        Play Turn
      </button>

      <pre>{output}</pre>

      {/* Board */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(7, 40px)",
          marginTop: 20,
        }}
      >
        {board.flat().map((cell, i) => (
          <div
            key={i}
            style={{
              width: 40,
              height: 40,
              border: "1px solid black",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background:
                cell === "X" ? "red" : cell === "O" ? "yellow" : "white",
            }}
          >
            {cell}
          </div>
        ))}
      </div>
    </div>
  );
}
