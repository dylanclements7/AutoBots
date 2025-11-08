"use client"
import { useEffect, useRef, useState } from "react";

const ComponentSandbox = () => {
  const [userCode, setUserCode] = useState(`<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      font-family: Arial, sans-serif;
      padding: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    .container {
      max-width: 600px;
      margin: 0 auto;
      background: rgba(255, 255, 255, 0.1);
      padding: 30px;
      border-radius: 10px;
      backdrop-filter: blur(10px);
    }
    button {
      background: white;
      color: #667eea;
      border: none;
      padding: 10px 20px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 16px;
      margin-top: 10px;
    }
    button:hover {
      background: #f0f0f0;
    }
    #counter {
      font-size: 48px;
      font-weight: bold;
      margin: 20px 0;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Counter Demo</h1>
    <div id="counter">0</div>
    <button onclick="increment()">Increment</button>
    <button onclick="decrement()">Decrement</button>
    <button onclick="reset()">Reset</button>
  </div>

  <script>
    let count = 0;
    const counterEl = document.getElementById('counter');

    function increment() {
      count++;
      updateDisplay();
    }

    function decrement() {
      count--;
      updateDisplay();
    }

    function reset() {
      count = 0;
      updateDisplay();
    }

    function updateDisplay() {
      counterEl.textContent = count;
    }
  </script>
</body>
</html>`);
  
  const [error, setError] = useState(null);
  const [iframeContent, setIframeContent] = useState('');

  const createSandboxedHTML = (code) => {
    return code;
  };

  const executeCode = () => {
    setError(null);
    const sandboxedHTML = createSandboxedHTML(userCode);
    setIframeContent(sandboxedHTML);
  };

  useEffect(() => {
    executeCode();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', gap: '10px', padding: '20px' }}>
      <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0 }}>HTML/CSS/JavaScript Code</h2>
          <button
            onClick={executeCode}
            style={{
              padding: '10px 20px',
              background: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            Run Code
          </button>
        </div>
        
        <textarea
          value={userCode}
          onChange={(e) => setUserCode(e.target.value)}
          style={{
            flex: 1,
            fontFamily: 'monospace',
            padding: '15px',
            border: '1px solid #ddd',
            borderRadius: '6px',
            fontSize: '14px',
            resize: 'none'
          }}
        />
      </div>

      <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <h2 style={{ margin: 0 }}>Sandboxed Output</h2>
        <div style={{ flex: 1, border: '2px solid #2563eb', borderRadius: '6px', overflow: 'hidden' }}>
          <iframe
            srcDoc={iframeContent}
            sandbox="allow-scripts allow-same-origin"
            style={{
              width: '100%',
              height: '100%',
              border: 'none',
              background: 'white'
            }}
            title="Sandboxed Component"
          />
        </div>
        <div style={{ fontSize: '12px', color: '#666', padding: '10px', background: '#f5f5f5', borderRadius: '6px' }}>
          <strong>Sandbox restrictions:</strong> allow-scripts and allow-same-origin (no forms, popups, top navigation, etc.)
        </div>
      </div>

      {error && (
        <div style={{ padding: '15px', background: '#fee', color: '#c00', borderRadius: '6px', border: '1px solid #fcc' }}>
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
};

export default ComponentSandbox;