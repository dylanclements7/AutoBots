"use client";
import GameCard from "@/components/GameCard/GameCard";
import Link from "next/link";
import { useEffect, useState } from "react";
import styles from "./page.module.css";
import { getGames } from "@/app/lib/api";

interface GameData {
  title: string;
  objective: string;
  game_summary: string;
  player_symbols: string[];
  difficulty: string;
  html?: string;
  description?: string;
}

interface Game {
  games: GameData[];  // Array of game objects
  gameData?: {
    [key: string]: GameData;
  };
}

export default function GameBrowsePage() {
  const [games, setGames] = useState<Game | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGames(setGames, setLoading);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="text-muted-foreground">Loading games...</div>
      </div>
    );
  }

  return (
    <>
      <div className={styles.header}>
        <h1>Browse Games</h1>
      </div>
      <div className="min-h-screen bg-background text-foreground p-8">
        <div className="max-w-100vh mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {games?.games.map((game) => (
              <GameCard 
                key={game.title}
                game={game.title} 
                gameData={game} 
              />
            ))}
          </div>
        </div>
      </div>
    </>
  );
}