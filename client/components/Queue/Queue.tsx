"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getQueue } from "@/app/lib/api";
import  LobbySocket  from "@/app/lib/websockets";
interface Player {
  id: string;
  name: string;
  isReady: boolean;
  rating?: number;
}

export default function MatchmakingQueue({gameId, name}: {gameId: string, name:string}) {
  const params = useParams();
  
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [isInQueue, setIsInQueue] = useState(false);
  const [socket, setSocket] = useState(false)
  useEffect(() => {
    
    const interval = setInterval(() => {
      getQueue(name, setPlayers, setLoading);
    }, 500); // every 500ms
  
    
    return () => clearInterval(interval);
  }, [gameId, name]);
  const username = localStorage.getItem('user')


  const handleLeaveQueue = () => {
    // TODO: Replace with actual API call
    // fetch(`/api/games/${gameId}/queue/leave`, { method: 'POST' })

    setIsInQueue(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="text-muted-foreground">Loading matchmaking...</div>
      </div>
    );
  }


  const totalPlayers = players.length + (isInQueue ? 1 : 0);

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
        
          {socket && <LobbySocket gameType={name} username={username}/>}
          {!isInQueue ? (
            <button
              onClick={() => setSocket(true)}
              className="bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors font-semibold"
            >
              
              Join Queue
            </button>
          ) : (
            <>
              <button
                
                className={
                  isReady
                    ? "flex-1 bg-muted text-muted-foreground px-6 py-3 rounded-lg hover:bg-muted/80 transition-colors font-semibold"
                    : "flex-1 bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors font-semibold"
                }
              >
                {isReady ? "Not Ready" : "Ready Up"}
              </button>
              <button
                onClick={handleLeaveQueue}
                className="px-6 py-3 rounded-lg border border-border hover:bg-muted transition-colors font-semibold"
              >
                Leave Queue
              </button>
            </>
          )}
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Players in Queue</h2>
          <div className="space-y-3">
            {isInQueue && (
              <div className="flex items-center justify-between bg-primary/10 border border-primary rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
                    You
                  </div>
                  <div>
                    <span className="font-medium">You</span>
                    <span className="text-sm text-muted-foreground ml-2">Rating: 1500</span>
                  </div>
                </div>
                
              </div>
            )}
            {players.map((player) => (
              <div
                key={player.id}
                className="flex items-center justify-between bg-muted rounded-lg p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-card border border-border flex items-center justify-center font-bold">
                    {player.name.charAt(0)}
                  </div>
                  <div>
                    <span className="font-medium">{player.name}</span>
                    {player.rating && (
                      <span className="text-sm text-muted-foreground ml-2">
                        Rating: {player.rating}
                      </span>
                    )}
                  </div>
                </div>
                
              </div>
            ))}
            {players.length === 0 && !isInQueue && (
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