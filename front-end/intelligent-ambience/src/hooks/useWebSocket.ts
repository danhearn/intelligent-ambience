import { useState, useRef, useEffect } from 'react';

interface WebSocketMessage {
  type: string;
  text?: string;
  message?: string;
  step?: string;
  percent?: number;
}

export const useWebSocket = (url: string) => {
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState("idle");
  const [thinking, setThinking] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  
  const wsRef = useRef<WebSocket | null>(null);

  const connect = (data: any) => {
    // Close any existing socket first
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }
    
    setThinking("");
    setStatus("connecting");
    setDone(false);
    setError(null);

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      setStatus("connected");
      ws.send(JSON.stringify({
        type: "init",
        ...data
      }));
    };

    ws.onmessage = (event) => {
      const msg: WebSocketMessage = JSON.parse(event.data);
      switch (msg.type) {
        case "token":
          setThinking(prev => prev + (msg.text ?? ""));
          break;
        case "status":
          setStatus(msg.message ?? "working...");
          break;
        case "progress":
          setStatus(`${msg.step ?? "Processing"} ${msg.percent ?? 0}%`);
          break;
        case "error":
          setError(msg.message ?? "Error");
          setConnected(false);
          ws.close();
          break;
        case "done":
          setDone(true);
          setConnected(false);
          ws.close();
          break;
      }
    };

    ws.onerror = () => {
      setError("WebSocket error");
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
    };
  };

  const disconnect = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "cancel" }));
      wsRef.current.close();
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    connected,
    status,
    thinking,
    error,
    done,
    connect,
    disconnect
  };
};
