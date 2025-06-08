/// <reference types="vite/client" />

// Web Audio API types
interface Window {
  webkitAudioContext?: typeof AudioContext;
}

// Safari compatibility
declare global {
  interface Navigator {
    webkitGetUserMedia?: typeof navigator.mediaDevices.getUserMedia;
  }
}
