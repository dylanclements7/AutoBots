"use client";
import { useState } from "react";
import styles from "./page.module.css";

interface DescriptionProps {
    data?: {
        title?: string;
        objective?: string;
        gameSummary?: string;
        winCondition?: string;
        task?: string;
        botInputFormat?: string;
        botOutputFormat?: string;
        stateFormat?: string;
        playerSymbols?: string;
        difficulty?: string;
    };
    onUpdate?: (data: any) => void;
}

export default function Description({ data, onUpdate }: DescriptionProps) {
    const [formData, setFormData] = useState({
        title: data?.title || "",
        objective: data?.objective || "",
        gameSummary: data?.gameSummary || "",
        winCondition: data?.winCondition || "",
        task: data?.task || "",
        botInputFormat: data?.botInputFormat || "",
        botOutputFormat: data?.botOutputFormat || "",
        stateFormat: data?.stateFormat || "",
        playerSymbols: data?.playerSymbols || "",
        difficulty: data?.difficulty || "medium"
    });

    const handleChange = (field: string, value: string) => {
        const updated = { ...formData, [field]: value };
        setFormData(updated);
        onUpdate?.(updated);
    };

    return (
        <div className="p-6 overflow-y-auto h-[calc(100vh-60px)]">
            <div className="max-w-4xl mx-auto space-y-6">
                <h2 className="text-2xl font-bold mb-6">Game Description</h2>

                {/* Title */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium">
                        Title <span className="text-red-500">*</span>
                    </label>
                    <input
                        type="text"
                        value={formData.title}
                        onChange={(e) => handleChange("title", e.target.value)}
                        placeholder="Enter game title"
                        className="w-full px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                </div>

                {/* Objective */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium">
                        Objective <span className="text-red-500">*</span>
                    </label>
                    <input
                        type="text"
                        value={formData.objective}
                        onChange={(e) => handleChange("objective", e.target.value)}
                        placeholder="What is the main objective of the game?"
                        className="w-full px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                </div>

                {/* Game Summary */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium">
                        Game Summary <span className="text-red-500">*</span>
                    </label>
                    <textarea
                        value={formData.gameSummary}
                        onChange={(e) => handleChange("gameSummary", e.target.value)}
                        placeholder="Provide a brief summary of the game"
                        rows={4}
                        className="w-full px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                    />
                </div>

                {/* Win Condition */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium">
                        Win Condition <span className="text-red-500">*</span>
                    </label>
                    <textarea
                        value={formData.winCondition}
                        onChange={(e) => handleChange("winCondition", e.target.value)}
                        placeholder="Describe how a player wins the game"
                        rows={3}
                        className="w-full px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                    />
                </div>

                {/* Task */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium">
                        Task <span className="text-red-500">*</span>
                    </label>
                    <textarea
                        value={formData.task}
                        onChange={(e) => handleChange("task", e.target.value)}
                        placeholder="What task should the bot perform?"
                        rows={3}
                        className="w-full px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                    />
                </div>

                {/* Bot Input Format */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium">
                        Bot Input Format <span className="text-red-500">*</span>
                    </label>
                    <textarea
                        value={formData.botInputFormat}
                        onChange={(e) => handleChange("botInputFormat", e.target.value)}
                        placeholder="Describe the format of input the bot will receive (e.g., JSON structure, parameters)"
                        rows={4}
                        className="w-full px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none font-mono text-sm"
                    />
                </div>

                {/* Bot Output Format */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium">
                        Bot Output Format <span className="text-red-500">*</span>
                    </label>
                    <textarea
                        value={formData.botOutputFormat}
                        onChange={(e) => handleChange("botOutputFormat", e.target.value)}
                        placeholder="Describe the expected output format from the bot (e.g., JSON structure, return value)"
                        rows={4}
                        className="w-full px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none font-mono text-sm"
                    />
                </div>

                {/* State Format */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium">
                        State Format (JSON) <span className="text-red-500">*</span>
                    </label>
                    <textarea
                        value={formData.stateFormat}
                        onChange={(e) => handleChange("stateFormat", e.target.value)}
                        placeholder='{"board": [[null, null, null], [null, null, null], [null, null, null]], "currentPlayer": "X"}'
                        rows={6}
                        className="w-full px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none font-mono text-sm"
                    />
                </div>

                {/* Player Symbols */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium">
                        Player Symbols <span className="text-red-500">*</span>
                    </label>
                    <input
                        type="text"
                        value={formData.playerSymbols}
                        onChange={(e) => handleChange("playerSymbols", e.target.value)}
                        placeholder="e.g., X, O or Red, Blue"
                        className="w-full px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                </div>

                {/* Difficulty */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium">
                        Difficulty <span className="text-red-500">*</span>
                    </label>
                    <select
                        value={formData.difficulty}
                        onChange={(e) => handleChange("difficulty", e.target.value)}
                        className="w-full px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                        <option value="expert">Expert</option>
                    </select>
                </div>

                {/* Save Button */}
                <div className="pt-4">
                    <button
                        className={styles.button + " w-full"}
                        onClick={() => console.log("Saving:", formData)}
                    >
                        Save Game Description
                    </button>
                </div>
            </div>
        </div>
    );
}