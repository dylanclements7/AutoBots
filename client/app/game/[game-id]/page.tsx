"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import CodeEditor from "@/components/CodeEditor/editor";

export default function Game() {
    const params = useParams();
    const gameId = params["game-id"] as string;
    const [gamePhase, setGamePhase] = useState("1");
    const [currentTime, setCurrentTime] = useState(5);

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
            {gamePhase === "1" && (
                <CodeEditor time={currentTime} parameters={[
                    {name: "num1", type: "int"}, 
                    {name: "num2", type: "int"}
                ]} />
            )}
            {gamePhase === "2" && (
                <div>
                    <h1>Game Over</h1>
                </div>
            )}
        </>
    );
    
}