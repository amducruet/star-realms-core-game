/**
 * WebSocket hook for real-time game updates.
 */
import { useEffect, useRef, useState } from 'react';
import { WSMessage } from '../types/game';

export function useWebSocket(gameId: string | null, onMessage: (message: WSMessage) => void) {
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!gameId) return;

    const backendUrl = import.meta.env.VITE_API_URL ?? '';
    const wsBase = backendUrl
      ? backendUrl.replace(/^http/, 'ws')
      : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`;
    const wsUrl = `${wsBase}/api/ws/${gameId}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);
        onMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    return () => {
      ws.current?.close();
    };
  }, [gameId, onMessage]);

  return { connected };
}
