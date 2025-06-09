# リアルタイム音声文字起こしアプリ

Google Gemini Live APIを使用したリアルタイム音声文字起こしアプリケーション。フロントエンド/バックエンド分離アーキテクチャで、ブラウザからの音声入力をリアルタイムで日本語に文字起こしします。

## 機能

- **リアルタイム音声文字起こし**: Google Gemini Live APIによる高精度な音声認識
- **フィラー除去**: 「えー」「あのー」などの不要な音を自動削除
- **自然な日本語整形**: 重複や冗長な表現を自然な日本語に修正
- **WebSocket通信**: フロントエンド/バックエンド間のリアルタイム通信

## プロジェクト構成

```
realtime_transcription_app/
├── backend/                    # FastAPI + WebSocketサーバー
│   ├── src/
│   │   ├── main.py            # FastAPIアプリケーション
│   │   ├── transcribe_service.py # Gemini Live API連携
│   │   └── transcribe.py      # オリジナル文字起こしスクリプト
│   ├── mic_test.py            # マイクテスト用クライアント
│   └── pyproject.toml         # 依存関係管理
├── frontend/                   # React + TypeScript Webアプリ
│   ├── src/
│   │   ├── components/        # Reactコンポーネント
│   │   ├── hooks/             # カスタムフック
│   │   └── App.tsx           # メインアプリ
│   ├── package.json          # フロントエンド依存関係
│   └── vite.config.ts        # Vite設定
├── ARCHITECTURE.md            # 詳細アーキテクチャ設計
└── CLAUDE.md                  # 開発ガイダンス
```

## セットアップ

### 必要な環境

- Python 3.13+
- Node.js 18+
- uv (Pythonパッケージマネージャー)
- npm (Node.jsパッケージマネージャー)
- Google API Key (Gemini API)

### バックエンド

1. **依存関係インストール**
   ```bash
   cd backend
   uv sync
   ```

2. **環境変数設定**
   ```bash
   # backend/.env ファイルを作成
   export GOOGLE_API_KEY="your_google_api_key_here"
   ```

3. **サーバー起動**
   ```bash
   uv run python -m src.main
   ```
   
   サーバーは http://localhost:8000 で起動します。

### フロントエンド

1. **依存関係インストール**
   ```bash
   cd frontend
   npm install
   ```

2. **開発サーバー起動**
   ```bash
   npm run dev
   ```
   
   フロントエンドは http://localhost:5173 で起動します。

## 使用方法

1. **両方のサーバーを起動**
   ```bash
   # ターミナル1: バックエンド
   cd backend
   uv run python -m src.main
   
   # ターミナル2: フロントエンド  
   cd frontend
   npm run dev
   ```

2. **ブラウザでアクセス**
   - Safariでhttp://localhost:5173 を開く (いまのところChromeではエラーになります)
   - 「録音開始」ボタンをクリック
   - マイクアクセスを許可
   - 話し始める（2秒間沈黙で文字起こし実行）
   - 文字起こし結果がリアルタイムで表示される

### テスト（バックエンドのみ）

マイク入力でバックエンドAPIをテスト：

```bash
cd backend
uv run python mic_test.py
```

## API仕様

### WebSocket エンドポイント

- **URL**: `ws://localhost:8000/ws/transcribe`
- **プロトコル**: JSON over WebSocket

### メッセージフォーマット

**セッション開始** (Client → Server):
```json
{"type": "start_session"}
```

**音声データ送信** (Client → Server):
```json
{
  "type": "audio_chunk",
  "data": "base64_encoded_audio_data",
  "timestamp": 1234567890
}
```

**文字起こし結果** (Server → Client):
```json
{
  "type": "transcription_result",
  "text": "文字起こしされたテキスト",
  "timestamp": 1234567890
}
```

## 開発状況

### 完了済み機能
- ✅ バックエンドAPI (FastAPI + WebSocket)
- ✅ Gemini Live API連携
- ✅ 音声チャンク処理
- ✅ 日本語文字起こし・整形機能
- ✅ フロントエンド (React + TypeScript)
- ✅ ブラウザマイク音声収集
- ✅ 音声区切り検出
- ✅ リアルタイムUI表示
- ✅ エンドツーエンド統合

### 主な特徴
- **ブラウザベース**: インストール不要、Webブラウザで動作
- **リアルタイム処理**: 発話終了を自動検出して即座に文字起こし
- **高精度文字起こし**: Google Gemini Live APIによる日本語認識
- **フィラー除去**: 「えー」「あのー」等の不要語句を自動削除
- **モダンUI**: レスポンシブデザイン、視覚的フィードバック

## 技術スタック

- **バックエンド**: FastAPI, WebSocket, Google GenAI, uvicorn
- **フロントエンド**: React, TypeScript, Web Audio API, Vite
- **通信**: WebSocket (Binary + JSON)
- **音声処理**: Google Gemini Live API
- **UI**: モダンCSS、レスポンシブデザイン
- **開発環境**: uv (Python), npm (Node.js)
