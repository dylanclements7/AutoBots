"use client";
import Link from "next/link";
import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import CodeEditor from "@/components/CodeEditor/editor";
import { useWebSocket } from "@/app/lib/websockets";
import { Pyodide } from "@/app/lib/pyodide";
export default function Game() {
    const params = useParams();
    const gameId = params["game-id"] as string;
    const [gamePhase, setGamePhase] = useState("1");
    const [currentTime, setCurrentTime] = useState(5);
    
    const [code, setCode] = useState("def game(state):\n return None");
    const [gameState, setGameState] = useState<any>(null);
    const pyodideRef = useRef<any>(null);
    const { socket, isConnected, lobbyState, matchState, gameMessage, roomId, connect, disconnect, sendMessage, setMatchState } = useWebSocket();

    // Load Pyodide on mount
    useEffect(() => {
        async function loadPyodide() {
             console.log('loading pyodide')
            const py = await Pyodide.getInstance();
            pyodideRef.current = py;
            console.log('loaded pyodide')
        }
        loadPyodide();
        
    }, []);

    useEffect(() => {
        console.log("Match state changed:", matchState);
    }, [matchState]);

    // Handle game messages
    useEffect(() => {
        if (!gameMessage) return;
        
        console.log("Game message received:", gameMessage);
        
        if (gameMessage.type === "game_start") {
            setGameState(gameMessage.gameState);
        }
        
        if (gameMessage.type === "your_turn") {
            setGameState(gameMessage.gameState);
            // Execute bot code to get move
            handleBotTurn(gameMessage.gameState);
        }
        
        if (gameMessage.type === "board_update") {
            setGameState(gameMessage.gameState);
        }
        
        if (gameMessage.type === "game_over") {
            console.log("Game over:", gameMessage);
            setGameState(gameMessage.gameState);
        }
    }, [gameMessage]);

    const handleBotTurn = async (state: any) => {
        if (!pyodideRef.current || !code) {
            console.error("Pyodide not loaded or no code");
            return;
        }
        
        try {
            // Load the user's function
            await pyodideRef.current.runPythonAsync(code);
            
            // Convert game state to Python
            const pyState = pyodideRef.current.toPy(state);
            
            // Call the game function with the state
            const move = await pyodideRef.current.runPythonAsync(`game(${JSON.stringify(state)})`);
            
            console.log("Bot returned move:", move);
            
            // Send the move back to the server
            sendMessage({
                type: "move",
                roomId: roomId,
                move: move
            });
        } catch (e: any) {
            console.error("Error executing bot code:", e);
        }
    };

    useEffect(() => {
        if (currentTime <= 0) return;

        const interval = setInterval(() => {
            setCurrentTime((prevTime) => {
                if (prevTime <= 1) {
                    clearInterval(interval);
                    setGamePhase("2");
                    return 0;
                }
                return prevTime - 1;
            });
        }, 1000);

        return () => clearInterval(interval);
    }, [currentTime]);

    return (
        <>
        {matchState === 0 && (
            <div>
                <h1>Match Starting</h1>
            </div>
        )}
        {matchState === 1 && (
            <CodeEditor 
            code={code} 
            setCode = {setCode}
            time={currentTime} parameters={[
                {name: "num1", type: "int"}, 
                {name: "num2", type: "int"}
            ]} />
            )}
            {matchState === 2 && (
                <div>
                    <h1>play game</h1>
                </div>
            )}
        </>
    );
    
}