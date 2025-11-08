"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

interface Player {
  id: string;
  name: string;
  isReady: boolean;
  rating?: number;
}

export default function MatchmakingQueue({gameId}: {gameId: string}) {
  const params = useParams();
  
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [isReady, setIsReady] = useState(false);
  const [isInQueue, setIsInQueue] = useState(false);

  useEffect(() => {
    // TODO: Replace with actual API call and WebSocket connection
    // const ws = new WebSocket(`ws://api/games/${gameId}/queue`);
    // ws.onmessage = (event) => setPlayers(JSON.parse(event.data));
    
    // Placeholder data
    const placeholderPlayers: Player[] = [
      {
        id: "player-1",
        name: "CodeMaster",
        isReady: true,
        rating: 1850
      },
      {
        id: "player-2",
        name: "BotBuilder",
        isReady: true,
        rating: 1720
      },
      {
        id: "player-3",
        name: "AlgoWizard",
        isReady: false,
        rating: 1920
      },
      {
        id: "player-4",
        name: "PyThonPro",
        isReady: true,
        rating: 1650
      },
      {
        id: "player-5",
        name: "JavaJunkie",
        isReady: false,
        rating: 1780
      }
    ];
    
    setTimeout(() => {
      setPlayers(placeholderPlayers);
      setLoading(false);
    }, 300);
  }, [gameId]);

  const handleToggleReady = () => {
    // TODO: Replace with actual API call
    // fetch(`/api/games/${gameId}/queue/ready`, { method: 'POST', body: JSON.stringify({ ready: !isReady }) })
    
    setIsReady(!isReady);
    if (!isInQueue) {
      setIsInQueue(true);
    }
  };

  const handleLeaveQueue = () => {
    // TODO: Replace with actual API call
    // fetch(`/api/games/${gameId}/queue/leave`, { method: 'POST' })
    
    setIsReady(false);
    setIsInQueue(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="text-muted-foreground">Loading matchmaking...</div>
      </div>
    );
  }

  const readyCount = players.filter(p => p.isReady).length;
  const totalPlayers = players.length + (isInQueue ? 1 : 0);

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          
          <h1 className="text-4xl font-bold mb-2 capitalize">
            {/* {gameId.replace(/-/g, " ")} Matchmaking */}
          </h1>
          <p className="text-muted-foreground">
            {totalPlayers} player{totalPlayers !== 1 ? 's' : ''} in queue • {readyCount} ready
          </p>
        </div>

        <div className="mb-6 flex gap-4">
          {!isInQueue ? (
            <button
              onClick={handleToggleReady}
              className="bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors font-semibold"
            >
              Join Queue
            </button>
          ) : (
            <>
              <button
                onClick={handleToggleReady}
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
                <span
                  className={
                    isReady
                      ? "text-primary font-semibold"
                      : "text-muted-foreground"
                  }
                >
                  {isReady ? "✓ Ready" : "Not Ready"}
                </span>
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
                <span
                  className={
                    player.isReady
                      ? "text-primary font-semibold"
                      : "text-muted-foreground"
                  }
                >
                  {player.isReady ? "✓ Ready" : "Not Ready"}
                </span>
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
            <p className="text-accent-foreground">
              {isReady
                ? "Waiting for match... You will be notified when a game is ready."
                : "Click 'Ready Up' when you're ready to play!"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}