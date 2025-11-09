import styles from "./page.module.css";
import QueueDrawer from "../QueueDrawer/drawer";

interface Game {
  title: string;
  difficulty: string;
  objective: string;
  game_summary: string;
  player_symbols: string[];
  // add other fields as needed
}

export default function GameCard({ game, gameData }: { game: Game; gameData: any }) {
  return (
    <QueueDrawer game={game} gameData={gameData}>
      <div className={styles.gameCard}>
        <div>
          <h2 className={styles.gameName}>{game.title}</h2>
          <div className={styles.line}></div>
          <p className={styles.gameDescription}>{game.game_summary}</p>
          <p className={styles.gamePlayerCount}>
            Players: {game.player_symbols.join(" / ")}
          </p>
          <p className={styles.gameDifficulty}>Difficulty: {game.difficulty}</p>
        </div>
      </div>
    </QueueDrawer>
  );
}