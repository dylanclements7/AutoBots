"use client";
import styles from "./page.module.css";
import React, { useEffect, useState, useRef } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";
import { Pyodide } from "./lib/pyodide";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import CodeEditor from "@/components/CodeEditor/editor"

export default function App() {
  return (
    <CodeEditor parameters={[
      //use python types
      {name: "num1", type: "int"}, {name: "num2", type: "int"}
    ]} />
    
  );
}
