import { useEffect, useState } from "react";

type Props = { gameType: string; username: string };

export default function LobbySocket({ gameType, username }: Props) {
  const [messages, setMessages] = useState<string[]>([]);
  const [status, setStatus] = useState("Connecting...");
  const url =  `ws://localhost:8000/${gameType}/${username}`
  
  useEffect(() => {
    // Replace with your WebSocket server URL
    const socket = new WebSocket(url);
    socket.onopen = () => {
      setStatus("Connected ");
      console.log("connected");
      socket.send(JSON.stringify({ type: "join", username }));;
    };

    socket.onmessage = (event: MessageEvent) => {
      setMessages((prev) => [...prev, event.data]);
    };

    socket.onclose = () => setStatus("Disconnected");
    socket.onerror = (err) => console.error("WebSocket error:", err);

    // Cleanup on component unmount
    return () => socket.close();
  }, [gameType, username]);

  return <></>;
}
