import { useState, useRef, useCallback } from 'react';

export interface AudioCaptureConfig {
  sampleRate: number;
  channels: number;
  bufferSize: number;
  silenceThreshold: number;
  silenceDuration: number; // ms
}

export interface AudioChunk {
  data: ArrayBuffer;
  timestamp: number;
  audioLevel: number;
}

const DEFAULT_CONFIG: AudioCaptureConfig = {
  sampleRate: 16000,
  channels: 1,
  bufferSize: 2048, // Must be power of 2: 256, 512, 1024, 2048, 4096, 8192, 16384
  silenceThreshold: 20,
  silenceDuration: 1500, // 1.5秒
};

export const useAudioCapture = (config: Partial<AudioCaptureConfig> = {}) => {
  const fullConfig = { ...DEFAULT_CONFIG, ...config };
  
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  
  const audioBufferRef = useRef<Int16Array[]>([]);
  const silenceStartRef = useRef<number | null>(null);
  const lastAudioLevelRef = useRef<number>(0);
  
  const onAudioChunkRef = useRef<((chunk: AudioChunk) => void) | null>(null);
  
  const calculateAudioLevel = useCallback((audioData: Float32Array): number => {
    let sum = 0;
    for (let i = 0; i < audioData.length; i++) {
      sum += audioData[i] * audioData[i];
    }
    return Math.sqrt(sum / audioData.length) * 32768; // Convert to 16-bit scale
  }, []);
  
  const processAudioBuffer = useCallback((audioBuffer: Float32Array) => {
    // Convert Float32Array to Int16Array
    const int16Buffer = new Int16Array(audioBuffer.length);
    for (let i = 0; i < audioBuffer.length; i++) {
      const sample = Math.max(-1, Math.min(1, audioBuffer[i]));
      int16Buffer[i] = sample * 32767;
    }
    
    audioBufferRef.current.push(int16Buffer);
    
    // Calculate audio level
    const level = calculateAudioLevel(audioBuffer);
    setAudioLevel(level);
    lastAudioLevelRef.current = level;
    
    // Check for silence
    const now = Date.now();
    if (level < fullConfig.silenceThreshold) {
      if (!silenceStartRef.current) {
        silenceStartRef.current = now;
      } else if (now - silenceStartRef.current > fullConfig.silenceDuration) {
        // Silence detected, send accumulated audio
        if (audioBufferRef.current.length > 0) {
          sendAudioChunk();
        }
      }
    } else {
      silenceStartRef.current = null;
    }
  }, [fullConfig.silenceThreshold, fullConfig.silenceDuration, calculateAudioLevel]);
  
  const sendAudioChunk = useCallback(() => {
    if (audioBufferRef.current.length === 0 || !onAudioChunkRef.current) return;
    
    // Combine all audio buffers
    const totalLength = audioBufferRef.current.reduce((sum, buffer) => sum + buffer.length, 0);
    const combinedBuffer = new Int16Array(totalLength);
    
    let offset = 0;
    for (const buffer of audioBufferRef.current) {
      combinedBuffer.set(buffer, offset);
      offset += buffer.length;
    }
    
    // Create audio chunk
    const chunk: AudioChunk = {
      data: combinedBuffer.buffer,
      timestamp: Date.now(),
      audioLevel: lastAudioLevelRef.current,
    };
    
    // Send chunk
    onAudioChunkRef.current(chunk);
    
    // Clear buffer
    audioBufferRef.current = [];
    silenceStartRef.current = null;
    
    console.log(`🎤 音声チャンク送信: ${combinedBuffer.length * 2} bytes, レベル: ${chunk.audioLevel.toFixed(1)}`);
  }, []);
  
  const startRecording = useCallback(async (onAudioChunk: (chunk: AudioChunk) => void) => {
    try {
      setError(null);
      onAudioChunkRef.current = onAudioChunk;
      
      console.log('🎤 マイクアクセス要求中...');
      
      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: fullConfig.sampleRate,
          channelCount: fullConfig.channels,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      
      mediaStreamRef.current = stream;
      
      // Create audio context (Safari compatibility)
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) {
        throw new Error('お使いのブラウザはWeb Audio APIをサポートしていません');
      }
      
      const audioContext = new AudioContextClass({
        sampleRate: fullConfig.sampleRate,
      });
      audioContextRef.current = audioContext;
      
      // Create analyser for audio level monitoring
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;
      
      // Create processor for audio processing
      const processor = audioContext.createScriptProcessor(fullConfig.bufferSize, 1, 1);
      processorRef.current = processor;
      
      // Connect audio nodes
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.connect(processor);
      processor.connect(audioContext.destination);
      
      // Process audio data
      processor.onaudioprocess = (event: AudioProcessingEvent) => {
        const inputBuffer = event.inputBuffer.getChannelData(0);
        processAudioBuffer(inputBuffer);
      };
      
      setIsRecording(true);
      audioBufferRef.current = [];
      silenceStartRef.current = null;
      
      console.log('🎤 録音開始');
      
    } catch (err) {
      const message = err instanceof Error ? err.message : 'マイクアクセスに失敗しました';
      setError(message);
      console.error('❌ 録音開始エラー:', err);
    }
  }, [fullConfig.sampleRate, fullConfig.channels, fullConfig.bufferSize, processAudioBuffer]);
  
  const stopRecording = useCallback(() => {
    console.log('🔚 録音停止');
    
    // Send remaining audio if any
    if (audioBufferRef.current.length > 0) {
      sendAudioChunk();
    }
    
    // Clean up audio context
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    
    if (analyserRef.current) {
      analyserRef.current.disconnect();
      analyserRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    // Stop media stream
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }
    
    setIsRecording(false);
    setAudioLevel(0);
    onAudioChunkRef.current = null;
    audioBufferRef.current = [];
  }, [sendAudioChunk]);
  
  return {
    isRecording,
    audioLevel,
    error,
    startRecording,
    stopRecording,
  };
};