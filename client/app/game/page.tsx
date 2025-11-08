"use client";
import GameCard from "@/components/GameCard/GameCard";
import Link from "next/link";
import { useEffect, useState } from "react";
import styles from "./page.module.css";
import { getGames } from "@/lib/api";
interface Game {
  id: string;
  name: string;
  description: string;
  playerCount: string;
  imageUrl?: string;
}

export default function GameBrowsePage() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Replace with actual API call
    // fetch('/api/games').then(res => res.json()).then(setGames)
    getGames(setGames);
    // Placeholder data
    
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="text-muted-foreground">Loading games...</div>
      </div>
    );
  }

  return (
    <> <div className={styles.header}>
          <h1 >Browse Games</h1>
          
        </div>
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-100vh mx-auto">
       
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {games.map((game) => (
            // <Link
            //   key={game.id}
            //   href={`/game/${game.id}`}
            //   className="block group"
            // >
              <GameCard game={game} />
            // </Link>
          ))}
        </div>
      </div>
    </div>
    </>
  );
}