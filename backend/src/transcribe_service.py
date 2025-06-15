import asyncio
import numpy as np
from google import genai
from google.genai import types
from typing import Optional
import io

class TranscribeService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        self.session = None
        self.session_context = None
        self.model = "gemini-2.0-flash-live-001"
        self.is_session_active = False
        self.session_lock = asyncio.Lock()
        
        self.system_instruction = """
        あなたは正確な音声文字起こしシステムです。聞こえた音声を正確に文字起こししてください。
        会話や応答は不要で、聞こえた内容を書き起こすだけです。
        ただし、えー、あのー、などのフィラー音は削除して回答してください。
        重複や冗長な表現があれば自然な日本語に修正してください。
        """
        
        self.config = {
            "response_modalities": ["TEXT"],
            "system_instruction": types.Content(
                parts=[types.Part(text=self.system_instruction)],
            ),
            "realtime_input_config": {
                "automatic_activity_detection": {
                    "disabled": False,
                    "start_of_speech_sensitivity": types.StartSensitivity.START_SENSITIVITY_HIGH,
                    "end_of_speech_sensitivity": types.EndSensitivity.END_SENSITIVITY_LOW,
                    "silence_duration_ms": 1500,
                    "prefix_padding_ms": 300,
                }
            }
        }

    async def start_session(self):
        """転写セッション開始 - 実際のGemini Live APIセッションを開始"""
        async with self.session_lock:
            if self.is_session_active:
                print("⚠️ セッション既に開始済み")
                return True
                
            try:
                print("📢 Gemini Live APIセッション開始")
                self.session_context = self.client.aio.live.connect(
                    model=self.model, 
                    config=self.config
                )
                self.session = await self.session_context.__aenter__()
                self.is_session_active = True
                print("✅ セッション開始完了")
                return True
            except Exception as e:
                print(f"❌ セッション開始エラー: {e}")
                return False

    async def transcribe_audio_chunk(self, audio_data: bytes) -> Optional[str]:
        """音声チャンクを既存セッションで処理"""
        async with self.session_lock:
            if not self.is_session_active or not self.session:
                # セッションが無い場合は開始
                success = await self.start_session()
                if not success:
                    return None
            
            try:
                print(f"🎤 音声データ受信: {len(audio_data)} bytes")
                
                # 既存セッションに音声データを送信
                await self.session.send_realtime_input(
                    audio=types.Blob(
                        data=audio_data,
                        mime_type="audio/pcm;rate=16000"
                    )
                )
                print("📤 音声データ送信完了")
                
                # 即座に結果を待機せず、バッファリング
                return None
                
            except Exception as e:
                print(f"❌ 音声チャンク処理エラー: {e}")
                return None

    async def end_session(self):
        """セッション終了 - 最終的な転写結果を取得"""
        async with self.session_lock:
            if not self.is_session_active or not self.session:
                print("⚠️ セッションが開始されていません")
                return None
                
            try:
                print("🔚 音声ストリーム終了通知")
                await self.session.send_realtime_input(audio_stream_end=True)
                
                # 最終結果を収集
                print("⏳ 最終転写結果待機（最大15秒）...")
                all_responses = []
                
                async def collect_final_responses():
                    async for response in self.session.receive():
                        if response.text is not None:
                            text = response.text.strip()
                            if text:
                                all_responses.append(text)
                                print(f"📝 最終結果: {text}")
                        
                        if hasattr(response, 'server_content') and response.server_content:
                            if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                                print("✅ 転写完了")
                                break
                
                await asyncio.wait_for(collect_final_responses(), timeout=15.0)
                
                # 最終結果を返す
                if all_responses:
                    final_result = " ".join(all_responses)
                    print(f"📄 セッション終了時の最終結果: '{final_result}'")
                    return final_result
                else:
                    print("❌ 最終転写結果が取得できませんでした")
                    return None
                    
            except asyncio.TimeoutError:
                print("⏰ 最終結果取得タイムアウト")
                return None
            except Exception as e:
                print(f"❌ セッション終了エラー: {e}")
                return None
            finally:
                await self._cleanup_session()

    async def _cleanup_session(self):
        """セッションクリーンアップ"""
        try:
            if self.session_context:
                await self.session_context.__aexit__(None, None, None)
                self.session_context = None
            
            self.session = None
            self.is_session_active = False
            print("🧹 セッションクリーンアップ完了")
        except Exception as e:
            print(f"❌ クリーンアップエラー: {e}")

    async def cleanup(self):
        """リソースクリーンアップ"""
        await self._cleanup_session()