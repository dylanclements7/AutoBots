
export const Pyodide = (function () {
    let instancePromise = null;
  
    async function createInstance() {
      if (typeof window === "undefined") {
        throw new Error("Pyodide can only run in the browser");
      }
  
      if (!window.loadPyodide) {
        await new Promise((resolve) => {
          const script = document.createElement("script");
          script.src = "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js";
          script.onload = resolve;
          document.body.appendChild(script);
        });
      }
  
      const pyodide = await window.loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/",
      });
  
      return pyodide;
    }
  
    return {
      getInstance: async function () {
        if (!instancePromise) {
          instancePromise = createInstance();
        }
        return instancePromise;
      },
    };
  })();

  
  