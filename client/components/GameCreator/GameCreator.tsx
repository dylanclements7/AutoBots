"use client"
import PythonEditor from "./PythonEditor";
import styles from "./page.module.css";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable"
import { useState } from "react";
import HtmlEditor from "./HtmlEditor";
import Description from "./Description";

export default function GameCreator() {
    const [activeTab, setActiveTab] = useState(0);
    const [pythonCode, setPythonCode] = useState("def is_valid_move(board, move, piece):\n    return True \n \ndef make_move(board, move):\n    return board \n\ndef check_winner(board):\n    return None")
    const [htmlCode, setHtmlCode] = useState("");
    const [descriptionData, setDescriptionData] = useState({});

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
                <button className={styles.button}>Publish</button>
            </div>

           {activeTab === 0 && (<PythonEditor time={0} parameters={[]} code={pythonCode} setCode={setPythonCode} gameData={{}}/>)}
           {activeTab === 1 && (<HtmlEditor time={0} parameters={[]} code={htmlCode} setCode={setHtmlCode} gameData={{}}/>)}
            {activeTab === 2 && (<Description  data = {descriptionData} onUpdate={(data) => setDescriptionData(data)} />)}
        </div>

    )} 
    


   
   
