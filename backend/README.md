# Backend - リアルタイム音声文字起こしAPI

FastAPIとWebSocketを使用したリアルタイム音声文字起こしのバックエンドサービス。Google AIのGemini Live APIを活用し、高精度な日本語音声認識を実現します。

## 主な機能

- **リアルタイム音声認識**: WebSocketを使用した低遅延な音声文字起こし
- **Gemini Live API連携**: Google AIによる高精度な音声認識
- **音声処理**: 16kHz mono PCM音声の最適化処理
- **日本語最適化**: 
  - フィラー（「えーと」「あのー」など）の自動除去
  - 自然な日本語文章への整形
  - 句読点の適切な配置

## 技術スタック

- **Webフレームワーク**: FastAPI
- **WebSocket**: websockets
- **音声認識**: Google Gemini Live API
- **音声処理**: PyAudio
- **数値計算**: NumPy
- **サーバー**: Uvicorn
- **環境管理**: Python-dotenv

## セットアップ

### 必要条件
- Python 3.13以上
- UVパッケージマネージャー

### インストール
```bash
# 依存関係のインストール
uv pip install -r requirements.txt
```

### 環境変数の設定
`.env`ファイルを作成し、以下の環境変数を設定してください：
```
GOOGLE_API_KEY=your_api_key_here
```

## 使用方法

### サーバーの起動
```bash
uv run python -m src.main
```

### テスト
```bash
# マイク入力テスト
uv run python mic_test.py
```

## API エンドポイント

### WebSocket
- `ws://localhost:8000/ws/transcribe`
  - 音声データをストリーミング
  - リアルタイムで文字起こし結果を返却

### HTTP
- `GET /health`
  - サーバーの状態確認用エンドポイント

## 開発

### プロジェクト構造
```
backend/
├── src/           # ソースコード
├── .venv/         # 仮想環境
├── mic_test.py    # マイクテスト用スクリプト
└── pyproject.toml # プロジェクト設定
```

### 依存関係の管理
- brew install portaudio (pyaudioのインストールに必要です)
- `pyproject.toml`で依存関係を管理
- UVを使用してパッケージのインストールと管理
