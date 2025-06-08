"""
実際のマイク音声でWebSocket APIをテスト
"""
import asyncio
import websockets
import json
import base64
import numpy as np
import pyaudio
from typing import Optional

async def test_with_microphone():
    """マイク音声でWebSocket APIテスト"""
    
    # WebSocket接続
    uri = "ws://localhost:8000/ws/transcribe"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"🔗 WebSocket接続成功: {uri}")
            
            # セッション開始
            await websocket.send(json.dumps({"type": "start_session"}))
            response = await websocket.recv()
            print(f"📥 応答: {response}")
            
            # マイク録音設定
            audio = pyaudio.PyAudio()
            stream = None
            
            try:
                # マイクストリーム開始（元のtranscribe.pyと同じ設定）
                stream = audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1600  # 100ms分
                )
                
                print("🎤 5秒間録音開始...")
                print("何か話してください...")
                
                # 5秒間録音して音声データを蓄積
                audio_chunks = []
                total_audio_level = 0
                audio_count = 0
                
                for i in range(50):  # 50 * 100ms = 5秒
                    audio_data = stream.read(1600, exception_on_overflow=False)
                    audio_chunks.append(audio_data)
                    
                    # 音声レベル確認
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    level = np.sqrt(np.mean(audio_array**2))
                    
                    if level > 20:
                        total_audio_level += level
                        audio_count += 1
                        if i % 10 == 0:  # 1秒ごとに表示
                            print(f"🎤 音声検出中... レベル: {level:.0f}")
                    
                    await asyncio.sleep(0.1)
                
                print("🔚 録音終了")
                
                # 平均音声レベルを表示
                if audio_count > 0:
                    avg_level = total_audio_level / audio_count
                    print(f"📊 平均音声レベル: {avg_level:.0f}")
                else:
                    print("⚠️ 音声が検出されませんでした")
                
                # 全音声データを結合
                full_audio = b''.join(audio_chunks)
                print(f"🎵 録音完了: {len(full_audio)} bytes")
                
                # Base64エンコードしてWebSocketで送信
                encoded_audio = base64.b64encode(full_audio).decode('utf-8')
                audio_message = {
                    "type": "audio_chunk",
                    "data": encoded_audio,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                print("📤 音声データ送信中...")
                await websocket.send(json.dumps(audio_message))
                
                # 転写結果待機
                print("⏳ 転写結果待機...")
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=20.0)
                    result = json.loads(response)
                    
                    if result["type"] == "transcription_result":
                        print("=" * 50)
                        print(f"📝 転写結果: '{result['text']}'")
                        print("=" * 50)
                    else:
                        print(f"📥 応答: {response}")
                        
                except asyncio.TimeoutError:
                    print("⏰ タイムアウト: 転写結果が返されませんでした")
                
            except Exception as e:
                print(f"❌ 録音エラー: {e}")
            finally:
                if stream:
                    stream.stop_stream()
                    stream.close()
                audio.terminate()
            
            # セッション終了
            await websocket.send(json.dumps({"type": "end_session"}))
            final_response = await websocket.recv()
            print(f"🔚 終了応答: {final_response}")
            
    except ConnectionRefusedError:
        print("❌ 接続拒否: サーバーが起動していません")
        print("サーバーを起動してください: uv run python -m src.main")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    print("🎯 マイク音声テスト開始")
    print("注意: マイクへのアクセス許可が必要です")
    asyncio.run(test_with_microphone())