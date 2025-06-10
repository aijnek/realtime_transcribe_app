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
        print("📢 文字起こしサービス準備完了")
        return True

    async def transcribe_audio_chunk(self, audio_data: bytes) -> Optional[str]:
        """音声チャンクを文字起こし - 元のtranscribe.pyパターンを使用"""
        
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
                print("⏳ 転写結果待機（最大10秒）...")
                all_responses = []
                
                try:
                    # asyncio.wait_forでタイムアウトを確実に制御
                    async def collect_responses():
                        async for response in session.receive():
                            print(f"📨 レスポンス受信: {type(response)}")
                            
                            if response.text is not None:
                                text = response.text.strip()
                                if text:
                                    all_responses.append(text)
                                    print(f"📝 部分結果: {text}")
                            
                            # サーバーコンテンツをチェック
                            if hasattr(response, 'server_content') and response.server_content:
                                print(f"🔍 サーバーコンテンツ: {response.server_content}")
                                if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                                    print("✅ 文字起こし完了")
                                    break
                    
                    await asyncio.wait_for(collect_responses(), timeout=10.0)
                    
                except asyncio.TimeoutError:
                    print("⏰ 10秒でタイムアウト - 強制終了")
                except Exception as e:
                    print(f"❌ レスポンス処理エラー: {e}")
                
                # 最終結果を返す
                if all_responses:
                    final_result = " ".join(all_responses)
                    print(f"📄 最終文字起こし結果: '{final_result}'")
                    return final_result
                else:
                    print("❌ 文字起こし結果が取得できませんでした")
                    return None
                    
        except Exception as e:
            print(f"❌ 文字起こしエラー: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def end_session(self):
        """文字起こしセッション終了"""
        print("🔚 文字起こしサービス終了")

    async def cleanup(self):
        """リソースクリーンアップ"""
        await self.end_session()