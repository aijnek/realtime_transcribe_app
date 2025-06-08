import { useState, useCallback, useEffect } from 'react';
import { useAudioCapture } from '../hooks/useAudioCapture';
import { useWebSocket, type WebSocketMessage } from '../hooks/useWebSocket';

const WEBSOCKET_URL = 'ws://localhost:8000/ws/transcribe';

export const AudioTranscriber: React.FC = () => {
  const [transcriptionResults, setTranscriptionResults] = useState<string[]>([]);
  const [currentTranscription, setCurrentTranscription] = useState<string>('');
  
  const audioCapture = useAudioCapture({
    bufferSize: 2048, // Valid power of 2
    silenceThreshold: 50, // Adjust based on environment
    silenceDuration: 2000, // 2 seconds of silence
  });
  
  const webSocket = useWebSocket(WEBSOCKET_URL);
  
  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'transcription_result':
        if (message.text) {
          setTranscriptionResults(prev => [...prev, message.text!]);
          setCurrentTranscription('');
        }
        break;
      case 'error':
        console.error('サーバーエラー:', message.message);
        break;
      case 'session_started':
        break;
      case 'session_ended':
        break;
    }
  }, []);
  
  // Set up WebSocket message handler
  useEffect(() => {
    webSocket.setOnMessage(handleWebSocketMessage);
  }, [webSocket, handleWebSocketMessage]);
  
  // Handle audio chunks
  const handleAudioChunk = useCallback((chunk: { data: ArrayBuffer; timestamp: number; audioLevel: number }) => {
    if (webSocket.isConnected) {
      webSocket.sendAudioChunk(chunk.data, chunk.timestamp);
    }
  }, [webSocket]);
  
  // Start recording
  const startRecording = useCallback(async () => {
    try {
      // Connect WebSocket first
      if (!webSocket.isConnected) {
        webSocket.connect();
        // Wait a bit for connection
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      if (webSocket.isConnected) {
        webSocket.startSession();
        await audioCapture.startRecording(handleAudioChunk);
        setCurrentTranscription('録音中...');
      } else {
        console.error('WebSocket接続に失敗しました');
      }
    } catch (error) {
      console.error('録音開始エラー:', error);
    }
  }, [webSocket, audioCapture, handleAudioChunk]);
  
  // Stop recording
  const stopRecording = useCallback(() => {
    audioCapture.stopRecording();
    webSocket.endSession();
    setCurrentTranscription('');
  }, [audioCapture, webSocket]);
  
  // Clear results
  const clearResults = useCallback(() => {
    setTranscriptionResults([]);
    setCurrentTranscription('');
  }, []);
  
  // Audio level indicator
  const getAudioLevelColor = (level: number): string => {
    if (level < 20) return '#ccc';
    if (level < 100) return '#4CAF50';
    if (level < 200) return '#FFC107';
    return '#F44336';
  };
  
  return (
    <div style={{ 
      padding: '20px', 
      maxWidth: '900px', 
      margin: '0 auto',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <h1 style={{ 
        textAlign: 'center', 
        color: '#333',
        marginBottom: '30px',
        fontSize: '32px'
      }}>
        🎤 リアルタイム音声文字起こし
      </h1>
      
      {/* Status indicators */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '10px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: webSocket.isConnected ? '#4CAF50' : '#F44336',
          }} />
          <span>WebSocket: {webSocket.isConnected ? '接続済み' : '未接続'}</span>
          
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: audioCapture.isRecording ? '#4CAF50' : '#ccc',
          }} />
          <span>録音: {audioCapture.isRecording ? '実行中' : '停止中'}</span>
        </div>
        
        {/* Audio level indicator */}
        {audioCapture.isRecording && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>音声レベル:</span>
            <div style={{
              width: '200px',
              height: '20px',
              backgroundColor: '#eee',
              borderRadius: '10px',
              overflow: 'hidden',
            }}>
              <div style={{
                width: `${Math.min(100, (audioCapture.audioLevel / 300) * 100)}%`,
                height: '100%',
                backgroundColor: getAudioLevelColor(audioCapture.audioLevel),
                transition: 'width 0.1s ease',
              }} />
            </div>
            <span>{audioCapture.audioLevel.toFixed(0)}</span>
          </div>
        )}
      </div>
      
      {/* Error display */}
      {(audioCapture.error || webSocket.error) && (
        <div style={{
          padding: '10px',
          backgroundColor: '#ffebee',
          color: '#c62828',
          borderRadius: '5px',
          marginBottom: '20px',
        }}>
          {audioCapture.error || webSocket.error}
        </div>
      )}
      
      {/* Control buttons */}
      <div style={{ 
        marginBottom: '30px', 
        display: 'flex', 
        gap: '12px',
        justifyContent: 'center',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={startRecording}
          disabled={audioCapture.isRecording || webSocket.isConnecting}
          style={{
            padding: '14px 28px',
            backgroundColor: audioCapture.isRecording ? '#6c757d' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: audioCapture.isRecording ? 'not-allowed' : 'pointer',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            transition: 'all 0.2s ease',
            minWidth: '120px'
          }}
        >
          {webSocket.isConnecting ? '接続中...' : audioCapture.isRecording ? '録音中' : '🎤 録音開始'}
        </button>
        
        <button
          onClick={stopRecording}
          disabled={!audioCapture.isRecording}
          style={{
            padding: '14px 28px',
            backgroundColor: !audioCapture.isRecording ? '#6c757d' : '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: !audioCapture.isRecording ? 'not-allowed' : 'pointer',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            transition: 'all 0.2s ease',
            minWidth: '120px'
          }}
        >
          ⏹️ 録音停止
        </button>
        
        <button
          onClick={clearResults}
          style={{
            padding: '14px 28px',
            backgroundColor: '#fd7e14',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            transition: 'all 0.2s ease',
            minWidth: '120px'
          }}
        >
          🗑️ クリア
        </button>
      </div>
      
      {/* Current transcription */}
      {currentTranscription && (
        <div style={{
          padding: '15px',
          backgroundColor: '#e3f2fd',
          borderRadius: '5px',
          marginBottom: '20px',
          fontStyle: 'italic',
        }}>
          {currentTranscription}
        </div>
      )}
      
      {/* Transcription results */}
      <div style={{
        border: '2px solid #e0e0e0',
        borderRadius: '12px',
        minHeight: '300px',
        padding: '24px',
        backgroundColor: '#ffffff',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}>
        <h3 style={{ 
          margin: '0 0 20px 0', 
          color: '#333',
          fontSize: '20px',
          fontWeight: '600'
        }}>
          文字起こし結果
        </h3>
        {transcriptionResults.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '60px 20px',
            color: '#888',
            fontSize: '16px'
          }}>
            📝 録音開始ボタンを押して音声文字起こしを開始してください
          </div>
        ) : (
          <div>
            {transcriptionResults.map((result, index) => (
              <div
                key={index}
                style={{
                  padding: '16px 20px',
                  marginBottom: '16px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '10px',
                  border: '1px solid #e9ecef',
                  borderLeft: '4px solid #4CAF50',
                }}
              >
                <div style={{ 
                  fontSize: '12px', 
                  color: '#6c757d',
                  marginBottom: '8px',
                  fontWeight: '500'
                }}>
                  {new Date().toLocaleTimeString()} #{index + 1}
                </div>
                <div style={{ 
                  fontSize: '18px', 
                  lineHeight: '1.6', 
                  color: '#212529',
                  fontWeight: '400'
                }}>
                  {result}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};