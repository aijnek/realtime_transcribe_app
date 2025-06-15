import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json
import asyncio
from typing import Dict, Any
import base64

from .transcribe_service import TranscribeService

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(title="Realtime Transcription API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, TranscribeService] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "APIキーが設定されていません",
                "code": "missing_api_key"
            }))
            await websocket.close()
            return
        
        transcribe_service = TranscribeService(api_key)
        self.active_connections[websocket] = transcribe_service
        print(f"🔗 WebSocket接続確立: {len(self.active_connections)}個の接続")

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            transcribe_service = self.active_connections[websocket]
            await transcribe_service.cleanup()
            del self.active_connections[websocket]
        print(f"🔗 WebSocket接続終了: {len(self.active_connections)}個の接続")

    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except:
            await self.disconnect(websocket)

manager = ConnectionManager()

@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if websocket not in manager.active_connections:
                break
                
            transcribe_service = manager.active_connections[websocket]
            
            if message["type"] == "audio_chunk":
                audio_data = base64.b64decode(message["data"])
                
                # 音声チャンクを転写サービスに送信（結果は end_session で取得）
                await transcribe_service.transcribe_audio_chunk(audio_data)
            
            elif message["type"] == "start_session":
                await transcribe_service.start_session()
                await manager.send_message(websocket, {
                    "type": "session_started"
                })
            
            elif message["type"] == "end_session":
                final_result = await transcribe_service.end_session()
                if final_result:
                    await manager.send_message(websocket, {
                        "type": "transcription_result",
                        "text": final_result,
                        "timestamp": message.get("timestamp")
                    })
                await manager.send_message(websocket, {
                    "type": "session_ended"
                })
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"❌ WebSocketエラー: {e}")
        await manager.send_message(websocket, {
            "type": "error",
            "message": str(e),
            "code": "websocket_error"
        })
    finally:
        await manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Realtime Transcription API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)