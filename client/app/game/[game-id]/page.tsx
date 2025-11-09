"use client";
import Link from "next/link";
import { useEffect, useState, useRef, useMemo } from "react";
import { useParams } from "next/navigation";
import CodeEditor from "@/components/CodeEditor/editor";
import { useWebSocket } from "@/app/lib/websockets";
import { Pyodide } from "@/app/lib/pyodide";

// NEW: Game Board Component
function GameBoard({ 
    boardHtml, 
    gameState, 
    gameMessage,
    mySymbol 
}: { 
    boardHtml: string; 
    gameState: any;
    gameMessage: any;
    mySymbol: string;
}) {
    const iframeRef = useRef<HTMLIFrameElement>(null);
    const [boardReady, setBoardReady] = useState(false);
    
    // Create blob URL from HTML string
    const boardUrl = useMemo(() => {
        if (!boardHtml) return null;
        const blob = new Blob([boardHtml], { type: 'text/html' });
        return URL.createObjectURL(blob);
    }, [boardHtml]);
    
    // Cleanup blob URL
    useEffect(() => {
        return () => {
            if (boardUrl) URL.revokeObjectURL(boardUrl);
        };
    }, [boardUrl]);
    
    // Listen for iframe ready message
    useEffect(() => {
        const handleIframeMessage = (event: MessageEvent) => {
            if (event.data.type === 'board_ready') {
                setBoardReady(true);
                console.log('Board iframe ready');
            }
        };
        
        window.addEventListener('message', handleIframeMessage);
        return () => window.removeEventListener('message', handleIframeMessage);
    }, []);
    
    // Send messages to iframe
    const sendToIframe = (message: any) => {
        if (iframeRef.current?.contentWindow && boardReady) {
            iframeRef.current.contentWindow.postMessage(message, '*');
        }
    };
    
    // Forward game messages to iframe
    useEffect(() => {
        if (!gameMessage || !boardReady) return;
        
        console.log('Forwarding to iframe:', gameMessage.type);
        
        // Add symbol to message if not present
        const messageWithSymbol = {
            ...gameMessage,
            symbol: mySymbol
        };
        
        sendToIframe(messageWithSymbol);
    }, [gameMessage, boardReady, mySymbol]);
    
    // Send initial game state when board becomes ready
    useEffect(() => {
        if (boardReady && gameState) {
            sendToIframe({
                type: 'game_start',
                gameState: gameState,
                board: gameState,
                symbol: mySymbol
            });
        }
    }, [boardReady, gameState, mySymbol]);
    
    if (!boardUrl) {
        return <div>Loading board...</div>;
    }
    
    return (
        <iframe
            ref={iframeRef}
            src={boardUrl}
            style={{
                width: '100%',
                height: '600px',
                border: 'none',
                borderRadius: '10px'
            }}
            sandbox="allow-scripts"
            title="Game Board"
        />
    );
}

export default function Game() {
    const params = useParams();
    const gameId = params["game-id"] as string;
    const [gamePhase, setGamePhase] = useState("1");
    const [currentTime, setCurrentTime] = useState(5);
    
    const [code, setCode] = useState("def game(state):\n return None");
    const [gameState, setGameState] = useState<any>(null);
    const [mySymbol, setMySymbol] = useState<string>("");
    
    // NEW: Board HTML from database
    const [boardHtml, setBoardHtml] = useState<string>("");
    
    const pyodideRef = useRef<any>(null);
    const { socket, isConnected, lobbyState, matchState, gameMessage, roomId, connect, disconnect, sendMessage, setMatchState, gameData } = useWebSocket();

    // Load Pyodide on mount
    useEffect(() => {
        async function loadPyodide() {
            console.log('loading pyodide');
            const py = await Pyodide.getInstance();
            pyodideRef.current = py;
            console.log('loaded pyodide');
        }
        loadPyodide();
    }, []);

    // NEW: Load board HTML from your FastAPI backend
    useEffect(() => {
        async function loadBoardHtml() {
            try {
                // Get game type from gameData or params
                const gameType = gameData?.gameType || gameId; // e.g., "connect4"
                console.log(gameData);
                if (!gameType) {
                    console.log("No game type available yet");
                    return;
                }
                
                console.log(`Loading board HTML for game type: ${gameType}`);
                
                // // Call your FastAPI endpoint
                // const response = await fetch(`http://localhost:8000/game/${gameType}/html`);
                
                // if (!response.ok) {
                //     throw new Error(`Failed to load board: ${response.status}`);
                // }
                
                const htmlContent = gameData.html // Get raw HTML string
                setBoardHtml(htmlContent);
                
                console.log("Board HTML loaded successfully");
            } catch (error) {
                console.error("Error loading board HTML:", error);
            }
        }
        
        loadBoardHtml();
    }, [gameId, gameData]);

    useEffect(() => {
        console.log("Match state changed:", matchState);
    }, [matchState]);

    // Handle game messages
    useEffect(() => {
        if (!gameMessage) return;
        
        console.log("Game message received:", gameMessage);
        
        if (gameMessage.type === "game_start") {
            setGameState(gameMessage.gameState);
            // Store player's symbol
            if (gameMessage.symbol) {
                setMySymbol(gameMessage.symbol);
            }
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
            
            // Call the game function with the state
            const move = await pyodideRef.current.runPythonAsync(
                `game(${JSON.stringify(state)})`
            );
            
            console.log("Bot returned move:", move);
            
            // Send the move back to the server
            sendMessage({
                type: "move",
                roomId: roomId,
                move: move
            });
        } catch (e: any) {
            console.error("Error executing bot code:", e);
            // Send fallback move on error
            sendMessage({
                type: "move",
                roomId: roomId,
                move: 0 // or appropriate fallback for your game
            });
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
                    setCode={setCode}
                    gameData={gameData}
                    time={currentTime} 
                    parameters={[
                        {name: "num1", type: "int"}, 
                        {name: "num2", type: "int"}
                    ]} 
                />
            )}
            
            {matchState === 2 && (
                <div style={{ padding: '20px' }}>
                    <h1>Game in Progress</h1>
                    
                    {/* NEW: Show the board from database */}
                    {boardHtml ? (
                        <GameBoard 
                            boardHtml={boardHtml}
                            gameState={gameState}
                            gameMessage={gameMessage}
                            mySymbol={mySymbol}
                        />
                    ) : (
                        <div>Loading game board...</div>
                    )}
                    
                    {/* Optional: Show game state as text for debugging */}
                    <details style={{ marginTop: '20px' }}>
                        <summary>Debug Info</summary>
                        <pre>{JSON.stringify(gameState, null, 2)}</pre>
                        <pre>My Symbol: {mySymbol}</pre>
                    </details>
                </div>
            )}
        </>
    );
}