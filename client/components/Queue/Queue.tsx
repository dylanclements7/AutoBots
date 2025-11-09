"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getQueue } from "@/app/lib/api";
import { useWebSocket } from "@/app/lib/websockets";
interface Player {
  id: string;
  name: string;
  isReady: boolean;
  rating?: number;
}

export default function MatchmakingQueue({gameId, name}: {gameId: string, name:string}) {
  const params = useParams();
  
  const [players, setPlayers] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [isInQueue, setIsInQueue] = useState(false);
  const username = localStorage.getItem('user') || 'user1';
  const { connect, disconnect, lobbyState, isConnected } = useWebSocket();
  
  useEffect(() => {
    // Load initial queue state on mount
    getQueue(name, (queueData: any) => {
      if (queueData && queueData.players) {
        setPlayers(queueData.players);
      }
    }, setLoading);
  }, [name]);

  // Update players when lobby state changes
  useEffect(() => {
    if (lobbyState) {
      console.log('Lobby update:', lobbyState);
      setPlayers(lobbyState.players);
    }
  }, [lobbyState]);

  const handleJoinQueue = () => {
    connect(name, username);
    setIsInQueue(true);
  };

  const handleLeaveQueue = () => {
    disconnect();
    setIsInQueue(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="text-muted-foreground">Loading matchmaking...</div>
      </div>
    );
  }


  const totalPlayers = players.length;

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          
          <h1 className="text-4xl font-bold mb-2 capitalize">
            {/* {gameId.replace(/-/g, " ")} Matchmaking */}
          </h1>
          <p className="text-muted-foreground">
            {totalPlayers} player{totalPlayers !== 1 ? 's' : ''} 
          </p>
        </div>

        <div className="mb-6 flex gap-4">
          {!isInQueue ? (
            <button
              onClick={handleJoinQueue}
              className="bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors font-semibold"
            >
              Join Queue
            </button>
          ) : (
            <button
              onClick={handleLeaveQueue}
              className="px-6 py-3 rounded-lg border border-border hover:bg-muted transition-colors font-semibold"
            >
              Leave Queue
            </button>
          )}
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Players in Queue</h2>
          <div className="space-y-3">
            {players.map((playerName) => {
              const isCurrentUser = playerName === username;
              return (
                <div
                  key={playerName}
                  className={`flex items-center justify-between rounded-lg p-4 ${
                    isCurrentUser ? 'bg-primary/10 border border-primary' : 'bg-muted'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      isCurrentUser ? 'bg-primary text-primary-foreground' : 'bg-card border border-border'
                    }`}>
                      {playerName.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <span className="font-medium">{isCurrentUser ? 'You' : playerName}</span>
                    </div>
                  </div>
                </div>
              );
            })}
            {players.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                No players in queue. Be the first to join!
              </div>
            )}
          </div>
        </div>

        {isInQueue && (
          <div className="mt-6 bg-accent/10 border border-accent rounded-lg p-4 text-center">
            
          </div>
        )}
      </div>
    </div>
  );
}