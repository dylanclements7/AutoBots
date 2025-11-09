import styles from "./page.module.css";
import QueueDrawer from "../QueueDrawer/drawer";

export default function GameCard({game}: {game: any}) {
    return (
        <QueueDrawer game={game}>
            <div className={styles.gameCard}>
                <div>
                    <h2 className={styles.gameName}>{game}</h2>
                    <div className={styles.line}></div>
                    {/* <p className={styles.gameDescription}>{game.description}</p>
                    <p className={styles.gamePlayerCount}>{game.playerCount}</p> */}
                </div>
            </div>
        </QueueDrawer>
    )
}