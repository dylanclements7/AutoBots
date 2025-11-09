"use client";
import styles from "./page.module.css";
import React, { useEffect, useState, useRef } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";
import { Pyodide } from "@/app/lib/pyodide";
import { useWebSocket } from "@/app/lib/websockets";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
function generateStartFunction(parameters: any){
    let startFunction = "def game(";
    for (let i = 0; i < parameters.length; i++) {
        startFunction += parameters[i].name + ", ";
    }
    startFunction += "):\n pass";
    return startFunction;
}

async function runCode(code: string, pyodide: any, vals: any[], setOutput: (output: string) => void){
    
    //load function
    await pyodide.runPythonAsync(code);
    //call game function
    const out = await pyodide.runPythonAsync("game(" + vals.join(", ") + ")")
    setOutput(out?.toString());
}

async function runAllTestCases(code: string, pyodide: any, testCases: any[], setTestCases: (testCases: any[]) => void){
    const updatedTestCases = [...testCases];
    
    for (let i = 0; i < testCases.length; i++) {
        try {
            // Load function once
            if (i === 0) {
                await pyodide.runPythonAsync(code);
            }
            // Run each test case
            const out = await pyodide.runPythonAsync("game(" + testCases[i].vals.join(", ") + ")");
            updatedTestCases[i] = {...updatedTestCases[i], output: out?.toString() || ""};
        } catch (e) {
            updatedTestCases[i] = {...updatedTestCases[i], output: "Error: " + e.message};
        }
    }
    
    setTestCases(updatedTestCases);
}

export default function CodeEditor({time, parameters, code, setCode, gameData}: {time: number, parameters: any, code: string, setCode: (code: string) => void, gameData: any}) {
  
  const [result, setResult] = useState("");
  const [pythonLoading, setPythonLoading] = useState(true);
  const pyodideRef = useRef(null);
  const { socket, roomId, sendMessage } = useWebSocket();
  const [waiting, setWaiting] = useState(false);
  const [testCases, setTestCases] = useState([{name: 'case 1', vals:[1,2], output: ""},{name: 'case 2', vals:[1,2], output: ""}]);
    const [activeTestCase, setActiveTestCase] = useState(0);
    
    useEffect(() => {
    async function loadPyodideInstance() {
      setPythonLoading(true);
      const py = await Pyodide.getInstance();
      pyodideRef.current = py;
      setPythonLoading(false);
    }
    loadPyodideInstance();
  }, []);



  const onChange = React.useCallback((val) => {
    setCode(val);
  }, []);

  const submit = () => {
    if (!roomId) {
      console.error("No roomId available");
      return;
    }
    setWaiting(true);
    sendMessage({ type: "bot_code", code: code, roomId: roomId });
  }
   


  return (
    <>
    {!waiting && <div className="h-[calc(100%-10px)]">
        <div className={styles.header}>
            <div>{gameData.title}</div>
            <div>
                <div className={styles.time}>{time}</div>
            </div>
            <button onClick={submit} className={styles.button}>Submit</button>
        </div>
     <ResizablePanelGroup
      id="horizontal-group"
      direction="horizontal"
      className="max-w-md rounded-lg border md:min-w-[100vw] min-h-[100vh]"
    >
      <ResizablePanel id="left-panel" defaultSize={50} className="margin-5" minSize={5}>
        <div className={styles.panel}  >
          <p>{gameData.description}</p>
        </div>
      </ResizablePanel>
      <ResizableHandle />
      <ResizablePanel id="right-panel" defaultSize={50}>
        <ResizablePanelGroup id="vertical-group" direction="vertical">
          <ResizablePanel id="code-panel" defaultSize={70} minSize={5}>
            <div className="h-full flex flex-col">
              <div className={styles.topPanel}>Code</div>
              <div className={styles.panel}>
                <CodeMirror
                  value={code}
                  extensions={[python()]}
                  onChange={onChange}
                  theme={vscodeDark}
                  width="100%"
                  height="100%"
                />
              </div>
            </div>
          </ResizablePanel>
          <ResizableHandle />
          <ResizablePanel id="testing-panel" defaultSize={30} minSize={5} maxSize={40}>
            <div className="h-full flex flex-col">
              <div className={styles.topPanel}><div className={styles.testTop}>
            <div>
            <h2>Testing</h2>
            </div>
            <div>
                <button className={styles.button} onClick={() => runAllTestCases(code,pyodideRef.current,testCases, setTestCases)}>Run Code </button>
            </div>
        </div></div>
              <div className={styles.panel}>
                <div className={styles.testCases}>
                    <div className={styles.testTabs}>
                        {testCases.map((testCase, index) => (
                            <button className={styles.testTab + (index === activeTestCase ? " " + styles.active : "")} key={index} onClick={() => setActiveTestCase(index)}>{testCase.name}</button>
                        ))}
                        <button className={styles.testTab} onClick={() => {
                            const newTestCase = {
                                name: `case ${testCases.length + 1}`,
                                vals: parameters.map(() => 0),
                                output: ""
                            };
                            setTestCases([...testCases, newTestCase]);
                            setActiveTestCase(testCases.length);
                        }}>+</button>
                    </div>
                    <div className={styles.output}>Output: {testCases[activeTestCase].output}</div>
                    {testCases[activeTestCase].vals.map((val, index) => (
                        <div className={styles.caseParam} key={index}>{parameters[index].name}: <input className={styles.caseParamInput} value={val} onChange={(e) => setTestCases(testCases.map((testCase, i) => i === activeTestCase ? {...testCase, vals: testCase.vals.map((v, j) => j === index ? e.target.value : v)} : testCase))}></input></div>
                    ))}

                </div>
                
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </ResizablePanel>
    </ResizablePanelGroup>
    </div>}
    {waiting && <div>Waiting for match to start...</div>} </>

    
  );
}