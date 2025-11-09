"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import CodeEditor from "@/components/CodeEditor/editor";
import {useWebSocket} from "@/app/lib/websockets";
export default function Game() {
    const params = useParams();
    const gameId = params["game-id"] as string;
    const [gamePhase, setGamePhase] = useState("1");
    const [currentTime, setCurrentTime] = useState(5);
    
    const [code, setCode] = useState("");
    const { socket, isConnected, lobbyState, matchState, connect, disconnect, sendMessage, setMatchState }= useWebSocket();
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