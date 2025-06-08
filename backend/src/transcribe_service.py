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
        self.model = "gemini-2.0-flash-live-001"
        
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
        """転写セッション開始 - 実際の処理は transcribe_audio_chunk で行う"""
        print("📢 転写サービス準備完了")
        return True

    async def transcribe_audio_chunk(self, audio_data: bytes) -> Optional[str]:
        """音声チャンクを転写 - 元のtranscribe.pyパターンを使用"""
        
        try:
            print(f"🎤 音声データ受信: {len(audio_data)} bytes")
            
            # 新しいセッションで処理（元のパターン）
            async with self.client.aio.live.connect(model=self.model, config=self.config) as session:
                print("📢 Gemini Live APIセッション開始")
                
                # 音声データを送信
                await session.send_realtime_input(
                    audio=types.Blob(
                        data=audio_data,
                        mime_type="audio/pcm;rate=16000"
                    )
                )
                print("📤 音声データ送信完了")
                
                # 音声ストリーム終了を通知
                await session.send_realtime_input(audio_stream_end=True)
                print("🔚 音声ストリーム終了通知")
                
                # 転写結果を待機
                print("⏳ 転写結果待機（最大15秒）...")
                timeout_count = 0
                all_responses = []
                
                async for response in session.receive():
                    timeout_count += 1
                    
                    if response.text is not None:
                        text = response.text.strip()
                        if text:
                            all_responses.append(text)
                            print(f"📝 部分結果: {text}")
                    
                    # サーバーコンテンツをチェック
                    if hasattr(response, 'server_content') and response.server_content:
                        if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                            print("✅ 転写完了")
                            break
                    
                    # タイムアウト (15秒)
                    if timeout_count > 150:
                        print("⏰ タイムアウト")
                        break
                    
                    await asyncio.sleep(0.1)
                
                # 最終結果を返す
                if all_responses:
                    final_result = " ".join(all_responses)
                    print(f"📄 最終転写結果: '{final_result}'")
                    return final_result
                else:
                    print("❌ 転写結果が取得できませんでした")
                    return None
                    
        except Exception as e:
            print(f"❌ 転写エラー: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def end_session(self):
        """転写セッション終了"""
        print("🔚 転写サービス終了")

    async def cleanup(self):
        """リソースクリーンアップ"""
        await self.end_session()