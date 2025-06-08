import os
import pyaudio
import asyncio
import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

system_instruction = """
あなたは正確な音声文字起こしシステムです。聞こえた音声を正確に文字起こししてください。
会話や応答は不要で、聞こえた内容を書き起こすだけです。
ただし、えー、あのー、などのフィラー音は削除して回答してください。
重複や冗長な表現があれば自然な日本語に修正してください。
"""

async def start_transcription(api_key):
    """文字起こし"""
    
    # Live API設定 - 文字起こし専用に最適化
    client = genai.Client(api_key=api_key)
    model = "gemini-2.0-flash-live-001"
    config = {
        "response_modalities": ["TEXT"],
        "system_instruction": types.Content(
            parts=[types.Part(text=system_instruction)],
        ),
        "realtime_input_config": {
            "automatic_activity_detection": {
                "disabled": False,
                "start_of_speech_sensitivity": types.StartSensitivity.START_SENSITIVITY_HIGH,
                "end_of_speech_sensitivity": types.EndSensitivity.END_SENSITIVITY_LOW,  # 発話終了を遅めに検出
                "silence_duration_ms": 1500,  # 1.5秒沈黙で終了
                "prefix_padding_ms": 300,  # 発話開始前の音声も含める
            }
        }
    }
    
    # PyAudio設定
    audio = pyaudio.PyAudio()
    stream = None
    
    try:
        # マイクストリーム開始
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1600  # 100ms分
        )
        
        print("📢 録音中です(10秒間)...")
        
        async with client.aio.live.connect(model=model, config=config) as session:
            
            total_audio_level = 0
            audio_count = 0
            
            # 10秒間音声を録音・送信
            for i in range(100):  # 100 * 100ms = 10秒
                audio_data = stream.read(1600, exception_on_overflow=False)
                
                # 音声レベル確認
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                level = np.sqrt(np.mean(audio_array**2))
                
                if level > 20:  # より低い閾値で検出
                    total_audio_level += level
                    audio_count += 1
                    if i % 10 == 0:  # 1秒ごとに表示
                        print(f"🎤 音声検出中... レベル: {level:.0f}")
                
                # Live APIに送信
                await session.send_realtime_input(
                    audio=types.Blob(
                        data=audio_data,
                        mime_type="audio/pcm;rate=16000"
                    )
                )
                
                await asyncio.sleep(0.1)
            
            # 平均音声レベルを表示
            if audio_count > 0:
                avg_level = total_audio_level / audio_count
                print(f"📊 平均音声レベル: {avg_level:.0f}")
            else:
                print("⚠️  音声が検出されませんでした")
            
            print("🔚 録音終了、応答待機中...")
            
            # 音声ストリーム終了を通知
            await session.send_realtime_input(audio_stream_end=True)
            
            # より長い時間応答を待機
            print("⏳ 文字起こし処理中（最大15秒待機）...")
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
                        print("✅ 文字起こし完了")
                        break
                
                # タイムアウト (15秒)
                if timeout_count > 150:
                    print("⏰ タイムアウト")
                    break
                
                await asyncio.sleep(0.1)
            
            # 最終結果を表示
            if all_responses:
                final_result = " ".join(all_responses)
                print("=" * 50)
                print(f"📄 最終文字起こし結果:")
                print(f"'{final_result}'")
                print("=" * 50)
            else:
                print("❌ 文字起こし結果が取得できませんでした")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # ストリームが定義済みかつ開いていれば停止・クローズ
        if stream is not None:
            try:
                stream.stop_stream()
            except Exception:
                pass
            stream.close()
        # PyAudioインスタンスを解放
        audio.terminate()


# メイン関数
async def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ APIキーを設定してください")
        return
    
    await start_transcription(api_key)

if __name__ == "__main__":
    asyncio.run(main())
