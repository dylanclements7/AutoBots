"use client";
import GameCard from "@/components/GameCard/GameCard";
import { useEffect, useState } from "react";
import styles from "./page.module.css";
import { getGames } from "@/app/lib/api";

interface GameSummary {
  title: string;
  difficulty: string;
  game_summary: string;
  objective: string;
  player_symbols: string[];
}

interface ApiResponse {
  games: GameSummary[];
  gameData: any[]; // full objects
}

export default function GameBrowsePage() {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGames(setData, setLoading);
  }, []);

  if (loading || !data) {
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.games.map((gameSummary, index) => {
            const fullGameData = data.gameData[index]; // ✅ since both arrays align

            return (
              <GameCard
                key={gameSummary.title} // ✅ unique key
                game={gameSummary}
                gameData={fullGameData}
              />
            );
          })}
        </div>
      </div>
    </>
  );
}