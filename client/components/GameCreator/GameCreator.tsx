"use client"
import PythonEditor from "./PythonEditor";
import styles from "./page.module.css";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable"
import { useState } from "react";
import HtmlEditor from "./HtmlEditor";
import Description from "./Description";
import { addGameToDb } from "@/app/lib/api";

export default function GameCreator() {
    const [activeTab, setActiveTab] = useState(0);
    const [pythonCode, setPythonCode] = useState("def is_valid_move(board, move, piece):\n    return True \n \ndef make_move(board, move):\n    return board \n\ndef check_winner(board):\n    return None")
    const [htmlCode, setHtmlCode] = useState("");
    const [descriptionData, setDescriptionData] = useState({});
    const [isPublishing, setIsPublishing] = useState(false);

    const handlePublish = async () => {
        setIsPublishing(true);
        try {
            // Parse state_format and player_symbols from strings to proper formats
            let stateFormat;
            try {
                stateFormat = JSON.parse(descriptionData.stateFormat || '{}');
            } catch (e) {
                alert('Invalid JSON format in State Format field');
                setIsPublishing(false);
                return;
            }

            const playerSymbols = descriptionData.playerSymbols
                ? descriptionData.playerSymbols.split(',').map((s: string) => s.trim())
                : [];

            const gameData = {
                title: descriptionData.title || '',
                objective: descriptionData.objective || '',
                game_summary: descriptionData.gameSummary || '',
                win_condition: descriptionData.winCondition || '',
                task: descriptionData.task || '',
                bot_input_format: descriptionData.botInputFormat || '',
                bot_output_format: descriptionData.botOutputFormat || '',
                state_format: stateFormat,
                player_symbols: playerSymbols,
                difficulty: descriptionData.difficulty || 'medium',
                code: pythonCode,
                html: htmlCode,
            };

            // Validate required fields
            if (!gameData.title || !gameData.objective || !gameData.game_summary) {
                alert('Please fill in all required fields (Title, Objective, Game Summary)');
                setIsPublishing(false);
                return;
            }

            const response = await addGameToDb(gameData);
            alert(`Game "${response.title}" published successfully!`);
        } catch (error: any) {
            alert(`Failed to publish game: ${error.message || 'Unknown error'}`);
        } finally {
            setIsPublishing(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className="flex gap-2">
                <button 
                    className={`${styles.button} ${activeTab === 0 ? styles.active : ''}`}
                    onClick={() => setActiveTab(0)}
                >
                    Game Logic
                </button>
                <button 
                    className={`${styles.button} ${activeTab === 1 ? styles.active : ''}`}
                    onClick={() => setActiveTab(1)}
                >
Visuals                </button>
                <button 
                    className={`${styles.button} ${activeTab === 2 ? styles.active : ''}`}
                    onClick={() => setActiveTab(2)}
                >
                    Description
                </button>
                </div>
                <button 
                    className={styles.button}
                    onClick={handlePublish}
                    disabled={isPublishing}
                >
                    {isPublishing ? 'Publishing...' : 'Publish'}
                </button>
            </div>

           {activeTab === 0 && (<PythonEditor time={0} parameters={[]} code={pythonCode} setCode={setPythonCode} gameData={{}}/>)}
           {activeTab === 1 && (<HtmlEditor time={0} parameters={[]} code={htmlCode} setCode={setHtmlCode} gameData={{}}/>)}
            {activeTab === 2 && (<Description data={descriptionData} onUpdate={(data: any) => setDescriptionData(data)} />)}
        </div>

    )} 
    


   
   
