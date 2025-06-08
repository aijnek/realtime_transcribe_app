import { useState, useRef, useCallback, useEffect } from 'react';

export interface TranscriptionResult {
  type: 'transcription_result';
  text: string;
  timestamp: number;
}

export interface WebSocketMessage {
  type: 'session_started' | 'session_ended' | 'error' | 'transcription_result';
  text?: string;
  message?: string;
  code?: string;
  timestamp?: number;
}

export interface WebSocketHookState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: WebSocketMessage | null;
}

export const useWebSocket = (url: string) => {
  const [state, setState] = useState<WebSocketHookState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    lastMessage: null,
  });
  
  const socketRef = useRef<WebSocket | null>(null);
  const onMessageRef = useRef<((message: WebSocketMessage) => void) | null>(null);
  
  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }
    
    setState(prev => ({ ...prev, isConnecting: true, error: null }));
    
    try {
      const socket = new WebSocket(url);
      socketRef.current = socket;
      
      socket.onopen = () => {
        setState(prev => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          error: null,
        }));
      };
      
      socket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setState(prev => ({ ...prev, lastMessage: message }));
          
          if (onMessageRef.current) {
            onMessageRef.current(message);
          }
        } catch (err) {
          console.error('WebSocketメッセージエラー:', err);
        }
      };
      
      socket.onclose = () => {
        setState(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
        }));
      };
      
      socket.onerror = () => {
        setState(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
          error: 'WebSocket接続エラーが発生しました',
        }));
      };
      
    } catch (err) {
      setState(prev => ({
        ...prev,
        isConnecting: false,
        error: 'WebSocket接続に失敗しました',
      }));
    }
  }, [url]);
  
  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    
    setState(prev => ({
      ...prev,
      isConnected: false,
      isConnecting: false,
    }));
  }, []);
  
  const sendMessage = useCallback((message: object) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      const messageStr = JSON.stringify(message);
      socketRef.current.send(messageStr);
    }
  }, []);
  
  const startSession = useCallback(() => {
    sendMessage({ type: 'start_session' });
  }, [sendMessage]);
  
  const endSession = useCallback(() => {
    sendMessage({ type: 'end_session' });
  }, [sendMessage]);
  
  const sendAudioChunk = useCallback((audioData: ArrayBuffer, timestamp: number) => {
    // Convert ArrayBuffer to base64
    const uint8Array = new Uint8Array(audioData);
    const base64 = btoa(String.fromCharCode(...uint8Array));
    
    sendMessage({
      type: 'audio_chunk',
      data: base64,
      timestamp,
    });
  }, [sendMessage]);
  
  const setOnMessage = useCallback((callback: (message: WebSocketMessage) => void) => {
    onMessageRef.current = callback;
  }, []);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);
  
  return {
    ...state,
    connect,
    disconnect,
    sendMessage,
    startSession,
    endSession,
    sendAudioChunk,
    setOnMessage,
  };
};