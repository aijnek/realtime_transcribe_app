# リアルタイム音声文字起こしアプリ - フロントエンド

このプロジェクトは、Google Gemini Live APIを使用したリアルタイム音声文字起こしアプリケーションのフロントエンド部分です。React + TypeScript + Viteを使用して構築されています。

## 主な機能

- ブラウザマイクからのリアルタイム音声収集
- WebSocketを使用したバックエンドとのリアルタイム通信
- 文字起こし結果のリアルタイム表示
- 音声レベルビジュアライザー
- レスポンシブデザイン

## 技術スタック

- **フレームワーク**: React 18
- **言語**: TypeScript
- **ビルドツール**: Vite
- **音声処理**: Web Audio API
- **通信**: WebSocket API
- **スタイリング**: モダンCSS

## 開発環境のセットアップ

### 必要条件

- Node.js 18+
- npm (Node.jsパッケージマネージャー)

### インストール

```bash
# 依存関係のインストール
npm install
```

### 開発サーバーの起動

```bash
npm run dev
```

アプリケーションは http://localhost:5173 で起動します。

### ビルド

```bash
npm run build
```

## プロジェクト構造

```
frontend/
├── src/
│   ├── components/        # Reactコンポーネント
│   ├── hooks/            # カスタムフック
│   ├── services/         # API通信サービス
│   ├── types/            # TypeScript型定義
│   └── App.tsx          # メインアプリケーション
├── public/              # 静的ファイル
├── index.html          # エントリーポイント
├── package.json        # 依存関係管理
└── vite.config.ts      # Vite設定
```

## 使用方法

1. バックエンドサーバーを起動（http://localhost:8000）
2. フロントエンド開発サーバーを起動（http://localhost:5173）
3. ブラウザで http://localhost:5173 にアクセス
4. 「録音開始」ボタンをクリック
5. マイクアクセスを許可
6. 話し始める（2秒間の沈黙で文字起こしが実行されます）

## 開発ガイドライン

### コンポーネント設計

- 機能ごとにコンポーネントを分割
- カスタムフックを使用してロジックを分離
- TypeScriptの型定義を活用

### 状態管理

- React Hooksを使用（useState, useEffect, useRef）
- 必要に応じてContext APIを活用

### スタイリング

- モダンなCSSアプローチ
- レスポンシブデザイン
- アクセシビリティに配慮

## 注意事項

- 現在のところ、Safariブラウザでの動作を推奨
- Chromeでは一部機能が制限される可能性があります
- マイクアクセスにはブラウザの許可が必要です

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
