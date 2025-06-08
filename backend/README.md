# Backend - リアルタイム音声文字起こしAPI

FastAPIとWebSocketを使用したリアルタイム音声文字起こしのバックエンドサービス。

## 機能

- **WebSocket API**: リアルタイム音声データ受信
- **Gemini Live API連携**: Google AI による高精度文字起こし
- **音声処理**: 16kHz mono PCM音声の処理
- **日本語最適化**: フィラー除去と自然な日本語整形

## API エンドポイント

### WebSocket
- `ws://localhost:8000/ws/transcribe` - 音声文字起こしWebSocket

### HTTP
- `GET /health` - ヘルスチェック

## 開発

### 起動
```bash
uv run python -m src.main
```

### テスト
```bash
# マイク入力テスト
uv run python mic_test.py
```

### 依存関係
- `fastapi`: Webフレームワーク
- `google-genai`: Gemini Live API
- `websockets`: WebSocket通信
- `uvicorn`: ASGIサーバー
- `python-dotenv`: 環境変数管理