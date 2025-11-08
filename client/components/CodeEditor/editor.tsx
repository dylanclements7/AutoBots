"use client";
import styles from "./page.module.css";
import React, { useEffect, useState, useRef } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";
import { Pyodide } from "@/app/lib/pyodide";
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

export default function CodeEditor({parameters}: {parameters: any}) {
  const [value, setValue] = useState(generateStartFunction(parameters));
  const [result, setResult] = useState("");
  const [pythonLoading, setPythonLoading] = useState(true);
  const pyodideRef = useRef(null);
  const [time, setTime] = useState(60);
  const [testCases, setTestCases] = useState([{name: 'case 1', vals:[1,2]},{name: 'case 2', vals:[1,2]}]);
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
    setValue(val);
  }, []);

   


  return (
    <div className="h-[calc(100%-10px)]">
        <div className={styles.header}>
            <div>Title Title</div>
            <div>
                <div className={styles.time}>{time}</div>
            </div>
        </div>
     <ResizablePanelGroup
      id="horizontal-group"
      direction="horizontal"
      className="max-w-md rounded-lg border md:min-w-[100vw] min-h-[100vh]"
    >
      <ResizablePanel id="left-panel" defaultSize={50} className="margin-5" minSize={5}>
        <div className={styles.panel}  >
          <p>Welcome to BotArena! Program. Compete. Dominate. In BotArena, you’ll design intelligent bots that battle for supremacy in a variety of games — from capture-the-flag to resource wars. Write your bot’s logic in Python or JavaScript, upload your code, and watch the chaos unfold. How it works: 1) Choose a Game Mode – select a battle type: Maze Runner, Tank Wars, or Grid Conquest. 2) Code Your Bot – write strategies, decision trees, or neural logic to guide your bot’s actions. 3) Simulate Battles – watch bots clash in real-time simulations or step-by-step replays. 4) Climb the Leaderboard – compete against classmates, friends, or global challengers for eternal glory. Example Bot (Python): class MyBot: def move(self, state): # Simple strategy: attack nearest enemy enemies = state.get_visible_enemies() if enemies: return self.attack(enemies[0]) return self.move_random(). Upcoming Tournaments: Bot Royale – every bot for itself. Only one survives. Team Tactics – collaborate and conquer in 2v2 battles. AI Gauntlet – face a lineup of developer-designed bosses. Get Started: Create your first bot now and join the next match. May the best algorithm win.</p>

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
                  value={value}
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
                <button className={styles.button} onClick={() => runCode(value,pyodideRef.current,testCases[activeTestCase].vals, setResult)}>Run Code </button>
            </div>
        </div></div>
              <div className={styles.panel}>
                <div className={styles.testCases}>
                    <div className={styles.testTabs}>
                        {testCases.map((testCase, index) => (
                            <button className={styles.testTab + (index === activeTestCase ? " " + styles.active : "")} key={index} onClick={() => setActiveTestCase(index)}>{testCase.name}</button>
                        ))}
                    </div>
                    {testCases[activeTestCase].vals.map((val, index) => (
                        <div className={styles.caseParam} key={index}>{parameters[index].name}: <input className={styles.caseParamInput} value={val} onChange={(e) => setTestCases(testCases.map((testCase, i) => i === activeTestCase ? {...testCase, vals: testCase.vals.map((v, j) => j === index ? e.target.value : v)} : testCase))}></input></div>
                    ))}

                </div>
                <div>RESULT: {result}</div>
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </ResizablePanel>
    </ResizablePanelGroup>
    </div>

    
  );
}
