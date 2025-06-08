# リアルタイム音声転写アプリ - アーキテクチャ設計書

## プロジェクト概要
現在のモノリシック構成（バックエンドでマイク収集も実行）から、フロントエンド/バックエンド分離アーキテクチャへ移行する。

## 目標アーキテクチャ

### 全体構成
```
Frontend (Browser) ←→ Backend (Python API) ←→ Google Gemini Live API
     ↑                        ↑
  マイク収集              リアルタイム転写
  音声送信                 結果配信
  結果表示
```

### データフロー
1. **音声収集**: フロントエンド（ブラウザ）でマイク音声をキャプチャ
2. **音声送信**: WebSocketでリアルタイムに音声データをバックエンドに送信
3. **転写処理**: バックエンドでGemini Live APIを使用して転写
4. **結果配信**: WebSocketで転写結果をフロントエンドに配信
5. **表示更新**: フロントエンドでリアルタイム転写結果を表示

## 技術スタック

### フロントエンド
- **React + TypeScript**: コンポーネントベース開発、型安全性
- **Web Audio API**: ブラウザネイティブ音声処理
- **WebSocket API**: リアルタイム双方向通信
- **Vite**: 高速開発環境とHMR
- **状態管理**: React hooks（useState, useEffect, useRef）

### バックエンド
- **FastAPI**: 非同期処理、自動API文書生成、WebSocket対応
- **WebSocket**: 持続的接続によるリアルタイム通信
- **Google GenAI**: 既存のGemini Live API連携を維持
- **uvicorn**: ASGI サーバー

### 通信プロトコル
- **WebSocket**: 音声データストリーミング + 転写結果配信
- **Binary Format**: 音声データ効率送信（Base64エンコード）
- **JSON**: 制御メッセージと転写結果

## 実装計画

### Phase 1: バックエンドAPI化 🎯
**目標**: 現在のtranscribe.pyをWebSocket APIに変換

1. **FastAPI環境構築**
   - pyproject.tomlに依存関係追加
   - FastAPIアプリケーション基盤作成

2. **WebSocketエンドポイント実装**
   - `/ws/transcribe` エンドポイント作成
   - 接続管理とセッション処理

3. **音声処理ロジック移植**
   - 既存のGemini Live API連携コードを移植
   - 音声データ受信・転送処理

4. **リアルタイム配信**
   - 転写結果のWebSocket配信
   - エラーハンドリングと接続状態管理

### Phase 2: フロントエンド構築 🎯
**目標**: React + TypeScriptでリアルタイム音声収集UI構築

1. **開発環境構築**
   - Vite + React + TypeScript セットアップ
   - 必要なライブラリインストール

2. **音声収集機能**
   - Web Audio APIでマイクアクセス
   - AudioContextと音声データ処理
   - リアルタイム音声データ取得

3. **WebSocket通信**
   - WebSocket接続管理
   - 音声データ送信（Binary/Base64）
   - 転写結果受信処理

4. **UI実装**
   - 録音開始/停止ボタン
   - リアルタイム転写結果表示
   - 接続状態インジケーター

### Phase 3: 統合とテスト 🎯
**目標**: エンドツーエンド接続とパフォーマンス最適化

1. **統合テスト**
   - フロントエンド ↔ バックエンド接続確認
   - 音声データ送受信テスト
   - 転写精度・遅延測定

2. **最適化**
   - 音声データ圧縮・効率化
   - WebSocket接続安定化
   - エラー処理とリトライ機能

3. **ユーザビリティ向上**
   - ロード状態表示
   - エラーメッセージ表示
   - 音声レベルビジュアライザー

## API仕様設計

### WebSocket エンドポイント
```
ws://localhost:8000/ws/transcribe
```

### メッセージフォーマット

**音声データ送信** (Client → Server):
```json
{
  "type": "audio_data",
  "data": "base64_encoded_audio_data",
  "timestamp": 1234567890
}
```

**制御メッセージ** (Client → Server):
```json
{
  "type": "start_transcription"
}
```

**転写結果** (Server → Client):
```json
{
  "type": "transcription_result",
  "text": "転写されたテキスト",
  "is_partial": false,
  "timestamp": 1234567890
}
```

**エラー通知** (Server → Client):
```json
{
  "type": "error",
  "message": "エラーメッセージ",
  "code": "error_code"
}
```

## ディレクトリ構造（予定）

```
realtime_transcription_app/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPIアプリケーション
│   │   ├── websocket_handler.py # WebSocket処理
│   │   ├── transcribe_service.py # Gemini API連携
│   │   └── models/              # データモデル
│   └── requirements files...
├── frontend/
│   ├── src/
│   │   ├── components/          # Reactコンポーネント
│   │   ├── hooks/               # カスタムhooks
│   │   ├── services/            # API通信
│   │   └── types/               # TypeScript型定義
│   ├── package.json
│   └── vite.config.ts
└── ARCHITECTURE.md              # このファイル
```

## パフォーマンス要件

- **音声遅延**: < 500ms（収集→転写結果表示）
- **接続安定性**: 長時間接続維持
- **音声品質**: 16kHz, mono, 16-bit（現在の設定維持）
- **同時接続**: 初期は1接続、将来的に複数接続対応

## セキュリティ考慮事項

- **CORS設定**: フロントエンド・バックエンド間通信
- **WebSocket認証**: 必要に応じてトークンベース認証
- **音声データ**: 一時的なメモリ保存のみ、永続化しない
- **API キー**: 環境変数での管理継続