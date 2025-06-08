import { useState } from 'react';
import { AudioTranscriber } from './components/AudioTranscriber';
import './App.css';

function App() {
  const [showTest, setShowTest] = useState(false);

  if (showTest) {
    return (
      <div className="App">
        <AudioTranscriber />
      </div>
    );
  }

  const hasGetUserMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  const hasAudioContext = !!(window.AudioContext || (window as any).webkitAudioContext);
  const hasWebSocket = !!window.WebSocket;

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>🎤 リアルタイム音声文字起こしアプリ</h1>
      <p>ブラウザでマイク音声をリアルタイムで日本語に文字起こしします</p>
      
      <div style={{ margin: '20px 0' }}>
        <h3>ブラウザ対応状況</h3>
        <div style={{ textAlign: 'left', maxWidth: '400px', margin: '0 auto' }}>
          <p>✅ getUserMedia: {hasGetUserMedia ? 'サポート' : '未サポート'}</p>
          <p>✅ AudioContext: {hasAudioContext ? 'サポート' : '未サポート'}</p>
          <p>✅ WebSocket: {hasWebSocket ? 'サポート' : '未サポート'}</p>
        </div>
      </div>

      <button 
        onClick={() => setShowTest(true)}
        style={{
          padding: '15px 30px',
          fontSize: '18px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          marginTop: '20px',
        }}
      >
        音声文字起こしを開始
      </button>
      
      <div style={{ marginTop: '30px', fontSize: '14px', color: '#666' }}>
        <p>※ マイクアクセス許可が必要です</p>
        <p>※ HTTPS環境または localhost で動作します</p>
      </div>
    </div>
  );
}

export default App;