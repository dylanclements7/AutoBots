
"use client";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { useCallback, useState, useRef, useEffect } from "react";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { Pyodide } from "@/app/lib/pyodide";
import styles from "../CodeEditor/page.module.css";

async function runAllTestCases(code: string, pyodide: any, testCases: any[], setTestCases: (testCases: any[]) => void){
    const updatedTestCases = [...testCases];
    
    for (let i = 0; i < testCases.length; i++) {
        try {
            // Load function once
            if (i === 0) {
                await pyodide.runPythonAsync(code);
            }
            // Run each test case
            const out1 = await pyodide.runPythonAsync("is_valid_move(" + testCases[i].vals[0] + ", " + testCases[i].vals[1] + ", '" + testCases[i].vals[2] + "')");
            const out2 = await pyodide.runPythonAsync("make_move(" + testCases[i].vals[0] + ", " + testCases[i].vals[1] + ")");
            const out3 = await pyodide.runPythonAsync("check_winner(" + testCases[i].vals[0] + ")");
            updatedTestCases[i] = {...updatedTestCases[i], output1: out1?.toString() || "", output2: out2?.toString() || "", output3: out3?.toString() || ""};
        } catch (e: any) {
            updatedTestCases[i] = {...updatedTestCases[i], output1: "Error: " + e.message, output2: "Error: " + e.message, output3: "Error: " + e.message};
        }
    }
    
    setTestCases(updatedTestCases);
}

export default function PythonEditor({time, parameters, code, setCode, gameData}: {time: number, parameters: any, code: string, setCode: (code: string) => void, gameData: any}) {
    const [pythonLoading, setPythonLoading] = useState(true);
    const pyodideRef = useRef<any>(null);
    const [testCases, setTestCases] = useState([{name: 'case 1', vals:['{}', '0', 'X'], output1: "", output2: "", output3: ""},{name: 'case 2', vals:['{}', '0', 'X'], output1: "", output2: "", output3: ""}]);
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
    
    const onChange = useCallback((val) => {
        setCode(val);
    }, [setCode]);
    return (
        <div>
            <ResizablePanelGroup
      id="horizontal-group"
      direction="horizontal"
      className="max-w-md rounded-lg border md:min-w-[100vw] min-h-[calc(100vh-140px)]"
    >
      <ResizablePanel id="left-panel" defaultSize={50} className="margin-5" minSize={5}>
        <CodeMirror
                value={code}
                extensions={[python()]}
                onChange={onChange}
                theme={vscodeDark}
                width="100%"
                height="100%"
                minHeight="650px"
            />
      </ResizablePanel>
      <ResizableHandle />
      <ResizablePanel id="right-panel" defaultSize={50}>
        <ResizablePanelGroup id="vertical-group" direction="vertical">
          <ResizablePanel id="code-panel" defaultSize={70} minSize={5}>
            <div className="h-full flex flex-col overflow-scroll">
              <div className={styles.topPanel}>Output</div>
              <div className={styles.panel}>
                <p className={styles.testLabel}>is_valid_move(board, move)</p>  
                <div className={styles.output}>Output: {testCases[activeTestCase].output1}</div>
                <p className={styles.testLabel}>make_move(board, move)</p>
                <div className={styles.output}>Output: {testCases[activeTestCase].output2}</div>
                <p className={styles.testLabel}>check_winner(board)</p>
                <div className={styles.output}>Output: {testCases[activeTestCase].output3}</div>
              </div>
            </div>
          </ResizablePanel>
          <ResizableHandle />
          <ResizablePanel id="testing-panel" defaultSize={30} minSize={5} maxSize={40}>
            <div className="h-full flex flex-col">
              <div className={styles.topPanel}>
                <div className={styles.testTop}>
                  <div>
                    <h2>Testing</h2>
                  </div>
                  <div>
                    <button className={styles.button} onClick={() => runAllTestCases(code, pyodideRef.current, testCases, setTestCases)}>Run Code</button>
                  </div>
                </div>
              </div>
              <div className={styles.panel}>
                <div className={styles.testCases}>
                  <div className={styles.testTabs}>
                    {testCases.map((testCase, index) => (
                      <button className={styles.testTab + (index === activeTestCase ? " " + styles.active : "")} key={index} onClick={() => setActiveTestCase(index)}>{testCase.name}</button>
                    ))}
                    <button className={styles.testTab} onClick={() => {
                      const newTestCase = {
                        name: `case ${testCases.length + 1}`,
                        vals: ['{}', '0', 'X'],
                        output1: "",
                        output2: "",
                        output3: ""
                      };
                      setTestCases([...testCases, newTestCase]);
                      setActiveTestCase(testCases.length);
                    }}>+</button>
                  </div>
                  
                  <div className={styles.caseParam}>board: <input className={styles.caseParamInput} value={testCases[activeTestCase].vals[0]} onChange={(e) => setTestCases(testCases.map((testCase, i) => i === activeTestCase ? {...testCase, vals: [e.target.value, testCase.vals[1], testCase.vals[2]]} : testCase))}></input></div>
                  <div className={styles.caseParam}>move: <input className={styles.caseParamInput} value={testCases[activeTestCase].vals[1]} onChange={(e) => setTestCases(testCases.map((testCase, i) => i === activeTestCase ? {...testCase, vals: [testCase.vals[0], e.target.value, testCase.vals[2]]} : testCase))}></input></div>
                  <div className={styles.caseParam}>piece: <input className={styles.caseParamInput} value={testCases[activeTestCase].vals[2]} onChange={(e) => setTestCases(testCases.map((testCase, i) => i === activeTestCase ? {...testCase, vals: [testCase.vals[0], testCase.vals[1], e.target.value]} : testCase))}></input></div>
                </div>
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </ResizablePanel>
    </ResizablePanelGroup>

            
        </div>
    )
}
