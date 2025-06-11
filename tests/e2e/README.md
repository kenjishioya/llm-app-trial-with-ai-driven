# 🎭 E2E Tests (Playwright)

このディレクトリは**エンドツーエンドテスト**専用です。
**Playwright**を使用してブラウザでの実際のユーザー操作をテストします。

## 📋 用途
- フロントエンド ↔ バックエンド統合テスト
- 実際のブラウザ操作テスト (Chromium, Firefox, Safari)
- 全体フローテスト（チャット送信・応答・ストリーミング）
- エラーケース・レスポンシブデザイン検証

## 🗂️ テストカテゴリ別配置
- **バックエンドテスト**: `backend/tests/`
- **フロントエンドテスト**: `frontend/tests/`
- **E2Eテスト**: `tests/e2e/` (ここ)

## 🚀 実行方法

### 基本実行
```bash
# E2Eテスト実行（ヘッドレス）
npm run test:e2e

# UI付きで実行（推奨）
npm run test:e2e:ui

# ヘッド表示で実行（デバッグ用）
npm run test:e2e:headed

# デバッグモード
npm run test:e2e:debug

# レポート表示
npm run test:e2e:report
```

### 個別テスト実行
```bash
# 基本チャットフローのみ
npx playwright test basic-chat.spec.ts

# エラーケースのみ
npx playwright test error-scenarios.spec.ts

# 特定のブラウザのみ
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## 📁 テストファイル構成

```
tests/e2e/
├── basic-chat.spec.ts       # 基本チャット機能
├── error-scenarios.spec.ts  # エラーケース・例外処理
└── README.md               # このファイル
```

## 🧪 テスト内容

### basic-chat.spec.ts
- ✅ チャットページ表示確認
- ✅ メッセージ送信・応答受信フロー
- ✅ Enterキー・Shift+Enter操作
- ✅ 複数メッセージ送信
- ✅ セッション継続（リロード後）
- ✅ レスポンシブデザイン

### error-scenarios.spec.ts
- ✅ 入力バリデーション（空文字・文字数制限）
- ✅ ネットワークエラーシミュレーション
- ✅ GraphQL APIエラー処理
- ✅ SSE接続エラー・再接続
- ✅ 重複送信防止
- ✅ タイムアウト処理
- ✅ JavaScriptエラー監視
- ✅ セッション復旧エラー

## ⚙️ 前提条件

テスト実行前に以下のサービスが起動している必要があります：

```bash
# フロントエンド（localhost:3000）
cd frontend && npm run dev

# バックエンド（localhost:8000）
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**注意**: playwright.config.tsの`webServer`設定により、テスト実行時に自動起動されます。

## 📊 レポート・結果

- **HTMLレポート**: `playwright-report/index.html`
- **JSON結果**: `test-results.json`
- **スクリーンショット**: `test-results/` (失敗時のみ)
- **動画録画**: `test-results/` (失敗時のみ)

## 🔧 設定ファイル

- **playwright.config.ts**: Playwright主設定
- **package.json**: npmスクリプト定義

## 🚨 トラブルシューティング

### よくある問題
1. **ポートが使用中**: 3000/8000ポートが使用されていないか確認
2. **ブラウザ未インストール**: `npx playwright install` を実行
3. **タイムアウト**: 重いテストは timeout 設定を調整

### デバッグ方法
```bash
# UI付きデバッグ
npm run test:e2e:debug

# 特定のテストのみデバッグ
npx playwright test basic-chat.spec.ts --debug
```
