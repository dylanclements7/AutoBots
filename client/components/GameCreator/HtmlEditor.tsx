"use client";
import CodeMirror from "@uiw/react-codemirror";
import { html } from "@codemirror/lang-html";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";
import { useCallback, useState, useEffect } from "react";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import styles from "../CodeEditor/page.module.css";

export default function HtmlEditor({time, parameters, code, setCode, gameData}: {time: number, parameters: any, code: string, setCode: (code: string) => void, gameData: any}) {
    const [iframeContent, setIframeContent] = useState('');
    
    const onChange = useCallback((val) => {
        setCode(val);
    }, [setCode]);
    
    const executeCode = () => {
        setIframeContent(code);
    };
    
    useEffect(() => {
        executeCode();
    }, []);
    
    return (
        <div>
            <ResizablePanelGroup
                id="html-editor-group"
                direction="horizontal"
                className="h-screen w-full"
            >
                <ResizablePanel id="html-code-panel" defaultSize={50} minSize={30}>
                    <div className="h-full flex flex-col">
                        <div className={styles.header}>
                            <h2>HTML Editor</h2>
                            <button className={styles.button} onClick={executeCode}>Run Code</button>
                        </div>
                        <div className="flex-1 overflow-scroll max-h-[calc(100vh-140px)]" >
                            <CodeMirror
                                value={code}
                                extensions={[html()]}
                                onChange={onChange}
                                theme={vscodeDark}
                                width="100%"
                                height="100%"
                                minHeight="650px"
                            />
                        </div>
                    </div>
                </ResizablePanel>
                <ResizableHandle />
                <ResizablePanel id="html-preview-panel" defaultSize={50} minSize={30}>
                    <div className="h-full flex flex-col">
                        <div className={styles.topPanel}>Preview</div>
                        <div className={styles.panel + " flex-1 overflow-scroll max-h-[calc(100vh-140px"}>
                            <iframe
                                srcDoc={iframeContent}
                                sandbox="allow-scripts allow-same-origin"
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    border: 'none',
                                    background: 'white'
                                }}
                                title="HTML Preview"
                            />
                        </div>
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )   
}